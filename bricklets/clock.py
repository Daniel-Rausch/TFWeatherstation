from tinkerforge.bricklet_real_time_clock import BrickletRealTimeClock

from datetime import datetime

from settings import settings
from bricklets.bricklet import Bricklet


class Clock(Bricklet):

    def __init__(self, controller):
        super().__init__(controller)
        self.__clock = BrickletRealTimeClock(settings["UIDs"]["RTC"], self._controller.ipcon)

    def getDateTime(self):
        year, month, day, hour, minute, second, centisecond, _ = self.__clock.get_date_time()
        return datetime(year, month, day, hour, minute, second, centisecond*10*1000)

    def getTimestamp(self): #returns posix timestamp, i.e., seconds since 1.1.1970
        return self.getDateTime().timestamp()
