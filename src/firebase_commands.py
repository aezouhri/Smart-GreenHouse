from moist_relay import *
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
storage = firebase.storage()
auth = firebase.auth()
adminEmail = 'lepsch22@gmail.com'
adminPassword = 'BenAndAdnane'
admin = auth.sign_in_with_email_and_password(adminEmail, adminPassword)

camera = PiCamera()

global curr_user

def get_current_user():
  curr_user = db.child("Users/current_user").get(admin['idToken']).val()
  return curr_user


def get_picture_of_plant(message):
  curr_user = get_current_user()
  print("Normal picture of plant listener.",curr_user)
  bool = db.child("Users/"+curr_user+"/get_picture_of_plant").get(admin['idToken']).val()
  if(bool):
    print("getting picture")
    db.child("Users/"+curr_user).update({"get_picture_of_plant":False},admin['idToken'])
    take_picture(camera)
    storage.child("normal_image/normal_"+curr_user+".jpg").put("/home/pi/Project/images/normal_pic.jpg")

def get_picture_of_segmented_plant(message):
  curr_user = get_current_user()
  print("Segmented picture of plant listener.",curr_user)
  bool = db.child("Users/"+curr_user+"/get_picture_of_segmented_image").get(admin['idToken']).val()
  if(bool):
    print("getting segmentred picture")
    db.child("Users/"+curr_user).update({"get_picture_of_segmented_image":False},admin['idToken'])
    color_detect(camera)
    storage.child("segmented_images/segmented_"+curr_user+".jpg").put("/home/pi/Project/images/color_outlined_pic.jpg")
 

def get_moisture(message):
    curr_user = get_current_user()
    print("moisture listener.",curr_user)
    bool = db.child("Users/"+curr_user+"/get_moisture").get(admin['idToken']).val()
    if(bool):
      db.child("Users/"+curr_user).update({"get_moisture":False},admin['idToken'])
      moisture = onlyMoisture()
      print("Fetching moisture level!")
      db.child("Users/"+curr_user+"/Current Values").update({"moisture":moisture},admin['idToken'])

def command_forcefeed(message):
    curr_user = get_current_user()
    print("force_water listener.",curr_user)
    bool = db.child("Users/"+curr_user+"/force_water").get(admin['idToken']).val()
    bool2 = db.child("Users/"+curr_user+"/water_status").get(admin['idToken']).val()
    if(bool and bool2):
      db.child("Users/"+curr_user).update({"force_water":False},admin['idToken'])
      print("Force feeding!")
      db.child("Users/"+curr_user).update({"water_status":False},admin['idToken'])
      forcefeed()
      db.child("Users/"+curr_user).update({"water_status":True},admin['idToken'])
    else:
      print("watering in progress")
      db.child("Users/"+curr_user).update({"force_water":False},admin['idToken'])


def get_temperature_soil(message):
    curr_user = get_current_user()
    print("soil_temp listener.",curr_user)
    bool = db.child("Users/"+curr_user+"/get_temperature_soil").get(admin['idToken']).val()
    if(bool):
      db.child("Users/"+curr_user).update({"get_temperature_soil":False},admin['idToken'])
      temp_of_soil = onlyTempF()
      print("Fetching temp of Soil!")
      db.child("Users/"+curr_user+"/Current Values").update({"temp_of_soil":temp_of_soil},admin['idToken'])


def force_check(message):
    curr_user = get_current_user()
    print("force_check listener.",curr_user)
    bool = db.child("Users/"+curr_user+"/force_check").get(admin['idToken']).val()
    if(bool):
      db.child("Users/"+curr_user).update({"force_check":False},admin['idToken'])
      waterCheck()
      print("Force checking garden status!")
      #db.child("Users/"+curr_user+"/Current Values").update({"temp_of_soil":temp_of_soil})

#INitialize listeners for all users   
temp_dict =  db.child("Users/").get(admin['idToken']).val().keys()
print(temp_dict)
for curr_user in temp_dict:
  if(curr_user != 'current_user'):
    print(curr_user, "user in listener loop")
    db.child("Users/"+curr_user+"/force_water").stream(command_forcefeed,admin['idToken'])
    db.child("Users/"+curr_user+"/get_moisture").stream(get_moisture,admin['idToken'])
    db.child("Users/"+curr_user+"/get_temperature_soil").stream(get_temperature_soil,admin['idToken'])
    db.child("Users/"+curr_user+"/force_check").stream(force_check,admin['idToken'])
    db.child("Users/"+curr_user+"/get_picture_of_plant").stream(get_picture_of_plant,admin['idToken'])
    db.child("Users/"+curr_user+"/get_picture_of_segmented_image").stream(get_picture_of_segmented_plant,admin['idToken'])

