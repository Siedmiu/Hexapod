#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Argument: tryb działania
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='sim',
        description="Tryb działania: 'sim' (symulacja) lub 'real' (rzeczywisty robot + symulacja)"
    )

    mode = LaunchConfiguration('mode')

    # Ścieżki do pakietów
    hex_gz_path = get_package_share_directory('hex_gz')
    pajak_path = get_package_share_directory('pajak')

    # Uruchamianie Gazebo z hexapodem (symulacja) — zawsze
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(hex_gz_path, 'launch', 'gazebo.launch.py')
        )
    )

    # Uruchamianie serwera ESP32 tylko w trybie 'real'
    esp32_commander = ExecuteProcess(
        cmd=[
            'python3',
            os.path.join(pajak_path, 'pajak', 'esp32_serial_commander.py')
        ],
        output='screen',
        condition=IfCondition(PythonExpression(["'", mode, "' == 'real'"]))
    )

    return LaunchDescription([
        mode_arg,
        gazebo_launch,
        esp32_commander
    ])
