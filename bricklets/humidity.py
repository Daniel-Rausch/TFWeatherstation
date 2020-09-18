from tinkerforge.bricklet_humidity import BrickletHumidity

from settings import settings
from bricklets.bricklet import Bricklet


class Humidity(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__humidity = BrickletHumidity(settings["UIDs"]["Humidity"], self._controller.ipcon)

    def getHumidity(self):
        return self.__humidity.get_humidity()/10 #measures as 1/10 percent