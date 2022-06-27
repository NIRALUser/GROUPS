#-----------------------------------------------------------------------------
set(MODULE_NAME RigidAlignmentModule)

#-----------------------------------------------------------------------------
set(${MODULE_NAME}_TITLE "Rigid Alignment Module" CACHE STRING "Module title")
set(${MODULE_NAME}_CATEGORY "Groups" CACHE STRING "Module category")

set(MODULE_METADATA_SCRIPT
  ${CMAKE_CURRENT_BINARY_DIR}/_${MODULE_NAME}Metadata/__init__.py
  )

set(TITLE_CONFIG ${${MODULE_NAME}_TITLE})
set(CATEGORY_CONFIG ${${MODULE_NAME}_CATEGORY})
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/_${MODULE_NAME}Metadata/__init__.py.in
  ${MODULE_METADATA_SCRIPT}
  @ONLY
  )

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_METADATA_SCRIPT}
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/UI/${MODULE_NAME}.ui
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
