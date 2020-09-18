import logging
from enum import Enum

from settings import settings


class DATATYPE(Enum):
    TEMPERATURE = 0



class Datahandler():

    def __init__(self, controller):
        self.__controller = controller
        self.__temp = self.__controller.bricklets["temperature"]

        self.__intermediateMeasurements = []
        self.__aggregatedValues = {DATATYPE.TEMPERATURE : []}

        logging.info("Initializing: "+ type(self).__name__)



    def update(self):
        if self.__controller.currentTick % settings["TicksPerMeasurement"] == 0:
            self.__intermediateMeasurements.append(self.__temp.getTemperature())
            if len(self.__intermediateMeasurements) == settings["AggregationsPerDataPoint"]:
                average = sum(self.__intermediateMeasurements)
                average /= len(self.__intermediateMeasurements)
                self.__aggregatedValues[DATATYPE.TEMPERATURE].append(average)
                self.__intermediateMeasurements = []
        logging.debug("Updating: "+ type(self).__name__)

    

    def getRecentDataPoints(self, datatype, count):
        return self.__aggregatedValues[datatype][-count:]



    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)