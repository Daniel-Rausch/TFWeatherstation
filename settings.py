TICKS_PER_SECOND = 10



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
        "TemperatureMin" : 20,
        "TemperatureMax" : 30,
    },

    #Ticks
    "TicksPerSecond" : TICKS_PER_SECOND,
    "TotalTicks" : -1, #Negative for endless exectuion

    #Joystick
    "TicksPerLongPress": TICKS_PER_SECOND*1, #Number of ticks after which joystick registers a long button press

    #Data model
    "AggregationsPerDataPoint": TICKS_PER_SECOND,
    "TicksPerMeasurement": 1,

    "LoggingLevel" : "INFO",
}