from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "hexapod", package_name="moveit_hexapod"
    ).to_moveit_configs()

    move_group_launch = generate_move_group_launch(moveit_config)

    # Load controllers (ros2_control)
    controllers_spawner = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[moveit_config.robot_description, moveit_config.robot_description_semantic],
        output="screen",
    )

    return LaunchDescription(move_group_launch.entities + [controllers_spawner])

