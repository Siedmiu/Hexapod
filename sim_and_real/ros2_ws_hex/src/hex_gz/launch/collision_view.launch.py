#!/usr/bin/env python3
"""
Plik launch wyświetlający model kolizyjny XACRO w RViz dla ROS2 Jazzy.
Skrypt ładuje model z pliku XACRO i konfiguruje RViz do wyświetlania geometrii kolizyjnej.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Parametry konfiguracyjne
    package_description_name = 'hexapod_description'  # Zastąp nazwą swojego pakietu
    package_gz_name = 'hex_gz'

    # Ścieżki do plików
    pkg_share_description = get_package_share_directory(package_description_name)
    pkg_share_gz = get_package_share_directory(package_gz_name)
    default_model_path = os.path.join(pkg_share_description, 'urdf', 'hexapod.urdf.xacro')
    default_rviz_config_path = os.path.join(pkg_share_gz, 'rviz', 'collision_view.rviz')
    
    # Deklaracje argumentów launch
    model_arg = DeclareLaunchArgument(
        name='model', 
        default_value=default_model_path,
        description='Ścieżka do pliku XACRO modelu'
    )
    
    rviz_arg = DeclareLaunchArgument(
        name='rviz_config', 
        default_value=default_rviz_config_path,
        description='Ścieżka do pliku konfiguracyjnego RViz'
    )
    
    gui_arg = DeclareLaunchArgument(
        name='gui', 
        default_value='true',
        description='Uruchom GUI kontrolera stawów'
    )
    
    # Parametry uruchomieniowe
    model = LaunchConfiguration('model')
    rviz_config = LaunchConfiguration('rviz_config')
    gui = LaunchConfiguration('gui')
    
    # Przetwarzanie modelu XACRO
    robot_description = ParameterValue(
        Command(['xacro ', model]),
        value_type=str
    )
    
    # Nody ROS
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_gui': gui}]
    )
    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config]
    )
    
    # Definicja LaunchDescription
    return LaunchDescription([
        model_arg,
        rviz_arg,
        gui_arg,
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node
    ])