#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def move_forward():
    print("[ROBOT] Ruch do przodu!")

def move_backward():
    print("[ROBOT] Ruch do tyłu!")

def turn_left():
    print("[ROBOT] Skręt w lewo!")

def turn_right():
    print("[ROBOT] Skręt w prawo!")

def stop():
    print("[ROBOT] STOP!")

def callback(msg):
    cmd = msg.data
    print(f"[MOTION_NODE] Otrzymano komendę: {cmd}")

    if cmd == "move_forward":
        move_forward()
    elif cmd == "move_backward":
        move_backward()
    elif cmd == "turn_left":
        turn_left()
    elif cmd == "turn_right":
        turn_right()
    elif cmd == "stop":
        stop()
    else:
        print("[MOTION_NODE] Nieznana komenda!")

def listener():
    rospy.init_node('motion_node', anonymous=True)
    rospy.Subscriber('/robot/command', String, callback)
    rospy.spin()

if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
