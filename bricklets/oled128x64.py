from tinkerforge.bricklet_oled_128x64 import BrickletOLED128x64

import time

from settings import settings
from bricklets.bricklet import Bricklet


class OLED128x64(Bricklet):

    WIDTH = 128 # Columns
    HEIGHT = 64 # Rows  

    def __init__(self, controller):
        super().__init__(controller)
        self.__oled = BrickletOLED128x64(settings["UIDs"]["OLED128x64"], self._controller.ipcon)
        self.__oled.clear_display()



    def shutdown(self):
        super().shutdown()
        self.clear()

    

    def displayDatapoints(self, data, lowerBound, upperBound, drawBorder):
        #Convert into pixel matrix. 0,0 is top left
        pixels = [[0] * self.WIDTH for _ in range(0, self.HEIGHT)]
        for i in range(-1, max(-len(data) - 1, -self.WIDTH - 1), -1):
            if data[i] != None and lowerBound <= data[i] < upperBound:
                position = int((data[i] - lowerBound)/(upperBound-lowerBound)*(self.HEIGHT - 2 * int(drawBorder))) #Position counted from bottom
                pixels[self.HEIGHT - 1 - position - int(drawBorder)][self.WIDTH + i - int(drawBorder)] = 1
        
        if drawBorder:
            pixels[0] = [1] * self.WIDTH
            pixels[-1] = [1] * self.WIDTH
            for i in range (0, self.HEIGHT):
                pixels[i][0] = 1
                pixels[i][-1] = 1

        self.printPixelMatrix(pixels)



    #Prints a 2 dimension matrix containing only 0's and 1's. Top left is (0,0)
    def printPixelMatrix(self, pixels):
        #Convert pixel matrix to byte matrix for oled
        bytepixels = [[0] * self.WIDTH for _ in range(0,self.HEIGHT//8)]
        for row in range(0, self.HEIGHT//8):
            for column in range(0, self.WIDTH):
                for i in range (0,8):
                    bytepixels[row][column] |= pixels[row*8 +i][column] << i
        
        #Write output
        for i in range (0,16):
            args = [i%2 * self.WIDTH//2, (i%2 + 1) * self.WIDTH//2 -1, i//2, i//2]
            self.__oled.new_window(*args)
            self.__oled.write(bytepixels[i//2][i%2 * self.WIDTH//2 : (i%2 +1) * self.WIDTH//2 ])



    def clear(self):
        self.__oled.new_window(0 , self.WIDTH-1 , 0, self.HEIGHT/8 -1)
        self.__oled.clear_display()

