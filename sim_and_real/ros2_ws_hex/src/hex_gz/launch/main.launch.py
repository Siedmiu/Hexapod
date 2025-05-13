#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import TimerAction

def generate_launch_description():
    # Argument: tryb działania
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='sim',
        description="Tryb działania: 'sim' (symulacja) lub 'real' (rzeczywisty robot + symulacja)"
    )
    
    walk_arg = DeclareLaunchArgument(
        'walk',
        default_value = 'false',
        description = "Czy odpalać chodzenie od początku?"
    )
    
    mode = LaunchConfiguration('mode')
    walk = LaunchConfiguration('walk')
    
    # Ścieżki do pakietów
    hex_gz_path = get_package_share_directory('hex_gz')
    pajak_path = get_package_share_directory('pajak')
    
    script_path = os.path.join(get_package_share_directory('hex_gz'), 'scripts', 'leg_sequence_player.py')
    script_path = os.path.abspath(script_path)
    
    # Uruchamianie Gazebo z hexapodem (symulacja) — zawsze
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(hex_gz_path, 'launch', 'gazebo.launch.py')
        )
    )
    
    # Uruchamianie serwera ESP32 tylko w trybie 'real'
    wifi_connect = ExecuteProcess(
        cmd=[
            'xterm', '-e', 'python3', os.path.join(pajak_path, 'pajak', 'wifi_connect.py')
        ],
        output='screen',
        condition=IfCondition(PythonExpression(["'", mode, "' == 'real'"]))
    )
    
    # Uruchamianie leg_sequence_player.py w osobnym terminalu w trybie 'real', z opóźnieniem
    # Dodanie "bash -c" i "; bash" utrzyma terminal otwarty nawet po zakończeniu skryptu
    hex_walk = TimerAction(
        period=10.0,  # seconds
        actions=[
            ExecuteProcess(
                cmd=[
                    'xterm', '-hold', '-e', 'bash', '-c', f'python3 {script_path}; echo "\nScript completed or terminated. Press Enter to close this window."; read'
                ],
                output='screen',
                condition=IfCondition(PythonExpression(["'", walk, "' == 'true' and '", mode, "' == 'real'"]))
            )
        ]
    )
    
    hex_walk_sim = TimerAction(
        period=10.0,  # seconds
        actions=[
            ExecuteProcess(
                cmd=[
                    'python3', script_path
                ],
                output='screen',
                condition=IfCondition(PythonExpression(["'", walk, "' == 'true' and '", mode, "' != 'real'"]))
            )
        ]
    )
    
    return LaunchDescription([
        mode_arg,
        walk_arg,
        gazebo_launch,
        wifi_connect,
        hex_walk,
        hex_walk_sim
    ])