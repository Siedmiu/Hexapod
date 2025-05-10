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
        
        # Wydawcy dla kontrolerów wszystkich nóg
        self.trajectory_publishers = {
            1: self.create_publisher(JointTrajectory, '/leg1_controller/joint_trajectory', 10),
            2: self.create_publisher(JointTrajectory, '/leg2_controller/joint_trajectory', 10),
            3: self.create_publisher(JointTrajectory, '/leg3_controller/joint_trajectory', 10),
            4: self.create_publisher(JointTrajectory, '/leg4_controller/joint_trajectory', 10),
            5: self.create_publisher(JointTrajectory, '/leg5_controller/joint_trajectory', 10),
            6: self.create_publisher(JointTrajectory, '/leg6_controller/joint_trajectory', 10)
        }
        
        # Definicje pozycji (możesz dostosować wartości na podstawie twoich pozycji)
        self.positions = {
            # Na podstawie twoich definicji w pliku SRDF
            'home_1': {
                'joint1_1': 0.0,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'przod_1': {
                'joint1_1': 0.349066,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'tyl_1': {
                'joint1_1': -0.349066,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'up_1': {
                'joint1_1': 0.0,
                'joint2_1': -0.174533,
                'joint3_1': 1.047197551,
            },
            'half_up_1': {
                'joint1_1': 0.174533,
                'joint2_1': -0.174533,
                'joint3_1': 1.047197551,
            },
            'half_back_1': {
                'joint1_1': -0.174533,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'half_back_up_1': {
                'joint1_1': -0.174533,
                'joint2_1': -0.174533,
                'joint3_1': 1.047197551,
            },
            'half_front_1': {
                'joint1_1': 0.174533,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'three_quarters_front_up_1': {
                'joint1_1': 0.087266,
                'joint2_1': -0.174533,
                'joint3_1': 1.047197551,
            },
            'quarter_back_1': {
                'joint1_1': -0.087266,
                'joint2_1': 0,
                'joint3_1': 1.047197551,
            },
            'three_quarters_back_1': {
                'joint1_1': -0.261799,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },




            'home_2': {
                'joint1_2': 0.0,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'przod_2': {
                'joint1_2': 0.349066,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'tyl_2': {
                'joint1_2': -0.349066,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'up_2': {
                'joint1_2': 0.0,
                'joint2_2': -0.174533,
                'joint3_2': 1.047197551,
            },
            'half_up_2': {
                'joint1_2': 0.174533,
                'joint2_2': -0.174533,
                'joint3_2': 1.047197551,
            },
            'half_back_2': {    
                'joint1_2': -0.174533,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'half_back_up_2': {
                'joint1_2': -0.174533,
                'joint2_2': -0.174533,
                'joint3_2': 1.047197551,
            },
            'half_front_2': {
                'joint1_2': 0.174533,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'three_quarters_front_up_2': {
                'joint1_2': 0.087266,
                'joint2_2': -0.174533,
                'joint3_2': 1.047197551,
            },
            'quarter_back_2': {
                'joint1_2': -0.087266,
                'joint2_2': 0,
                'joint3_2': 1.047197551,
            },
            'three_quarters_back_2': {
                'joint1_2': -0.261799,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },



            'home_3': {
                'joint1_3': 0.0,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'przod_3': {
                'joint1_3': 0.349066,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'tyl_3': {
                'joint1_3': -0.349066,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'up_3': {
                'joint1_3': 0.0,
                'joint2_3': -0.174533,
                'joint3_3': 1.047197551,
            },
            'half_up_3': {
                'joint1_3': 0.174533,
                'joint2_3': -0.174533,
                'joint3_3': 1.047197551,
            },
            'half_back_3': {
                'joint1_3': -0.174533,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'half_back_up_3': {
                'joint1_3': -0.174533,
                'joint2_3': -0.174533,
                'joint3_3': 1.047197551,
            },
            'half_front_3': {
                'joint1_3': 0.174533,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'three_quarters_front_up_3': {
                'joint1_3': 0.087266,
                'joint2_3': -0.174533,
                'joint3_3': 1.047197551,
            },
            'quarter_back_3': {
                'joint1_3': -0.087266,
                'joint2_3': 0,
                'joint3_3': 1.047197551,
            },
            'three_quarters_back_3': {
                'joint1_3': -0.261799,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },



            'home_4': {
                'joint1_4': 0.0,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            'przod_4': {
                'joint1_4': -0.349066,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            'tyl_4': {
                'joint1_4': 0.349066,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            'up_4': {
                'joint1_4': 0.0,
                'joint2_4': -0.174533,
                'joint3_4': 1.047197551,
            },
            'half_up_4': {
                'joint1_4': -0.174533,
                'joint2_4': -0.174533,
                'joint3_4': 1.047197551,
            },
            'half_back_4': {
                'joint1_4': 0.174533,
                'joint2_4': 0.0,    
                'joint3_4': 1.047197551,
            },
            'half_back_up_4': {
                'joint1_4': 0.174533,
                'joint2_4': -0.174533,
                'joint3_4': 1.047197551,
            },
            'half_front_4': {
                'joint1_4': -0.174533,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            'three_quarters_front_up_4': {
                'joint1_4': -0.087266,
                'joint2_4': -0.174533,
                'joint3_4': 1.047197551,
            },
            'quarter_back_4': {
                'joint1_4': 0.087266,
                'joint2_4': 0,
                'joint3_4': 1.047197551,
            },
            'three_quarters_back_4': {
                'joint1_4': 0.261799,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },




            'home_5': {
                'joint1_5': 0.0,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'przod_5': {
                'joint1_5': -0.349066,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'tyl_5': {
                'joint1_5': 0.349066,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'up_5': {
                'joint1_5': 0.0,
                'joint2_5': -0.174533,
                'joint3_5': 1.047197551,
            },
            'half_up_5': {
                'joint1_5': -0.174533,
                'joint2_5': -0.174533,
                'joint3_5': 1.047197551,
            },
            'half_back_5': {
                'joint1_5': 0.174533,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'half_back_up_5': {
                'joint1_5': 0.174533,
                'joint2_5': -0.174533,
                'joint3_5': 1.047197551,
            },
            'half_front_5': {
                'joint1_5': -0.174533,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'three_quarters_front_up_5': {
                'joint1_5': -0.087266,
                'joint2_5': -0.174533,
                'joint3_5': 1.047197551,
            },
            'quarter_back_5': {
                'joint1_5': 0.087266,
                'joint2_5': 0,
                'joint3_5': 1.047197551,
            },
            'three_quarters_back_5': {
                'joint1_5': 0.261799,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },



            'home_6': {
                'joint1_6': 0.0,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            'przod_6': {
                'joint1_6': -0.349066,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            'tyl_6': {
                'joint1_6': 0.349066,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,  # Poprawione, było 'joint3_4'
            },
            'up_6': {
                'joint1_6': 0.0,
                'joint2_6': -0.174533,
                'joint3_6': 1.047197551,
            },
            'half_up_6': {  # Poprawione, było 'half_up_4'
                'joint1_6': -0.174533,
                'joint2_6': -0.174533,
                'joint3_6': 1.047197551,
            },
            'half_back_6': {
                'joint1_6': 0.174533,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            'half_back_up_6': {
                'joint1_6': 0.174533,
                'joint2_6': -0.174533,
                'joint3_6': 1.047197551,
            },
            'half_front_6': {
                'joint1_6': -0.174533,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            'three_quarters_front_up_6': {
                'joint1_6': -0.087266,
                'joint2_6': -0.174533,
                'joint3_6': 1.047197551,
            },
            'quarter_back_6': {
                'joint1_6': 0.087266,
                'joint2_6': 0,
                'joint3_6': 1.047197551,
            },
            'three_quarters_back_6': {
                'joint1_6': 0.261799,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
        }

        # Listy stawów dla nóg
        self.joint_names = {
            1: ['joint1_1', 'joint2_1', 'joint3_1'],
            2: ['joint1_2', 'joint2_2', 'joint3_2'],
            3: ['joint1_3', 'joint2_3', 'joint3_3'],
            4: ['joint1_4', 'joint2_4', 'joint3_4'],
            5: ['joint1_5', 'joint2_5', 'joint3_5'],
            6: ['joint1_6', 'joint2_6', 'joint3_6']
        }
        
    def send_trajectory_to_all_legs(self, positions_dict, duration_sec=2.0):
        """
        Wysyła trajektorię do kontrolerów wszystkich nóg jednocześnie
        positions_dict to słownik z pozycjami dla wszystkich nóg, np. {"home_1", "home_2", ...}
        """
        self.get_logger().info(f'Wysyłam trajektorię do pozycji: {positions_dict}')
        
        # Sprawdź, czy wszystkie pozycje istnieją
        for leg_num, position_name in positions_dict.items():
            if position_name not in self.positions:
                self.get_logger().error(f'Pozycja {position_name} nie istnieje!')
                return False
        
        # Ustaw czas trwania ruchu
        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        
        # Dla każdej nogi przygotuj i wyślij trajektorię
        for leg_num, position_name in positions_dict.items():
            # Utwórz wiadomość trajektorii dla nogi
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names[leg_num]
            
            # Utwórz punkt trajektorii
            point = JointTrajectoryPoint()
            
            # Ustaw pozycje stawów
            position_values = []
            for joint in self.joint_names[leg_num]:
                position_values.append(self.positions[position_name][joint])
            
            point.positions = position_values
            point.velocities = [0.0] * len(self.joint_names[leg_num])
            point.accelerations = [0.0] * len(self.joint_names[leg_num])
            
            # Ustaw czas trwania ruchu
            point.time_from_start = duration
            
            # Dodaj punkt do trajektorii
            trajectory.points.append(point)
            
            # Wyślij trajektorię
            self.trajectory_publishers[leg_num].publish(trajectory)
        
        self.get_logger().info('Wysłano trajektorie dla wszystkich nóg')
        return True
    
    def execute_sequence(self):
        """Wykonanie sekwencji ruchów dla wszystkich nóg równocześnie"""
        self.get_logger().info('Rozpoczynam sekwencję ruchów dla wszystkich nóg')
        
        # Przejście do pozycji początkowej dla wszystkich nóg
        self.send_trajectory_to_all_legs({
            1: "home_1",
            2: "home_2",
            3: "home_3",
            4: "home_4",
            5: "home_5",
            6: "home_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(2.0)  # Daj czas na wykonanie ruchu

        # 1.ruch
        self.send_trajectory_to_all_legs({
            1: "half_up_1",
            2: "half_back_2",
            3: "quarter_back_3",
            4: "half_up_4",
            5: "half_back_5",
            6: "quarter_back_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)
        
        #2.ruch
        self.send_trajectory_to_all_legs({
            1: "przod_1",
            2: "tyl_2",
            3: "half_back_3",
            4: "przod_4",
            5: "tyl_5",
            6: "half_back_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(2.0)  # Daj czas na wykonanie ruchu
        
        for i in range(3):
            #3.ruch
            self.send_trajectory_to_all_legs({
                1: "half_front_1",
                2: "three_quarters_front_up_2",
                3: "three_quarters_back_3",
                4: "half_front_4",
                5: "three_quarters_front_up_5",
                6: "three_quarters_back_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)  # Daj czas na wykonanie ruchu

            #4.ruch
            self.send_trajectory_to_all_legs({
                1: "home_1",
                2: "przod_2",
                3: "tyl_3",
                4: "home_4",
                5: "przod_5",
                6: "tyl_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu

            #5.ruch
            self.send_trajectory_to_all_legs({
                1: "half_back_1",
                2: "half_front_2",
                3: "up_3",
                4: "half_back_4",
                5: "half_front_5",
                6: "up_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)

            #6 ruch
            self.send_trajectory_to_all_legs({
                1: "tyl_1",
                2: "home_2",
                3: "przod_3",
                4: "tyl_4",
                5: "home_5",
                6: "przod_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu

            #7 ruch
            self.send_trajectory_to_all_legs({
                1: "up_1",
                2: "half_back_2",
                3: "half_front_3",
                4: "up_4",
                5: "half_back_5",
                6: "half_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu

            #8 ruch
            self.send_trajectory_to_all_legs({
                1: "przod_1",
                2: "tyl_2",
                3: "home_3",
                4: "przod_4",
                5: "tyl_5",
                6: "home_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu


        self.send_trajectory_to_all_legs({
            1: "half_front_1",
            2: "half_back_up_2",
            3: "home_3",
            4: "half_front_4",
            5: "half_back_up_5",
            6: "home_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)

        self.send_trajectory_to_all_legs({
            1: "home_1",
            2: "home_2",
            3: "home_3",
            4: "home_4",
            5: "home_5",
            6: "home_6"
        })

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