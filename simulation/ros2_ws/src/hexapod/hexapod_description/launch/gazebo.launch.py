import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Nazwa robota
    robotXacroName = 'hexapod'
    namePackage = 'hexapod_description'
    modelFileRelativePath = 'urdf/hexapod/hexapod.xacro'

    pathModelFile = os.path.join(
        get_package_share_directory(namePackage),
        modelFileRelativePath
    )

    robotDescription = xacro.process_file(pathModelFile).toxml()

    # Ścieżka do świata SDF
    gz_world_path = os.path.join(
        get_package_share_directory("hexapod_gazebo"),
        "worlds",
        "world.sdf"
    )

    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )
    )

    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments=[
            ('gz_args', f'-r -v 4 {gz_world_path}'),
            ('on_exit_shutdown', 'true')
        ]
    )

    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robotDescription,
            'use_sim_time': True
        }]
    )

    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robotXacroName,
            '-topic', 'robot_description'
        ],
        output='screen',
    )

    bridge_params = os.path.join(
        get_package_share_directory('hexapod_moveit_config'),
        'config',
        'bridge_parameters.yaml'
    )

    start_gazebo_ros_bridge_smd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[bridge_params],
        output='screen',
    )

    return LaunchDescription([
        gazeboLaunch,
        nodeRobotStatePublisher,
        spawnModelNodeGazebo,
        start_gazebo_ros_bridge_smd
    ])
