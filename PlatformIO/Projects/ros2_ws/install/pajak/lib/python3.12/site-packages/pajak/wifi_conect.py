import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import websocket
import math
import threading
import time

# Mapowanie nazw jointów na numery serw
joint_to_servo = {
    "joint1": 1,
    "joint2": 2,
    "joint3": 3
}

# WebSocket klient – łączymy w osobnym wątku
class JointStateSender(Node):
    def __init__(self):
        super().__init__('joint_state_sender')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10)

        self.ws = None
        self.connected = False

        # Start WebSocket client in a separate thread
        threading.Thread(target=self.connect_ws, daemon=True).start()

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

    def joint_state_callback(self, msg):
        if not self.connected:
            return

        for name, position in zip(msg.name, msg.position):
            if name in joint_to_servo:
                servo_num = joint_to_servo[name]
                angle_deg = math.degrees(position)
                angle_deg = max(0, min(180, int(angle_deg)))  # clamp 0–180

                command = f"servo{servo_num} {angle_deg}"
                self.get_logger().info(f"Sending: {command}")
                try:
                    self.ws.send(command)
                except Exception as e:
                    self.get_logger().warn(f"WebSocket send error: {e}")
                    self.connected = False  # spróbuj połączyć się ponownie
                    threading.Thread(target=self.connect_ws, daemon=True).start()

def main(args=None):
    rclpy.init(args=args)
    node = JointStateSender()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()