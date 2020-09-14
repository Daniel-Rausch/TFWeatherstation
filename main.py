HOST = "localhost"
PORT = 4223
UID = "vBF" # Change XYZ to the UID of your LCD 20x4 Bricklet


from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_20x4 import BrickletLCD20x4
from tinkerforge.bricklet_temperature import BrickletTemperature
import time


from settings import settings

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    lcd = BrickletLCD20x4(settings["UIDs"]["LCD20x4"], ipcon) # Create device object
    temperature = BrickletTemperature(settings["UIDs"]["Temperature"], ipcon)

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # Turn backlight on
    lcd.backlight_on()

    for i in range(0,100):
        lcd.clear_display()
        lcd.write_line(0, 0, "Temp: " + str(temperature.get_temperature()/100) + " °C")
        time.sleep(0.1)

    #input("Press key to exit\n") # Use raw_input() in Python 2
    lcd.backlight_off()
    ipcon.disconnect()