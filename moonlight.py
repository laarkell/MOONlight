# https://peppe8o.com/download/python/8x8LedDisplay.py

import RPi.GPIO as GPIO
import sys

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

#main program, calling shift register function to activate 16x16 LED Matrix
while True:
  try:
    RowSelect=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,16): # last value in rage is not included by default
      # send row data and row selection to registers
      shift_update_matrix(''.join(map(str, waxCres[i])),columnDataPin,\
                          ''.join(map(str, RowSelect)),rowDataPin,clockPIN,latchPIN)
      #shift row selector
      RowSelect = RowSelect[-1:] + RowSelect[:-1]

#PINs final cleaning on interrupt
  except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()

