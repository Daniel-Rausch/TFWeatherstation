from bricklets.joystick import DIR
from screens.screen import Screen
import screens.mainscreen as mainscreen



class ShutdownScreen(Screen):

    OPTIONS = (
        "Abort",
        "Only program",
        "System"
    )



    def __init__(self, controller):
        super().__init__(controller)

        self.__currentOption = 0



    def update(self):
        super().update()

        self.__processInputs()

        #Build and display LCD Text
        text = ["","","",""]
        text[0] = "Shutdown?"
        for i in range(0,3):
            text[i+1] = "{:1}{:19}".format("\x7E" if self.__currentOption == i else "",self.OPTIONS[i])
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
            if self.__currentOption == 0:
                self._changeScreen(mainscreen.MainScreen(self._controller))
            elif self.__currentOption == 1:
                self._controller.shutdown = True
            elif self.__currentOption == 2:
                self._controller.shutdown = True
                self._controller.shutdownSystem = True
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.UP:
                self.__currentOption = (self.__currentOption - 1) % len(self.OPTIONS)
            elif dirInput == DIR.DOWN:
                self.__currentOption = (self.__currentOption + 1) % len(self.OPTIONS)
