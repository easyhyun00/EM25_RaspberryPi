import firebase_admin
import RPi.GPIO as GPIO
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
import time
import pyfirmata
from rpi_ws281x import *
import argparse
import board
import neopixel 
from neopixel import NeoPixel
import atexit
import Adafruit_DHT
import datetime
import schedule

def load_user():
    db=firestore.client()
    doc_ref=db.collection("Users").document("W6pS60AsPTQP0dduTOTU7YCVvp13")
    users = doc_ref.get()
    plantNo = users.to_dict()["plantNo"]
    time.sleep(1)
    return plantNo
    
def save_LED(LED):
    db = firestore.client()
    data = {
        u'LED' : LED}
    doc_ref = db.collection(u'farminformation').document("LED")
    doc_ref.set(data)
    time.sleep(1)
    
def call_light():
    plantNo = load_user()
    db=firestore.client()
    doc_ref=db.collection("Plants").document(plantNo)
    plant = doc_ref.get()
    plant_light = plant.to_dict()["plantLight"]
    time.sleep(1)
    return plant_light

def call_high_tem():
    plantNo = load_user()
    db=firestore.client()
    doc_ref=db.collection("Plants").document(plantNo)
    plant = doc_ref.get()
    High = plant.to_dict()["plantTemperatureHigh"]
    time.sleep(1)
    return High

def call_low_tem():
    plantNo = load_user()
    db=firestore.client()
    doc_ref=db.collection("Plants").document(plantNo)
    plant = doc_ref.get()
    Low = plant.to_dict()["plantTemperatureLow"]
    time.sleep(1)
    return Low

def call_current_tem():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('tem_hum')
    doc = doc_ref.get()
    current_temperature = doc.to_dict()['temperature']
    print("현재 온도: ", current_temperature)
    time.sleep(1)
    return current_temperature

def call_current_light():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('light')
    doc = doc_ref.get()
    current_light = doc.to_dict()['light']
    print("현재 lux: ", current_light)
    time.sleep(1)
    return current_light

def call_soil_water():
    plantNo = load_user()
    db=firestore.client()
    doc_ref=db.collection("Plants").document(plantNo)
    plant = doc_ref.get()
    plant_Water = plant.to_dict()["plantWater"]
    time.sleep(1)
    return plant_Water

def call_current_soil_water():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('soil_water')
    doc = doc_ref.get()
    current_soil_water = doc.to_dict()['soil_water_percent']
    print("현재 soil_water: ", current_soil_water)
    time.sleep(1)
    return current_soil_water

def call_LED():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('LED')
    doc = doc_ref.get()
    LED = doc.to_dict()['LED']
    print("LED: ", LED)
    time.sleep(1)
    return LED

def call_Color():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('Color_LED')
    doc = doc_ref.get()
    red = doc.to_dict()['red']
    yellow = doc.to_dict()['yellow']
    if red==0 and yellow==0:
        time.sleep(1)
        return 1
    else:
        time.sleep(1)
        return 0

def save_red(red):
    db = firestore.client()
    data = {
        u'red' : red}
    
    doc_ref = db.collection(u'farminformation').document("Color_LED")
    doc_ref.update(data)
    time.sleep(1)
    
def save_yellow(yellow):
    db = firestore.client()
    data = {
        u'yellow' : yellow}
    
    doc_ref = db.collection(u'farminformation').document("Color_LED")
    doc_ref.update(data)
    time.sleep(1)
    
def save_green(green):
    db = firestore.client()
    data = {
        u'green' : green}
    
    doc_ref = db.collection(u'farminformation').document("Color_LED")
    doc_ref.update(data)
    time.sleep(1)
    
def led_light():
    NUM_LEDS = 30
    PIN =board.D21
    pixels = neopixel.NeoPixel(PIN,NUM_LEDS)

    # 파란색과 빨간색 값 설정
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    
    try:
        while True:
            # DB에서 light 값 가져오기
            plant_light=call_light()
            print("plant_light : ", plant_light)
            current_time = datetime.datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            kst = datetime.timezone(datetime.timedelta(hours=9))
            current_time_kst = current_time.astimezone(kst)
            
            current_light = call_current_light()
            
            if plant_light == '1': # 9시부터 18시까지 LED 항상 켜기
                if current_time_kst.hour > 9 and current_time_kst.hour < 18:
                    # LED 켜기
                    for i in range(NUM_LEDS):
                        if i % 6 == 0:
                            pixels[i] = BLUE
                        else:
                            pixels[i] = RED
                    pixels.show()
                    save_LED(1)
                else:
                    # LED 끄기
                    pixels.fill((0,0,0))
                    pixels.show()
                    save_LED(0)
            elif plant_light == '2': # 9시부터 18시까지 LUX가 800 이상 LED 켜기
                if current_time_kst.hour > 9 and current_time_kst.hour < 18 and current_light <= 800:
                    # LED 켜기
                    for i in range(NUM_LEDS):
                        if i % 6 == 0:
                            pixels[i] = BLUE
                        else:
                            pixels[i] = RED
                    pixels.show()
                    save_LED(1)
                else:
                    # LED 끄기
                    print("led off")
                    pixels.fill((0,0,0))
                    pixels.show()
                    save_LED(0)
            else: # 항상 LED 끄기
                if current_time_kst.hour > 9 and current_time_kst.hour < 18 and current_light < 300:
                    for i in range(NUM_LEDS):
                        if i % 6 == 0:
                            pixels[i] = BLUE
                        else:
                            pixels[i] = RED
                    pixels.show()
                    save_LED(1)
                else:
                    pixels.fill((0,0,0))
                    pixels.show()
                    save_LED(0)
    finally:
        print("끝")
        
