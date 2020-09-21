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
        "TemperatureMin" : 13, #celsius
        "TemperatureMax" : 28,
        "LightMin" : 0, #lux
        "LightMax" : 100,
        "HumidityMin" : 0, #percent
        "HumidityMax" : 100,
        "PressureMin" : 950, #hPa
        "PressureMax" : 1050,
    },
    "DisplayExtremeBounds": {
        "TemperatureMin" : -20, #celsius
        "TemperatureMax" : 40,
        "LightMin" : 0, #lux
        "LightMax" : 10000,
        "HumidityMin" : 0, #percent
        "HumidityMax" : 100,
        "PressureMin" : 0, #hPa
        "PressureMax" : 2000,
    },
    "DisplayBoundStepSize": {
        "Temperature" : 1, #celsius
        "Light" : 10, #lux
        "Humidity" : 1, #percent
        "Pressure" : 10, #hPa
    },
    "DisplayTimeframes": [ # Second component specifies the time in seconds.
        ("Seconds", 1), 
        ("Minutes", 60),
        ("15 Minutes", 60*15),
        ("Hours", 60 * 60),
        ("Days", 60 * 60 * 24),
        ("Weeks", 60 * 60 * 24 * 7),
    ],
    "DefaultDisplayTimeframe": 0, # Index that determines which of the above timeframes is the default
    "DisplayBorderForGraph": True,
    "DisplayMoveRangeStepSize" : 10,  #How many timeframes/pixels are moved to the left or right while moving the graph?

    #Ticks
    "TicksPerSecond" : TICKS_PER_SECOND,
    "TotalTicks" : -1, #Negative for endless exectuion

    #Joystick
    "TicksPerLongPress": TICKS_PER_SECOND * 1, #Number of ticks after which joystick registers a long button press
    "TicksBeforeRepeatedDirectionalPresses": 5, #Negative to disable multiple direction presses
    "TicksPerRepeatedDirectionalPress": 2,

    #Data model
    "TicksPerMeasurement": TICKS_PER_MEASUREMENT,
    "AggregationsPerDataPoint": int(TICKS_PER_SECOND/TICKS_PER_MEASUREMENT),
    "DBPath": "data",
    "DBFolderFormatstring": "db-{:d}",

    #Data saving
    "AutomaticSaveInterval": TICKS_PER_SECOND * 60 * 15, #negative or 0 to disable

    "LoggingLevel" : "INFO",
}