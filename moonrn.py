import math, decimal, datetime
import sys
from datetime import datetime, timedelta
import time
import calendar

PI   = 3.141592653589793 # math.pi
sin  = math.sin
cos  = math.cos
tan  = math.tan
asin = math.asin
atan = math.atan2
acos = math.acos
rad  = PI / 180.0
e    = rad * 23.4397 # obliquity of the Earth

dayMs = 1000 * 60 * 60 * 24
J1970 = 2440588
J2000 = 2451545
J0 = 0.0009

# CURRENT TIME
rntime = datetime.now()

# PHASE CACLUALATION
dec = decimal.Decimal

def position(now=None):
   if now is None:
      now = datetime.now()

   diff = now - datetime(2001, 1, 1)
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
print(phasename)

# RISE AND SET CALCULATIONS

def altitude(H, phi, dec):
    return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H))

def siderealTime(d, lw):
     return rad * (280.16 + 360.9856235 * d) - lw

def toDays(date):
    return toJulian(date) - J2000

def declination(l, b):
    return asin(sin(b) * cos(e) + cos(b) * sin(e) * sin(l))

def rightAscension(l, b):
    return atan(sin(l) * cos(e) - tan(b) * sin(e), cos(l))

def azimuth(H, phi, dec):
    return atan(sin(H), cos(H) * sin(phi) - tan(dec) * cos(phi))

def toJulian(date):
    return (time.mktime(date.timetuple()) * 1000) / dayMs - 0.5 + J1970

# geocentric ecliptic coordinates of the moon
def moonCoords(d):
    L = rad * (218.316 + 13.176396 * d)
    M = rad * (134.963 + 13.064993 * d)
    F = rad * (93.272 + 13.229350 * d)

    l  = L + rad * 6.289 * sin(M)
    b  = rad * 5.128 * sin(F)
    dt = 385001 - 20905 * cos(M)

    return dict(
        ra=rightAscension(l, b),
        dec=declination(l, b),
        dist=dt
    )

def hoursLater(date, h):
    return date + timedelta(hours=h)

def getMoonTimes(date, lat, lng):
    """Gets moon rise/set properties for the given time and location."""

    t = date.replace(hour=0,minute=0,second=0)

    hc = 0.133 * rad
    h0 = getMoonPosition(t, lat, lng)["altitude"] - hc
    rise = 0
    sett = 0

    # go in 2-hour chunks, each time seeing if a 3-point quadratic curve crosses zero (which means rise or set)
    for i in range(1,25,2):
        h1 = getMoonPosition(hoursLater(t, i), lat, lng)["altitude"] - hc
        h2 = getMoonPosition(hoursLater(t, i + 1), lat, lng)["altitude"] - hc

        a = (h0 + h2) / 2 - h1
        b = (h2 - h0) / 2
        xe = -b / (2 * a)
        ye = (a * xe + b) * xe + h1
        d = b * b - 4 * a * h1
        roots = 0

        if d >= 0:
            dx = math.sqrt(d) / (abs(a) * 2)
            x1 = xe - dx
            x2 = xe + dx
            if abs(x1) <= 1:
                roots += 1
            if abs(x2) <= 1:
                roots += 1
            if x1 < -1:
                x1 = x2

        if roots == 1:
            if h0 < 0:
                rise = i + x1
            else:
                sett = i + x1

        elif roots == 2:
            rise = i + (x2 if ye < 0 else x1)
            sett = i + (x1 if ye < 0 else x2)

        if (rise and sett):
            break

        h0 = h2

    result = dict()

    if (rise):
        result["rise"] = hoursLater(t, rise)
    if (sett):
        result["set"] = hoursLater(t, sett)

    if (not rise and not sett):
        value = 'alwaysUp' if ye > 0 else 'alwaysDown'
        result[value] = True

    return result

def getMoonPosition(date, lat, lng):
    """Gets positional attributes of the moon for the given time and location."""

    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c = moonCoords(d)
    H = siderealTime(d, lw) - c["ra"]
    h = altitude(H, phi, c["dec"])

    # altitude correction for refraction
    h = h + rad * 0.017 / tan(h + rad * 10.26 / (h + rad * 5.10))
    pa = atan(sin(H), tan(phi) * cos(c["dec"]) - sin(c["dec"]) * cos(H))

    return dict(
        azimuth=azimuth(H, phi, c["dec"]),
        altitude=h,
        distance=c["dist"],
        parallacticAngle=pa
    )

moontimes = getMoonTimes(datetime.now(), 35.499, -80.848)
moonrise1 = list(moontimes.values())[0]
moonset1 = list(moontimes.values())[0]

# RASPBERRY PI STUFF

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

# PHASE MATRICES

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


#MAIN PROGRAM

if moonrise1 > rntime and moonset1 < rntime:
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
