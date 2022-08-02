import board
import RPi.GPIO as GPIO
from color_detect import color_detection_function
from adafruit_seesaw.seesaw import Seesaw
from picamera import PiCamera
import time
from influxdb import InfluxDBClient
from bluepy import *
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point,WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from timeloop import Timeloop
from datetime import timedelta
t1 = Timeloop()
from firebase import firebase
import pyrebase
fbConfig={
  "apiKey": "AIzaSyA9PLfBhOuJdqI8nbKuFghO-0TAWvnuJPc",
  "authDomain": "iot-smart-greenhouse-ce933.firebaseapp.com",
  "databaseURL": "https://iot-smart-greenhouse-ce933-default-rtdb.firebaseio.com",
  "projectId": "iot-smart-greenhouse-ce933",
  "storageBucket": "iot-smart-greenhouse-ce933.appspot.com",
  "messagingSenderId": "610991632200",
  "appId": "1:610991632200:web:966fb7740dd50b5cf70d7d",
  "measurementId": "G-54GYR0G3RP"
}

firebase=pyrebase.initialize_app(fbConfig)
db = firebase.database()
auth = firebase.auth()
adminEmail = 'lepsch22@gmail.com'
adminPassword = 'BenAndAdnane'
admin = auth.sign_in_with_email_and_password(adminEmail, adminPassword)
def get_current_user():
  curr_user = db.child("Users/current_user").get(admin['idToken']).val()
  return curr_user


# You can generate an API token from the "API Tokens Tab" in the UI
token = 'OA1ibsmsqPOZcb6ocPPo3-t3kn834xRN-z-GvH4HwEbJI_qGshgm_-lRGyUzoi_cBhV3E0aGTm6PPKZjXSKt_g=='
org = "ezouhriadnane@gmail.com"
bucket = "ezouhriadnane's Bucket"

with InfluxDBClient(url="https://us-central1-1.gcp.cloud2.influxdata.com", token=token, org=org) as client:
    point = Point("Sampling").tag("Measurement", "GreenHouse1").time(datetime.utcnow(), WritePrecision.NS)
    write_api=client.write_api(write_options=SYNCHRONOUS)




# Initialize the InfluxDB client
#influx_client = InfluxDBClient(host='localhost', port=8086, username='root',
#password='root', database='Project')

#Setting up I2C for GPIO Pins only GPIO 17 is used.
GPIO.setmode(GPIO.BCM)
i2c_bus = board.I2C()
pinList = [17]
#Initialize the GPIO Pins, and signal to send out.
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
#Adafruit library used to communicate with Moisture Sensor
ss = Seesaw(i2c_bus, addr=0x36)

#@t1.job(interval=timedelta(seconds=5))
def grafana_data():
  touch = ss.moisture_read()
  print("Sending moisture to grafana")
  send_data("moisture",touch)
  temp = ss.get_temp()#Celsius
  temp_f = round(((temp * 1.8) + 32),2)#Farenheit
  print("Sending soil_temp to grafana")
  send_data("soil temperature F",temp_f)

print('Test')

def onlyMoisture():
  # read moisture level through capacitive touch pad
  touch = ss.moisture_read()
  print("Moisture level of soil: " + str(touch))
  point3= Point("Sampling").tag("Measurement","GreenHouse1").field("Moisture",touch).time(datetime.utcnow(), WritePrecision.NS)
  write_api.write(bucket=bucket, record=[point3])
  #send_data("moisture",touch)
  return touch

def onlyTempF():
  temp = ss.get_temp()#Celsius
  temp_f = round(((temp * 1.8) + 32),2)#Farenheit
  print("Temperature in F: "+str(temp_f))
  send_data("soil temperature F",temp_f)
  return temp_f


def send_data(measurename,measure):
  point_data= {

    "measurement": measurename,
    "fields":
    {
    "Value":measure
    }
    }
  print(measure,"sent value" )
  #influx_client.write_points( [ point_data ] )


#Check the moisture level of the water.
def waterCheck():
  # read moisture level through capacitive touch pad
  touch = ss.moisture_read()
  # read temperature from the temperature sensor
  temp = ss.get_temp()#Celsius
  temp_f = round(((temp * 1.8) + 32),2)#Farenheit
  print("Moisture level of soil: " + str(touch)+", Temperature in f: "+str(temp_f),", Temperature in C")
  
  point3= Point("Sampling").tag("Measurement","GreenHouse1").field("Moisture",touch).time(datetime.utcnow(), WritePrecision.NS)
  write_api.write(bucket=bucket, record=[point3])

  curr_user = get_current_user()
  db.child("Users/"+curr_user+"/Current Values").update({"moisture":touch},admin['idToken'])
  db.child("Users/"+curr_user+"/Current Values").update({"temp_of_soil":temp_f},admin['idToken'])
  bool2 = db.child("Users/"+curr_user+"/water_status").get(admin['idToken']).val()
  if touch < 500 and bool2:
    db.child("Users/"+curr_user).update({"water_status":False},admin['idToken'])
    try:
      #Setting up GPIO this is needed because to stop the pin we are using pin cleanup which cleans all deafults
      GPIO.setmode(GPIO.BCM)
      pinList = [17]  
      for i in pinList:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
      
      print("Watering for 10 seconds.")
      GPIO.output(17, GPIO.LOW)
      print ("Relay engaged, watering...")
      time.sleep(10)
      db.child("Users/"+curr_user).update({"water_status":True},admin['idToken'])
      GPIO.cleanup()
    except KeyboardInterrupt:
          print ("Critical error!")
          # Reset GPIO settings
          GPIO.cleanup()
  else:
    print("Watering not needed!")
    print("Moisture level of soil: " + str(touch)+", Temperature in f: "+str(temp_f),", Temperature in C")
    db.child("Users/"+curr_user+"/Current Values").update({"moisture":touch},admin['idToken'])
    db.child("Users/"+curr_user+"/Current Values").update({"temp_of_soil":temp_f},admin['idToken'])
  

#In case of sensor failure manual watering is necessary.
def forcefeed():
  startTime = time.time()
  try:
      GPIO.setmode(GPIO.BCM)
      pinList = [17]  
      for i in pinList:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
      print("Manual watering for 10 seconds.")
      GPIO.output(17, GPIO.LOW)
      print ("Relay engaged, watering...")
      while(time.time() < startTime+10):{}
      #time.sleep(10)
  except KeyboardInterrupt:
      print ("Critical error!")
      # Reset GPIO settings
      GPIO.cleanup()
  GPIO.cleanup()
  #return True
def color_detect(camera):
  time.sleep(2)
  camera.awb_mode = 'auto'
  camera.capture("/home/pi/Project/images/pre_color_detect.jpg")
  color_detection_function("/home/pi/Project/images/pre_color_detect.jpg")
  
def take_picture(camera):
  time.sleep(2)
  camera.capture("/home/pi/Project/images/normal_pic.jpg")
  print("Done.")


