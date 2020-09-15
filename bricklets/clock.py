from tinkerforge.bricklet_real_time_clock import BrickletRealTimeClock

from settings import settings
from bricklets.bricklet import Bricklet


class Clock(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__clock = BrickletRealTimeClock(settings["UIDs"]["RTC"], self._controller.ipcon)

    def getDateTime(self):
        year, month, day, hour, minute, second, centisecond, weekday = self.__clock.get_date_time()
        #return self.__clock.get_temperature()
