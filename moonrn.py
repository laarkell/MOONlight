import math, decimal, datetime
import RPi.GPIO as GPIO
import sys

dec = decimal.Decimal

def position(now=None):
   if now is None:
      now = datetime.datetime.now()

   diff = now - datetime.datetime(2001, 1, 1)
   days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
   lunations = dec("0.20439731") + (days * dec("0.03386319269"))

   return lunations % dec(1)

def phase(pos):
   index = (pos * dec(8)) + dec("0.5")
   index = math.floor(index)
   return {
      0: "newMoon",
      1: "waxCres",
      2: "firstQ",
      3: "waxGib",
      4: "fullMoon",
      5: "wanGib",
      6: "lastQ",
      7: "wanCres",
   }[int(index) & 7]

pos = position()
phasename = phase(pos)

#define PINs according to cabling
columnDataPin = 20
rowDataPin = 21
latchPIN = 14
clockPIN = 15

#set pins to putput
GPIO.setmode(GPIO.BCM)
GPIO.setup((columnDataPin,rowDataPin,latchPIN,clockPIN),GPIO.OUT)

#define shift register update function
def shift_update_matrix(input_Col,Column_PIN,input_Row,Row_PIN,clock,latch):
  #put latch down to start data sending
  GPIO.output(clock,0)
  GPIO.output(latch,0)
  GPIO.output(clock,1)

  #load data in reverse order
  for i in range(15, -1, -1):
    GPIO.output(clock,0)
    #instead of controlling only 1 shift register, we drive both together
    GPIO.output(Column_PIN, int(input_Col[i]))
    GPIO.output(Row_PIN, int(input_Row[i]))
    GPIO.output(clock,1)

  #put latch up to store data on register
  GPIO.output(clock,0)
  GPIO.output(latch,1)
  GPIO.output(clock,1)

#map your output into 1 (LED off) and 0 (led on) sequences

fullMoon = [["1111110000111111"],
            ["1111000000001111"],
            ["1110000000000111"], 
            ["1100000000000011"], 
            ["1000000000000001"], 
            ["1000000000000001"], 
            ["0000000000000000"],
            ["0000000000000000"],
            ["0000000000000000"],
            ["0000000000000000"],
            ["1000000000000001"],
            ["1000000000000001"],
            ["1100000000000011"], 
            ["1110000000000111"],
            ["1111000000001111"],
            ["1111110000111111"]]

newMoon = [["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"],
           ["1111111111111111"]]

waxCres =  [["1111111000111111"],
            ["1111111110001111"],
            ["1111111111000111"], 
            ["1111111111100011"], 
            ["1111111111100001"], 
            ["1111111111100001"], 
            ["1111111111111000"],
            ["1111111111111000"],
            ["1111111111111000"],
            ["1111111111111000"],
            ["1111111111100001"],
            ["1111111111100001"],
            ["1111111111100011"], 
            ["1111111111000111"],
            ["1111111110001111"],
            ["1111111000111111"]]

firstQ  =  [["1111111100111111"],
            ["1111111100001111"],
            ["1111111100000111"], 
            ["1111111100000011"], 
            ["1111111100000001"], 
            ["1111111100000001"], 
            ["1111111100000000"],
            ["1111111100000000"],
            ["1111111100000000"],
            ["1111111100000000"],
            ["1111111100000001"],
            ["1111111100000001"],
            ["1111111100000011"], 
            ["1111111100000111"],
            ["1111111100001111"],
            ["1111111100111111"]]

waxGib  =  [["1111110000111111"],
            ["1111000000001111"],
            ["1110110000000111"], 
            ["1111111000000011"], 
            ["1111111100000001"], 
            ["1111111100000001"], 
            ["1111111100000000"],
            ["1111111110000000"],
            ["1111111110000000"],
            ["1111111100000000"],
            ["1111111100000001"],
            ["1111111100000001"],
            ["1111111000000011"], 
            ["1110110000000111"],
            ["1111000000001111"],
            ["1111110000111111"]]

wanGib   = [["1111110000111111"],
            ["1111000000001111"],
            ["1110000000110111"], 
            ["1100000001111111"], 
            ["1000000011111111"], 
            ["1000000011111111"], 
            ["0000000011111111"],
            ["0000000111111111"],
            ["0000000111111111"],
            ["0000000011111111"],
            ["1000000011111111"],
            ["1000000011111111"],
            ["1100000001111111"], 
            ["1110000000110111"],
            ["1111000000001111"],
            ["1111110000111111"]]

lastQ    = [["1111110011111111"],
            ["1111000011111111"],
            ["1110000011111111"], 
            ["1100000011111111"], 
            ["1000000011111111"], 
            ["1000000011111111"], 
            ["0000000011111111"],
            ["0000000111111111"],
            ["0000000111111111"],
            ["0000000011111111"],
            ["1000000011111111"],
            ["1000000011111111"],
            ["1100000011111111"], 
            ["1110000011111111"],
            ["1111000011111111"],
            ["1111110011111111"]]

wanCres  = [["1111110000111111"],
            ["1111000111111111"],
            ["1110001111111111"], 
            ["1100011111111111"], 
            ["1000011111111111"], 
            ["1000011111111111"], 
            ["0001111111111111"],
            ["0001111111111111"],
            ["0001111111111111"],
            ["0001111111111111"],
            ["1000011111111111"],
            ["1000011111111111"],
            ["1100011111111111"], 
            ["1110001111111111"],
            ["1111000111111111"],
            ["1111110000111111"]]


#main program, calling shift register function to activate 16x16 LED Matrix
while True:
  try:
    RowSelect=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,16): # last value in rage is not included by default
      # send row data and row selection to registers
      shift_update_matrix(''.join(map(str, phasename[i])),columnDataPin,\
                          ''.join(map(str, RowSelect)),rowDataPin,clockPIN,latchPIN)
      #shift row selector
      RowSelect = RowSelect[-1:] + RowSelect[:-1]

#PINs final cleaning on interrupt
  except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
