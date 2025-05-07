import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class SerialControlNode(Node):
    def __init__(self):
        super().__init__('serial_control_node')
        self.ser = serial.Serial('/dev/ttyUSB0', 115200)  # Ustawienie portu szeregowego
        self.publisher = self.create_publisher(String, 'servo_control', 10)
        self.timer = self.create_timer(0.1, self.send_command)  # Szybszy timer = płynniejszy ruch
        self.angle = 0
        self.direction = 1  # 1 = w górę, -1 = w dół

    def send_command(self):
        msg = String()
        msg.data = f"servo1 {self.angle}"
        self.publisher.publish(msg)
        self.get_logger().info(f"Sending command: {msg.data}")
        self.ser.write((msg.data + '\n').encode())  # Dodaj \n jeśli Twój mikrokontroler tego oczekuje

        self.angle += self.direction * 1  # Zmieniamy kąt co 1 stopień

        if self.angle >= 180:
            self.angle = 180
            self.direction = -5
        elif self.angle <= 0:
            self.angle = 0
            self.direction = 5

def main(args=None):
    rclpy.init(args=args)
    node = SerialControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
