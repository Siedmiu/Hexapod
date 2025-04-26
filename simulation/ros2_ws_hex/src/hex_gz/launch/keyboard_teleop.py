#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, termios, tty, select

class TeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.get_logger().info('Teleop node started. Use WASD keys to move. Press Q to quit.')

        self.linear_speed = 0.5
        self.angular_speed = 1.0
        self.run()

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
        return key

    def run(self):
        try:
            while True:
                key = self.get_key()
                twist = Twist()
                if key.lower() == 'w':
                    twist.linear.x = self.linear_speed
                elif key.lower() == 's':
                    twist.linear.x = -self.linear_speed
                elif key.lower() == 'a':
                    twist.angular.z = self.angular_speed
                elif key.lower() == 'd':
                    twist.angular.z = -self.angular_speed
                elif key.lower() == 'q':
                    break
                else:
                    twist = Twist()  # Stop

                self.pub.publish(twist)

        except Exception as e:
            self.get_logger().error(f'Exception: {e}')
        finally:
            twist = Twist()
            self.pub.publish(twist)
            print("Exiting teleop node")

def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
