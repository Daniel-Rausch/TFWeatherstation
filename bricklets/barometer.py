from tinkerforge.bricklet_barometer import BrickletBarometer

from settings import settings
from bricklets.bricklet import Bricklet


class Barometer(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__humidity = BrickletBarometer(settings["UIDs"]["Barometer"], self._controller.ipcon)

    def getPressure(self):
        return self.__humidity.get_air_pressure()/1000 #measures as 1/1000 hpa