import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math
import threading
import websocket
import time

# Mapowanie jointów na numery serw
joint_to_servo = {
    "joint1_1": 6, "joint2_1": 7, "joint3_1": 8,
    "joint1_2": 3, "joint2_2": 4, "joint3_2": 5,
    "joint1_3": 0, "joint2_3": 1, "joint3_3": 2,
    "joint1_4": 15, "joint2_4": 16, "joint3_4": 17,
    "joint1_5": 12, "joint2_5": 13, "joint3_5": 14,
    "joint1_6": 9, "joint2_6": 10, "joint3_6": 11,
}

# Mapowanie jointów do nazw topiców kontrolerów
joint_to_topic = {
    "joint1_1": "/leg1_controller/joint_trajectory",
    "joint2_1": "/leg1_controller/joint_trajectory",
    "joint3_1": "/leg1_controller/joint_trajectory",
    "joint1_2": "/leg2_controller/joint_trajectory",
    "joint2_2": "/leg2_controller/joint_trajectory",
    "joint3_2": "/leg2_controller/joint_trajectory",
    "joint1_3": "/leg3_controller/joint_trajectory",
    "joint2_3": "/leg3_controller/joint_trajectory",
    "joint3_3": "/leg3_controller/joint_trajectory",
    "joint1_4": "/leg4_controller/joint_trajectory",
    "joint2_4": "/leg4_controller/joint_trajectory",
    "joint3_4": "/leg4_controller/joint_trajectory",
    "joint1_5": "/leg5_controller/joint_trajectory",
    "joint2_5": "/leg5_controller/joint_trajectory",
    "joint3_5": "/leg5_controller/joint_trajectory",
    "joint1_6": "/leg6_controller/joint_trajectory",
    "joint2_6": "/leg6_controller/joint_trajectory",
    "joint3_6": "/leg6_controller/joint_trajectory",
}

class FullControlNode(Node):
    def __init__(self):
        super().__init__('full_control_node')

        # Subskrypcja danych z aplikacji
        self.create_subscription(JointTrajectory, 'app_control', self.control_callback, 10)
        self.get_logger().info("Subscribed to 'app_control'")

        # Publishery do wszystkich nóg
        self.trajectory_publishers = {}
        for topic in set(joint_to_topic.values()):
            self.trajectory_publishers[topic] = self.create_publisher(JointTrajectory, topic, 10)

        # WebSocket
        self.ws = None
        self.connected = False
        threading.Thread(target=self.connect_ws, daemon=True).start()

    def connect_ws(self):
        while not self.connected:
            try:
                self.ws = websocket.WebSocket()
                self.ws.connect("ws://192.168.229.80:80/")  # IP Twojego ESP32
                self.connected = True
                self.get_logger().info("Connected to ESP32 WebSocket.")
            except Exception as e:
                self.get_logger().warn(f"WebSocket connection failed: {e}")
                time.sleep(2)

    def control_callback(self, msg: JointTrajectory):
        if not msg.points:
            self.get_logger().warn("Received empty trajectory message")
            return

        point = msg.points[0]

        # Grupuj dane wg kontrolera (czyli topicu)
        topic_joint_map = {}
        for joint_name, position in zip(msg.joint_names, point.positions):
            if joint_name not in joint_to_topic:
                self.get_logger().warn(f"Unknown joint: {joint_name}")
                continue

            topic = joint_to_topic[joint_name]
            if topic not in topic_joint_map:
                topic_joint_map[topic] = {"names": [], "positions": []}

            topic_joint_map[topic]["names"].append(joint_name)
            topic_joint_map[topic]["positions"].append(position)

            # Wysyłanie do ESP32
            if self.connected and joint_name in joint_to_servo:
                servo_num = joint_to_servo[joint_name]
                angle_deg = int(math.degrees(position))
                angle_deg = max(0, min(180, angle_deg))
                command = f"servo{servo_num} {angle_deg}"
                try:
                    self.ws.send(command)
                    self.get_logger().info(f"Sent to ESP32: {command}")
                except Exception as e:
                    self.get_logger().warn(f"WebSocket send error: {e}")
                    self.connected = False
                    threading.Thread(target=self.connect_ws, daemon=True).start()

        # Publikacja do Gazebo (symulacja)
        for topic, joint_data in topic_joint_map.items():
            traj_msg = JointTrajectory()
            traj_msg.joint_names = joint_data["names"]
            point = JointTrajectoryPoint()
            point.positions = joint_data["positions"]
            point.time_from_start.sec = 1
            traj_msg.points.append(point)
            self.trajectory_publishers[topic].publish(traj_msg)
            self.get_logger().info(f"Published to {topic}: {joint_data['names']}")

def main(args=None):
    rclpy.init(args=args)
    node = FullControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