def fan_control():
    GPIO.setmode(GPIO.BCM)
    # 모터 드라이버 핀 번호
    motor_pin1 = 20 # GPIO 23, A-1A
    motor_pin2 = 16 # GPIO 24, B-1A

    GPIO.setup(motor_pin1, GPIO.OUT)
    GPIO.setup(motor_pin2, GPIO.OUT)
    
    try: 
        while True:
            # 온습도 센서값 읽어오기
            current_temperature = call_current_tem()
            High = call_high_tem()
            # 온도값 비교하여 모터 드라이버 제어
            if float(current_temperature) > int(High):
                print("if")
                GPIO.output(motor_pin1, GPIO.HIGH)
                GPIO.output(motor_pin2, GPIO.HIGH)
                time.sleep(10)
                print("높아요")
            else:
               print("else")
               # 팬 작동 X
               GPIO.output(motor_pin1, GPIO.LOW)
               GPIO.output(motor_pin2, GPIO.LOW)
               time.sleep(10)
               print("낮아요")
    
    finally:
        GPIO.cleanup()

def find_step(current_soil_water):
    # 4단계 중 어느 곳에 해당하는지 구분
    if 0 < current_soil_water and current_soil_water <= 20:
        Soil_step = 4
    elif 20 < current_soil_water and current_soil_water <= 30:
        Soil_step = 3
    elif 30 < current_soil_water and current_soil_water <= 55:
        Soil_step = 2
    else:
        Soil_step = 1
    return Soil_step

def call_water():
    db=firestore.client()
    doc_ref = db.collection('farminformation').document('push')
    doc = doc_ref.get()
    water = doc.to_dict()['water']
    return water

def save_water(n):
    db = firestore.client()
    data = {
        u'water' : n}
    
    doc_ref = db.collection(u'farminformation').document("push")
    doc_ref.update(data)
    time.sleep(1)

def water_servo():
    GPIO.setmode(GPIO.BCM)
    # 핀 설정
    pump_pin = 25
    servo_pin = 19
    
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(pump_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)
    
    plant_Water = call_soil_water()
    
    try:
        #current_soil_water = call_current_soil_water()
        current_soil_water = 25
        plant_Water = 2
        Soil_step = find_step(current_soil_water)
        # 조건에 따라 모터와 서보모터를 작동
        if (Soil_step > plant_Water):
            #gap = Soil_step - plant_Water
            #print(gap)
            gap = 1
            pwm.start(3.0) # 0.6ms
            pwm.ChangeDutyCycle(4.0)
            time.sleep(1)
            print("서보모터 가동")        

            GPIO.output(pump_pin, GPIO.HIGH)
            print("워터펌프 가동")
            time.sleep(gap*4) # 차이 클수록 물 주는 양 증가, 즉 워터펌프 가동 시간 증가

            GPIO.output(pump_pin, GPIO.LOW)
            print("워터펌프 중지")
        
            time.sleep(5) # 남은 물 공급
        
            print("뚜껑 닫는 중..")
            pwm.ChangeDutyCycle(7.8)
            time.sleep(1)
            
            #push/water 값에 따라 물 공급 알림
            water = call_water()
            if water == 5:
                save_water(gap)
            else:
                save_water(water+gap)
        
    finally:
        print("1111")
        
def control_red():
    GPIO.setmode(GPIO.BCM)
    red_led = 5
    GPIO.setup(red_led, GPIO.OUT)
    GPIO.output(red_led, GPIO.LOW)
    
    try:
        while True:
            current_temperature = call_current_tem()
            High = call_high_tem()
            Low = call_low_tem()
            if current_temperature <= High and current_temperature >= Low:
                print("온도 만족")
                GPIO.output(red_led, GPIO.LOW)
                # 온도 만족 시 빨간색 LED 꺼짐
                save_red(0)
                time.sleep(1)
            else:
                print("온도 불만족")
                GPIO.output(red_led, GPIO.HIGH) # 온도 불만족 시 빨간색 LED 켜짐
                save_red(1)
                time.sleep(1)
                
    finally:
        GPIO.output(red_led, GPIO.LOW)
        GPIO.cleanup()
        
def control_yellow():
    GPIO.setmode(GPIO.BCM)
    yellow_led = 6
    GPIO.setup(yellow_led, GPIO.OUT)
    GPIO.output(yellow_led, GPIO.LOW)
    
    try:
        while True:
            LED = call_LED()
            
            if LED == 0:
                print("조도 만족")
                GPIO.output(yellow_led, GPIO.LOW)
                save_yellow(0)
                time.sleep(1)
            else:
                print("조도 부족")
                GPIO.output(yellow_led, GPIO.HIGH)
                save_yellow(1)
                time.sleep(1)
                
    finally:
        GPIO.output(yellow_led, GPIO.LOW)
        GPIO.cleanup()

def control_green():
    GPIO.setmode(GPIO.BCM)
    green_led = 13
    GPIO.setup(green_led, GPIO.OUT)
    GPIO.output(green_led, GPIO.LOW)
    
    try:
        while True:
            green = call_Color()
            
            if green == 0:
                print("some problem")
                GPIO.output(green_led, GPIO.LOW)
                save_green(0)
                time.sleep(1)
            else:
                print("good")
                GPIO.output(green_led, GPIO.HIGH)
                save_green(1)
                time.sleep(1)
    finally:
        GPIO.output(green_led, GPIO.LOW)
        GPIO.cleanup()
    