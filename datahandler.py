import logging
from enum import Enum

from settings import settings


class DATATYPE(Enum):
    TEMPERATURE = 0
    LIGHT = 1
    HUMIDITY = 2
    PRESSURE = 3



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

    

    def getRecentDataPoints(self, datatype, count):
        return self.__datacontainer[datatype].getRecentDataPoints(count)



    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)





class DataContainer():

    def __init__(self, controller, datatype):
        self.__controller = controller
        self.__datatype = datatype

        if self.__datatype == DATATYPE.TEMPERATURE:
            self.__bricklet = self.__controller.bricklets["temperature"]
        elif self.__datatype == DATATYPE.LIGHT:
            self.__bricklet = self.__controller.bricklets["light"]
        elif self.__datatype == DATATYPE.HUMIDITY:
            self.__bricklet = self.__controller.bricklets["humidity"]
        elif self.__datatype == DATATYPE.PRESSURE:
            self.__bricklet = self.__controller.bricklets["barometer"]

        self.__intermediateMeasurements = []
        self.__aggregatedValues = []



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
            self.__aggregatedValues.append(average)
            self.__intermediateMeasurements = []

    

    def getRecentDataPoints(self, count):
        return self.__aggregatedValues[-count:]