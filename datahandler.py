import logging
from enum import Enum

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



class Datahandler():

    def __init__(self, controller):
        self.__controller = controller

        self.__datacontainer = {}
        for datatype in DATATYPE:
            self.__datacontainer[datatype] = DataContainer(self.__controller, datatype)

        logging.info("Initializing: "+ type(self).__name__)



    def update(self):
        if self.__controller.currentTick % settings["TicksPerMeasurement"] == 0:
            for datacontainer in self.__datacontainer.values():
                datacontainer.performMeasurement()
        logging.debug("Updating: "+ type(self).__name__)

    

    def getRecentDataPoints(self, datatype, timeframeType, count, offset): #Returns array containing values (timestamp, value, numAggregations)
        return self.__datacontainer[datatype].getRecentDataPoints(timeframeType, count, offset)

    

    def getTotalNumberOfDataPoints(self, datatype, timeframeType):
        return self.__datacontainer[datatype].getTotalNumberOfDataPoints(timeframeType)



    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)





class DataContainer():

    def __init__(self, controller, datatype):
        self.__controller = controller
        self.__datatype = datatype
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

        self.__valueID = 0
        self.__aggregatedValues = [] # Format is (id, timestamp, value)
        self.__aggregationsPerTimeframe = {} # Dict of different time frames. each entry is an array of values (timestamp, value, numAggregations)
        self.__indexNextValueToBeMergedIntoTimeframe = {} # Dict of different time frames. Each entry is an integer denoting the first position from __aggregatedValues that still needs to be merged into __aggregationsPerTimeframe

        self.__initiateData()



    def __initiateData(self):
        for [timeframeName, _ ] in self.__timeframes:
            self.__aggregationsPerTimeframe[timeframeName] = []
            self.__indexNextValueToBeMergedIntoTimeframe[timeframeName] = -1



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

            timestamp = self.__clock.getTimestamp()
            self.__aggregatedValues.append((id, timestamp, average))
                

            #Check whether intermediate aggregations can be combined into a new aggregated field
            #TODO needs some handling for overlapping cases where a timeframe was already initialized with partial data
            for [timeframeName, timeFrameDuration] in self.__timeframes:
                lastTimeframe = -1
                if len(self.__aggregationsPerTimeframe[timeframeName]) > 0:
                    lastTimeframe = int(self.__aggregationsPerTimeframe[timeframeName][-1][0] // timeFrameDuration)
                currentTimeFrame = int(timestamp // timeFrameDuration)

                #Timeframe has advanced, so data values for new timeframe need to be updated
                if currentTimeFrame > lastTimeframe:

                    #First check whether time frame has moved more than one step and, if so, add some none values
                    diff = currentTimeFrame - lastTimeframe
                    if lastTimeframe != -1 and diff > 1:
                        for i in range(1, diff):
                            self.__aggregationsPerTimeframe[timeframeName].append((int((lastTimeframe + i) * timeFrameDuration), None, 0))

                    #Special case: At the start of the measurements, the first aggregated value will be for currentTimeFrame. I.e., there are no previous values yet that can already be merged. So only merge if there are some previous values.
                    if self.__indexNextValueToBeMergedIntoTimeframe[timeframeName] != -1:
                        countToBeMerged = (len(self.__aggregatedValues) - 1) - self.__indexNextValueToBeMergedIntoTimeframe[timeframeName]
                        mergedValues = 0
                        for (_, _, value) in self.__aggregatedValues[(-1 - countToBeMerged):-1]:
                            mergedValues += value
                        mergedValues /= countToBeMerged
                        self.__aggregationsPerTimeframe[timeframeName].append((int(currentTimeFrame * timeFrameDuration), mergedValues, countToBeMerged))
                    
                    self.__indexNextValueToBeMergedIntoTimeframe[timeframeName] = len(self.__aggregatedValues) - 1

            #Everything updated. Reset intermediate measurements
            self.__intermediateMeasurements = []

    

    def getRecentDataPoints(self, timeframeName, count, offset):
        length = len(self.__aggregationsPerTimeframe[timeframeName])
        return self.__aggregationsPerTimeframe[timeframeName][max(length - count - offset, 0) : max(length - offset, 0)]

    

    def getTotalNumberOfDataPoints(self, timeframeName):
        return len(self.__aggregationsPerTimeframe[timeframeName])
