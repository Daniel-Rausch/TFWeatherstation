from tinkerforge.bricklet_temperature import BrickletTemperature

from settings import settings
from bricklets.bricklet import Bricklet


class Temperature(Bricklet):

    def __init__(self, ipcon):
        super().__init__()
        self.__temperature = BrickletTemperature(settings["UIDs"]["Temperature"], ipcon)

    def getTemperature(self):
        return self.__temperature.get_temperature()