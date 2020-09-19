HOST = "localhost"
PORT = 4223


from tinkerforge.ip_connection import IPConnection

import logging
import time


from datahandler import Datahandler, DATATYPE
from settings import settings

from bricklets.temperature import Temperature
from bricklets.light import Light
from bricklets.humidity import Humidity
from bricklets.barometer import Barometer
from bricklets.clock import Clock
from bricklets.lcd20x4 import LCD20x4
from bricklets.oled128x64 import OLED128x64
from bricklets.joystick import Joystick

from screens.mainscreen import MainScreen
from screens.datascreen import DataScreen



class Controller:

    mainController = ""    


    def __init__(self):
        self.bricklets = {}
        self.datahandler = None
        self.currentScreen = None

        self.ipcon = None
        self.currentTick = 0
        self.shutdown = False

        #Ensure that there is ever only a single controller instance
        if not Controller.mainController == "":
            logging.error("Controller already instantiated. Aborted second instantiation.")
            return
        else:
            self.mainController = self

        #Prepare Logging
        logginglevels = {
            "DEBUG" : logging.DEBUG,
            "INFO" : logging.INFO,
            "WARNING" : logging.WARNING,
            "ERROR" : logging.ERROR,
            "CRITICAL" : logging.CRITICAL,
        }
        logging.basicConfig(level=logginglevels.get(settings["LoggingLevel"], logging.ERROR), format = "LOGGING:%(levelname)s   %(message)s")

        #Create all bricklet classes and store them
        self.ipcon = IPConnection()
        self.ipcon.connect(HOST, PORT)

        self.bricklets["temperature"] = Temperature(self)
        self.bricklets["light"] = Light(self)
        self.bricklets["humidity"] = Humidity(self)
        self.bricklets["barometer"] = Barometer(self)
        self.bricklets["clock"] = Clock(self)
        self.bricklets["lcd20x4"] = LCD20x4(self)
        self.bricklets["oled128x64"] = OLED128x64(self)
        self.bricklets["joystick"] = Joystick(self)

        #Initialize data handler
        self.datahandler = Datahandler(self)

        #Initialize main screen
        #self.currentScreen = DataScreen(self, DATATYPE.PRESSURE)
        self.currentScreen = MainScreen(self)

        logging.info("Finished controller Initiatilization at time " + str(self.bricklets["clock"].getDateTime()))



    def startStation(self):

        while (self.currentTick < settings["TotalTicks"] or settings["TotalTicks"] < 0) and not self.shutdown:

            #Update data handler
            self.datahandler.update()

            #Update I/O
            self.bricklets["joystick"].update()

            #Update Screen
            self.currentScreen.update()

            #Sleep until the next tick can occur
            tickDuration = 1.0 / settings["TicksPerSecond"]
            delay = tickDuration - (time.time() % tickDuration)
            logging.debug("Current tick took " + str(time.time() % tickDuration) + " seconds. Next tick delay: " + str(delay))
            time.sleep(delay)
            self.currentTick = self.currentTick + 1


        #Program has finished. Shutdown.
        self.__shutdownStation()



    def __shutdownStation(self):
        logging.info("Shutdown at time " + str(self.bricklets["clock"].getDateTime()))
        for bricklet in self.bricklets.values():
            bricklet.shutdown()
        self.datahandler.shutdown()
        self.ipcon.disconnect()







if __name__ == "__main__":
    controller = Controller()
    controller.startStation()