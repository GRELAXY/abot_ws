#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import Int32  # 导入 Int32 消息类型

# 定义回调函数，当接收到消息时会被调用
def result_callback(msg):
    rospy.loginfo("Received result: %d", msg.data)  # 打印接收到的消息内容

def int32_subscriber():
    # 初始化 ROS 节点，名称为 int32_subscriber
    rospy.init_node('int32_subscriber', anonymous=True)
    
    # 创建订阅者，订阅 /vlm_node/result 话题
    rospy.Subscriber('/vlm_node/result', Int32, result_callback)
    
    # 保持节点运行，等待消息
    rospy.spin()

if __name__ == '__main__':
    try:
        int32_subscriber()
    except rospy.ROSInterruptException:
        pass

