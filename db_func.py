import Adafruit_DHT
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from rpi_ws281x import *
import spidev
import RPi.GPIO as GPIO

spi=spidev.SpiDev()
spi.open(0,0)

def save_humidity_temperature(temperature, humidity):

    db = firestore.client()
    
    data = {
        u'temperature': temperature,
        u'humidity': humidity}
    print("!!!!!")
    doc_ref = db.collection(u'farminformation').document("tem_hum")
    doc_ref.set(data)
    
def read_adc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    # SPI 데이터 전송
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    # 아날로그 값 계산
    adcout = ((r[1] & 3) << 8) + r[2]
    return adcout
    
def read_spi_adc(adcChannel):
    adcValue=0
    buff=spi.xfer2([1, (8+adcChannel)<<4,0])
    adcValue = ((buff[1]&3)<<8)+buff[2]
    return adcValue

def convert_to_percentage(sensor_value):
    adc_ratio = sensor_value / 1023.0
    percent_value = adc_ratio * 100.0
    return percent_value

def save_soil_water(soil_water):
    db = firestore.client()
    data = {
        u'soil_water_percent': soil_water}
    doc_ref = db.collection(u'farminformation').document("soil_water")
    doc_ref.set(data)
    
def save_light(light):
    db = firestore.client()
    data = {
        u'light' : light}
    doc_ref = db.collection(u'farminformation').document("light")
    doc_ref.set(data)
    

    
def humidity_temperature():
    sensor = Adafruit_DHT.DHT22 # sensor
    pin = 4 # GPIO 4
    
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        temperature = format(temperature, ".1f")
        humidity = format(humidity, ".1f")
        print("Temp={0} Humidity={1}".format(temperature, humidity))
        save_humidity_temperature(temperature, humidity)
        time.sleep(5)

def soil_water():
    
    spi.max_speed_hz=50000
    
    try:
        while True:
            adcValue=read_spi_adc(0)
            print("Water Sensor : {0}".format(adcValue))
        
            # 습도(%)로 변환
            water_percent=convert_to_percentage(adcValue)
            water_percent=format(100-water_percent, ".1f")
            print("Water Sensor percent: ", water_percent, "%")
            save_soil_water(water_percent)
            time.sleep(5)
        
    finally: 
        print("finish!")
        GPIO.cleanup()
        spi.close()
        
def light_sensor():
    
    spi.max_speed_hz=1350000
    pin = 1
    
    try:
        while True:
            # 조도 값 읽어오기
            light_value = read_adc(pin)
        
            # LUX
            K = 3.3 / 1024.0
            B = 0.6
            voltage = light_value * K
            resistance = (3.3 - voltage) * 10 / voltage
            lux_value = (10 * pow(resistance, 3) - 20 * pow(resistance, 2) + 128 * resistance - 76) * K / B
            lux = round(lux_value,1)
            print("LUX 값: ", lux)
            save_light(lux)
            time.sleep(5)
        
    finally:
        # 프로그램 종료 시 GPIO 리소스 해제
        GPIO.cleanup()
    