from datetime import datetime, timedelta

from bricklets.joystick import DIR
from bricklets.oled128x64 import OLED128x64
from screens.screen import Screen
import screens.mainscreen as mainscreen
from datahandler import DATATYPE, DATATYPE_STRING_MAPPING
from settings import settings



class DataScreen(Screen):

    OPTIONS = (
        "Back",
        "Range",
        "Bounds"
    )

    WIDTH_OF_GRAPH = OLED128x64.WIDTH - 2 * int(settings["DisplayBorderForGraph"])



    def __init__(self, controller, datatype):
        super().__init__(controller)

        self.__datahandler = self._controller.datahandler
        self.__datatype = datatype
        self.__datatypestring = DATATYPE_STRING_MAPPING[datatype]

        self.__currentOption = 0
        self.__currentMode = None
        
        self.__lowerDisplayBound = settings["DisplayDefaultBounds"][self.__datatypestring + "Min"]
        self.__upperDisplayBound = settings["DisplayDefaultBounds"][self.__datatypestring + "Max"]
        self.__lowerExtremeBound = settings["DisplayExtremeBounds"][self.__datatypestring + "Min"]
        self.__upperExtremeBound = settings["DisplayExtremeBounds"][self.__datatypestring + "Max"]
        self.__displayBoundStepSize = settings["DisplayBoundStepSize"][self.__datatypestring]

        self.__timeframes = settings["DisplayTimeframes"]
        self.__currentTimeframeType = settings["DefaultDisplayTimeframe"]
        self.__displayMoveRangeStepSize = settings["DisplayMoveRangeStepSize"]
        self.__currentTimeframeOffset = 0




    def update(self):
        super().update()

        self.__processInputs()

        data = self.__datahandler.getRecentDataPoints(self.__datatype, self.__timeframes[self.__currentTimeframeType][0], self.WIDTH_OF_GRAPH, self.__currentTimeframeOffset)
        pureData = []
        for (_, value, _) in data:
            pureData.append(value)

        #Display LCD Text
        if self.__currentMode == None:
            self.__displayLCDTextModeNone(data, pureData)
        elif self.__currentMode == self.OPTIONS[1]:
            self.__displayLCDTextModeRange(data)
        elif self.__currentMode == self.OPTIONS[2]:
            self.__displayLCDTextModeBounds()

        #Display OLED data
        self._oled.displayDatapoints(pureData, self.__lowerDisplayBound, self.__upperDisplayBound, settings["DisplayBorderForGraph"])



    def __processInputs(self):
        #Process button long press
        if self._joystick.getButtonLongPress():
            #Back (independently of current mode)
            self._changeScreen(mainscreen.MainScreen(self._controller))
            return

        #Process button press and directional inputs
        press = self._joystick.getButtonPress()
        if press: #Button press
            if self.__currentMode == None:
                #Currently in main view of datascreen
                if self.__currentOption == 0:
                    #Back
                    self._changeScreen(mainscreen.MainScreen(self._controller))
                elif self.__currentOption == 1:
                    #Range
                    self.__currentMode = self.OPTIONS[1]
                    self.__currentOption = self.__currentTimeframeType
                elif self.__currentOption == 2:
                    #Bounds
                    self.__currentMode = self.OPTIONS[2]
                    self.__currentOption = 0

            elif self.__currentMode == self.OPTIONS[1]:
                #Currently selecting Range
                self.__currentMode = None
                self.__currentOption = 1

            elif self.__currentMode == self.OPTIONS[2]:
                #Currently selecting Bounds
                self.__currentMode = None
                self.__currentOption = 2

        else: #Directional inputs
            dirInput = self._joystick.getDirInput()

            if self.__currentMode == None:
                #Currently in main view of datascreen
                if dirInput == DIR.LEFT:
                    self.__currentOption = (self.__currentOption - 1)%len(self.OPTIONS)
                elif dirInput == DIR.RIGHT:
                    self.__currentOption = (self.__currentOption + 1)%len(self.OPTIONS)

            elif self.__currentMode == self.OPTIONS[1]:
                #Currently selecting Range
                if dirInput == DIR.UP:
                    self.__currentOption = (self.__currentOption - 1)%len(self.__timeframes)
                    timeratio = self.__timeframes[self.__currentTimeframeType][1] / self.__timeframes[self.__currentOption][1]
                    self.__currentTimeframeType = self.__currentOption
                    self.__currentTimeframeOffset = int(self.__currentTimeframeOffset * timeratio)
                elif dirInput == DIR.DOWN:
                    self.__currentOption = (self.__currentOption + 1)%len(self.__timeframes)
                    timeratio = self.__timeframes[self.__currentTimeframeType][1] / self.__timeframes[self.__currentOption][1]
                    self.__currentTimeframeType = self.__currentOption
                    self.__currentTimeframeOffset = int(self.__currentTimeframeOffset * timeratio)
                elif dirInput == DIR.LEFT:
                    maxOffset = max (0, self.__datahandler.getTotalNumberOfDataPoints(self.__datatype, self.__timeframes[self.__currentTimeframeType][0]) - 1 - self.WIDTH_OF_GRAPH)
                    self.__currentTimeframeOffset = min(self.__currentTimeframeOffset + self.__displayMoveRangeStepSize, maxOffset)
                elif dirInput == DIR.RIGHT:
                    self.__currentTimeframeOffset = max(self.__currentTimeframeOffset - self.__displayMoveRangeStepSize, 0)

            elif self.__currentMode == self.OPTIONS[2]:
                #Currently selecting Bounds
                if dirInput == DIR.UP:
                    self.__currentOption = (self.__currentOption - 1) % 2
                elif dirInput == DIR.DOWN:
                    self.__currentOption = (self.__currentOption + 1) % 2
                elif dirInput == DIR.LEFT:
                    if self.__currentOption == 0 and not self.__upperDisplayBound - self.__displayBoundStepSize <= self.__lowerDisplayBound:
                        self.__upperDisplayBound -= self.__displayBoundStepSize
                    elif self.__currentOption == 1 and not self.__lowerDisplayBound == self.__lowerExtremeBound:
                        self.__lowerDisplayBound = max(self.__lowerDisplayBound - self.__displayBoundStepSize, self.__lowerExtremeBound)
                elif dirInput == DIR.RIGHT:
                    if self.__currentOption == 0 and not self.__upperDisplayBound == self.__upperExtremeBound:
                        self.__upperDisplayBound = min(self.__upperDisplayBound + self.__displayBoundStepSize, self.__upperExtremeBound)
                    elif self.__currentOption == 1 and not self.__lowerDisplayBound + self.__displayBoundStepSize >= self.__upperDisplayBound:
                        self.__lowerDisplayBound += self.__displayBoundStepSize

    

    def __displayLCDTextModeNone(self, data, pureData):
        text = ["","","",""]
        if self.__datatype == DATATYPE.TEMPERATURE:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Temperature: {:5.1f}\xDFC".format(pureData[-1])
            else:
                text[0] = "Temperature: {:>5}\xDFC".format("-.-")
        elif self.__datatype == DATATYPE.LIGHT:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Light: {:10.1f} lx".format(pureData[-1])
            else:
                text[0] = "Light: {:>10} lx".format("-.-")
        elif self.__datatype == DATATYPE.HUMIDITY:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Humidity: {:8.1f} %".format(pureData[-1])
            else:
                text[0] = "Humidity: {:>8} %".format("-.-")
        elif self.__datatype == DATATYPE.PRESSURE:
            if len(pureData) > 0 and pureData[-1] != None:
                text[0] = "Pressure: {:5d} hPa".format(int(pureData[-1]))
            else:
                text[0] = "Pressure: {:>5} hPa".format("---")

        text[1] = self.__getCurrentBoundFormattedAsText(False, 8, ">")  + " to " + self.__getCurrentBoundFormattedAsText(True, 8, ">")

        #text[2] = self.__clock.getDateTime().strftime("%y-%m-%d") + " to " + self.__clock.getDateTime().strftime("%y-%m-%d")
        if len(data) >= 1:
            currentTime = datetime.fromtimestamp(data[-1][0])
            initialTime = currentTime - timedelta(seconds= self.__timeframes[self.__currentTimeframeType][1] * self.WIDTH_OF_GRAPH)
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
    


    def __displayLCDTextModeRange(self, data):
        text = ["","","",""]
        text[0] = "Data range:"

        if len(data) >= 1:
            currentTime = datetime.fromtimestamp(data[-1][0])
            initialTime = currentTime - timedelta(seconds= self.__timeframes[self.__currentTimeframeType][1] * self.WIDTH_OF_GRAPH)
            if self.__currentTimeframeOffset == 0:
                text[1] = initialTime.strftime("%y-%m-%d") + " to " + "{:8}".format("now")
            else:
                text[1] = initialTime.strftime("%y-%m-%d") + " to " + currentTime.strftime("%y-%m-%d")

        offset = max(0, self.__currentOption-1)
        for i in range(0, min(2, len(self.__timeframes))):
            text[i+2] = "{:1}{:19}".format(
                "\x7E" if self.__currentOption == i + offset else "",
                self.__timeframes[i + offset][0]
            )
        self._lcd.displayText(text)
    


    def __displayLCDTextModeBounds(self):

        boundText = [
            self.__getCurrentBoundFormattedAsText(True, 8, "^"),
            self.__getCurrentBoundFormattedAsText(False, 8, "^")
        ]

        text = ["","","",""]
        text[0] = "Change upper bound:"

        leftarrow = "\x7F"
        if self.__currentOption != 0 or self.__upperDisplayBound - self.__displayBoundStepSize <= self.__lowerDisplayBound:
            leftarrow = ""
        rightarrow = "\x7E"
        if self.__currentOption != 0 or self.__upperDisplayBound == self.__upperExtremeBound:
            rightarrow = ""
        text[1] = "   {:1}{:^12}{:1}   ".format(leftarrow, boundText[0], rightarrow)

        text[2] = "Change lower bound:"

        leftarrow = "\x7F"
        if self.__currentOption != 1 or self.__lowerDisplayBound == self.__lowerExtremeBound:
            leftarrow = ""
        rightarrow = "\x7E"
        if self.__currentOption != 1 or self.__lowerDisplayBound + self.__displayBoundStepSize >= self.__upperDisplayBound:
            rightarrow = ""
        text[3] = "   {:1}{:^12}{:1}   ".format(leftarrow, boundText[1], rightarrow)

        self._lcd.displayText(text)
    


    def __getCurrentBoundFormattedAsText(self, upper, length, align): # upper is boolean. length is int. align is "<", "^", or ">".
        formatString = "{:" + align + str(length) + "}"
        bound = int(self.__upperDisplayBound) if upper else int(self.__lowerDisplayBound)

        if self.__datatype == DATATYPE.TEMPERATURE:
            return formatString.format("{}\xDFC".format(bound))
        elif self.__datatype == DATATYPE.LIGHT:
            return formatString.format("{} lx".format(bound))
        elif self.__datatype == DATATYPE.HUMIDITY:
            return formatString.format("{} %".format(bound))
        elif self.__datatype == DATATYPE.PRESSURE:
            return formatString.format("{} hPa".format(bound))
        