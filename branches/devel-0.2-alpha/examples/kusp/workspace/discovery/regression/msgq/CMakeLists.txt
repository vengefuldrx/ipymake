CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

PROJECT( msgq )

INCLUDE_DIRECTORIES( ${CMAKE_CURRENT_BINARY_DIR} )

SET(CMAKE_C_FLAGS "-Wall")
ADD_EXECUTABLE( msgq msgq.c )

TARGET_LINK_LIBRARIES(msgq pthread rt)

