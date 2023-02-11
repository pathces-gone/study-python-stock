cmake_minimum_required(VERSION 3.5)
project (AssetAllocationV3)

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)
if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++14 support. Please use a different C++ compiler.")
endif()


set(SOURCES
    src/main.cpp
)


find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

add_executable(assetv3 ${SOURCES})

target_link_libraries(assetv3 ${PYTHON_LIBRARIES})
target_include_directories(assetv3 PRIVATE 
        ${PROJECT_SOURCE_DIR}/include/LibCommon
)

target_compile_definitions(assetv3 PRIVATE 
    PYTHON_RUN_BY_FILE
    #PYTHON_RUN_BY_STRING
)

install (TARGETS assetv3 DESTINATION ${PROJECT_SOURCE_DIR}/bin)
