if(${EXTENSION_NAME}_BUILD_CLI_MODULE_Groups)
  add_subdirectory(CLI/Groups)
endif()

if(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_RigidAlignmentModule)
  add_subdirectory(Scripted/RigidAlignmentModule)
endif()

if(${EXTENSION_NAME}_BUILD_SCRIPTED_MODULE_GroupWiseRegistrationModule)
  add_subdirectory(Scripted/GroupWiseRegistrationModule)
endif()
