HOST = "localhost"
PORT = 4223


from tinkerforge.ip_connection import IPConnection

import logging
import time
import os

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

from screens.startscreen import StartScreen



class Controller:

    mainController = ""    


    def __init__(self):
        self.bricklets = {}
        self.datahandler = None
        self.currentScreen = None

        self.ipcon = None
        self.currentTick = 0
        self.DBInitialized = False #Will be set by the initializeDB() function, which is called via the startscreen
        self.shutdown = False
        self.shutdownSystem = False

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

        #Create data handler (will be initialized by the initializeDB() function)
        self.datahandler = Datahandler(self)

        #Initialize starting screen
        self.currentScreen = StartScreen(self)

        logging.info("Finished controller Initiatilization at time " + str(self.bricklets["clock"].getDateTime()))



    def startStation(self):

        while (self.currentTick < settings["TotalTicks"] or settings["TotalTicks"] < 0) and not self.shutdown:

            starttime = time.time()

            #Update data handler
            self.datahandler.update()

            #Update I/O
            self.bricklets["joystick"].update()

            #Update Screen
            self.currentScreen.update()

            #Automatic data saving
            if settings["AutomaticSaveInterval"] > 0 and (self.currentTick % settings["AutomaticSaveInterval"]) == 0 and not self.currentTick == 0:
                logging.info("Autosaving data at time " + str(self.bricklets["clock"].getDateTime()))
                self.datahandler.writeRecentDataToFile()

            #Sleep until the next tick can occur
            tickDuration = 1.0 / settings["TicksPerSecond"]
            duration = (time.time() - starttime)
            delay = tickDuration - (time.time() % tickDuration)
            if duration > tickDuration:
                logging.warning("Current tick took {:d} ms, instead of intended maximum of {:d} ms. Next tick delay: {:d} ms".format(int(duration*1000), int(tickDuration*1000), int(delay*1000)))
            else:
                logging.debug("Current tick took {:d} ms. Next tick delay: {:d} ms".format(int(duration*1000), int(delay*1000)))
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

        if self.shutdownSystem and os.name == "posix":
            os.system("sudo shutdown -h now")







if __name__ == "__main__":
    controller = Controller()
    controller.startStation()
