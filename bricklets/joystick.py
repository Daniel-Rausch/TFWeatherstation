from tinkerforge.bricklet_joystick import BrickletJoystick

import logging
from enum import Enum

from settings import settings
from bricklets.bricklet import Bricklet



class DIR(Enum):
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3
    CENTER = 4



class Joystick(Bricklet):


    def __init__(self, controller):
        super().__init__(controller)
        self.__joystick = BrickletJoystick(settings["UIDs"]["Joystick"], self._controller.ipcon)

        self.__buttonPressedDown = False
        self.__tickButtonPress = -1

        self.__lastPos = [0,0]
        self.__lastDir = DIR.CENTER



    def update(self):
        #Process button press
        pressed = self.__joystick.is_pressed()

        #Check whether button state has changed and update accordingly
        if not pressed == self.__buttonPressedDown:
            self.__buttonPressedDown = pressed
            if pressed:
                logging.debug("Registered joystick press.")
                self.__tickButtonPress = self._controller.currentTick

        #process directional presses
        curPos = [self.__joystick.get_position().x, self.__joystick.get_position().y]
        curDir = self.__mapPosToDir(curPos, 0)
        print(curPos, curDir)
        


    def __mapPosToDir(self, curPos, margin):
        #Margin is the amount of pixel that is added to the center, i.e., it shrinks the area of the other directions

        threshold = 75

        #Left
        if curPos[0] < -threshold - margin and abs(curPos[0]) > (abs(curPos[1]) + margin):
            return DIR.LEFT

        #Right
        if curPos[0] > threshold + margin and abs(curPos[0]) > (abs(curPos[1]) + margin):
            return DIR.RIGHT

        #Up
        if curPos[1] > threshold + margin and abs(curPos[1]) >= (abs(curPos[0]) + margin):
            return DIR.UP

        #Down
        if curPos[1] < - threshold - margin and abs(curPos[1]) >= (abs(curPos[0]) + margin):
            return DIR.DOWN

        #Return default: center
        return DIR.CENTER
        
    

    def getButtonPress(self):
        #Returns true if the button was pressed in the current tick. might need to be changed in the future
        if self.__buttonPressedDown == True and self._controller.currentTick == self.__tickButtonPress:
            return True
        return False


    def getDirectionPress(self):
        #Returns a directional presses, if any. Press is then deleted to prevent multiple activations.
        pass
