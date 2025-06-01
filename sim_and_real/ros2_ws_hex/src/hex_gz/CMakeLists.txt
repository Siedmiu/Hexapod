################################################################################
# Set minimum required version of cmake, project name and compile options
################################################################################
cmake_minimum_required(VERSION 3.5)
project(hex_gz)

################################################################################
# Find and load build settings from external packages
################################################################################
find_package(ament_cmake REQUIRED)
find_package(Python3 REQUIRED)

################################################################################
# Install
################################################################################
install(
  DIRECTORY launch config worlds rviz
  DESTINATION share/${PROJECT_NAME}
)

install(FILES open-manipulator-x-cdc.rules
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/x_create_udev_rules
  # scripts/init_position_for_x.py
  scripts/one_leg.py
  scripts/initial_positions_publisher.py
  scripts/setup.py
  scripts/leg_sequence_player.py
  scripts/imu_processer.py
  scripts/wifi_conect.py
  scripts/imu_data.py
  scripts/bi_gate.py
  scripts/wave_gate.py
  scripts/ripple_gate.py
  scripts/rotation.py
  scripts/point_to_point.py
  DESTINATION lib/${PROJECT_NAME}
)

################################################################################
# Macro for ament package
################################################################################
ament_package()
