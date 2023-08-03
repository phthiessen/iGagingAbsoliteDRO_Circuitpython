#iGaging AbsoluteDRO Plus interface hack
#Philip Thiessen
#created 2023-08-03

import digitalio
import time
import board
import simpleio


CLK = digitalio.DigitalInOut(board.D5)  #corresponds to D- (white) on a USB Micro breakout board
DATA = digitalio.DigitalInOut(board.D6) #corresponds to D+ (green) on a USB Micro breakout board
REQ = digitalio.DigitalInOut(board.D9)  #corresponds to ID (other) on a USB Micro breakout board

REQ.direction = digitalio.Direction.OUTPUT
CLK.direction = digitalio.Direction.INPUT
CLK.pull = digitalio.Pull.UP  #using an additional pullup resistor of >= 10kOhm can help too
DATA.direction = digitalio.Direction.INPUT
DATA.pull = digitalio.Pull.UP #using an additional pullup resistor of >= 10kOhm can help too

REQ.value = True #initialize request HIGH to avoid timing errors


def read():
    REQ.value = False  #pull REQ pin low to request data from read head
    myData = []
    i = 0
    clock = 0
    lastClock = 0
    x = 0

    #using while loops for this helps avoid timing errors and uncertain clock speed
    while i < 13:  #data is split into 13 four bit binary numbers
        j = 0
        while j < 4:  #read the 4 bits on the falling edge of the CLK pin.
            clock = int(CLK.value)
            if clock == 0 and clock != lastClock:
                x = simpleio.bitWrite(x, j, int(DATA.value)) #flip bits as appropriate
                j = j + 1
            lastClock = clock
        myData.append(x)
        i = i + 1
    
    #number is negative only if place 4 is equal to 8
    if myData[4] == 8:
        negate = -1
    else:
        negate = 1

    #ignore places 0-3 in myData list, and places 11 and 12 are for units and decimal place, but decimal is always 2 and units are always 'mm'

    number = (myData[5]*1000 + myData[6]*100 + myData[7]*10 + myData[8] + myData[9]*.1 + myData[10]*.01)*negate #build the bits together into a measurement

    REQ.value = True #turn request back off to avoid future timing errors

    return number
    

while True:


    number = read()
    print(number)

    time.sleep(2)



