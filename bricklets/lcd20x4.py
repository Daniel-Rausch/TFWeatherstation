from tinkerforge.bricklet_lcd_20x4 import BrickletLCD20x4

from settings import settings
from bricklets.bricklet import Bricklet


class LCD20x4(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__lcd = BrickletLCD20x4(settings["UIDs"]["LCD20x4"], self._controller.ipcon)
        self.__lcd.backlight_on()



    def shutdown(self):
        super().shutdown()
        self.__lcd.backlight_off()

    

    def displayText(self, text):
        i = 0
        for line in text:
            if len(line) < 20:
                line = line + " " * (20-len(line))
            self.__lcd.write_line(i, 0, line)
            i = i + 1
            if i == 4:
                break

