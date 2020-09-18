from bricklets.joystick import DIR
from screens.screen import Screen
from datahandler import DATATYPE
from settings import settings



class DataScreen(Screen):

    OPTIONS = (
        "Back",
        "Range",
        "Bounds"
    )



    def __init__(self, controller):
        super().__init__(controller)

        self.__clock = self._controller.bricklets["clock"]

        self.__datahandler = self._controller.datahandler

        self.__currentOption = 0

        self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMin"]
        self.__upperDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMax"]



    def update(self):
        super().update()

        self._processInputs()

        data = self.__datahandler.getRecentDataPoints(DATATYPE.TEMPERATURE, 128)

        #Build and display LCD Text
        text = ["","","",""]
        if len(data) > 0:
            text[0] = "Temperature: {:5.1f}\xDFC".format(data[-1])
        else:
            text[0] = "Temperature: {:>5}\xDFC".format("--.-")
        text[1] = "{:<8}".format("{}\xDFC".format(int(self.__lowerDisplayBound)))  + " to " + "{:<8}".format("{}\xDFC".format(int(self.__upperDisplayBound)))
        text[2] = self.__clock.getDateTime().strftime("%y-%m-%d") + " to " + self.__clock.getDateTime().strftime("%y-%m-%d")
        text[3] = "\x7F {:^8} \x7E".format(self.OPTIONS[self.__currentOption])

        self._lcd.displayText(text)


        #Display OLED data
        self._oled.displayDatapoints(data, self.__lowerDisplayBound, self.__upperDisplayBound)

    

    def _processInputs(self):
        super()._processInputs()

        press = self._joystick.getButtonPress()
        if press:
            pass
        #     if self.__currentOption == self.OPTIONS.index("Shutdown"):
        #         self._controller.shutdown = True
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.LEFT:
                self.__currentOption = (self.__currentOption - 1)%len(self.OPTIONS)
            elif dirInput == DIR.RIGHT:
                self.__currentOption = (self.__currentOption + 1)%len(self.OPTIONS)