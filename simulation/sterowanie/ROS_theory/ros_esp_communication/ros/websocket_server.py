import rclpy
from rclpy.node import Node
import asyncio
import websockets
import json

class WebSocketServer(Node):
    def __init__(self):
        super().__init__('websocket_server')
        self.get_logger().info("WebSocket Server Node Started")
        self.server = None
        self.led_state = 0  

    async def handler(self, websocket, path):
        self.get_logger().info("New WebSocket Connection Established")
        try:
            async for message in websocket:
                self.get_logger().info(f"Received message: {message}")
                data = json.loads(message)

                if "joystick_x" in data:
                    x_value = data["joystick_x"]
                    self.update_led_state(x_value)

                response = json.dumps({"led_state": self.led_state})
                await websocket.send(response)

        except websockets.exceptions.ConnectionClosed:
            self.get_logger().info("WebSocket Connection Closed")

    def update_led_state(self, x_value):
        threshold_right = 4000  
        threshold_left = 500   

        if x_value > threshold_right and self.led_state < 3:
            self.led_state += 1  
        elif x_value < threshold_left and self.led_state > 0:
            self.led_state -= 1  

        self.get_logger().info(f"Updated LED state: {self.led_state}")

    async def start_server(self):
        self.server = await websockets.serve(self.handler, "0.0.0.0", 8765)
        self.get_logger().info("WebSocket Server Running on ws://0.0.0.0:8765")
        await self.server.wait_closed()

def main(args=None):
    rclpy.init(args=args)
    node = WebSocketServer()
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(node.start_server())
    except KeyboardInterrupt:
        node.get_logger().info("Shutting Down WebSocket Server")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
