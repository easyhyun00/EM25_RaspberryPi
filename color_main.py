import cv2, sys
from matplotlib import pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
import time
import os

cred = credentials.Certificate('/home/pi/servicekey3.json')
firebase_admin.initialize_app(cred)

def compare_file_sizes():
    directory = '/home/pi/PlantSystem/image/'

    # 이미지 파일 목록 가져오기
    files = os.listdir(directory)
    
    # 파일 이름 추출
    filenames = [file for file in files]

    # 파일 크기 비교
    if filenames[0] > filenames[1]:
        my_image = filenames[0]
        my_previous_image = filenames[1]
    else:
        my_image = filenames[1]
        my_previous_image = filenames[0]
        
    return my_image, my_previous_image

def color_ratio(n):
    image = compare_file_sizes()
    recent = image[0]
    previous = image[1]
    if n==1:
        #이미지 불러오기
        image = cv2.imread(f'/home/pi/PlantSystem/image/{recent}')
        image_gray = cv2.imread(f'/home/pi/PlantSystem/image/{recent}', cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(f'/home/pi/PlantSystem/image/{previous}')
        image_gray = cv2.imread(f'/home/pi/PlantSystem/image/{previous}', cv2.IMREAD_GRAYSCALE)
    
    #r,b,g로 되어있는 이미지를 분리하면 b,g,r이 되고 이를 다시 r,g,b 순서로 합침
    b,g,r = cv2.split(image)
    image2 = cv2.merge([r,g,b])
    #입력 영상, 커널 크기, X방향 표준편차, Y방향 표준편차, 외곽 테두리 보정 방식

    #ret : cv2.getGaussianKernel(ksize,sigma,[ktype])
    #ksize=(3,3)
    blur = cv2.GaussianBlur(image_gray, ksize=(7,7), sigmaX=0)
    ret, thresh1 = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
    edged = cv2.Canny(blur, 50, 200)

    #엣지 이미지로 closed를 찾는다
    #흰 선이 굵어지며 edge이미지에서 보이는 각 경계들이 이어지며 중간에 끊어지지 않는 선으로 바뀜
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    #컨투어 경계 찾음
    contours, _ = cv2.findContours(closed.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    total = 0

    # 외곽선 그리는 용도. 이미지에 그리기 때문에 이 코드 적용하면 원래 이미지에
    # 초록색 선 생김
    contours_image = cv2.drawContours(image, contours, -1, (255,0,0), 7)
    cv2.imwrite('/home/pi/PlantSystem/image2/contours_image.jpg', contours_image)

    img = cv2.imread('/home/pi/PlantSystem/image2/contours_image.jpg')
    
    #plant_image
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
     # yellow color
    low_yellow = np.array([20,100,100])
    high_yellow = np.array([29,255,255])
    yellow_mask = cv2.inRange(hsv_img, low_yellow, high_yellow)
    
    #red color(red1+red2)
    low_red = np.array([0,100,100])
    high_red = np.array([19,255,255])
    red_mask1 = cv2.inRange(hsv_img, low_red, high_red)
    low_red = np.array([170,100,100])
    high_red = np.array([180,255,250])
    red_mask2 = cv2.inRange(hsv_img, low_red, high_red)
    
    #빨강 두가지 합침
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    yellow = cv2.bitwise_and(img, img, mask=yellow_mask)
    red = cv2.bitwise_and(img, img, mask=red_mask)
    mask_fin = cv2.bitwise_or(yellow,red)

    mask = cv2.bitwise_or(yellow_mask, red_mask)
    # 전체 픽셀 수 계산
    total_pixels = img.shape[0] * img.shape[1]
    # 검출된 픽셀 수 계산.
    detected_pixels = cv2.countNonZero(mask)
    # 검출된 픽셀 수 대비 전체 픽셀 수 비율 계산
    detection_ratio = detected_pixels / total_pixels
    return detection_ratio

def save_leaf(recent, a):
    db = firestore.client()
    data = {
        recent : a}
    
    doc_ref = db.collection(u'farminformation').document("leaf")
    doc_ref.update(data)

# 최근 사진과 직전 사진의 노란 비율 비교
time.sleep(12)
detection_recent_ratio = color_ratio(1)
detection_previous_ratio = color_ratio(2)
print("recent: ", detection_recent_ratio)
print("previous: ", detection_previous_ratio)
image = compare_file_sizes()
recent = image[0]
if detection_recent_ratio > detection_previous_ratio :
    save_leaf(recent, 1)
    print("1")
else :
    print("0")

# 이미지 폴더 초기화
file_list = os.listdir("/home/pi/PlantSystem/image")
for file_name in file_list:
    file_path = os.path.join("/home/pi/PlantSystem/image", file_name)
    os.remove(file_path)
        

