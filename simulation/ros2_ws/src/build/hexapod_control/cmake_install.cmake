# Install script for directory: /home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/hexapod_control

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/install/hexapod_control")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/hexapod_control" TYPE EXECUTABLE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/hexapod_joint_control")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control"
         OLD_RPATH "/home/julia-hrycyna/ws_moveit/install/moveit_ros_planning_interface/lib:/home/julia-hrycyna/ws_moveit/install/moveit_ros_move_group/lib:/opt/ros/jazzy/lib:/home/julia-hrycyna/ws_moveit/install/moveit_ros_warehouse/lib:/home/julia-hrycyna/ws_moveit/install/moveit_ros_planning/lib:/home/julia-hrycyna/ws_moveit/install/moveit_ros_occupancy_map_monitor/lib:/home/julia-hrycyna/ws_moveit/install/moveit_core/lib:/opt/ros/jazzy/lib/x86_64-linux-gnu:/home/julia-hrycyna/ws_moveit/install/moveit_msgs/lib:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/hexapod_control/hexapod_joint_control")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  include("/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/CMakeFiles/hexapod_joint_control.dir/install-cxx-module-bmi-noconfig.cmake" OPTIONAL)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/hexapod_control")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/hexapod_control")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control/environment" TYPE FILE FILES "/opt/ros/jazzy/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control/environment" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control/environment" TYPE FILE FILES "/opt/ros/jazzy/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control/environment" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/local_setup.bash")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/local_setup.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_environment_hooks/package.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_index/share/ament_index/resource_index/packages/hexapod_control")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control/cmake" TYPE FILE FILES
    "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_core/hexapod_controlConfig.cmake"
    "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/ament_cmake_core/hexapod_controlConfig-version.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/hexapod_control" TYPE FILE FILES "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/hexapod_control/package.xml")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/julia-hrycyna/Pulpit/Hexapod/simulation/ros2_ws/src/build/hexapod_control/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
