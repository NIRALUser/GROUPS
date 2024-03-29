cmake_minimum_required(VERSION 3.5)

# Update CMake module path
set(GROUPS_CMAKE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/CMake")
list(INSERT CMAKE_MODULE_PATH 0 ${GROUPS_CMAKE_DIR})
add_subdirectory(${GROUPS_CMAKE_DIR})
list(INSERT CMAKE_MODULE_PATH 0 "${CMAKE_CURRENT_BINARY_DIR}/CMake")

project(GROUPS)

set(GROUPS_VERSION_MAJOR 1)
set(GROUPS_VERSION_MINOR 0)
set(GROUPS_VERSION_PATCH 0)
set(GROUPS_VERSION
${GROUPS_VERSION_MAJOR}.${GROUPS_VERSION_MINOR}.${GROUPS_VERSION_PATCH})

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "")
set(EXTENSION_CATEGORY "GROUPS")
set(EXTENSION_CONTRIBUTORS "Mahmoud Mostapha (UNC), Laura Pascal (Kitware, Inc.")
set(EXTENSION_DESCRIPTION "Cortical correspondence method employing group-wise registration in a spherical parametrization space for the use in neuroimaging studies")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS ShapePopulationViewer)
set(EXTENSION_BUILD_SUBDIRECTORY inner-build)

set(SUPERBUILD_TOPLEVEL_PROJECT inner)

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})
mark_as_superbuild(Slicer_DIR)

find_package(Git REQUIRED)
mark_as_superbuild(GIT_EXECUTABLE)

#-----------------------------------------------------------------------------
# Options
option(${EXTENSION_NAME}_BUILD_CLI_MODULE_Groups "Build Groups CLI module" ON)
mark_as_superbuild(${EXTENSION_NAME}_BUILD_CLI_MODULE_Groups)

option(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_RigidAlignmentModule "Build RigidAlignmentModule scripted module" ON)
mark_as_superbuild(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_RigidAlignmentModule)

option(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_GroupWiseRegistrationModule "Build GroupWiseRegistrationModule scripted module" ON)
mark_as_superbuild(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_GroupWiseRegistrationModule)

#-----------------------------------------------------------------------------
# SuperBuild setup
option(${EXTENSION_NAME}_SUPERBUILD "Build ${EXTENSION_NAME} and the projects it depends on." ON)
mark_as_advanced(${EXTENSION_NAME}_SUPERBUILD)
if(${EXTENSION_NAME}_SUPERBUILD)
  include("${CMAKE_CURRENT_SOURCE_DIR}/SuperBuild.cmake")
  return()
endif()

#-----------------------------------------------------------------------------
find_package(MeshLib REQUIRED)

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Modules)
## NEXT_MODULE

#-----------------------------------------------------------------------------
set(EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS)
list(APPEND EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS "${MeshLib_DIR};MeshLib;RuntimeLibraries;/")
list(APPEND EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS "${RigidAlignment_DIR};RigidAlignment;RuntimeLibraries;/")
list(APPEND EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS "${SurfRemesh_DIR};SurfRemesh;RuntimeLibraries;/")
set(${EXTENSION_NAME}_CPACK_INSTALL_CMAKE_PROJECTS "${EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS}" CACHE STRING "List of external projects to install" FORCE)

#-----------------------------------------------------------------------------
list(APPEND CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};RuntimeLibraries;/")
list(APPEND CPACK_INSTALL_CMAKE_PROJECTS "${${EXTENSION_NAME}_CPACK_INSTALL_CMAKE_PROJECTS}")
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
