import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
from std_msgs.msg import String  # Do odbierania komunikatów o wyborze algorytmu
import websocket
import math
import threading
import time
import serial
import subprocess  # Do uruchamiania procesów w terminalu
import os
import signal  # Do zarządzania procesami

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
    deg = math.degrees(position_rad)

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

class HexapodController(Node):
    def __init__(self):
        super().__init__('hexapod_controller')

        # Lista topiców do subskrypcji dla trajektorii
        self.trajectory_topics = [
            '/leg1_controller/joint_trajectory',
            '/leg2_controller/joint_trajectory',
            '/leg3_controller/joint_trajectory',
            '/leg4_controller/joint_trajectory',
            '/leg5_controller/joint_trajectory',
            '/leg6_controller/joint_trajectory'
        ]
        # Konfiguracja algorytmów chodzenia
        self.algorithm_configs = {
            'bi_gate': {
                'topic': '/algorithm/bi_gate',
                'command': 'ros2 run hex_gz leg_sequence_player.py',
                'process': None
            },
            'wave_gate': {
                'topic': '/algorithm/wave_gate',
                'command': 'ros2 run hex_walker wave_gate_node',
                'process': None
            },
            'tri_gate': {
                'topic': '/algorithm/tri_gate',
                'command': 'ros2 run hex_walker tri_gate_node',
                'process': None
            },
            'ripple_gate': {
                'topic': '/algorithm/ripple_gate',
                'command': 'ros2 run hex_walker ripple_gate_node',
                'process': None
            }
        }

        self.current_algorithm = None
        self.serial_port = None
        self.serial_connected = False

        # Inicjalizacja połączenia UART w osobnym wątku
        threading.Thread(target=self.connect_serial, daemon=True).start()

        # Subskrypcje dla trajektorii każdej nogi
        for topic in self.trajectory_topics:
            self.create_subscription(
                JointTrajectory,
                topic,
                self.trajectory_callback,
                10
            )
            self.get_logger().info(f"Subscribed to trajectory topic: {topic}")

        # Subskrypcja do topicu wyboru algorytmu
        self.create_subscription(
            String,
            '/algorithm/select',
            self.algorithm_select_callback,
            10
        )
        self.get_logger().info("Subscribed to algorithm selection topic: /algorithm/select")

        # Dodatkowe subskrypcje do wykrywania aktywacji poszczególnych algorytmów
        for alg_name, config in self.algorithm_configs.items():
            self.create_subscription(
                String,
                config['topic'],
                lambda msg, name=alg_name: self.algorithm_activation_callback(msg, name),
                10
            )
            self.get_logger().info(f"Subscribed to algorithm topic: {config['topic']}")

    def connect_serial(self):
        """Ustanawia połączenie z ESP32 przez port szeregowy."""
        while not self.serial_connected:
            try:
                # Zmień port na odpowiedni dla Twojego systemu
                self.serial_port = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
                self.serial_connected = True
                self.get_logger().info("Connected to ESP32 via UART.")
            except Exception as e:
                self.get_logger().warn(f"Serial connection failed: {e}")
                time.sleep(2)

    def trajectory_callback(self, msg):
        """Obsługuje otrzymane trajektorie i wysyła komendy do serwomechanizmów."""
        if not self.serial_connected or not msg.points:
            return

        point = msg.points[0]  # Tylko pierwszy punkt trajektorii

        for joint_name, position_rad in zip(msg.joint_names, point.positions):
            if joint_name in joint_to_servo:
                servo_num = joint_to_servo[joint_name]
                angle_deg = map_ros_angle_to_servo(joint_name, position_rad)
                
                angle_deg = max(0, min(180, angle_deg))  # ograniczenie do 0–180 stopni

                command = f"servo{servo_num} {angle_deg}\n"

                if servo_num == 17:
                    self.get_logger().debug(f"Joint: {joint_name}, Servo: {servo_num}, Angle: {angle_deg}")
                
                try:
                    self.serial_port.write(command.encode('utf-8'))
                except Exception as e:
                    self.get_logger().warn(f"UART send error: {e}")
                    self.serial_connected = False
                    threading.Thread(target=self.connect_serial, daemon=True).start()

    def algorithm_select_callback(self, msg):
        """Obsługuje wiadomości o wyborze algorytmu chodzenia."""
        algorithm_name = msg.data.strip().lower()
        
        self.get_logger().info(f"Received algorithm selection: {algorithm_name}")
        
        if algorithm_name in self.algorithm_configs:
            self.start_algorithm(algorithm_name)
        else:
            self.get_logger().warn(f"Unknown algorithm: {algorithm_name}")

    def algorithm_activation_callback(self, msg, algorithm_name):
        """Obsługuje aktywacje poszczególnych algorytmów."""
        # Sprawdź, czy wiadomość zawiera triggera dla uruchomienia algorytmu
        if "start" in msg.data.lower() or "activate" in msg.data.lower() or "run" in msg.data.lower():
            self.get_logger().info(f"Activating algorithm: {algorithm_name}")
            self.start_algorithm(algorithm_name)

    def start_algorithm(self, algorithm_name):
        """Uruchamia wybrany algorytm chodzenia w nowym terminalu."""
        # Najpierw zatrzymaj aktualnie uruchomiony algorytm, jeśli taki jest
        if self.current_algorithm:
            self.stop_algorithm(self.current_algorithm)
        
        self.current_algorithm = algorithm_name
        config = self.algorithm_configs[algorithm_name]
        
        # Uruchom nowy proces w terminalu
        try:
            # Komenda do otwarcia nowego terminala z uruchomionym programem
            terminal_command = f"gnome-terminal -- bash -c '{config['command']}; exec bash'"
            
            # Dla innych terminali możesz użyć:
            # terminal_command = f"xterm -e {config['command']}"  # dla xterm
            # terminal_command = f"konsole -e {config['command']}"  # dla KDE Konsole
            
            process = subprocess.Popen(terminal_command, shell=True)
            config['process'] = process
            
            self.get_logger().info(f"Started algorithm: {algorithm_name} (PID: {process.pid})")
        except Exception as e:
            self.get_logger().error(f"Failed to start algorithm {algorithm_name}: {e}")

    def stop_algorithm(self, algorithm_name):
        """Zatrzymuje uruchomiony algorytm."""
        config = self.algorithm_configs[algorithm_name]
        
        if config['process']:
            try:
                # Próba delikatnego zakończenia procesu
                os.killpg(os.getpgid(config['process'].pid), signal.SIGTERM)
                self.get_logger().info(f"Stopping algorithm: {algorithm_name}")
                
                # Daj procesowi czas na zakończenie
                time.sleep(0.5)
                
                # Sprawdź, czy proces nadal działa
                if config['process'].poll() is None:
                    # Jeśli nadal działa, zabij go
                    os.killpg(os.getpgid(config['process'].pid), signal.SIGKILL)
                    self.get_logger().warn(f"Force stopping algorithm: {algorithm_name}")
            except Exception as e:
                self.get_logger().warn(f"Error stopping algorithm {algorithm_name}: {e}")
            
            config['process'] = None
        
        self.current_algorithm = None

    def cleanup(self):
        """Sprzątanie przed zamknięciem."""
        # Zatrzymaj wszystkie uruchomione algorytmy
        if self.current_algorithm:
            self.stop_algorithm(self.current_algorithm)
        
        # Zamknij połączenie szeregowe
        if self.serial_connected and self.serial_port is not None:
            self.serial_port.close()
            self.get_logger().info("Serial connection closed.")


def main(args=None):
    rclpy.init(args=args)
    
    node = HexapodController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Właściwe sprzątanie
        node.cleanup()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()