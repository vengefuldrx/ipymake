################ Basic CMake support code ####################

CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

INCLUDE_DIRECTORIES( ${CMAKE_CURRENT_BINARY_DIR} $ENV{KUSPINSTALL}/include )
LINK_DIRECTORIES( $ENV{KUSPINSTALL}/lib )

# Generate an executable file by name.
# Sources can be specified past the name
# and they will be used as the source files.
# If no sources are specified then a 
# ${NAME}.c source will be assumed.
#
# DSUI is automatically genereated if dsui is 
# specified in ${LIBS}.
#
FUNCTION(AUTO_EXE NAME)

# CMake enforces the minimum number of argumetns.
# This will never have < 1.
IF(${ARGC} GREATER 1)
   # Setup any specified sources.
   SET(SOURCES ${ARGN})
ELSE(${ARGC} EQUAL 1)
   # No spcified sources. Generate one.
   SET(SOURCES ${NAME}.c)
ENDIF()

IF(DEFINED LIBS)
   STRING(REGEX MATCH "dsui" USE_DSUI ${LIBS})

   IF(USE_DSUI)
      IF(NOT DEFINED DSUI_PREFIX)
         SET(DSUI_PREFIX ${NAME})
      ENDIF()

      EXECUTE_PROCESS(COMMAND dsui-header --prefix ${DSUI_PREFIX} )
      SET(SOURCES ${SOURCES} ${DSUI_PREFIX}_dsui.c)
   ENDIF()
ENDIF()

ADD_EXECUTABLE( ${NAME} ${SOURCES} )

IF(DEFINED LIBS)
   TARGET_LINK_LIBRARIES(${NAME} ${LIBS})
ENDIF()

FOREACH(CF ${CONFIG_FILES})
	   CONFIGURE_FILE(${CMAKE_CURRENT_SOURCE_DIR}/${CF} 
  	      ${CMAKE_CURRENT_BINARY_DIR}/${CF} COPYONLY)
ENDFOREACH(CF)

ENDFUNCTION(AUTO_EXE)

################ Begin Configuration Options ####################

# Set full project name.
PROJECT( safety_test )

# These options can be repeated after each AUTO_EXE call to
# generate a different executable.

################################################
##### This lie will cause a kernel panic. ######
################################################
SET(CMAKE_C_FLAGS "-DCONFIG_DSUI -ggdb -Wall")

####################################
##### No panic for this line. ######
####################################
#SET(CMAKE_C_FLAGS "-ggdb -Wall")

SET(CONFIG_FILES test.dski test.pipes run cleanup)

# Libraries to pass to the linker.
# If dsui is linked in then AUTO_EXE will create the dsui files.
# This is an optional specification.
SET(LIBS pthread kusp dsui gsched m)

# Create the executable.
# This can be used multiple times to create multiple executables.
# If the source file has the same name as the executable
# then it does not need to be specified.
# Multiple source files can be specified.
AUTO_EXE(test test.c)

