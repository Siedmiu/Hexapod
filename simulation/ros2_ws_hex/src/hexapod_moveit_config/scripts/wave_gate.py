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
            

            #LEG`1!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_1': {
                'joint1_1': 0.0,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '20_deg_front_1': {
                'joint1_1': 0.349066,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '16_deg_front_1': {
                'joint1_1': 0.279253,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '12_deg_front_1': {
                'joint1_1': 0.20944,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '8_deg_front_1': {
                'joint1_1': 0.139626,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '4_deg_front_1': {
                'joint1_1': 0.069813,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '4_deg_back_1': {
                'joint1_1': -0.069813,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '8_deg_back_1': {
                'joint1_1': -0.139626,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '12_deg_back_1': {
                'joint1_1': -0.20944,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '16_deg_back_1': {
                'joint1_1': -0.279253,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            '20_deg_back_1': {
                'joint1_1': -0.349066,
                'joint2_1': 0.0,
                'joint3_1': 1.047197551,
            },
            'up_1': {
                'joint1_1': 0.0,
                'joint2_1': -0.174533,
                'joint3_1': 1.047197551,
            },





            #LEG 2!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_2': {
                'joint1_2': 0.0,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '20_deg_front_2': {
                'joint1_2': 0.349066,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '16_deg_front_2': {
                'joint1_2': 0.279253,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '12_deg_front_2': {
                'joint1_2': 0.20944,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '8_deg_front_2': {
                'joint1_2': 0.139626,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '4_deg_front_2': {
                'joint1_2': 0.069813,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '4_deg_back_2': {
                'joint1_2': -0.069813,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '8_deg_back_2': {
                'joint1_2': -0.139626,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '12_deg_back_2': {
                'joint1_2': -0.20944,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '16_deg_back_2': {
                'joint1_2': -0.279253,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            '20_deg_back_2': {
                'joint1_2': -0.349066,
                'joint2_2': 0.0,
                'joint3_2': 1.047197551,
            },
            'up_2': {
                'joint1_2': 0.0,
                'joint2_2': -0.174533,
                'joint3_2': 1.047197551,
            },



            #LEG 3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_3': {
                'joint1_3': 0.0,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '20_deg_front_3': {
                'joint1_3': 0.349066,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '16_deg_front_3': {
                'joint1_3': 0.279253,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '12_deg_front_3': {
                'joint1_3': 0.20944,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '8_deg_front_3': {
                'joint1_3': 0.139626,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '4_deg_front_3': {
                'joint1_3': 0.069813,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '4_deg_back_3': {
                'joint1_3': -0.069813,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '8_deg_back_3': {
                'joint1_3': -0.139626,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '12_deg_back_3': {
                'joint1_3': -0.20944,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '16_deg_back_3': {
                'joint1_3': -0.279253,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            '20_deg_back_3': {
                'joint1_3': -0.349066,
                'joint2_3': 0.0,
                'joint3_3': 1.047197551,
            },
            'up_3': {
                'joint1_3': 0.0,
                'joint2_3': -0.174533,
                'joint3_3': 1.047197551,
            },



            #LEG 4!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_4': {
                'joint1_4': 0.0,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '20_deg_front_4': {
                'joint1_4': -0.349066,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '16_deg_front_4': {
                'joint1_4': -0.279253,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '12_deg_front_4': {
                'joint1_4': -0.20944,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '8_deg_front_4': {
                'joint1_4': -0.139626,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '4_deg_front_4': {
                'joint1_4': -0.069813,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '4_deg_back_4': {
                'joint1_4': 0.069813,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '8_deg_back_4': {
                'joint1_4': 0.139626,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '12_deg_back_4': {
                'joint1_4': 0.20944,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '16_deg_back_4': {
                'joint1_4': 0.279253,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            '20_deg_back_4': {
                'joint1_4': 0.349066,
                'joint2_4': 0.0,
                'joint3_4': 1.047197551,
            },
            'up_4': {
                'joint1_4': 0.0,
                'joint2_4': -0.174533,
                'joint3_4': 1.047197551,
            },


            #LEG 5!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_5': {
                'joint1_5': 0.0,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '20_deg_front_5': {
                'joint1_5': -0.349066,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '16_deg_front_5': {
                'joint1_5': -0.279253,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '12_deg_front_5': {
                'joint1_5': -0.20944,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '8_deg_front_5': {
                'joint1_5': -0.139626,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '4_deg_front_5': {
                'joint1_5': -0.069813,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '4_deg_back_5': {
                'joint1_5': 0.069813,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '8_deg_back_5': {
                'joint1_5': 0.139626,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '12_deg_back_5': {
                'joint1_5': 0.20944,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '16_deg_back_5': {
                'joint1_5': 0.279253,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            '20_deg_back_5': {
                'joint1_5': 0.349066,
                'joint2_5': 0.0,
                'joint3_5': 1.047197551,
            },
            'up_5': {
                'joint1_5': 0.0,
                'joint2_5': -0.174533,
                'joint3_5': 1.047197551,
            },




            #LEG 6!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            'home_6': {
                'joint1_6': 0.0,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '20_deg_front_6': {
                'joint1_6': -0.349066,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '16_deg_front_6': {
                'joint1_6': -0.279253,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '12_deg_front_6': {
                'joint1_6': -0.20944,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '8_deg_front_6': {
                'joint1_6': -0.139626,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '4_deg_front_6': {
                'joint1_6': -0.069813,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '4_deg_back_6': {
                'joint1_6': 0.069813,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '8_deg_back_6': {
                'joint1_6': 0.139626,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '12_deg_back_6': {
                'joint1_6': 0.20944,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '16_deg_back_6': {
                'joint1_6': 0.279253,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            '20_deg_back_6': {
                'joint1_6': 0.349066,
                'joint2_6': 0.0,
                'joint3_6': 1.047197551,
            },
            'up_6': {
                'joint1_6': 0.0,
                'joint2_6': -0.174533,
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
        time.sleep(3.0)  # Daj czas na wykonanie ruchu

        
        for i in range(3):

            #RUCH 1
            self.send_trajectory_to_all_legs({
                1: "16_deg_front_1",
                2: "up_2",
                3: "16_deg_back_3",
                4: "8_deg_back_4",
                5: "home_5",
                6: "8_deg_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)  # Daj czas na wykonanie ruchu

            #RUCH 2
            self.send_trajectory_to_all_legs({
                1: "12_deg_front_1",
                2: "20_deg_front_2",
                3: "20_deg_back_3",
                4: "12_deg_back_4",
                5: "4_deg_back_5",
                6: "4_deg_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)  # Daj czas na wykonanie ruchu


            #RUCH 3
            self.send_trajectory_to_all_legs({
                1: "8_deg_front_1",
                2: "16_deg_front_2",
                3: "up_3",
                4: "16_deg_back_4",
                5: "8_deg_back_5",
                6: "home_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
 
            #RUCH 4
            self.send_trajectory_to_all_legs({
                1: "4_deg_front_1",
                2: "12_deg_front_2",
                3: "20_deg_front_3",
                4: "20_deg_back_4",
                5: "12_deg_back_5",
                6: "4_deg_back_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)  # Daj czas na wykonanie ruchu

            #RUCH 5
            self.send_trajectory_to_all_legs({
                1: "home_1",
                2: "8_deg_front_2",
                3: "16_deg_front_3",
                4: "up_4",
                5: "16_deg_back_5",
                6: "8_deg_back_6"
            })

            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 6
            self.send_trajectory_to_all_legs({
                1: "4_deg_back_1",
                2: "4_deg_front_2",
                3: "12_deg_front_3",
                4: "20_deg_front_4",
                5: "20_deg_back_5",
                6: "12_deg_back_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 7
            self.send_trajectory_to_all_legs({
                1: "8_deg_back_1",
                2: "home_2",
                3: "8_deg_front_3",
                4: "16_deg_front_4",
                5: "up_5",
                6: "16_deg_back_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 8
            self.send_trajectory_to_all_legs({
                1: "12_deg_back_1",
                2: "4_deg_back_2",
                3: "4_deg_front_3",
                4: "12_deg_front_4",
                5: "20_deg_front_5",
                6: "20_deg_back_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 9
            self.send_trajectory_to_all_legs({
                1: "16_deg_back_1",
                2: "8_deg_back_2",
                3: "home_3",
                4: "8_deg_front_4",
                5: "16_deg_front_5",
                6: "up_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 10    
            self.send_trajectory_to_all_legs({
                1: "20_deg_back_1",
                2: "12_deg_back_2",
                3: "4_deg_back_3",
                4: "4_deg_front_4",
                5: "12_deg_front_5",
                6: "20_deg_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 11
            self.send_trajectory_to_all_legs({
                1: "up_1",
                2: "16_deg_back_2",
                3: "8_deg_back_3",
                4: "home_4",
                5: "8_deg_front_5",
                6: "16_deg_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)
            #RUCH 12
            self.send_trajectory_to_all_legs({
                1: "20_deg_front_1",
                2: "20_deg_back_2",
                3: "12_deg_back_3",
                4: "4_deg_back_4",
                5: "4_deg_front_5",
                6: "12_deg_front_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)

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