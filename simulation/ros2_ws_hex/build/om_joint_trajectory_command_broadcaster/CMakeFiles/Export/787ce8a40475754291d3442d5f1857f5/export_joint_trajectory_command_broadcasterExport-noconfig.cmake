#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "om_joint_trajectory_command_broadcaster::joint_trajectory_command_broadcaster" for configuration ""
set_property(TARGET om_joint_trajectory_command_broadcaster::joint_trajectory_command_broadcaster APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(om_joint_trajectory_command_broadcaster::joint_trajectory_command_broadcaster PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libjoint_trajectory_command_broadcaster.so"
  IMPORTED_SONAME_NOCONFIG "libjoint_trajectory_command_broadcaster.so"
  )

list(APPEND _cmake_import_check_targets om_joint_trajectory_command_broadcaster::joint_trajectory_command_broadcaster )
list(APPEND _cmake_import_check_files_for_om_joint_trajectory_command_broadcaster::joint_trajectory_command_broadcaster "${_IMPORT_PREFIX}/lib/libjoint_trajectory_command_broadcaster.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
