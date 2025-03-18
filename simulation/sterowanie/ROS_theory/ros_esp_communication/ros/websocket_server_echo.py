# use if u want to test the ros server running
# to use - rename file to websocket_server.py, and run using instructions that are given in README file

import rclpy
from rclpy.node import Node
import asyncio
import websockets

class WebSocketServer(Node):
    def __init__(self):
        super().__init__('websocket_server')
        self.get_logger().info("WebSocket Server Node Started")
        self.server = None

    async def handler(self, websocket, path):
        self.get_logger().info("New WebSocket Connection")
        try:
            async for message in websocket:
                self.get_logger().info(f"Received: {message}")
                await websocket.send(f"Echo: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            self.get_logger().info("WebSocket Connection Closed")

    async def start_server(self):
        self.server = await websockets.serve(self.handler, "0.0.0.0", 8765)
        self.get_logger().info("WebSocket Server Started on ws://0.0.0.0:8765")
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
