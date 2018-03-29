import ephem
import requests
import json
import math
import time
import stepperAzi
import stepperAlt

from Adafruit_CharLCD import Adafruit_CharLCD

print("deze is gemaakt met sshfs andere branch")
#Initiate LCD
lcd = Adafruit_CharLCD(rs = 21,en=20,d4=24,d5=25,d6=12,d7=16,cols=16,lines=2)
lcd.clear()
lcd.message('Prep orbital\n Tracking') #\n is new line

#StepperAzi
stepsTakenAzi = 1472
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
    stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))
else:
    stepperAlt.clockwise(5,abs(stepsToTakeAlt))

stepsToTakeAlt = -128
stepsTakenAlt = 128
if stepsToTakeAlt > 0:
    stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))
else:
    stepperAlt.clockwise(5,abs(stepsToTakeAlt))

     
lcd.clear()
lcd.message('Prep orbital\n Tracking')

degrees_per_radian = 180.0 / math.pi

send_url = 'http://freegeoip.net/json'  #site used to obtain gps coordinate from ip adress
r = requests.get(send_url)
j = json.loads(r.text)
lat = j['latitude']
lon = j['longitude']


#Get most recent TLE from: https://www.celestrak.com/NORAD/elements/stations.txt
celestrack = requests.get("https://celestrak.com/NORAD/elements/stations.txt")
trackedBody = celestrack.text.splitlines()[0]
TLE1 = celestrack.text.splitlines()[1]
TLE2 = celestrack.text.splitlines()[2]
iss = ephem.readtle(trackedBody, TLE1,TLE2)



gatech = ephem.Observer()
gatech.lon, gatech.lat = lon/degrees_per_radian, lat/degrees_per_radian #Set gps coordinates for observer in radian
gatech.elevation = 5 # elevation of observer
    
print(gatech.date)
print('latitude:',lat,' longitude:',lon) # prints the lattitude and longitude of the observer

#lcd.clear()
#lcdstring = 'Lat:' + str(lat) + '\nLon:'+ str(lon)
#lcd.message(lcdstring)

while True:

    gatech = ephem.Observer()
    gatech.lon, gatech.lat = lon/degrees_per_radian, lat/degrees_per_radian #Set gps coordinates for observer in radian
    gatech.elevation = 5 # elevation of observer
    
    iss.compute(gatech) #All angles returned are in radians!
    
    issAzi = round(iss.az * degrees_per_radian,2)
    issAlt = round(iss.alt * degrees_per_radian,2)
    
    #Stepper
    stepsAzimuth = math.floor((iss.az * degrees_per_radian/360)*stepsPerRev*2.875)  
    stepsToTakeAzi= stepsAzimuth - stepsTakenAzi
    stepsTakenAzi = stepsTakenAzi + stepsToTakeAzi
    if stepsTakenAzi == 0:
        stepsTakenAzi = 1472; #resets to inital if north is crossed.
    
    if stepsToTakeAzi < 0: # Ja hier gaat het mis (Dit is de goeie branch denk ik)
        stepperAzi.clockwise(5,abs(stepsToTakeAzi))
    else:
        stepperAzi.counterclockwise(5,abs(stepsToTakeAzi))
       
    augmentedAlt = issAlt+90  #Makes sure you don't have to work with negatives

    stepsToTakeAlt = math.floor((augmentedAlt/180)*256 - stepsTakenAlt)  #Altitude percentage times step raange
    stepsTakenAlt = stepsTakenAlt + stepsToTakeAlt

    if stepsToTakeAlt > 0: 
        stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))
    else:
        stepperAlt.clockwise(5,abs(stepsToTakeAlt))
       
    #Print in Python Shell    
    print('iss: altitude: %4.1f deg azimuth: %5.1f deg' %(issAlt , issAzi) ,gatech.date,'stepsAzimuth: %4.1f stepsToTakeAzi: %4.1F ' %(stepsAzimuth,stepsToTakeAzi) ,'stepsTakenAzi: %4.1f stepsToTakeAzi: %4.1F ' %(stepsTakenAzi,stepsToTakeAzi) ,'stepsTakenAlt:  %4.1f   stepsToTakeAlt: %5.1f' %(stepsTakenAlt,stepsToTakeAlt)) 

    #Print on LCD Screen
    lcd.clear()
    lcdstring = 'ISS Azi:' + str(issAzi) + '\nAlt:'+ str(issAlt)
    lcd.message(lcdstring)
    #lcd.message('ISS (Zarya)\n Azi{}'.format(issAzi).'Alt{}'.format(issAlt))




    time.sleep(1.0)


    