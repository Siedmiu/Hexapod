#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "om_spring_actuator_controller::spring_actuator_controller" for configuration ""
set_property(TARGET om_spring_actuator_controller::spring_actuator_controller APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(om_spring_actuator_controller::spring_actuator_controller PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libspring_actuator_controller.so"
  IMPORTED_SONAME_NOCONFIG "libspring_actuator_controller.so"
  )

list(APPEND _cmake_import_check_targets om_spring_actuator_controller::spring_actuator_controller )
list(APPEND _cmake_import_check_files_for_om_spring_actuator_controller::spring_actuator_controller "${_IMPORT_PREFIX}/lib/libspring_actuator_controller.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
