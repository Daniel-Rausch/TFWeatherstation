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

    DIR_INPUT_THRESHOLD = 75
    DIR_INPUT_MARGIN = 5



    def __init__(self, controller):
        super().__init__(controller)
        self.__joystick = BrickletJoystick(settings["UIDs"]["Joystick"], self._controller.ipcon)

        self.__buttonPressedDuringLastTick = False
        self.__buttonPressedStartedAtTick = -1
        self.__buttonLongPressWasRegisteredDuringThisPressPeriod = False
        self.__buttonPress = False
        self.__buttonLongPress = False

        self.__lastDir = DIR.CENTER
        self.__dirInput = None



    def update(self):
        #Process button press
        pressed = self.__joystick.is_pressed()

        #Check whether button state has changed and update accordingly
        if not pressed == self.__buttonPressedDuringLastTick:
            self.__buttonPressedDuringLastTick = pressed
            if not pressed: #Register press when joystick is released
                logging.debug("Registered joystick button press.")

                #Only store button press if long press wasn't already registered
                if not self.__buttonLongPressWasRegisteredDuringThisPressPeriod:
                    self.__buttonPress = True
                self.__buttonLongPressWasRegisteredDuringThisPressPeriod = False
            else:
                self.__buttonPressedStartedAtTick = self._controller.currentTick
        
        #Check for long press
        if pressed and self._controller.currentTick >= self.__buttonPressedStartedAtTick + settings["TicksPerLongPress"]:
            self.__buttonLongPress = True
            self.__buttonLongPressWasRegisteredDuringThisPressPeriod = True

        #process directional presses
        curPos = [self.__joystick.get_position().x, self.__joystick.get_position().y]
        curDir = self.__mapPosToDir(curPos, 0)
        curDirPadded = self.__mapPosToDir(curPos, self.DIR_INPUT_MARGIN)
        if curDir == self.__lastDir:
            #No change of direction
            pass
        elif(curDirPadded != DIR.CENTER):
            #Change direction and queue input
            logging.debug("Registered joystick direction: " + str(curDirPadded.name))
            self.__lastDir = curDirPadded
            self.__dirInput = curDirPadded
        else:
            #Change to no directional input
            logging.debug("Registered joystick direction: " + str(DIR.CENTER.name))
            self.__lastDir = DIR.CENTER
            self.__dirInput = None
            
        


    def __mapPosToDir(self, curPos, margin):
        #Margin is the amount of pixel that is added to the center, i.e., it shrinks the area of the other directions

        threshold = self.DIR_INPUT_THRESHOLD

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
        #Returns a directional presses, if any. Press is then deleted to prevent multiple activations.
        buttonPress = self.__buttonPress
        self.__buttonPress = False
        return buttonPress
        
    

    def getButtonLongPress(self):
        #Returns a directional presses, if any. Press is then deleted to prevent multiple activations.
        buttonLongPress = self.__buttonLongPress
        self.__buttonLongPress = False
        return buttonLongPress



    def getDirInput(self):
        #Returns a directional presses, if any. Press is then deleted to prevent multiple activations.
        dirInput = self.__dirInput
        self.__dirInput = None
        return dirInput
