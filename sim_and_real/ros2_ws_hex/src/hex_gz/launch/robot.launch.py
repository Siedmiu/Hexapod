#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare launch arguments
    declared_arguments = [
        DeclareLaunchArgument(
            'start_rviz', 
            default_value='false', 
            description='Whether to execute rviz2'
        ),
        DeclareLaunchArgument(
            'prefix',
            default_value='""',
            description='Prefix of the joint and link names',
        ),
        DeclareLaunchArgument(
            'use_gazebo',
            default_value='false',
            description='Start robot in Gazebo simulation.',
        ),
        DeclareLaunchArgument(
            'use_fake_hardware',
            default_value='false',
            description='Use fake hardware mirroring command.',
        ),
        DeclareLaunchArgument(
            'fake_sensor_commands',
            default_value='false',
            description='Enable fake sensor commands.',
        ),
        DeclareLaunchArgument(
            'port_name',
            default_value='/dev/ttyUSB0',
            description='Port name for ESP32 connection.',
        ),
        DeclareLaunchArgument(
            'baud_rate',
            default_value='115200',
            description='Baud rate for ESP32 communication.',
        ),
        DeclareLaunchArgument(
            'version',
            default_value='2',
            description='Hexapod version (1 or 2).',
        ),
    ]

    # Launch configurations
    start_rviz = LaunchConfiguration('start_rviz')
    prefix = LaunchConfiguration('prefix')
    use_gazebo = LaunchConfiguration('use_gazebo')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')
    fake_sensor_commands = LaunchConfiguration('fake_sensor_commands')
    port_name = LaunchConfiguration('port_name')
    baud_rate = LaunchConfiguration('baud_rate')
    version = LaunchConfiguration('version')

    # Generate URDF file using xacro
    urdf_file = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]),
        ' ',
        PathJoinSubstitution([
            FindPackageShare('hexapod_description'),
            'urdf',
            'hexapod.urdf.xacro',
        ]),
        ' ',
        'prefix:=',
        prefix,
        ' ',
        'use_gazebo:=',
        use_gazebo,
        ' ',
        'use_fake_hardware:=',
        use_fake_hardware,
        ' ',
        'fake_sensor_commands:=',
        fake_sensor_commands,
        ' ',
        'port_name:=',
        port_name,
        ' ',
        'baud_rate:=',
        baud_rate,
        ' ',
        'version:=',
        version,
    ])

    robot_description = {'robot_description': urdf_file}

    # Paths for configuration files
    controller_manager_config = PathJoinSubstitution([
        FindPackageShare('hex_gz'),
        'config',
        'gazebo_controller_manager.yaml',
    ])

    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('hexapod_description'),
        'rviz',
        'hexapod.rviz',
    ])

    # Define nodes
    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_description, controller_manager_config],
        output='both',
        condition=UnlessCondition(use_gazebo),  # Only when NOT using Gazebo
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description, {'use_sim_time': use_gazebo}],
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen',
        condition=IfCondition(start_rviz),
    )

    # Controller spawner node
    robot_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'leg1_controller',
            'leg2_controller', 
            'leg3_controller',
            'leg4_controller',
            'leg5_controller',
            'leg6_controller',
            'joint_state_broadcaster',
        ],
        parameters=[robot_description],
    )

    # Event handlers to ensure order of execution
    delay_rviz_after_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner, 
            on_exit=[rviz_node]
        )
    )

    return LaunchDescription(
        declared_arguments
        + [
            control_node,
            robot_controller_spawner,
            robot_state_publisher_node,
            delay_rviz_after_controller_spawner,
        ]
    )