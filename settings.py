TICKS_PER_SECOND = 10
TICKS_PER_MEASUREMENT = 1



settings = {
    "UIDs" : {
        "LCD20x4" : "vBF",
        "OLED128x64" : "yfN",
        "Joystick" : "wa5",
        "RTC" : "xKm",
        "Temperature" : "tab",
        "Humidity" : "xtp",
        "Light2.0" : "uLj",
        "Barometer" : "vLp",
    },

    #Display
    "DisplayDefaultBounds": {
        "TemperatureMin" : 20, #celsius
        "TemperatureMax" : 30,
        "LightMin" : 0, #lux
        "LightMax" : 100,
        "HumidityMin" : 0, #percent
        "HumidityMax" : 100,
        "PressureMin" : 950, #hPa
        "PressureMax" : 1050,
    },
    "DisplayTimeFrames": [
        ("Seconds", 1), # Second component specifies the time in seconds.
        ("Minutes", 60),
        ("Hours", 60 * 60),
        ("Days", 60 * 60 * 24),
        ("Weeks", 60 * 60 * 24 * 7),
    ],

    #Ticks
    "TicksPerSecond" : TICKS_PER_SECOND,
    "TotalTicks" : -1, #Negative for endless exectuion

    #Joystick
    "TicksPerLongPress": TICKS_PER_SECOND * 1, #Number of ticks after which joystick registers a long button press

    #Data model
    "TicksPerMeasurement": TICKS_PER_MEASUREMENT,
    "AggregationsPerDataPoint": int(TICKS_PER_SECOND/TICKS_PER_MEASUREMENT),

    "LoggingLevel" : "INFO",
}