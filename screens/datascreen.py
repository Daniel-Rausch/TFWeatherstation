from bricklets.joystick import DIR
from screens.screen import Screen

class DataScreen(Screen):

    OPTIONS = (
        "Back",
        "Move",
        "Shutdown"
    )

    def __init__(self, controller):
        super().__init__(controller)

        self.__temp = self._controller.bricklets["temperature"]
        self.__clock = self._controller.bricklets["clock"]
        self.__joystick = self._controller.bricklets["joystick"]

        self.__currentOption = 0



    def update(self):
        super().update()

        self.processInputs()

        #Build and display LCD Text
        text = ["","","",""]
        text[0] = "Temperature"
        text[1] = "{:6.2f}".format(self.__temp.getTemperature())  + "\xDFC to " + "{:6.2f}".format(self.__temp.getTemperature()) + "\xDFC"
        text[2] = self.__clock.getDateTime().strftime("%y-%m-%d") + " to " + self.__clock.getDateTime().strftime("%y-%m-%d")
        text[3] = "\x7F {:^8} \x7E".format(self.OPTIONS[self.__currentOption])

        self._lcd.displayText(text)

    

    def processInputs(self):
        press = self.__joystick.getButtonPress()
        if press:
            if self.__currentOption == 2:
                self._controller.shutdown = True
        else:
            dirInput = self.__joystick.getDirInput()
            if dirInput == DIR.LEFT:
                self.__currentOption = (self.__currentOption - 1)%len(self.OPTIONS)
            elif dirInput == DIR.RIGHT:
                self.__currentOption = (self.__currentOption + 1)%len(self.OPTIONS)


