EXECUTE_PROCESS( COMMAND python generate_config_header -p ${CMAKE_INSTALL_PREFIX} --rpm_build=${IS_RPM_BUILD}
	WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} )

INSTALL( FILES ${CMAKE_CURRENT_SOURCE_DIR}/configfile.h
			${CMAKE_CURRENT_SOURCE_DIR}/exception.h
			${CMAKE_CURRENT_SOURCE_DIR}/hashtable.h 
			${CMAKE_CURRENT_SOURCE_DIR}/kusp_common.h
			${CMAKE_CURRENT_SOURCE_DIR}/linkedlist.h
			${CMAKE_CURRENT_SOURCE_DIR}/misc.h
			${CMAKE_CURRENT_SOURCE_DIR}/mutex.h
			${CMAKE_CURRENT_SOURCE_DIR}/net.h
			${CMAKE_CURRENT_SOURCE_DIR}/rdwr.h
			${CMAKE_CURRENT_SOURCE_DIR}/taskalias.h
			${CMAKE_CURRENT_SOURCE_DIR}/taskmapper.h
			${CMAKE_CURRENT_SOURCE_DIR}/vector.h 
			DESTINATION include )