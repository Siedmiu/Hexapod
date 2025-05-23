import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory  # ← zmiana typu
from sensor_msgs.msg import Imu  
import websocket
import math
import threading
import time
import serial
import json

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

def map_ros_angle_to_servo(joint_name, position_rad):
    if math.isnan(position_rad):
        print(f"OSTRZEŻENIE: Otrzymano wartość NaN dla {joint_name}, używam wartości domyślnej")
        # Możesz zwrócić wartość domyślną dla danego typu stawu
        if "joint1" in joint_name:
            return 90  # środkowa pozycja dla joint1
        elif "joint2" in joint_name:
            return 60  # wartość domyślna dla joint2
        elif "joint3" in joint_name:
            return 90  # wartość domyślna dla joint3
        else:
            return 90  # neutralna pozycja w razie nieznanego jointa

    deg = math.degrees(position_rad)
    if "joint3_4" in joint_name: 
        print(f"moveit: {joint_name}, Position (rad): {position_rad}, Position (deg): {deg}")

    if "joint1" in joint_name:
        # ROS: [-30°, 30°] → Serwo: [0°, 180°]
        return int((deg + 30) * (180 / 60))  # przesunięcie i skalowanie
    elif "joint2" in joint_name:
        # ROS: [-15°, 75°] → Serwo: [0°, 180°]
        return int((deg + 15) * (180 / 90))
    elif "joint3" in joint_name:
        # ROS: [0°, 90°] → Serwo: [0°, 180°]
        return int(deg * (180 / 90))
    else:
        return 90  # neutralna pozycja w razie nieznanego jointa

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

        self.serial_port = None
        self.serial_connected = False

        # Czas ostatniego wysłania danych IMU (ograniczenie częstotliwości)
        self.last_imu_send_time = 0
        self.imu_send_interval = 0.05  # 20Hz (wysyłanie co 50ms)

        # Inicjalizacja połączenia UART w osobnym wątku
        threading.Thread(target=self.connect_serial, daemon=True).start()

        # Subskrypcje dla każdej nogi
        for topic in self.trajectory_topics:
            self.create_subscription(
                JointTrajectory,
                topic,
                self.trajectory_callback,
                10
            )
            self.get_logger().info(f"Subscribed to {topic}")

        # Subskrypcja do topiku IMU
        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu/data',  # Standardowy topic ROS dla danych IMU
            self.imu_callback,
            10
        )
        self.get_logger().info("Subscribed to /imu/data")

    def connect_serial(self):
        while not self.serial_connected:
            try:
                # Zmień port na odpowiedni dla Twojego systemu (np. COM3 na Windows)
                self.serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
                self.serial_connected = True
                self.get_logger().info("Connected to ESP32 via UART.")
            except Exception as e:
                self.get_logger().warn(f"Serial connection failed: {e}")
                time.sleep(2)

    def trajectory_callback(self, msg):
        if not self.serial_connected or not msg.points:
            return

        point = msg.points[0]  # Tylko pierwszy punkt trajektorii

        for joint_name, position_rad in zip(msg.joint_names, point.positions):
            if joint_name in joint_to_servo:
                servo_num = joint_to_servo[joint_name]
                angle_deg = map_ros_angle_to_servo(joint_name, position_rad)
                                
                angle_deg = max(0, min(180, angle_deg))  # ograniczenie do 0–180 stopni

                command = f"servo{servo_num} {angle_deg}\n"

                # if(servo_num == 17):
                #     print(f"Joint: {joint_name}, Servo: {servo_num}, Angle: {angle_deg}")
                
                # self.get_logger().info(f"Sending: {command.strip()}")
                try:
                    self.serial_port.write(command.encode('utf-8'))
                except Exception as e:
                    self.get_logger().warn(f"UART send error: {e}")
                    self.serial_connected = False
                    threading.Thread(target=self.connect_serial, daemon=True).start()

    def imu_callback(self, msg):
        """
        Callback dla danych IMU
        Formatuje dane IMU do JSON i wysyła przez UART do ESP32
        """
        if not self.serial_connected:
            return
            
        # Ograniczenie częstotliwości wysyłania (do ~20Hz)
        current_time = time.time()
        if (current_time - self.last_imu_send_time) < self.imu_send_interval:
            return
            
        self.last_imu_send_time = current_time
            
        # Tworzymy uproszczoną wersję danych IMU do wysłania
        imu_data = {
            # Orientation (quaternion)
            "orientation": {
                "x": msg.orientation.x,
                "y": msg.orientation.y,
                "z": msg.orientation.z,
                "w": msg.orientation.w
            },
            # Angular velocity (rad/s)
            "angular_velocity": {
                "x": msg.angular_velocity.x,
                "y": msg.angular_velocity.y,
                "z": msg.angular_velocity.z
            },
            # Linear acceleration (m/s^2)
            "linear_acceleration": {
                "x": msg.linear_acceleration.x,
                "y": msg.linear_acceleration.y,
                "z": msg.linear_acceleration.z
            }
        }
        
        # Konwertujemy do JSON i wysyłamy
        try:
            # Dodajemy prefiks "imu" i zakończenie linii
            imu_command = f"imu {json.dumps(imu_data)}\n"
            self.serial_port.write(imu_command.encode('utf-8'))
            
            # Debugowanie (odkomentuj, jeśli potrzebne)
            # self.get_logger().debug(f"Sent IMU data: {imu_command.strip()}")
        except Exception as e:
            self.get_logger().warn(f"UART IMU send error: {e}")
            self.serial_connected = False
            threading.Thread(target=self.connect_serial, daemon=True).start()



def main(args=None):
    rclpy.init(args=args)
    node = MultiLegTrajectorySender()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
