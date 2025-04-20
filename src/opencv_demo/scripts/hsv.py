#!/usr/bin/env python
# coding:utf-8

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import cv2
import numpy as np
import time
"""
功能：读取摄像头图像，显示出来，转化为HSV色彩空间
     并通过滑块调节HSV阈值，实时显示
"""

def h_low(value): 
    hsv_low[0] = value
def h_high(value): 
    hsv_high[0] = value
def s_low(value): 
    hsv_low[1] = value
def s_high(value): 
    hsv_high[1] = value
def v_low(value): 
    hsv_low[2] = value
def v_high(value): 
    hsv_high[2] = value

hsv_low = np.array([0, 0, 0])
hsv_high = np.array([0, 0, 0])

cv2.namedWindow('image')
cv2.createTrackbar('H low', 'image', 0, 255, h_low) # 初始值， 最大值
cv2.createTrackbar('H high', 'image', 255, 255, h_high)
cv2.createTrackbar('S low', 'image', 0, 255, s_low)
cv2.createTrackbar('S high', 'image', 255, 255, s_high)
cv2.createTrackbar('V low', 'image', 0, 255, v_low)
cv2.createTrackbar('V high', 'image', 255, 255, v_high)

def callback(data):
    global bridge, cv_img, flag
    flag = True
    cv_img = bridge.imgmsg_to_cv2(data, "bgr8")
    
if __name__ == '__main__':
    flag = False
    cv_img = np.zeros((640,480))
    rospy.init_node('hsv_slider_node', anonymous=True)
    bridge = CvBridge()
    rospy.Subscriber('image', Image, callback)
    
    while not rospy.is_shutdown():
        if flag == True:
            cv2.imshow("frame", cv_img)
            hsv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV) # BGR转HSV
            hsv_img = cv2.inRange(hsv_img, hsv_low, hsv_high) # 通过HSV的高低阈值，提取图像部分区域
            cv2.imshow('hsv_img', hsv_img)
            cv2.waitKey(1)
            flag = False

