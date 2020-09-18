from tinkerforge.bricklet_temperature import BrickletTemperature

from settings import settings
from bricklets.bricklet import Bricklet


class Temperature(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__temperature = BrickletTemperature(settings["UIDs"]["Temperature"], self._controller.ipcon)

    def getTemperature(self):
        return self.__temperature.get_temperature()/100  #measures as 1/100 celsius