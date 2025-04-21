# abot_ws
人工智能大赛-自主巡航和目标设计

# 主要功能包
1. `src/track_tag/src/ar_track.cpp`
功能：该文件主要实现了基于 AR 标签的跟踪功能。它订阅 AR 标签的位置信息，计算小车的控制速度，并根据标签的位置信息控制小车的运动。当小车与标签的相对位置满足一定条件时，会发布射击指令。
关键部分：
`tag_cb` 函数：处理 AR 标签的消息，计算小车的线速度和角速度。
`arrive_cb` 函数：处理到达消息，更新到达标志。
`satfunc` 函数：饱和函数，用于限制速度。
2. `src/robot_slam/scripts/navigation_multi_goals.py` 及相关文件（navigation_multi_goals_1112final.py、navigation_multi_goals_1113final.py）
功能：这些文件实现了小车的导航功能，包括起点移动、旋转、到达指定识别点拍照识别、到达目标点等操作。可以根据不同的识别结果进行不同的导航操作，最终到达终点。
关键部分：
`navigation_demo` 类：包含导航相关的方法，如设置位置、到达目标点等。
`move2end` 函数：控制小车移动到指定位置。
`move_rotate_180` 函数：控制小车旋转 180 度。

# 需要更改的部分
1. 导航目标点更新
修改现有代码：在`navigation_multi_goals.py` 等文件中，根据计算结果更新导航目标点。你可以在识别和计算完成后，将计算结果映射到相应的目标点坐标，然后调用 `navi.goto` 方法导航到新的目标点。

2. 豆包PROMPt提示词要修改


3. 语音播报功能
修改现有代码：在计算完成后，使用 os.system 调用语音播报工具，如 mplayer 播放语音文件。可以将计算结果转换为语音文件并播放。

4. 地图定点的点位
修改 `navigation_multi_goals.py` 等文件：在这些文件中，通过 `rospy.get_param` 获取导航目标点的参数。你可以修改这些参数来更改地图定点的点位。


`goalListX = rospy.get_param('~goalListX', '2.0, 2.0')
goalListY = rospy.get_param('~goalListY', '2.0, 4.0')
goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0')
你可以在启动节点时通过命令行参数或修改 ROS 参数服务器来更改这些值。`

5. 控制参数
修改 ar_track.cpp 文件：在该文件中，通过 nh.param 获取控制参数，如 kpx_track、kpz_track 等。你可以修改这些参数来调整小车的跟踪性能。
`cpp
nh.param<float>("kpx_track", kpx_track, 1.0);
nh.param<float>("kpz_track", kpz_track, 8.0);`

调试步骤
启动 ROS 核心：打开终端，运行 roscore。
启动 SLAM 节点：根据你的 SLAM 配置，启动相应的 SLAM 节点，如 gmapping 或 hector_slam。
启动导航节点：运行 navigation_multi_goals.py 等文件，启动导航功能。
启动 AR 跟踪节点：运行 ar_track.cpp 编译后的可执行文件，启动 AR 跟踪功能。
启动图片识别与计算节点：运行你编写的图片识别与计算节点。
观察调试信息：通过 rostopic echo 等命令观察各个节点的输出信息，检查是否正常工作。