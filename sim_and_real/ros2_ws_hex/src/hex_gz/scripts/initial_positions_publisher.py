#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time
import yaml
import os
from ament_index_python.packages import get_package_share_directory

class InitialPositionsPublisher(Node):
    def __init__(self):
        super().__init__('initial_positions_publisher')
        
        # Najpierw zainicjuj zmienne klasy
        self._publishers = {}
        self._config = None
        self._leg_joints = {}
        
        # Znajdź plik konfiguracyjny
        config_file = os.path.join(
            get_package_share_directory('hex_gz'),
            'config',
            'initial_positions.yaml'
        )
        
        # Wczytaj konfigurację początkowych pozycji z pliku YAML
        try:
            with open(config_file, 'r') as file:
                self._config = yaml.safe_load(file)
                self.get_logger().info(f"Załadowano konfigurację z {config_file}")
        except Exception as e:
            self.get_logger().error(f"Nie można załadować konfiguracji: {e}")
            return
        
        # Pobierz parametry z konfiguracji
        params = self._config.get('joint_trajectory_executor', {}).get('ros__parameters', {})
        joint_names = params.get('joint_names', [])
        
        # Sprawdź czy istnieje konfiguracja "default"
        default_positions = None
        if 'default' in params:
            default_positions = params.get('default', [])
        else:
            # Jeśli nie ma "default", sprawdź pierwszy step_name
            step_names = params.get('step_names', [])
            if step_names and step_names[0] in params:
                default_positions = params.get(step_names[0], [])
            
        if not joint_names or not default_positions or len(joint_names) != len(default_positions):
            self.get_logger().error("Nieprawidłowa konfiguracja - brak nazw stawów lub pozycji, lub ich liczba się nie zgadza")
            self.get_logger().error(f"Stawów: {len(joint_names)}, Pozycji: {len(default_positions) if default_positions else 0}")
            return
        
        # Pogrupuj stawy według nóg (zakładamy, że nazwy są w formacie joint[1-3]_[1-6])
        for i in range(len(joint_names)):
            # Pobierz numer nogi z nazwy stawu (np. z "joint1_3" pobierz "3")
            joint_name = joint_names[i]
            try:
                leg_num = joint_name.split('_')[-1]
                
                if f'leg{leg_num}' not in self._leg_joints:
                    self._leg_joints[f'leg{leg_num}'] = []
                
                self._leg_joints[f'leg{leg_num}'].append(default_positions[i])
            except Exception as e:
                self.get_logger().error(f"Błąd podczas przetwarzania stawu {joint_name}: {e}")
        
        # Utwórz wydawców dla każdej nogi
        for leg_name in self._leg_joints.keys():
            self._publishers[leg_name] = self.create_publisher(
                Float64MultiArray,
                f'/{leg_name}_controller/commands',
                10
            )
        
        # Odczekaj chwilę, aby wydawcy mogli się zainicjalizować
        self.get_logger().info("Oczekiwanie na gotowość wydawców...")
        time.sleep(1.0)
        
        # Opublikuj początkowe pozycje
        self.publish_initial_positions()
    
    def publish_initial_positions(self):
        """Publikuje początkowe pozycje dla wszystkich nóg."""
        if not self._config:
            self.get_logger().error("Brak konfiguracji, nie można opublikować pozycji.")
            return
        
        for leg_name, positions in self._leg_joints.items():
            if leg_name not in self._publishers:
                self.get_logger().error(f"Brak wydawcy dla {leg_name}")
                continue
                
            msg = Float64MultiArray()
            msg.data = positions
            
            # Publikowanie pozycji kilkukrotnie, aby upewnić się, że zostały odebrane
            for _ in range(3):
                self._publishers[leg_name].publish(msg)
                time.sleep(0.1)
            
            self.get_logger().info(f"Opublikowano początkowe pozycje dla {leg_name}: {positions}")
        
        self.get_logger().info("Wszystkie początkowe pozycje zostały opublikowane!")

def main(args=None):
    rclpy.init(args=args)
    node = InitialPositionsPublisher()
    
    try:
        # Wykonaj jeden cykl, node zakończy się automatycznie po publikacji
        rclpy.spin_once(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()