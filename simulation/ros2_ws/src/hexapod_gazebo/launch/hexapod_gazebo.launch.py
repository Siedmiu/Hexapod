import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Ścieżki do katalogów modeli i świata
    package_name = 'hexapod_gazebo'
    package_share_directory = get_package_share_directory(package_name)
    
    world_path = os.path.join(package_share_directory, 'models', 'world', 'world.sdf')
    hexapod_model_path = os.path.join(package_share_directory, 'models', 'hexapod')

    # Ustawienie zmiennej GAZEBO_MODEL_PATH, aby Gazebo znalazło modele
    gazebo_model_path = os.path.join(package_share_directory, 'models')

    return LaunchDescription([
        # Ustawienie zmiennej środowiskowej dla ścieżki do modeli
        DeclareLaunchArgument(
            'gazebo_model_path',
            default_value=gazebo_model_path,
            description='Ścieżka do katalogu modeli Gazebo'
        ),

        # Uruchomienie Gazebo z odpowiednim plikiem świata
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
            )]),
            launch_arguments={'world': world_path}.items(),
        ),

        # Spawn modelu Hexapoda w świecie Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'hexapod',
                '-file', os.path.join(hexapod_model_path, 'hexapod.sdf'),
                '-x', '0', '-y', '0', '-z', '0.2'
            ],
            output='screen'
        )
    ])
