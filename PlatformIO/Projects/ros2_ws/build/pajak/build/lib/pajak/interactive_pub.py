import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class InteractivePublisher(Node):
    def __init__(self):
        super().__init__('interactive_publisher')
        self.publisher = self.create_publisher(String, 'esp32_command', 10)

    def run(self):
        print("🔧 Wpisuj komendy np. 'servo1 90'. Wpisz 'exit' aby zakończyć.")
        try:
            while rclpy.ok():
                cmd = input(">>> ")
                if cmd.lower() == 'exit':
                    break
                msg = String()
                msg.data = cmd.strip()
                self.publisher.publish(msg)
                self.get_logger().info(f"Wysłano: {msg.data}")
        except KeyboardInterrupt:
            pass

def main():
    rclpy.init()
    node = InteractivePublisher()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
