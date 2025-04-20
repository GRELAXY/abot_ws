#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf-8

import rospy
import os
import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import Path
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped, Point, Vector3
from tf_conversions import transformations
from math import pi
from std_msgs.msg import String
from std_msgs.msg import Int32
from ar_track_alvar_msgs.msg import AlvarMarker, AlvarMarkers
from rospy import Time,Duration
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')

nowtimeflag=0
find_id = 0
point_msg = 255
goal1 = 0
goal2 = 0
goal3 = 0
goal4 = 0

#start_time = rospy.Time.now()
rotate_time1 = 3.8   #刚开始的强制旋转1
rotate_time4 = 4.4   #5或者6之后的强制旋转4
rotate_180_z = 2.0   #强制旋转180的z速度

start_x_v = 0.2
start_x_time = 2
start_y_v = -0.2
start_y_time = 2.5

end_y7_v = 0.3       
end_y7_time = 0.9
end_x7_v = 0.3
end_x7_time = 4.9

end_y8_v = 0.3
end_y8_time = 4.0
end_x8_v = 0.2
end_x8_time = 1.65

def result_callback(msg):
    global find_id
    find_id = msg.data
    #rospy.loginfo("Received result: %d", msg.data)  # 打印接收到的消息内容
    
    # 创建订阅者，订阅 /vlm_node/result 话题
    rospy.Subscriber('/vlm_node/result', Int32, result_callback)

class navigation_demo():
    def __init__(self):
        self.set_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=5)
        self.arrive_pub = rospy.Publisher('/voiceWords',String,queue_size=10)
        self.ar_sub1 = rospy.Subscriber('/ar_pose_marker',AlvarMarkers,self.ar_track_cb)
        self.ar_sub = rospy.Subscriber('/object_position', Point, self.ar_cb)
        self.ar_cb2 = rospy.Subscriber('/vlm_node/result', Int32, result_callback)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))
    
    def ar_track_cb(self,data):
        #print ("zhixing AR callback")
        global find_id
        for marker in data.markers:
            find_id = marker.id
        #print(find_id)

    def ar_cb(self, data):
        #print ("zhixing hanzi callback")
        global point_msg, find_id
        point_msg = data
        #rospy.loginfo('z = %d', point_msg.z)
        if(point_msg.z>=1 and point_msg.z<=20):
            find_id = 1
            print(find_id)
        elif(point_msg.z>=21 and point_msg.z<=40 ):
            find_id = 2
            print(find_id)
        #point_msg = None
        elif (point_msg.z>=41 and point_msg.z<=60 ):
            find_id = 3
            print(find_id)
        #point_msg = None
        elif (point_msg.z>=61 and point_msg.z<=80 ):
            find_id = 4
            print(find_id)
        #point_msg = None
        elif (point_msg.z>=81 and point_msg.z<=110 ):
            find_id = 5
            print(find_id)
        #point_msg = None
        elif (point_msg.z>=111 and point_msg.z<=130):
            find_id = 6
            #print(find_id)
        #point_msg = None
        elif (point_msg.z>=131 and point_msg.z<=140 ):
            find_id = 7
            print(find_id)
        #point_msg = None
        elif (point_msg.z>=141 and point_msg.z<=160 ):
            find_id = 8
            print(find_id)
        #elif (rospy.Time.now()-start_time > duration and nowtimeflag == 1):
        #find_id = 5
        #print(find_id)
        #nowtimeflag = 0
        #point_msg = None
        #print flog0 , flog1 , flog2
        #rospy.loginfo('id = %d', id)

    def set_pose(self, p):
        if self.move_base is None:
            return False
        x, y, th = p

        pose = PoseWithCovarianceStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y
        q = transformations.quaternion_from_euler(0.0, 0.0, th/180.0*pi)
        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]
        self.set_pose_pub.publish(pose)
        return True

    def _done_cb(self, status, result):
        rospy.loginfo("navigation done! status:%d result:%s"%(status, result))
        arrive_str = "arrived to traget point"
        self.arrive_pub.publish(arrive_str)

    def _active_cb(self):
        rospy.loginfo("[Navi] navigation has be actived")

    def _feedback_cb(self, feedback):
        msg = feedback
        #rospy.loginfo("[Navi] navigation feedback\r\n%s"%feedback)

    def goto(self, p):
        rospy.loginfo("[Navi] goto %s"%p)
        #arrive_str = "going to next point"
        #self.arrive_pub.publish(arrive_str)
        goal = MoveBaseGoal()

        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = p[0]
        goal.target_pose.pose.position.y = p[1]
        q = transformations.quaternion_from_euler(0.0, 0.0, p[2]/180.0*pi)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.move_base.send_goal(goal, self._done_cb, self._active_cb, self._feedback_cb)
        result = self.move_base.wait_for_result(rospy.Duration(60))
        #rospy.sleep(2)
        if not result:
            self.move_base.cancel_goal()
            rospy.loginfo("Timed out achieving goal")
        else:
            state = self.move_base.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("reach goal %s succeeded!"%p)
        return True

    def cancel(self):
        self.move_base.cancel_all_goals()
        return True


