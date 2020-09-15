from screens.screen import Screen

class DataScreen(Screen):

    def __init__(self, controller):
        super().__init__(controller)

        self.__temp = self._controller.bricklets["temperature"]



    def update(self):
        super().update()

        text = ["Temp: " + str(self.__temp.getTemperature()) + " \xDFC"]
        self._lcd.displayText(text)

