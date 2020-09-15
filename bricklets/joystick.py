from tinkerforge.bricklet_joystick import BrickletJoystick

import logging

from settings import settings
from bricklets.bricklet import Bricklet


class Joystick(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__joystick = BrickletJoystick(settings["UIDs"]["Joystick"], self._controller.ipcon)

        self.__buttonPressedDown = False
        self.__tickButtonPress = -1



    def update(self):
        pressed = self.__joystick.is_pressed()

        #Check whether button state has changed and update accordingly
        if not pressed == self.__buttonPressedDown:
            self.__buttonPressedDown = pressed
            if pressed:
                logging.debug("Registered joystick press.")
                self.__tickButtonPress = self._controller.currentTick
    


    def getButtonPress(self):
        #Returns true if the button was pressed in the current tick. might need to be changed in the future
        if self.__buttonPressedDown == True and self._controller.currentTick == self.__tickButtonPress:
            return True
        return False
