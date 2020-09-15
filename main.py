HOST = "localhost"
PORT = 4223
UID = "vBF" # Change XYZ to the UID of your LCD 20x4 Bricklet


from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_20x4 import BrickletLCD20x4

import logging
import time


from settings import settings
from bricklets.temperature import Temperature
from bricklets.clock import Clock



class Controller:

    mainController = ""    


    def __init__(self):
        self.bricklets = {}
        self.ipcon = ""

        #Ensure that there is ever only a single controller instance
        if not Controller.mainController == "":
            logging.error("Controller already instantiated. Aborted second instantiation.")
            return
        else:
            self.mainController = self

        print(self.mainController)

        #Prepare Logging
        logginglevels = {
            "DEBUG" : logging.DEBUG,
            "INFO" : logging.INFO,
            "WARNING" : logging.WARNING,
            "ERROR" : logging.ERROR,
            "CRITICAL" : logging.CRITICAL,
        }
        logging.basicConfig(level=logginglevels.get(settings["LoggingLevel"], logging.WARNING), format = "LOGGING:%(levelname)s   %(message)s")

        #Create all bricklet classes and store them
        self.ipcon = IPConnection()

        self.bricklets["temperature"] = Temperature(self)
        self.bricklets["clock"] = Clock(self)

        self.ipcon.connect(HOST, PORT)



    def startStation(self):

        for i in range(0,5):
            temperature = str(self.bricklets["temperature"].getTemperature()/100)
            print("Temp: " + temperature + " °C")

            time.sleep(0.1)

        #Program has finished. Shutdown.
        self.__shutdownStation()



    def __shutdownStation(self):
        for bricklet in self.bricklets.values():
            bricklet.shutdown()
        self.ipcon.disconnect()







if __name__ == "__main__":
    controller = Controller()
    controller.startStation()

    # ipcon = IPConnection() # Create IP connection
    # lcd = BrickletLCD20x4(settings["UIDs"]["LCD20x4"], ipcon) # Create device object
    # temperature = BrickletTemperature(settings["UIDs"]["Temperature"], ipcon)
    # clock = BrickletRealTimeClock(settings["UIDs"]["RTC"], ipcon)

    # ipcon.connect(HOST, PORT) # Connect to brickd
    # # Don't use device before ipcon is connected

    # # Turn backlight on
    # lcd.backlight_on()

    # for i in range(0,100):
    # #while True:
    #     lcd.clear_display()
    #     lcd.write_line(0, 0, "Temp: " + str(temperature.get_temperature()/100) + " °C")
    #     year, month, day, hour, minute, second, centisecond, weekday = clock.get_date_time()
    #     lcd.write_line(1,0,str(year)[-2:] + "-" + str(month) + "-" + str(day))
    #     lcd.write_line(1,10,str(hour) + ":" + str(minute) + ":" + str(second))
    #     time.sleep(0.1)

    # #input("Press key to exit\n") # Use raw_input() in Python 2
    # lcd.backlight_off()
    # ipcon.disconnect()