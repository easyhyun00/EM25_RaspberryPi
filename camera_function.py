import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import cv2, sys
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
import time
import pytz
from picamera import PiCamera
from time import sleep
import sys, os
import requests
from uuid import uuid4
import schedule
                
def fileUpload(file):
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    blob = bucket.blob('camera_test_1/'+file)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    #upload file
    blob.upload_from_filename(filename='/home/pi/camera_test/'+file, content_type='image/png')
    print("good")
    print(blob.public_url)
 
def execute_camera():
    basename = "smr"
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S") + '.png'
    filename = "_".join([basename, suffix])
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.start_preview()
    sleep(3)
    camera.capture('/home/pi/camera_test/' + filename)
    fileUpload(filename)
    camera.stop_preview()
    camera.close()

def clearAll():
    path = '/home/pi/camera_test'
    os.system('rm -rf %s/*' % path)
 
def camera_upload():
    try:
        execute_camera()
    finally:
        print("Upload end..")
            
def save_image():
    time.sleep(10)
    bucket = storage.bucket()
    blobs = list(bucket.list_blobs())
    try:
        latest_blob = None
        previous_blob = None
        latest_time = datetime.min.replace(tzinfo=pytz.UTC)
        previous_time = datetime.min.replace(tzinfo=pytz.UTC)

        for blob in blobs:
            updated_time = blob.updated # 파일 업데이트 시간 가져오기
            updated_time = updated_time.astimezone(pytz.UTC)
            if updated_time > latest_time:
                previous_blob = latest_blob
                previous_time = latest_time
                latest_blob = blob
                latest_time = updated_time
            elif updated_time > previous_time:
                previous_blob = blob
                previous_time = updated_time

        # 가장 최근 파일을 로컬에 다운로드하기
        if latest_blob is not None:
            filename = latest_blob.name.split('/')[-1]
            latest_blob.download_to_filename(f'/home/pi/PlantSystem/image/{filename}')
    
        if previous_blob is not None:
            previous_filename = previous_blob.name.split('/')[-1]
            previous_blob.download_to_filename(f'/home/pi/PlantSystem/image/{previous_filename}')
        
        print("complete!")
        
    finally:
        print("save end..")
    