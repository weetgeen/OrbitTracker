import ephem
import requests
import json
import math
import time
import stepperAzi
import stepperAlt

from Adafruit_CharLCD import Adafruit_CharLCD

degrees_per_radian = 180.0 / math.pi

#Initiate LCD
lcd = Adafruit_CharLCD(rs = 21,en=20,d4=24,d5=25,d6=12,d7=16,cols=16,lines=2)
lcd.clear()
lcd.message('Prep orbital\n Tracking') #\n is new line

#StepperAzi
stepsTakenAzi = 0
stepsPerRev = 512

stepsTakenAlt = 0


#Stepper Freedom of motion checks
lcd.clear()
lcd.message('Initialize Alt\n Stepper') #\n is new line
#Stepper
stepsTakenAlt = 128
stepsToTakeAlt = 128
stepsTakenAlt = 256 
if stepsToTakeAlt > 0:
    stepperAlt.clockwise(5,abs(stepsToTakeAlt))
else:
    stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))

stepsToTakeAlt = -128
stepsTakenAlt = 128
if stepsToTakeAlt > 0:
    stepperAlt.clockwise(5,abs(stepsToTakeAlt))
else:
    stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))

     
lcd.clear()
lcd.message('Prep orbital\n Tracking')

send_url = 'http://freegeoip.net/json'  #site used to obtain gps coordinate from ip adress
r = requests.get(send_url)
j = json.loads(r.text)
lat = j['latitude']
lon = j['longitude']
    
gatech = ephem.Observer()
gatech.lon, gatech.lat = lon/degrees_per_radian, lat/degrees_per_radian #Set gps coordinates for observer in radian
gatech.elevation = 5 # elevation of observer
    
print(gatech.date)
print('latitude:',lat,' longitude:',lon) # prints the lattitude and longitude of the observer

while True:


    
    sun = ephem.Sun(gatech) #All angles returned are in radians!
    
    sunAzi = round(sun.az * degrees_per_radian,2)
    sunAlt = round(sun.alt * degrees_per_radian,2)

       
    #Stepper
    stepsAzimuth = math.floor((sunAzi/360)*stepsPerRev*2.875)  
    stepsToTakeAzi= stepsAzimuth - stepsTakenAzi
    stepsTakenAzi = stepsTakenAzi + stepsToTakeAzi
    if stepsToTakeAzi < 0:
        stepperAzi.clockwise(5,abs(stepsToTakeAzi))
    else:
        stepperAzi.counterclockwise(5,abs(stepsToTakeAzi))
       
    augmentedAlt = sunAlt+90  #Makes sure you don't have to work with negatives

    stepsToTakeAlt = math.floor((augmentedAlt/180)*256 - stepsTakenAlt)  #Altitude percentage times step raange
    stepsTakenAlt = stepsTakenAlt + stepsToTakeAlt

    if stepsToTakeAlt > 0:#Moves stepper altitude
        stepperAlt.clockwise(5,abs(stepsToTakeAlt))
    else:
        stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))
       
    #Print in Python Shell    
    print('sun: altitude: %4.1f deg azimuth: %5.1f deg' %(sunAlt , sunAzi) ,gatech.date,'stepsTakenAzi: %4.1f stepsToTakeAzi: %4.1F ' %(stepsTakenAzi,stepsToTakeAzi) ,'stepsTakeAlt:  %4.1f   stepsToTakeAlt: %5.1f' %(stepsTakenAlt,stepsToTakeAlt)) 

    #Print on LCD Screen
    lcd.clear()
    lcdstring = 'sun Azi:' + str(sunAzi) + '\nAlt:'+ str(sunAlt)
    lcd.message(lcdstring)
    #lcd.message('ISS (Zarya)\n Azi{}'.format(sunAzi).'Alt{}'.format(sunAlt))



    time.sleep(3600.0)


    
