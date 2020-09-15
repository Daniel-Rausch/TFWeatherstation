import logging

class Bricklet():
    def __init__(self, controller):
        self._controller = controller
        logging.info("Initializing: "+ type(self).__name__)


    def shutdown(self):
        logging.info("Shutdown: "+ type(self).__name__)