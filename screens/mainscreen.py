from bricklets.joystick import DIR
from screens.screen import Screen
import screens.datascreen as datascreen
from datahandler import DATATYPE
from settings import settings



class MainScreen(Screen):

    OPTIONS = ((
        "Temp.",
        "Shutdown"
    ), (
        "Light", ""
    ), (
        "Humidity", ""
    ), (
        "Pressure", ""
    ))

    OPTIONS_PER_COLUMN = (4,1)



    def __init__(self, controller):
        super().__init__(controller)

        self.__currentOption = [0,0]




    def update(self):
        super().update()

        self.__processInputs()

        #Build and display LCD Text
        text = ["","","",""]
        for row in range(0,4):
            if len(self.OPTIONS) > row:
                formatStringInputs = (
                    "\x7E" if self.__currentOption == [row,0] else " ",
                    self.OPTIONS[row][0],
                    "\x7E" if self.__currentOption == [row,1] else " ",
                    self.OPTIONS[row][1] if len(self.OPTIONS[row]) == 2 else ""
                    )
                text[row] = "{:1}{:8} {:1}{:9}".format(*formatStringInputs)
        self._lcd.displayText(text)


        #Clear OLED
        self._oled.clear()

    

    def __processInputs(self):
        #Process button long press
        if self._joystick.getButtonLongPress():
            pass

        #Process button press and directional inputs
        press = self._joystick.getButtonPress()
        if press:
            if self.__currentOption == [0,0]:
                self._changeScreen(datascreen.DataScreen(self._controller, DATATYPE.TEMPERATURE))
            elif self.__currentOption == [0,1]:
                self._controller.shutdown = True
            if self.__currentOption == [1,0]:
                self._changeScreen(datascreen.DataScreen(self._controller, DATATYPE.LIGHT))
            if self.__currentOption == [2,0]:
                self._changeScreen(datascreen.DataScreen(self._controller, DATATYPE.HUMIDITY))
            if self.__currentOption == [3,0]:
                self._changeScreen(datascreen.DataScreen(self._controller, DATATYPE.PRESSURE))
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.LEFT:
                self.__currentOption[1] = (self.__currentOption[1] - 1)
                self.__currentOption[0] %= self.OPTIONS_PER_COLUMN[self.__currentOption[1]]
            elif dirInput == DIR.RIGHT:
                self.__currentOption[1] = (self.__currentOption[1] + 1)
                self.__currentOption[0] %= self.OPTIONS_PER_COLUMN[self.__currentOption[1]]
            elif dirInput == DIR.UP:
                self.__currentOption[0] = (self.__currentOption[0] - 1) % self.OPTIONS_PER_COLUMN[self.__currentOption[1]]
            elif dirInput == DIR.DOWN:
                self.__currentOption[0] = (self.__currentOption[0] + 1) % self.OPTIONS_PER_COLUMN[self.__currentOption[1]]
