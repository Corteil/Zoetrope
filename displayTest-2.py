from SimpleCV import VirtualCamera, Image, Color
import spidev
import time
import RPi.GPIO as GPIO

# define static variables

resetPin = 25
DCpin = 24

SSD1351WIDTH = 128
SSD1351HEIGHT = 96  # SET TO 96 FOR 1.27




#end static

# functions

def rgb_hex565(red, green, blue):
    # take in the red, green and blue values (0-255) as 8 bit values and then combine
    # and shift them to make them a 16 bit hex value in 565 format.
    RGB = (int(red / 8) << 11) | (int(green / 4) << 5) | (int(blue / 8))
    return RGB

#end rgb_hex565

def writeCommand(command):
    GPIO.output(DCpin, False)
    spi.xfer(command)
    

#end writeCommand

def writeData(data):
    GPIO.output(DCpin, True)
    spi.xfer(data)
    
#end writeData

def goTo(x, y):
    if ((x >= SSD1351WIDTH) or (y >= SSD1351HEIGHT)):
        return
    writeCommand([0x15]) # set column
    writeData([x])
    writeData([SSD1351WIDTH-1])
    writeCommand([0x75]) # set row
    writeData([y])
    writeCommand([(SSD1351HEIGHT-1)])
    
    writeCommand([0x5c])  #write ram
    
#end goTo

def drawPixel(x, y, color):
    if ((x >= SSD1351WIDTH) or (y >= SSD1351HEIGHT)):
        return
    if ((x < 0) or (y < 0)):
        return
    
    goTo(x,y)
    
    
    
    GPIO.output(DCpin, True)
    spi.cshigh = False
    
    spi.writebytes([(color >> 8),color])
    spi.cshigh = True
    
    
    
    
    
#end drawPixel

def bigDump(list):
    
    
    GPIO.output(DCpin, True)
    spi.cshigh = False
    
    
    spi.writebytes(list)
    spi.cshigh = True

def fillRect(x, y, w, h, fillcolor):
    if (x >=SSD1351WIDTH) or (y >= SSD1351HEIGHT):
        return
    if y+h > SSD1351HEIGHT:
        h = SSD1351HEIGHT - y - 1
    if x+w > SSD1351WIDTH:
        w = SSD1351WIDTH - x - 1
    
    goTo(x,y)
    
    writeCommand([0x5c])  #write ram
    spi.cshigh = False
    GPIO.output(DCpin, True)
    for i in range(0, w * h,1):
        
        GPIO.output(DCpin, True)
        
        spi.writebytes([(fillcolor >> 8),fillcolor])
        
        
    spi.cshigh = True
  
def fillScreen(fillcolor):
    fillRect(0,0,SSD1351WIDTH, SSD1351HEIGHT, fillcolor)
    
    
# end of functions

# ***** Setup ******


# outputs

GPIO.setmode(GPIO.BCM)              #set GPIO mode to BCM

# reset pin

GPIO.setup(resetPin, GPIO.OUT)
GPIO.output(resetPin, False)

# DC pin

GPIO.setup(DCpin, GPIO.OUT)
GPIO.output(DCpin, False)

#end outputs

#setup SPI bus

spi = spidev.SpiDev()

spi.open(0, 0)
spi.max_speed_hz = 20000000

#end SPI bus

#setup Initialization Sequence for display SSD1351

# spi low
spi.cshigh = True
time.sleep(0.1)
spi.cshigh = False

# toggle reset pin

GPIO.output(resetPin, True)
time.sleep(0.5)
GPIO.output(resetPin, False)
time.sleep(0.5)
GPIO.output(resetPin, True)
time.sleep(0.5)

# start screen config

writeCommand([0xFD]) # set command lock
writeData([0x12])
writeCommand([0xFD]) # set command lock
writeData([0xB1])
writeCommand([0xAE]) # display off
writeCommand([0xB3]) # clockdiv
writeData([0xF1]) # Oscillator Frequency
writeCommand([0xCA]) # MUXRATIO
writeData([127])
writeCommand([0xA0]) # SETREMAP
writeData([0x74])
writeCommand([0x15]) # SETCOLUMN
writeData([0x00])
writeData([0x7F])
writeCommand([0x75]) # SETROW
writeData([0x00])
writeData([0x7F])
writeCommand([0xA1]) # STARTLINE
if (SSD1351HEIGHT == 96):
    writeData([96])
else:
    writeData([0])
writeCommand([0xA2]) # DISPLAYOFFSET
writeData([0x0])
writeCommand([0xB5]) # SETGPIO
writeData([0x00])
writeCommand([0xAB]) # FUNCTIONSELECT
writeData([0x01]) # internal (diode drop)
writeCommand([0xB1]) # PRECHARGE
writeCommand([0x32])
writeCommand([0xBE]) # VCOMH
writeCommand([0x05])
writeCommand([0xA6]) # NORMALDISPLAY
writeCommand([0xC1]) # CONTRASTABC
writeData([0xC8])
writeData([0x80])
writeData([0x55])
writeCommand([0xC7]) # CONTRASTMASTER
writeData([0x0F])
writeCommand([0xB4]) # SETVSL
writeData([0xA0])
writeData([0xB5])
writeData([0x55])
writeCommand([0xB6]) # PRECHARGE2
writeData([0x01])
writeCommand([0xAF]) # DISPLAYON

#end Initialization Sequence for display SSD1351

# Setup video 

video = VirtualCamera("Pirate.mp4", "video") # Load an existing video into a virtual camera

#end set up

# main program

image = video.getImage()
image.embiggen((128, 96), Color.BLUE, (0, 11))#.save("test.jpg") remove '#' if you wish to save test image. Enlarge image and add selected colour bars

#image test
'''
image.show()
print image.getPixel(50,25)
pixelRGB = image.getPixel(50,25)
red = pixelRGB[0]
green = pixelRGB[1]
blue = pixelRGB[2]
hexString = rgb_hex565(red, green, blue)
print hex(hexString)
'''
block = []
for i in range(0,1536,1):
        for x in range(0,128,1):
            for y in range(0,96,1):
                print i
                pixelRGB = image.getPixel(x,y)
                block[i].append(pixelRGB >> 8)
                block[i].append(pixelRGB)


fillScreen(0x0000)

spi.cshigh = False # need to set to cs line to False

goTo(0,0)
for i in range(0,8):
    bigDump(block[0])
print time.time()

spi.close()
