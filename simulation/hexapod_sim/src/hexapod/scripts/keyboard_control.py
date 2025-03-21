#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import sys, termios, tty, select
from std_msgs.msg import Float64

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher = self.create_publisher(Float64, '/up_section_joint/command', 10)
        self.position = 0.0  # Current position
        self.increment = 0.1  # Position change step
        self.get_logger().info("Sterowanie: W = góra, S = dół, Q = wyjście")

    def get_key(self):
        """Reads a single keypress without blocking."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)  # Timeout to avoid blocking
            if rlist:
                return sys.stdin.read(1)
            else:
                return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key()
                if key is None:
                    continue

                if key.lower() == 'w':
                    self.position += self.increment
                elif key.lower() == 's':
                    self.position -= self.increment
                elif key.lower() == 'q':
                    self.get_logger().info("Zamykanie węzła...")
                    break
                else:
                    self.get_logger().warn("Nieznany klawisz! Użyj W (góra), S (dół), Q (wyjście)")
                    continue

                msg = Float64()
                msg.data = self.position
                self.publisher.publish(msg)
                self.get_logger().info(f"Nowa pozycja: {self.position}")

        except KeyboardInterrupt:
            self.get_logger().info("Przerwano przez użytkownika.")
        finally:
            self.get_logger().info("Zamykanie węzła...")
            self.destroy_node()
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    node.run()

if __name__ == '__main__':
    main()
