import logging
from enum import Enum
import os

from settings import settings


class DATATYPE(Enum):
    TEMPERATURE = 0
    LIGHT = 1
    HUMIDITY = 2
    PRESSURE = 3



DATATYPE_STRING_MAPPING = {
    DATATYPE.TEMPERATURE : "Temperature",
    DATATYPE.LIGHT : "Light",
    DATATYPE.HUMIDITY : "Humidity",
    DATATYPE.PRESSURE : "Pressure",
}



DATATYPE_SHORTSTRING_MAPPING = {
    DATATYPE.TEMPERATURE : "temp",
    DATATYPE.LIGHT : "light",
    DATATYPE.HUMIDITY : "humid",
    DATATYPE.PRESSURE : "press",
}



DB_HEADER = "version,creation date\n1,{}\nid,posix timestamp,value\n"



class Datahandler():

    def __init__(self, controller):
        self.__controller = controller
        self.__DBid = -1
        self.__initialized = False

        self.__datacontainer = {}
        for datatype in DATATYPE:
            self.__datacontainer[datatype] = DataContainer(self.__controller, datatype)

        logging.info("Creating: "+ type(self).__name__)
    

    
    def initializeDB(self, DBid): #DBid is integer. -1 for new database creation, otherwise an existing one with that ID is loaded.
        logging.info(f"Started DB (ID: {DBid}) initialization at time " + str(self.__controller.bricklets["clock"].getDateTime()))

        #New DB: set id to first unused integer
        if DBid < 0:
            self.__DBid = self.getExistingDBCount()
        else:
            self.__DBid = DBid

        #Create DB if non existant
        if not os.path.exists(settings["DBPath"]):
            os.mkdir(settings["DBPath"])
        if not os.path.exists(settings["DBPath"] + "/" + settings["DBFolderFormatstring"].format(self.__DBid)):
            os.mkdir(settings["DBPath"] + "/" + settings["DBFolderFormatstring"].format(self.__DBid))
        for shortstring in DATATYPE_SHORTSTRING_MAPPING.values():
            file = settings["DBPath"] + "/" + settings["DBFolderFormatstring"].format(self.__DBid) + "/" + shortstring + ".csv"
            if not os.path.exists(file):
                with open(file, "w") as f:
                    f.write(DB_HEADER.format(self.__controller.bricklets["clock"].getDateTime()))

        #Initialize each of the containers
        for container in self.__datacontainer.values():
            container.initializeData(self.__DBid)

        self.__initialized = True

        logging.info(f"Finished DB  (ID: {DBid} --> {self.__DBid}) initialization at time " + str(self.__controller.bricklets["clock"].getDateTime()))

    

    def getExistingDBCount(self):
        if not os.path.exists(settings["DBPath"]):
            return 0
        else:
            i = 0
            while True:
                if os.path.exists(settings["DBPath"] + "/" + settings["DBFolderFormatstring"].format(i)):
                    i += 1
                else:
                    break
            return i



    def update(self):
        if not self.__initialized:
            return

        if self.__controller.currentTick % settings["TicksPerMeasurement"] == 0:
            for datacontainer in self.__datacontainer.values():
                datacontainer.performMeasurement()
        logging.debug("Updating: "+ type(self).__name__)

    

    def getRecentDataPoints(self, datatype, timeframeType, count, offset): #Returns array containing values (timestamp, value, numAggregations)
        if not self.__initialized:
            return []

        return self.__datacontainer[datatype].getRecentDataPoints(timeframeType, count, offset)

    

    def getTotalNumberOfDataPoints(self, datatype, timeframeType):
        if not self.__initialized:
            return 0

        return self.__datacontainer[datatype].getTotalNumberOfDataPoints(timeframeType)

    

    def writeRecentDataToFile(self):
        if not self.__initialized:
            return
            
        for container in self.__datacontainer.values():
            container.writeRecentDataToFile()



    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)
        
        if not self.__initialized:
            return
        
        self.writeRecentDataToFile()








