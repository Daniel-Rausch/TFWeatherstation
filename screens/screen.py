import logging

class Screen():

    def __init__(self, controller):
        self._controller = controller
        self._lcd = self._controller.bricklets["lcd20x4"]
        self._oled = self._controller.bricklets["oled128x64"]
        self._joystick = self._controller.bricklets["joystick"]

        self._lcd.clear()
        self._oled.clear()

        logging.debug("Initializing new screen: "+ type(self).__name__)

    def update(self):
        logging.debug("Updating screen: " + type(self).__name__)