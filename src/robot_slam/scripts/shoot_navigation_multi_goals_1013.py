#!/usr/bin/env python
# -*- coding: utf-8 -*-


import rospy
import os
import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf_conversions import transformations
from math import pi
from std_msgs.msg import String
from geometry_msgs.msg import Point
from geometry_msgs.msg import Vector3
from ar_track_alvar_msgs.msg import AlvarMarkers
from ar_track_alvar_msgs.msg import AlvarMarker
from rospy import Time,Duration
import sys
import serial
import time
from geometry_msgs.msg import Twist
reload(sys)
sys.setdefaultencoding('utf-8')
music_path="~/'07.mp3'"
music1_path="~/'07.mp3'"
music2_path="~/'07.mp3'"
music3_path="~/'07.mp3'"

find_id_sh= 0
Yaw_th_y = -0.44
Yaw_th_x = 0.015
goal_1=4
goal_2=6
move_flog=1
place=0
serialPort = "/dev/shoot"
baudRate = 9600
ser = serial.Serial(port=serialPort,baudrate=baudRate,parity="N",bytesize=8,stopbits=1)
goal_over_1=0
goal_over_2=0
nowtimeflag=0

def movefortheta(flog0):
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0
	twist_msg.linear.y=0
	twist_msg.angular.z=-0.02*flog0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(0.1)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.01)

class navigation_demo():
    def __init__(self):
        self.set_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=5)
        self.arrive_pub = rospy.Publisher('/voiceWords',String,queue_size=10)
        self.ar_sub = rospy.Subscriber('/object_position', Point, self.ar_cb)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))   
	global goal_1,goal_2,move_flog,place,goal_over_1,goal_over_2
	#move_flog=1
	
	
#	rospy.init_node('object_position_node',anonymous=True)
	self.find_sub_1 = rospy.Subscriber('/ar_pose_marker',AlvarMarkers,self.ar_cb_1);
	self.find_sub_2 = rospy.Subscriber('/ar_pose_marker',AlvarMarkers,self.ar_cb_2);
	self.pub = rospy.Publisher("/cmd_vel",Twist,queue_size=1000)	

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



    def ar_cb(self,data):
	global flog0,flog1,move_flog,nowtimeflag
	global find_id_sh,place
	find_id_sh = 0
	flog0 = 0
	flog1 = 0
	point_msg = data
	if(point_msg.z>=146 and point_msg.z<=160):
		find_id_sh=9
	#print (find_id_sh)	
	flog0 = point_msg.x - 319.5
	flog1 = abs(flog0)
	
	#print("flog1")
	#print(flog1)
	#print("move_flog")
	#print(move_flog)
	if (abs(flog1) > 3 and find_id_sh == 9 and move_flog==0):
		msg = Twist()
		msg.angular.z = -0.02*flog0
		self.pub.publish(msg)
		rospy.sleep(0.2)
	elif (abs(flog1) <= 3 and find_id_sh == 9 and move_flog==0):
		print "ok"
		ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
		time.sleep(0.08)
		ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
		rospy.sleep(0.2)
		ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
		time.sleep(0.08)
		ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
		place=1
		move_flog=0#1111111111111
		find_id_sh=0
		nowtomeflag=0
	
	

    def ar_cb_1(self,data):
	global ar_x,ar_x_abs,Yaw_th_x,ar_y,ar_y_abs,Yaw_th_y,move_flog,place,goal_over_1
	print(place)
	for marker in data.markers:
		if (marker.id==goal_1 and place == 1):
			ar_x=marker.pose.pose.position.x+0.13
			ar_x_abs=abs(ar_x)
			ar_y=marker.pose.pose.position.y-Yaw_th_y
			ar_y_abs=abs(ar_y)
			print("ar_x")
			print(ar_x)
			print("ar_y")
			print(ar_y)
			
			if (ar_x_abs>Yaw_th_x and move_flog==0):
				moveforarcb(ar_x)
				#msg = Twist()
				#msg.angular.z=-1.5*ar_x
				#self.pub.publish(msg)
			elif (ar_x_abs<=Yaw_th_x and move_flog==0):
				if (ar_y_abs>0.04):
					time.sleep(0.01)
				elif (ar_y_abs<=0.04):
					print("ok")
					ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
					time.sleep(0.16)
					ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
					rospy.sleep(0.2)
					ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
					time.sleep(0.08)
					ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
					move_flog=1
					place=2
					goal_over_1=1


    def ar_cb_2(self,data):
	global ar_x,ar_x_abs,Yaw_th_x,ar_y,ar_y_abs,Yaw_th_y,move_flog,place,goal_over_1
	print(place)
	for marker in data.markers:
		if (marker.id==goal_2 and place == 2):
			ar_x=marker.pose.pose.position.x+0.15
			ar_x_abs=abs(ar_x)
			
			print("ar_x")
			print(ar_x)
			
			if (ar_x_abs>0.013 and move_flog==0):
				moveforarcb2(ar_x)
				#msg = Twist()
				#msg.angular.z=-1.5*ar_x
				#self.pub.publish(msg)
			elif (ar_x_abs<=0.013 and move_flog==0):
				print("ok")
				ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
				time.sleep(0.16)
				ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
				rospy.sleep(0.2)
				ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
				time.sleep(0.08)
				ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
				move_flog=1
				place=3
				goal_over_2=1


