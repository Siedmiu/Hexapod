#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time

class LegSequencePlayer(Node):
    def __init__(self):
        super().__init__('leg_sequence_player')
        self.get_logger().info('Inicjalizacja węzła do sekwencji ruchów')
        
        # Wydawca dla kontrolera nogi 1
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory, 
            '/leg1_controller/joint_trajectory', 
            10
        )
        
        # Definicje pozycji (możesz dostosować wartości na podstawie twoich pozycji)
        self.positions = {
            # Na podstawie twoich definicji w pliku SRDF
            'moja_nowa_poza': {
                'joint1_1': 0.436332,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'pose1': {
                'joint1_1': 0.5235,
                'joint2_1': 0.0,
                'joint3_1': 0.0,
            }
        }
        
        # Lista stawów dla pierwszej nogi
        self.joint_names = ['joint1_1', 'joint2_1', 'joint3_1']
        
    def send_joint_trajectory(self, position_name, duration_sec=2.0):
        """Wyślij trajektorię do kontrolera"""
        self.get_logger().info(f'Wysyłam trajektorię do pozycji: {position_name}')
        
        # Sprawdź, czy pozycja istnieje
        if position_name not in self.positions:
            self.get_logger().error(f'Pozycja {position_name} nie istnieje!')
            return False
        
        # Utwórz wiadomość trajektorii
        trajectory = JointTrajectory()
        trajectory.joint_names = self.joint_names
        
        # Utwórz punkt trajektorii
        point = JointTrajectoryPoint()
        
        # Ustaw pozycje stawów
        position_values = []
        for joint in self.joint_names:
            position_values.append(self.positions[position_name][joint])
        
        point.positions = position_values
        point.velocities = [0.0] * len(self.joint_names)
        point.accelerations = [0.0] * len(self.joint_names)
        
        # Ustaw czas trwania ruchu
        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        point.time_from_start = duration
        
        # Dodaj punkt do trajektorii
        trajectory.points.append(point)
        
        # Wyślij trajektorię
        self.trajectory_publisher.publish(trajectory)
        self.get_logger().info(f'Wysłano trajektorię do pozycji: {position_name}')
        
        return True
        
    def execute_sequence(self):
        """Wykonanie sekwencji ruchów"""
        self.get_logger().info('Rozpoczynam sekwencję ruchów')
        
        # Przejście do pozycji początkowej
        self.send_joint_trajectory("moja_nowa_poza")
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(3.0)  # Daj czas na wykonanie ruchu
        
        # Przejście do pozycji końcowej
        self.send_joint_trajectory("pose1")
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(3.0)  # Daj czas na wykonanie ruchu
        
        self.get_logger().info('Sekwencja zakończona')

def main(args=None):
    rclpy.init(args=args)
    
    # Utworzenie węzła
    node = LegSequencePlayer()
    
    try:
        # Krótkie oczekiwanie na inicjalizację
        print("Inicjalizacja... Poczekaj 2 sekundy.")
        time.sleep(2.0)
        
        # Wykonanie sekwencji
        print("Rozpoczynam sekwencję")
        node.execute_sequence()
        
        # Utrzymanie węzła aktywnego przez chwilę
        time.sleep(2.0)
        
    except KeyboardInterrupt:
        pass
    
    # Sprzątanie
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()