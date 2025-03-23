"""from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("hexapod", package_name="moveit_hexapod").to_moveit_configs()
    return generate_rsp_launch(moveit_config)
"""
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare

robot_description = Command([
    "xacro ", FindPackageShare("moveit_hexapod"), "/urdf/hexapod.xacro"
])

robot_state_publisher = Node(
    package="robot_state_publisher",
    executable="robot_state_publisher",
    output="screen",
    parameters=[{"robot_description": robot_description}]
)
