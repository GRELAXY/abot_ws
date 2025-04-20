#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import time
from sensor_msgs.msg import Image as ROSImage
from std_msgs.msg import Int32
from API_KEY import *
import json
import openai
from openai import OpenAI
import base64
import sys
import numpy as np
import re

def imgmsg_to_cv2(img_msg):
    dtype = np.dtype("uint8")  # Hardcode to 8 bits...
    dtype = dtype.newbyteorder('>' if img_msg.is_bigendian else '<')
    image_opencv = np.ndarray(shape=(img_msg.height, img_msg.width, 3), dtype=dtype, buffer=img_msg.data)

    # If the byte order is different between the message and the system.
    if img_msg.is_bigendian == (sys.byteorder == 'little'):
        image_opencv = image_opencv.byteswap().newbyteorder()

    # Convert to BGR if the encoding is not already BGR
    if img_msg.encoding == "rgb8":
        image_opencv = cv2.cvtColor(image_opencv, cv2.COLOR_RGB2BGR)
    elif img_msg.encoding == "mono8":
        image_opencv = cv2.cvtColor(image_opencv, cv2.COLOR_GRAY2BGR)
    elif img_msg.encoding != "bgr8":
        rospy.logerr("Unsupported encoding: %s", img_msg.encoding)
        return None

    return image_opencv

def cv2_to_imgmsg(cv_image):
    img_msg = Image()
    img_msg.height = cv_image.shape[0]
    img_msg.width = cv_image.shape[1]
    img_msg.encoding = "bgr8"
    img_msg.is_bigendian = 0
    img_msg.data = cv_image.tobytes()
    img_msg.step = len(img_msg.data) // img_msg.height
    return img_msg

def top_view_shot(image_msg):
    global im_flag, result_pub
    # 将ROS图像消息转换为OpenCV格式
    img_bgr = imgmsg_to_cv2(image_msg)
    # 从参数服务器获取im_flag的值
    im_flag = rospy.get_param('/top_view_shot_node/im_flag', 255)
    
    if im_flag == 1:
        # 保存图像
        rospy.loginfo('保存至temp/vl_now.jpg')
        cv2.imwrite('/home/abot/abot_ws/src/abot_vlm/temp/vl_now.jpg', img_bgr)
        rospy.set_param('/top_view_shot_node/im_flag', 255)
        cv2.waitKey(1)

        # 调用视觉大模型API并发布结果
        result = yi_vision_api()
        publish_result(result)



def yi_vision_api(PROMPT='图片中有一个计算式，请计算一下结果并输出，例如：图中内容为1+1=，你输出为2。', img_path='/home/abot/abot_ws/src/abot_vlm/temp/vl_now.jpg'):
    client = OpenAI(
        api_key=YI_KEY,
        base_url="https://api.lingyiwanwu.com/v1"
    )
    
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
    
    completion = client.chat.completions.create(
      model="yi-vision",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": PROMPT
            },
            {
              "type": "image_url",
              "image_url": {
                "url": image
              }
            }
          ]
        },
      ]
    )
    
    result_str = completion.choices[0].message.content.strip()
    # 使用正则表达式提取结果中的数字
    result_match = re.search(r'\d+', result_str)  # 匹配第一个连续的数字
    if result_match:
        result = int(result_match.group())  # 转换为整数
    else:
        rospy.logerr("未能从返回的文本中提取数字！")
        result = 0  # 如果未能提取数字，设置结果为0

    print('大模型调用成功！')
    print('结果:', result)
    return result


def publish_result(result):
    # 发布结果到话题
    result_msg = Int32()
    result_msg.data = result
    result_pub.publish(result_msg)
    rospy.loginfo("发布结果: %d", result)

def main():
    global im_flag, result_pub
    rospy.init_node('top_view_shot_node', anonymous=True)
    rospy.Subscriber('/usb_cam/image_raw', ROSImage, top_view_shot)
    result_pub = rospy.Publisher('/vlm_node/result', Int32, queue_size=10)
    rospy.loginfo('视觉大模型模块导入成功！')
    rospy.loginfo('准备识别...')
    
    im_flag = rospy.get_param('/top_view_shot_node/im_flag', 255)
    rospy.spin()

if __name__ == '__main__':
    main()

