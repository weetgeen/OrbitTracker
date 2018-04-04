import ephem
import requests
import json
import math
import time
import stepperAzi
import stepperAlt
import shelve


def north(stepsTakenAzi,stepsTakenAlt):
    
    stepsToTakeAzi= 1472 - stepsTakenAzi
    if stepsToTakeAzi < 0:
        stepperAzi.clockwise(5,abs(stepsToTakeAzi))
    else:
        stepperAzi.counterclockwise(5,abs(stepsToTakeAzi))
        
    
    stepsToTakeAlt = 128 - stepsTakenAlt
    if stepsToTakeAlt > 0: 
        stepperAlt.counterclockwise(5,abs(stepsToTakeAlt))
    else:
        stepperAlt.clockwise(5,abs(stepsToTakeAlt))
        


from Adafruit_CharLCD import Adafruit_CharLCD
#Initiate LCD
lcd = Adafruit_CharLCD(rs = 21,en=20,d4=24,d5=25,d6=12,d7=16,cols=16,lines=2)
lcd.clear()
lcd.message('Prep orbital\n Tracking') #\n is new line


#StepperAzi
stepsPerRev = 512

#Checking Shelve for previous position, then return to true north first. If there is non assume true North already taken
shelfDirection = shelve.open('Direction')
try:
    stepsTakenAzi = shelfDirection['Azi']
    stepsTakenAlt = shelfDirection['Alt']
    #Bring bot axis to true north
    lcd.clear()
    lcd.message('Initialize to\n True North')
    print("Redirect to true north")
    north(stepsTakenAzi,stepsTakenAlt)
    shelfDirection.close()
except KeyError:
    print("No previous direction value given assume start from true North")
    lcd.clear()
    lcd.message('Assumed True North as Start')
   

shelfDirection.close()

stepsTakenAzi = 1472 #Either north was assumed or the pointer is set to noth by north()
stepsTakenAlt = 128



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
    
    #StepperAzi
    stepsAzimuth = math.floor((iss.az * degrees_per_radian/360)*stepsPerRev*2.875)  
    stepsToTakeAzi= stepsAzimuth - stepsTakenAzi
    stepsTakenAzi = stepsTakenAzi + stepsToTakeAzi
    if stepsTakenAzi == 0:
        stepsTakenAzi = 1472; #resets to inital if north is crossed.
    
    if stepsToTakeAzi < 0:
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
    print('%s: altitude: %4.1f deg azimuth: %5.1f deg' %(trackedBody, issAlt , issAzi) ,gatech.date)

    #Print on LCD Screen
    lcd.clear()
    lcdstring = trackedBody + '\nAzi:%0.0f'  % (issAzi) + '  Alt:%0.0f' % (issAlt)
    lcd.message(lcdstring)
    #lcd.message('ISS (Zarya)\n Azi{}'.format(issAzi).'Alt{}'.format(issAlt))

    #Write to Shelve
    shelfDirection = shelve.open('Direction')
    shelfDirection['Alt'] = stepsTakenAlt
    shelfDirection['Azi'] = stepsTakenAzi
    shelfDirection.close()

    time.sleep(1.0)