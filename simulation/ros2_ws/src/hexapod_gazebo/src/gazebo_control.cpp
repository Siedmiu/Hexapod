#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>

constexpr double DEG_TO_RAD = M_PI / 180.0;

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("hexapod_moveit_control");
    auto logger = rclcpp::get_logger("hexapod_moveit_control");

    using moveit::planning_interface::MoveGroupInterface;
    MoveGroupInterface move_group(node, "hexapod_arm");

    // Ustawienie pozycji stawów
    std::map<std::string, double> joint_target;
    joint_target["up_section_joint"] = -30.0 * DEG_TO_RAD;  // -30 stopni

    move_group.setJointValueTarget(joint_target);

    // Tworzenie planu ruchu
    MoveGroupInterface::Plan plan;
    bool success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);

    if (success) {
        RCLCPP_INFO(logger, "Wykonuję plan...");
        move_group.execute(plan);  // MoveIt! wyśle trajektorie do Gazebo
    } else {
        RCLCPP_ERROR(logger, "Planowanie nie powiodło się!");
    }

    rclcpp::shutdown();
    return 0;
}
