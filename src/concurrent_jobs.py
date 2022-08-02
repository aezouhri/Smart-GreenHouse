from moist_relay import waterCheck
from timeloop import Timeloop
from datetime import timedelta
#import board
#import RPi.GPIO as GPIO
#from adafruit_seesaw.seesaw import Seesaw
t1 = Timeloop()

@t1.job(interval=timedelta(seconds=15))
def watercheck_job():
    waterCheck()

t1.start()
while(1):{}