import logging
from enum import Enum


class DATATYPE(Enum):
    TEMPERATURE = 0



class Datahandler():

    def __init__(self, controller):
        self.__controller = controller
        self.__temp = self.__controller.bricklets["temperature"]

        self.__aggregatedValues = {DATATYPE.TEMPERATURE : []}

        logging.info("Initializing: "+ type(self).__name__)



    def update(self):
        self.__aggregatedValues[DATATYPE.TEMPERATURE].append(self.__temp.getTemperature())
        logging.debug("Updating: "+ type(self).__name__)

    

    def getRecentDataPoints(self, datatype, count):
        return self.__aggregatedValues[datatype][-count:]



    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)