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



    def __init__(self, controller, datatype):
        super().__init__(controller)

        self.__clock = self._controller.bricklets["clock"]

        self.__datahandler = self._controller.datahandler
        self.__datatype = datatype

        self.__currentOption = 0

        if datatype == DATATYPE.TEMPERATURE:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMax"]
        elif datatype == DATATYPE.LIGHT:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["LightMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["LightMax"]




    def update(self):
        super().update()

        self.__processInputs()

        data = self.__datahandler.getRecentDataPoints(self.__datatype, 128)

        #Build and display LCD Text
        text = ["","","",""]
        if self.__datatype == DATATYPE.TEMPERATURE:
            if len(data) > 0:
                text[0] = "Temperature: {:5.1f}\xDFC".format(data[-1])
            else:
                text[0] = "Temperature: {:>5}\xDFC".format("-.-")
            text[1] = "{:>8}".format("{}\xDFC".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{}\xDFC".format(int(self.__upperDisplayBound)))
        elif self.__datatype == DATATYPE.LIGHT:
            if len(data) > 0:
                text[0] = "Light: {:10.1f} lx".format(data[-1])
            else:
                text[0] = "Light: {:>10} lx".format("-.-")
            text[1] = "{:>8}".format("{} lx".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{} lx".format(int(self.__upperDisplayBound)))
        text[2] = self.__clock.getDateTime().strftime("%y-%m-%d") + " to " + self.__clock.getDateTime().strftime("%y-%m-%d")
        text[3] = "\x7F {:^8} \x7E".format(self.OPTIONS[self.__currentOption])

        self._lcd.displayText(text)


        #Display OLED data
        self._oled.displayDatapoints(data, self.__lowerDisplayBound, self.__upperDisplayBound)

    

    def __processInputs(self):
        #Process button long press
        if self._joystick.getButtonLongPress():
            self._controller.shutdown = True #TODO: change to "back" function
            return

        #Process button press and directional inputs
        press = self._joystick.getButtonPress()
        if press:
            pass
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.LEFT:
                self.__currentOption = (self.__currentOption - 1)%len(self.OPTIONS)
            elif dirInput == DIR.RIGHT:
                self.__currentOption = (self.__currentOption + 1)%len(self.OPTIONS)