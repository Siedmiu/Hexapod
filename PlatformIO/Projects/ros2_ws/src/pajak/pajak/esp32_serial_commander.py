import rclpy
from rclpy.node import Node
import serial

from std_msgs.msg import String

class ESP32SerialCommander(Node):
    def __init__(self):
        super().__init__('esp32_serial_commander')

        # Ustaw port szeregowy do komunikacji z ESP32
        self.serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

        # Subskrybuje temat z komendami np. "servo1 90"
        self.subscription = self.create_subscription(
            String,
            'esp32_command',
            self.command_callback,
            10
        )

        self.get_logger().info("ESP32 Serial Commander started.")

    def command_callback(self, msg):
        command = msg.data.strip()
        self.get_logger().info(f"Sending to ESP32: {command}")
        try:
            self.serial_port.write((command + '\n').encode('utf-8'))
        except serial.SerialException as e:
            self.get_logger().error(f"Serial error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ESP32SerialCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.serial_port.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()