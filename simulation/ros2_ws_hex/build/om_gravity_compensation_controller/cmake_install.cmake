# Install script for directory: /home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/src/ros2_controller/om_gravity_compensation_controller

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/install/om_gravity_compensation_controller")
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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/include/om_gravity_compensation_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/src/ros2_controller/om_gravity_compensation_controller/gravity_compensation_plugin.xml")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/gravity_compensation_controller" TYPE DIRECTORY FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/src/ros2_controller/om_gravity_compensation_controller/include/")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/libgravity_compensation_controller.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so"
         OLD_RPATH "/opt/ros/jazzy/lib:/opt/ros/jazzy/lib/x86_64-linux-gnu:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libgravity_compensation_controller.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/opt/ros/jazzy/lib/python3.12/site-packages/ament_package/template/environment_hook/library_path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/library_path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/om_gravity_compensation_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/om_gravity_compensation_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/opt/ros/jazzy/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/opt/ros/jazzy/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/environment" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/local_setup.bash")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/local_setup.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_environment_hooks/package.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_index/share/ament_index/resource_index/packages/om_gravity_compensation_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/controller_interface__pluginlib__plugin" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_index/share/ament_index/resource_index/controller_interface__pluginlib__plugin/om_gravity_compensation_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake/export_gravity_compensation_controllerExport.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake/export_gravity_compensation_controllerExport.cmake"
         "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/CMakeFiles/Export/e3cca997e5ce944695f39e353ac71b35/export_gravity_compensation_controllerExport.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake/export_gravity_compensation_controllerExport-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake/export_gravity_compensation_controllerExport.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/CMakeFiles/Export/e3cca997e5ce944695f39e353ac71b35/export_gravity_compensation_controllerExport.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/CMakeFiles/Export/e3cca997e5ce944695f39e353ac71b35/export_gravity_compensation_controllerExport-noconfig.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_export_dependencies/ament_cmake_export_dependencies-extras.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_export_targets/ament_cmake_export_targets-extras.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller/cmake" TYPE FILE FILES
    "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_core/om_gravity_compensation_controllerConfig.cmake"
    "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/ament_cmake_core/om_gravity_compensation_controllerConfig-version.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/om_gravity_compensation_controller" TYPE FILE FILES "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/src/ros2_controller/om_gravity_compensation_controller/package.xml")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/bartosz-babi-ski/Hexapod_git2/Hexapod/simulation/ros2_ws_hex/build/om_gravity_compensation_controller/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
