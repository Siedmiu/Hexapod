import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    namePackage = 'hexapod'
    
    # Ścieżki do plików
    sdf_file = os.path.join(get_package_share_directory(namePackage), 'model', 'hexapod.sdf')
    bridge_params = os.path.join(get_package_share_directory(namePackage), 'parameters', 'hexapod_bridge.yaml')
    ros2_control_params = os.path.join(get_package_share_directory(namePackage), 'config', 'ros2_control.yaml')

    # Uruchomienie Gazebo
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [f'-r -v -v4 {sdf_file}'], 'on_exit_shutdown': 'true'}.items(),
    )

    # Wczytanie modelu SDF do Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', sdf_file, '-name', 'hexapod'],
        output='screen'
    )

    # Mostek ROS-Gazebo
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output='screen'
    )

    # Węzeł ROS 2 Control do sterowania silnikami
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_control_params],
        output="screen"
    )

    # Uruchomienie kontrolera jointa
    load_joint_controller = ExecuteProcess(
        cmd=["ros2", "control", "load_controller", "--set-state", "active", "up_section_joint_controller"],
        output="screen"
    )

    # Sterowanie klawiaturą
    keyboard_control_node = Node(
        package=namePackage,
        executable="keyboard_control.py",
        output="screen"
    )

    return LaunchDescription([
        gazebo_launch,
        spawn_entity,
        ros_gz_bridge,
        ros2_control_node,
        load_joint_controller,
        keyboard_control_node
    ])
