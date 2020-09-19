from datetime import datetime, timedelta

from bricklets.joystick import DIR
from screens.screen import Screen
import screens.mainscreen as mainscreen
from datahandler import DATATYPE
from settings import settings



class DataScreen(Screen):

    OPTIONS = (
        "Back",
        "Range",
        "Bounds"
    )

    WIDTH_OF_GRAPH = 128



    def __init__(self, controller, datatype):
        super().__init__(controller)

        self.__datahandler = self._controller.datahandler
        self.__datatype = datatype

        self.__currentOption = 0

        if datatype == DATATYPE.TEMPERATURE:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["TemperatureMax"]
        elif datatype == DATATYPE.LIGHT:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["LightMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["LightMax"]
        elif datatype == DATATYPE.HUMIDITY:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["HumidityMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["HumidityMax"]
        elif datatype == DATATYPE.PRESSURE:
            self.__lowerDisplayBound = settings["DisplayDefaultBounds"]["PressureMin"]
            self.__upperDisplayBound = settings["DisplayDefaultBounds"]["PressureMax"]

        self.__timeframes = settings["DisplayTimeframes"]
        self.__currentTimeframeIndex = settings["DefaultDisplayTimeframe"]




    def update(self):
        super().update()

        self.__processInputs()

        data = self.__datahandler.getRecentDataPoints(self.__datatype, self.__timeframes[self.__currentTimeframeIndex][0], self.WIDTH_OF_GRAPH)
        pureData = []
        for (_, value, _) in data:
            pureData.append(value)

        #Build and display LCD Text
        text = ["","","",""]
        if self.__datatype == DATATYPE.TEMPERATURE:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Temperature: {:5.1f}\xDFC".format(pureData[-1])
            else:
                text[0] = "Temperature: {:>5}\xDFC".format("-.-")
            text[1] = "{:>8}".format("{}\xDFC".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{}\xDFC".format(int(self.__upperDisplayBound)))
        elif self.__datatype == DATATYPE.LIGHT:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Light: {:10.1f} lx".format(pureData[-1])
            else:
                text[0] = "Light: {:>10} lx".format("-.-")
            text[1] = "{:>8}".format("{} lx".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{} lx".format(int(self.__upperDisplayBound)))
        elif self.__datatype == DATATYPE.HUMIDITY:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Humidity: {:8.1f} %".format(pureData[-1])
            else:
                text[0] = "Humidity: {:>8} %".format("-.-")
            text[1] = "{:>8}".format("{} %".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{} %".format(int(self.__upperDisplayBound)))
        elif self.__datatype == DATATYPE.PRESSURE:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Pressure: {:5d} hPa".format(int(pureData[-1]))
            else:
                text[0] = "Pressure: {:>5} hPa".format("---")
            text[1] = "{:>8}".format("{} hPa".format(int(self.__lowerDisplayBound)))  + " to " + "{:>8}".format("{} hPa".format(int(self.__upperDisplayBound)))
        #text[2] = self.__clock.getDateTime().strftime("%y-%m-%d") + " to " + self.__clock.getDateTime().strftime("%y-%m-%d")
        if len(data) >= 1:
            currentTime = datetime.fromtimestamp(data[-1][0])
            initialTime = currentTime - timedelta(seconds= self.__timeframes[self.__currentTimeframeIndex][1] * self.WIDTH_OF_GRAPH)
            text[2] = initialTime.strftime("%y-%m-%d") + " to " + currentTime.strftime("%y-%m-%d")
        else:
            text[2] = "xx-xx-xx to xx-xx-xx"
        #text[3] = "\x7F {:^8} \x7E".format(self.OPTIONS[self.__currentOption])
        formatStringData = (
            "\x7E" if self.__currentOption == 0 else "",
            self.OPTIONS[0],
            "\x7E" if self.__currentOption == 1 else "",
            self.OPTIONS[1],
            "\x7E" if self.__currentOption == 2 else "",
            self.OPTIONS[2]
        )
        text[3] = "{:1}{} {:1}{} {:1}{}".format(*formatStringData)

        self._lcd.displayText(text)


        #Display OLED data
        self._oled.displayDatapoints(pureData, self.__lowerDisplayBound, self.__upperDisplayBound)

    

    def __processInputs(self):
        #Process button long press
        if self._joystick.getButtonLongPress():
            self._changeScreen(mainscreen.MainScreen(self._controller))
            return

        #Process button press and directional inputs
        press = self._joystick.getButtonPress()
        if press:
            if self.__currentOption == 0:
                self._changeScreen(mainscreen.MainScreen(self._controller))
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.LEFT:
                self.__currentOption = (self.__currentOption - 1)%len(self.OPTIONS)
            elif dirInput == DIR.RIGHT:
                self.__currentOption = (self.__currentOption + 1)%len(self.OPTIONS)