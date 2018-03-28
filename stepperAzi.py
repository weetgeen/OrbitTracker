import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
coil_A_1_pin = 6 # pink
coil_A_2_pin = 13 # orange
coil_B_1_pin = 19 # blue
coil_B_2_pin = 26 # yellow

# adjust if different
StepCount = 8
Seq    = [0,0,0,0,0,0,0,0] #Initializes vector
Seq[0] = [0,1,0,0]
Seq[1] = [0,1,0,1]
Seq[2] = [0,0,0,1]
Seq[3] = [1,0,0,1]
Seq[4] = [1,0,0,0]
Seq[5] = [1,0,1,0]
Seq[6] = [0,0,1,0]
Seq[7] = [0,1,1,0]
 

GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)
 

 
def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)
 
def counterclockwise(delay, steps):
    for i in list(range(steps)):
        for j in list(range(StepCount)):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay/1000)
 
def clockwise(delay, steps):
    for i in list(range(steps)):
        for j in list(reversed(range(StepCount))):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay/1000)
 
#if __name__ == '__main__':
 #   while True:
  #      delay = input("Time Delay (s/1000000)?")
   #     steps = input("How many steps forward? ")
    #    clockwise(int(delay) / 1000.0, int(steps))
     #   steps = input("How many steps backwards? ")
      #  counterclockwise(int(delay) / 1000.0, int(steps))