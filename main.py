import threading
import db_func
import spidev
from rpi_ws281x import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import RPi.GPIO as GPIO
import control_func

GPIO.setwarnings(False)

cred = credentials.Certificate('/home/pi/servicekey3.json')
firebase_admin.initialize_app(cred)

hum_tem_thread = threading.Thread(target=db_func.humidity_temperature)
soil_water_thread = threading.Thread(target=db_func.soil_water)
light_sensor_thread = threading.Thread(target=db_func.light_sensor)

led_light_thread = threading.Thread(target=control_func.led_light)
fan_control_thread = threading.Thread(target=control_func.fan_control)
water_servo_thread = threading.Thread(target=control_func.water_servo)
control_red_thread = threading.Thread(target=control_func.control_red)
control_yellow_thread = threading.Thread(target=control_func.control_yellow)
control_green_thread = threading.Thread(target=control_func.control_green)


#hum_tem_thread.start()
#soil_water_thread.start()
light_sensor_thread.start()

led_light_thread.start()
fan_control_thread.start()
#water_servo_thread.start()
control_red_thread.start()
control_yellow_thread.start()
#control_green_thread.start()
