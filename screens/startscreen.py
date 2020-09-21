from bricklets.joystick import DIR
from screens.screen import Screen
import screens.mainscreen as mainscreen



class StartScreen(Screen):

    def __init__(self, controller):
        super().__init__(controller)

        self.__currentOption = 0

        self.__options = ["New"]
        dbcount = self._controller.datahandler.getExistingDBCount()
        for i in range(0, dbcount):
            self.__options.append(("DB #{:0" + str(len(str(dbcount))) + "d}").format(i))

        if len(self.__options) >= 2:
            self.__currentOption = 1 #Start default option with the first existing database, if any



    def update(self):
        super().update()

        self.__processInputs()

        #Build and display LCD Text
        text = ["","","",""]
        text[0] = "Choose database:"
        
        offset = max(0, self.__currentOption-2)
        for i in range(0, min(3, len(self.__options))):
            text[i+1] = "{:1}{:19}".format("\x7E" if self.__currentOption == i + offset else "", self.__options[i + offset])

        self._lcd.displayText(text)


        #Clear OLED
        self._oled.clear()

    

    def __processInputs(self):
        #Process button long press
        if self._joystick.getButtonLongPress():
            self._controller.shutdown = True

        #Process button press and directional inputs
        press = self._joystick.getButtonPress()
        if press:
            self._controller.datahandler.initializeDB(self.__currentOption - 1)
            self._changeScreen(mainscreen.MainScreen(self._controller))
        else:
            dirInput = self._joystick.getDirInput()
            if dirInput == DIR.UP:
                self.__currentOption = (self.__currentOption - 1) % len(self.__options)
            elif dirInput == DIR.DOWN:
                self.__currentOption = (self.__currentOption + 1) % len(self.__options)
