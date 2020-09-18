from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2

from settings import settings
from bricklets.bricklet import Bricklet


class Light(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__temperature = BrickletAmbientLightV2(settings["UIDs"]["Light2.0"], self._controller.ipcon)

    def getLight(self):
        return self.__temperature.get_illuminance()/100