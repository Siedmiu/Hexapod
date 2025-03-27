import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    namePackage = 'hexapod_gazebo'
    
    # Ścieżki do plików
    sdf_file = os.path.join(get_package_share_directory(namePackage), 'model', 'hexapod.sdf')
    bridge_params = os.path.join(get_package_share_directory(namePackage), 'parameters', 'hexapod_bridge.yaml')
    ros2_control_params = os.path.join(get_package_share_directory(namePackage), 'config', 'ros2_control.yaml')

    pkg_urdf_path = get_package_share_directory('hexapod_description')
    pkg_gazebo_path = get_package_share_directory('hexapod_gazebo')

    # === Argumenty ===
    rviz_launch_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Open RViz.'
    )

    world_arg = DeclareLaunchArgument(
        'world', default_value='world.sdf',
        description='Name of the Gazebo world file to load'
    )

    model_arg = DeclareLaunchArgument(
        'model', default_value='hexapod.xacro',
        description='Name of the URDF description to load'
    )

    # Ścieżka do pliku xacro
    urdf_file_path = PathJoinSubstitution([
        pkg_urdf_path, "urdf", "hexapod", LaunchConfiguration('model')
    ])

    # === Uruchamianie świata Gazebo ===
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r -v 4 {sdf_file}', 'on_exit_shutdown': 'true'}.items()
    )

    # === Spawnowanie modelu z pliku SDF ===
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', sdf_file, '-name', 'hexapod'],
        output='screen'
    )

    # === RViz ===
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_urdf_path, 'rviz', 'hexapod_description.rviz')],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': True}]
    )

    # === robot_state_publisher ===
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_file_path]),
            'use_sim_time': True
        }]
    )

    # === Bridge ROS <-> Gazebo ===
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[bridge_params],
        output='screen'
    )

    # === ROS 2 Control ===
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[ros2_control_params],
        output='screen'
    )

    # === Ładowanie kontrolera ===
    load_joint_controller = ExecuteProcess(
        cmd=["ros2", "control", "load_controller", "--set-state", "active", "up_section_joint_controller"],
        output="screen"
    )

    return LaunchDescription([
        rviz_launch_arg,
        world_arg,
        model_arg,
        gazebo_launch,
        spawn_entity,
        rviz_node,
        robot_state_publisher_node,
        ros_gz_bridge,
        ros2_control_node,
        load_joint_controller
    ])
