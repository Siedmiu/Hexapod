import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
import xacro
def generate_launch_description():
    #this name has to match the robot name in the Xacro file
    robotXacroName = 'differential_drive_robot'

    #this is the name of our pkg, at the same time it is the name of the folder 
    #that will be used to define the path
    namePackage='mobile_robot'

    #this is a relative path to the Gazebo world file
    modelFileRelativePath = 'model/robot.xacro'

    #uncomment this if you want to define your own empty world model
    #however, then you have to create empty_world.world
    #this is a relative path to the Gazebo world file
    # worldFileRelativePath = 'model/empty_world.world'

    #this is the absolute path to the model
    pathModelFile = os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)

    #uncomment this if you want to define your own empty world model
    #this is a relative path to the Gazebo world file
    # pathModelFile = os.path.join(get_package_share_directory(namePackage), worldFileRelativePath)

    #get the robot description from the xacro model file
    robotDescription = xacro.process_file(pathModelFile).toxml()

    #this is the launch file from the gazebo_ros package
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('ros_gz_sim'),
                                                                         'launch', 'gz_sim.launch.py'))
    
    #this is the launch description

    #this is if you are using your own world model
    # gazeboLaunch=IncludeLaunchDescription(gazebo_rosPackageLaunch, launch_arguments={'gz_args':['-r -v -v4 pathWorldFile'], 'on_exit_shutdown':'true'}.items())

    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments=[
            ('gz_args', '-r -v -v4 empty.sdf'),
            ('on_exit_shutdown', 'true')
        ]
    )

    #Gz node
    spawnModelNodeGazebo=  Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robotXacroName,
            '-topic', 'robot_description'
        ],
        output='screen',
    )

    #Robot state publisher node
    nodeRobotStatePublisher=Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robotDescription, 
                     'use_sim_time': 'true'}]

    )

    #this is very important so we can control the robot from ros2
    bridge_params = os.path.join(
        get_package_share_directory(namePackage),
        'parameters',
        'bridge_parameters.yaml'
    )


    start_gazebo_ros_bridge_smd=Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output='screen',
    )

    #here we create an empty launch description object
    launchDescriptionObject=LaunchDescription()

    #we add gazeboLaunch
    launchDescriptionObject.add_action(spawnModelNodeGazebo)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)
    launchDescriptionObject.add_action(start_gazebo_ros_bridge_smd)

    return launchDescriptionObject


