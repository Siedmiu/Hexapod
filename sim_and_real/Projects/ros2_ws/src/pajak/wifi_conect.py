import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory  # ← zmiana typu
import websocket
import math
import threading
import time

# Mapowanie nazw jointów na numery serw
joint_to_servo = {
    "joint1_3": 0,
    "joint2_3": 1,
    "joint3_3": 2,
    "joint1_2": 3,
    "joint2_2": 4,
    "joint3_2": 5,
    "joint1_1": 6,
    "joint2_1": 7,
    "joint3_1": 8,
    "joint1_6": 9,
    "joint2_6": 10,
    "joint3_6": 11,
    "joint1_5": 12,
    "joint2_5": 13,
    "joint3_5": 14,
    "joint1_4": 15,
    "joint2_4": 16,
    "joint3_4": 17,
}

class MultiLegTrajectorySender(Node):
    def __init__(self):
        super().__init__('multi_leg_trajectory_sender')

        # Lista topiców do subskrypcji
        self.trajectory_topics = [
            '/leg1_controller/joint_trajectory',
            '/leg2_controller/joint_trajectory',
            '/leg3_controller/joint_trajectory',
            '/leg4_controller/joint_trajectory',
            '/leg5_controller/joint_trajectory',
            '/leg6_controller/joint_trajectory'
        ]

        self.ws = None
        self.connected = False

        # WebSocket w osobnym wątku
        threading.Thread(target=self.connect_ws, daemon=True).start()

        # Subskrypcje
        for topic in self.trajectory_topics:
            self.create_subscription(
                JointTrajectory,
                topic,
                self.trajectory_callback,
                10
            )
            self.get_logger().info(f"Subscribed to {topic}")

    def connect_ws(self):
        while not self.connected:
            try:
                self.ws = websocket.WebSocket()
                self.ws.connect("ws://192.168.1.100:80/")  # <-- Zmień na IP ESP32
                self.connected = True
                self.get_logger().info("Connected to ESP32 WebSocket.")
            except Exception as e:
                self.get_logger().warn(f"WebSocket connection failed: {e}")
                time.sleep(2)

    def trajectory_callback(self, msg):
        if not self.connected or not msg.points:
            return

        point = msg.points[0]  # Bierzemy pierwszy punkt trajektorii

        for joint_name, position_rad in zip(msg.joint_names, point.positions):
            if joint_name in joint_to_servo:
                servo_num = joint_to_servo[joint_name]
                angle_deg = int(math.degrees(position_rad))
                angle_deg = max(0, min(180, angle_deg))  # ogranicz do 0–180

                command = f"servo{servo_num} {angle_deg}"
                self.get_logger().info(f"Sending: {command}")
                try:
                    self.ws.send(command)
                except Exception as e:
                    self.get_logger().warn(f"WebSocket send error: {e}")
                    self.connected = False
                    threading.Thread(target=self.connect_ws, daemon=True).start()

def main(args=None):
    rclpy.init(args=args)
    node = MultiLegTrajectorySender()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()