def moveforarcb2(x):
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0
	twist_msg.linear.y=0
	twist_msg.angular.z=-1*x
	start_time=rospy.Time.now()
	duration = Duration.from_sec(0.01)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.01)
	
	pub.publish(twist_msg)




def moveforarcb(x):
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0
	twist_msg.linear.y=0
	twist_msg.angular.z=-3*x
	start_time=rospy.Time.now()
	duration = Duration.from_sec(0.01)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.01)
	
	pub.publish(twist_msg)




def movefor2x():
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=-0.3
	twist_msg.linear.y=0
	twist_msg.angular.z=0.0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(2.8)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.1)
	
	pub.publish(twist_msg)

def movefor2y():
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0
	twist_msg.linear.y=-0.3
	twist_msg.angular.z=0.0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(3.8)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.1)
	
	pub.publish(twist_msg)

def movefor2x1():
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0.25
	twist_msg.linear.y=0
	twist_msg.angular.z=0.0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(3)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.1)
	
	pub.publish(twist_msg)
def move2endfory7():
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=0.0
	twist_msg.linear.y=-0.115
	twist_msg.angular.z=0.0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(2.8)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.1)
	
	pub.publish(twist_msg)

def move2endforx7():
	twist_msg=Twist()
        pub = rospy.Publisher('/cmd_vel',Twist,queue_size=10)
	twist_msg.linear.x=-0.16
	twist_msg.linear.y=0.0
	twist_msg.angular.z=0.0
	start_time=rospy.Time.now()
	duration = Duration.from_sec(1.5)
	while rospy.Time.now() - start_time<duration:
		pub.publish(twist_msg)
		rospy.sleep(0.1)
	
	pub.publish(twist_msg)


	
	



class ARTracker:
	def __init__(self):
		self.ar_sub = rospy.Subscriber('/ar_pose_marker',AlvarMarkers,self.ar_track_cb)
	def ar_track_cb(self,data):
		#print ("zhixing AR callback")
		global find_id
		for marker in data.markers:
			find_id = marker.id
			#print find_id
#class object_position:
#	def __init__(self):
#		global goal_1,goal_2,move_flog,place,goal_over_1,goal_over_2
#		move_flog=1
#		place=0
#		goal_over_1=0
#		goal_over_2=0
#		rospy.init_node('object_position_node',anonymous=True)
#		self.find_sub_1 = rospy.Subscriber('/object_position',Point,slef.find_cb_1);
#		self.find_sub_2 = rospy.Subscriber('/object_position',Point,slef.find_cb_2);
#		self.pub = rospy.Publisher("/cmd_vel",Twist,queue_size=10000)

	

if __name__ == "__main__":
    rospy.init_node('navigation_demo',anonymous=True)
    goalListX = rospy.get_param('~goalListX', '2.0, 2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0')

    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","),goalListY.split(","),goalListYaw.split(","))]
    print ('Please 1 to continue: ')
    input = raw_input()
    print (goals)
    r = rospy.Rate(1)
    r.sleep()
    navi = navigation_demo()
#    objection=objection_position()
    ARTracker = ARTracker()
    print("zhixing main")
    if (input == '1'):
	position_end = 0
	while(position_end == 0):
#first shoot_place
		if(move_flog==1 and place==0 and nowtimeflag==0):
			navi.goto(goals[0])
			rospy.sleep(1)
			move_flog=0
			print("first")
			nowtimeflag=1
			start_time = rospy.Time.now()
			duration = Duration.from_sec(12)
		elif(nowtimeflag == 1 and place==0 and move_flog==0):
			if(rospy.Time.now()-start_time > duration):
				print "ok"
				ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
				time.sleep(0.08)
				ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
				rospy.sleep(0.2)
				ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
				time.sleep(0.08)
				ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')
				place=1
				move_flog=1
				find_id_sh=0
				nowtimeflag = 0
			
			
			
#second shoot_place
		if(move_flog==1 and place==1):
			#movefor2x()
			#rospy.sleep(0.5)
			#movefor2y()
			#rospy.sleep(0.2)
			#movefor2x1()
			rospy.sleep(0.5)
			navi.goto(goals[5])
			rospy.sleep(1)
			navi.goto(goals[1])
			rospy.sleep(1)
			rospy.sleep(2)
			move_flog=0
			
#third shoot_place
		if(move_flog==1 and place==2):
			#movefor2x()
			#rospy.sleep(0.5)
			#movefor2y()
			#rospy.sleep(0.2)
			#movefor2x1()
			rospy.sleep(0.5)
			navi.goto(goals[4])
			rospy.sleep(1)
			navi.goto(goals[2])
			rospy.sleep(2)
			move_flog=0
			
		
#end place
		if(move_flog==1 and place==3):
			#move2endfor7()
			navi.goto(goals[3])
			rospy.sleep(0.5)
			move2endfory7()
			rospy.sleep(0.5)
			move2endforx7()
			rospy.sleep(1)
			position_end=1
		else :
			rospy.sleep(0.01)
			

	while not rospy.is_shutdown():
          		r.sleep()



