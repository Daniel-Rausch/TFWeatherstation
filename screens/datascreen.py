from screens.screen import Screen

class DataScreen(Screen):

    def __init__(self, controller):
        super().__init__(controller)

        self.__temp = self._controller.bricklets["temperature"]
        self.__joystick = self._controller.bricklets["joystick"]

        self.__text = ["", "", "", ""]



    def update(self):
        super().update()

        self.processInput()

        self.__text[0] = "Temp: " + str(self.__temp.getTemperature()) + " \xDFC"
        self._lcd.displayText(self.__text)

    

    def processInput(self):
        press = self.__joystick.getButtonPress()
        if press:
            # self.__text[1] =  "Pressed!"
            self._controller.shutdown = True