def move2end(x_v, y_v, time):
    twist_msg=Twist()
    pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
    twist_msg.linear.x=x_v
    twist_msg.linear.y=y_v
    twist_msg.angular.z=0.0
    start_time=rospy.Time.now()
    duration = Duration.from_sec(time)
    while rospy.Time.now() - start_time<duration:
        pub.publish(twist_msg)
        rospy.sleep(0.1)

def move2end(x_v, y_v, time):
    twist_msg=Twist()
    pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
    twist_msg.linear.x=x_v
    twist_msg.linear.y=y_v
    twist_msg.angular.z=0.0
    start_time=rospy.Time.now()
    duration = Duration.from_sec(time)
    while rospy.Time.now() - start_time<duration:
        pub.publish(twist_msg)
        rospy.sleep(0.1)

def move_rotate_180(rotate_time):
    twist_msg=Twist()
    pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
    twist_msg.linear.x=0.0
    twist_msg.linear.y=0.0
    twist_msg.angular.z=rotate_180_z
    start_time=rospy.Time.now()
    duration = Duration.from_sec(rotate_time)
    while rospy.Time.now() - start_time<duration:
        pub.publish(twist_msg)
        rospy.sleep(0.1)


if __name__ == "__main__":
    rospy.init_node('navigation_demo',anonymous=True)
    goalListX = rospy.get_param('~goalListX', '2.0, 2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0')
    goalListXX = rospy.get_param('~goalListXX', '2.0, 2.0')
    goalListYY = rospy.get_param('~goalListYY', '2.0, 4.0')
    goalListYawYaw = rospy.get_param('~goalListYawYaw', '0, 90.0')
    goalListXXX = rospy.get_param('~goalListXXX', '2.0, 2.0')
    goalListYYY = rospy.get_param('~goalListYYY', '2.0, 4.0')
    goalListYawYawYaw = rospy.get_param('~goalListYawYawYaw', '0, 90.0')
    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","),goalListY.split(","),goalListYaw.split(","))]
    goalshibie = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListXX.split(","),goalListYY.split(","),goalListYawYaw.split(","))]
    goalzhongzhuan = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListXXX.split(","),goalListYYY.split(","),goalListYawYawYaw.split(","))]
    print ('Please 1 to continue: ')
    input = raw_input()
    print (goals)
    r = rospy.Rate(1)
    r.sleep()
    navi = navigation_demo()
    #ARTracker = ARTracker()
    print("zhixing main")

    if (input == '1'):
        os.system('mplayer %s' % "~/music/arrive_begin.mp3")
        #navi.goto(goalzhongzhuan[1])
        #rospy.sleep(0.5)
        move2end(start_x_v,0,start_x_time)  #move_startforx
        rospy.sleep(0.5)
        move2end(0,start_y_v,start_y_time)  #move_startfory
        rospy.sleep(0.5)
        move_rotate_180(rotate_time1) #刚开始的强制旋转1
        navi.goto(goalshibie[0])
        rospy.set_param('/top_view_shot_node/im_flag',1)
        position_end = 0
        if(goal1 == 2):
            rospy.sleep(1)
            find_id = 2
        elif(goal1 == 1):
            rospy.sleep(1)
            find_id = 1
        while(position_end == 0):
            if(find_id == 1):
                os.system('mplayer %s' % "~/music/shibie_1.mp3")
                #input = raw_input()  #KKK第一个识别点调位置
                navi.goto(goals[0])
                os.system('mplayer %s' % "~/music/arrive_1.mp3")
                #input = raw_input()  #KKK第一个目标点调位置
                move_rotate_180(rotate_time1)
                #navi.goto(goalzhongzhuan[0])		
                navi.goto(goalshibie[1])
                find_id = 0
                if(goal2 == 4):
                    rospy.sleep(1)
                    find_id = 4
                elif(goal2 == 3):
                    rospy.sleep(1)
                    find_id = 3
            if(find_id == 2):
                os.system('mplayer %s' % "~/music/shibie_2.mp3")
                #input = raw_input()  #KKK第一个识别点调位置
                navi.goto(goals[1])
                os.system('mplayer %s' % "~/music/arrive_2.mp3")
                #input = raw_input()  #KKK第二个目标点调位置
                move_rotate_180(rotate_time1)
                navi.goto(goalzhongzhuan[0])		
                navi.goto(goalshibie[1])
                find_id = 0
                if(goal2 == 4):
                    rospy.sleep(1)
                    find_id = 4
                elif(goal2 == 3):
                    rospy.sleep(1)
                    find_id = 3
            if(find_id == 3):
                os.system('mplayer %s' % "~/music/shibie_3.mp3")
                #input = raw_input()  #KKK第二个识别点调位置
                navi.goto(goals[2])
                os.system('mplayer %s' % "~/music/arrive_3.mp3")
                #input = raw_input()  #KKK第三个目标点调位置
                #navi.goto(goalzhongzhuan[0])
                navi.goto(goalshibie[2])
                find_id = 0
                if(goal3 == 5):
                    rospy.sleep(1)
                    find_id = 5
                elif(goal3 == 6):
                    rospy.sleep(1)
                    find_id = 6
            if(find_id == 4):
                os.system('mplayer %s' % "~/music/shibie_4.mp3")
                #input = raw_input()  #KKK第二个识别点调位置
                navi.goto(goals[3])
                os.system('mplayer %s' % "~/music/arrive_4.mp3")
                #input = raw_input()  #KKK第四个目标点调位置
                navi.goto(goalzhongzhuan[0])
                navi.goto(goalshibie[2])
                find_id = 0
                if(goal3 == 5):
                    rospy.sleep(1)
                    find_id = 5
                elif(goal3 == 6):
                    rospy.sleep(1)
                    find_id = 6
            if(find_id == 5 ):#or (rospy.Time.now()-start_time > duration and nowtimeflag == 1)):
                os.system('mplayer %s' % "~/music/shibie_5.mp3")
                #input = raw_input()  #KKK第三个识别点调位置
                #nowtimeflag = 0
                navi.goto(goals[4])
                os.system('mplayer %s' % "~/music/arrive_5.mp3")
                #input = raw_input()  #KKK第五个目标点调位置
                #navi.goto(goalzhongzhuan[0])
                move_rotate_180(rotate_time4) #5或者6之后的强制旋转4
                navi.goto(goalshibie[3])
                find_id = 0
                if(goal4 == 7):
                    rospy.sleep(1)
                    find_id = 7
                elif(goal4 == 8):
                    rospy.sleep(1)
                    find_id = 8
            if(find_id == 6):
                os.system('mplayer %s' % "~/music/shibie_6.mp3")
                #input = raw_input()  #KKK第三个识别点调位置
                #nowtimeflag = 0
                navi.goto(goals[5])
                os.system('mplayer %s' % "~/music/arrive_6.mp3")
                #input = raw_input()  #KKK第六个目标点调位置
                navi.goto(goalzhongzhuan[0])
                move_rotate_180(rotate_time4) #5或者6之后的强制旋转4
                navi.goto(goalshibie[3])
                find_id = 0
                if(goal4 == 7):
                    rospy.sleep(1)
                    find_id = 7
                elif(goal4 == 8):
                    rospy.sleep(1)
                    find_id = 8
            if(find_id == 7):
                os.system('mplayer %s' % "~/music/shibie_7.mp3")
                #input = raw_input()  #KKK第四个识别点调位置
                navi.goto(goals[6])
                os.system('mplayer %s' % "~/music/arrive_7.mp3")
                #input = raw_input()  #KKK第七个目标点调位置
                #navi.goto(goalshibie[3])
                #rospy.sleep(0.5)
                move2end(0,end_y7_v,end_y7_time)  #move2endfory7
                rospy.sleep(0.5)
                move2end(end_x7_v,0,end_x7_time)  #move2endforx7
                os.system('mplayer %s' % "~/music/arrive_end.mp3")
                find_id = 0
                position_end = 1
            if(find_id == 8):
                os.system('mplayer %s' % "~/music/shibie_8.mp3")
                #input = raw_input()  #KKK第四个识别点调位置
                navi.goto(goals[7])
                os.system('mplayer %s' % "~/music/arrive_8.mp3")
                #input = raw_input()  #KKK第八个目标点调位置
                #navi.goto(goalshibie[3])
                #rospy.sleep(0.5)
                move2end(0,end_y8_v,end_y8_time)  #move2endfory8
                rospy.sleep(0.5)
                move2end(end_x8_v,0,end_x8_time)  #move2endforx8
                os.system('mplayer %s' % "~/music/arrive_end.mp3")
                find_id = 0
                position_end = 1
            else :
                rospy.sleep(0.01)

    while not rospy.is_shutdown():
        r.sleep()

