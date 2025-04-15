import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import websocket
import json

class WebSocketClientNode(Node):

    def __init__(self):
        super().__init__('websocket_client_node')

        # WebSocket server details (ESP32 IP i port)
        self.server_ip = "192.168.1.100"  # Zmień na IP swojego ESP32
        self.server_port = 8765
        self.websocket = websocket.WebSocket()

        # Połączenie z serwerem WebSocket
        self.connect_to_websocket()

        # Subskrypcja tematu ROS 2
        self.subscription = self.create_subscription(
            String,
            'esp32_command',
            self.listener_callback,
            10
        )
        self.subscription  # Prevent unused variable warning

    def connect_to_websocket(self):
        """Połączenie z serwerem WebSocket"""
        try:
            self.websocket.connect(f"ws://{self.server_ip}:{self.server_port}")
            self.get_logger().info(f"Połączono z WebSocket: {self.server_ip}:{self.server_port}")
        except Exception as e:
            self.get_logger().error(f"Błąd połączenia z WebSocket: {str(e)}")

    def listener_callback(self, msg: String):
        """Callback odbierający wiadomości z ROS 2 i wysyłający je do ESP32"""
        command = msg.data
        self.get_logger().info(f"Odebrano komendę z ROS 2: {command}")

        # Tworzymy wiadomość JSON do wysłania
        data = {
            "command": command
        }
        json_data = json.dumps(data)

        # Wysyłanie komendy do ESP32 przez WebSocket
        try:
            self.websocket.send(json_data)
            self.get_logger().info(f"Wysłano komendę do ESP32: {json_data}")
        except Exception as e:
            self.get_logger().error(f"Błąd wysyłania danych do ESP32: {str(e)}")

    def destroy_node(self):
        """Zamknięcie połączenia WebSocket po zakończeniu działania węzła"""
        self.websocket.close()
        self.get_logger().info("Zamknięte połączenie WebSocket")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WebSocketClientNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
