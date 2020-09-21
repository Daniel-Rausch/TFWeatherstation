# TFWeatherstation
Weatherstation using the Tinkerforge hardware set

Requires the following bricklets:
* LCD20x4
* OLED128x64
* Joystick
* RTC
* Temperature
* Humidity
* Light2.0
* Barometer

Software is intended to be run on a Raspberry Pi, but will also work on a windows machine (except for the "shutdown whole system" operation).

For setup on a Raspberry Pi, remember to enable sudo usage without password for the current user (otherwise the "shutdown whole system" operation will not work).