class DataContainer():

    def __init__(self, controller, datatype):
        self.__controller = controller
        self.__datatype = datatype
        self.__DBid = -1
        self.__clock = self.__controller.bricklets["clock"]

        if self.__datatype == DATATYPE.TEMPERATURE:
            self.__bricklet = self.__controller.bricklets["temperature"]
        elif self.__datatype == DATATYPE.LIGHT:
            self.__bricklet = self.__controller.bricklets["light"]
        elif self.__datatype == DATATYPE.HUMIDITY:
            self.__bricklet = self.__controller.bricklets["humidity"]
        elif self.__datatype == DATATYPE.PRESSURE:
            self.__bricklet = self.__controller.bricklets["barometer"]

        self.__timeframes = settings["DisplayTimeframes"]

        self.__intermediateMeasurements = []

        self.__nextID = 0
        self.__aggregatedValues = [] # Format is (id, timestamp, value)
        self.__aggregationsPerTimeframe = {} # Dict of different timeframes. each entry is an array of values [timestamp, value, numAggregations], where timestamp is the first timeunit in that frame
        self.__currentAggregationsPerTimeframe = {}     #Dict of timeframes. contains a single aggregated value [timestamp, value, numAggregations], where value has not been averaged yet.
                                                        #This is current set of measurements (which might overlap with the last time frame read from DB)

        self.__indexLastWrittenToFile = 0



    def initializeData(self, DBid):
        self.__DBid = DBid
        self.__DBfile = settings["DBPath"] + "/" + settings["DBFolderFormatstring"].format(self.__DBid) + "/" + DATATYPE_SHORTSTRING_MAPPING[self.__datatype] + ".csv"

        for [timeframeName, _ ] in self.__timeframes:
            self.__aggregationsPerTimeframe[timeframeName] = []
            self.__currentAggregationsPerTimeframe[timeframeName] = []

        #Read previous values from DB
        pastValues = []
        linecounter = 0
        with open(self.__DBfile, "r") as f:
            for line in f.readlines():
                line = line.rstrip("\n")

                #First 3 lines are header info. Skip those
                if linecounter < 3:
                    linecounter +=1
                    continue

                entry = line.split(",")
                pastValues.append(entry)
        

        if len(pastValues) > 0:
            #Set variables
            self.__nextID = int(pastValues[-1][0]) + 1


            #Compute timeframes from previous values
            initialTimestamp = int(pastValues[0][1])
            initialTimeframe = {}
            prevTimeframe = {}
            for [timeframeName, timeframeDuration] in self.__timeframes:
                initialTimeframe[timeframeName] = int(initialTimestamp // timeframeDuration)
                prevTimeframe[timeframeName] = initialTimeframe[timeframeName]-1

            for i in range(0, len(pastValues)):
                (_, timestamp, value) = pastValues[i]
                timestamp = int(timestamp)
                value = float(value)
                for [timeframeName, timeframeDuration] in self.__timeframes:
                    currentTimeframe = int(timestamp // timeframeDuration)
                    diff = currentTimeframe - prevTimeframe[timeframeName]
                    
                    #Check whether time frame has moved more than one step and, if so, add some none values
                    if diff > 1:
                        for i in range(1, diff):
                            self.__aggregationsPerTimeframe[timeframeName].append([int((prevTimeframe[timeframeName] + i) * timeframeDuration), None, 0])
                    
                    #Check whether the current datapoint creates a new entry
                    if diff >= 1:
                        self.__aggregationsPerTimeframe[timeframeName].append([int(currentTimeframe * timeframeDuration), value, 1])
                    else:
                        self.__aggregationsPerTimeframe[timeframeName][-1][1] += value
                        self.__aggregationsPerTimeframe[timeframeName][-1][2] += 1
                    
                    prevTimeframe[timeframeName] = currentTimeframe
            
            #Cut off last entry and move it into current aggregations
            for [timeframeName, _] in self.__timeframes:
                self.__currentAggregationsPerTimeframe[timeframeName] = self.__aggregationsPerTimeframe[timeframeName][-1]
                self.__aggregationsPerTimeframe[timeframeName] = self.__aggregationsPerTimeframe[timeframeName][:-1]
            
            #Compute averages for the timeframe values from above
            for [timeframeName, _] in self.__timeframes:
                for i in range(0, len(self.__aggregationsPerTimeframe[timeframeName])):
                    if self.__aggregationsPerTimeframe[timeframeName][i][2] > 1:
                        self.__aggregationsPerTimeframe[timeframeName][i][1] /= self.__aggregationsPerTimeframe[timeframeName][i][2]





    def performMeasurement(self):
        if self.__datatype == DATATYPE.TEMPERATURE:
            self.__intermediateMeasurements.append(self.__bricklet.getTemperature())
        elif self.__datatype == DATATYPE.LIGHT:
            self.__intermediateMeasurements.append(self.__bricklet.getLight())
        elif self.__datatype == DATATYPE.HUMIDITY:
            self.__intermediateMeasurements.append(self.__bricklet.getHumidity())
        elif self.__datatype == DATATYPE.PRESSURE:
            self.__intermediateMeasurements.append(self.__bricklet.getPressure())

        if len(self.__intermediateMeasurements) == settings["AggregationsPerDataPoint"]:
            average = sum(self.__intermediateMeasurements)
            average /= len(self.__intermediateMeasurements)
            self.__intermediateMeasurements = []

            timestamp = self.__clock.getTimestamp()
            self.__aggregatedValues.append((self.__nextID, timestamp, average))
            self.__nextID += 1


            for [timeframeName, timeframeDuration] in self.__timeframes:
                timeframeNow = int(timestamp // timeframeDuration)

                #Check whether there are any current measurements and add them if their respective timeframe has already concluded
                if not self.__currentAggregationsPerTimeframe[timeframeName] == []:
                    currentAggregationsTimeframe = int(self.__currentAggregationsPerTimeframe[timeframeName][0] // timeframeDuration)

                    if timeframeNow > currentAggregationsTimeframe:
                        self.__aggregationsPerTimeframe[timeframeName].append(self.__currentAggregationsPerTimeframe[timeframeName])
                        self.__aggregationsPerTimeframe[timeframeName][-1][1] /= self.__aggregationsPerTimeframe[timeframeName][-1][2] #compute average
                        self.__currentAggregationsPerTimeframe[timeframeName] = []
                    
                #Check whether more than one timeframe unit has passed since last measurement. add suitably many None entries
                #Note that, if more than one timeframe unit passes, then in particular current aggregations are empty
                if self.__currentAggregationsPerTimeframe[timeframeName] == [] and len(self.__aggregationsPerTimeframe[timeframeName]) > 0:
                    previousTimeframe = int(self.__aggregationsPerTimeframe[timeframeName][-1][0] // timeframeDuration)
                    diff = timeframeNow - previousTimeframe
                    for i in range(1, diff):
                        self.__aggregationsPerTimeframe[timeframeName].append([int((previousTimeframe + i) * timeframeDuration), None, 0])

            
                # Add intermediate aggregations to __currentAggregationsPerTimeframe
                if self.__currentAggregationsPerTimeframe[timeframeName] == []:
                    timeframeTimestamp = timeframeNow * timeframeDuration
                    self.__currentAggregationsPerTimeframe[timeframeName] = [timeframeTimestamp, average, 1]
                else:
                    self.__currentAggregationsPerTimeframe[timeframeName][1] += average
                    self.__currentAggregationsPerTimeframe[timeframeName][2] += 1

    

    def getRecentDataPoints(self, timeframeName, count, offset):
        data = self.__aggregationsPerTimeframe[timeframeName]
        if not self.__currentAggregationsPerTimeframe[timeframeName] == []:
            (timestamp, value, total) = self.__currentAggregationsPerTimeframe[timeframeName]
            data = data + [[timestamp, value, total]]
            data[-1][1] /= data[-1][2]
        length = len(data)
        return data[max(length - count - offset, 0) : max(length - offset, 0)]

    

    def getTotalNumberOfDataPoints(self, timeframeName):
        lenCurrAggregations = 0 if self.__currentAggregationsPerTimeframe[timeframeName] == [] else 1
        return len(self.__aggregationsPerTimeframe[timeframeName]) + lenCurrAggregations
    


    def writeRecentDataToFile(self):
        with open(self.__DBfile, "a") as f:
            for i in range(self.__indexLastWrittenToFile, len(self.__aggregatedValues)):
                (identifier, timestamp, value) = self.__aggregatedValues[i]
                f.write(f"{identifier},{timestamp},{value}\n")
        self.__indexLastWrittenToFile = len(self.__aggregatedValues) - 1
