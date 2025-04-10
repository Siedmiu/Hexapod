# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_hex_gz_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED hex_gz_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(hex_gz_FOUND FALSE)
  elseif(NOT hex_gz_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(hex_gz_FOUND FALSE)
  endif()
  return()
endif()
set(_hex_gz_CONFIG_INCLUDED TRUE)

# output package information
if(NOT hex_gz_FIND_QUIETLY)
  message(STATUS "Found hex_gz: 3.0.0 (${hex_gz_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'hex_gz' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT hex_gz_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(hex_gz_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${hex_gz_DIR}/${_extra}")
endforeach()
