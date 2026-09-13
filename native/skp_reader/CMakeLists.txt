cmake_minimum_required(VERSION 3.20)

project(staadprep_skp_reader LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

get_filename_component(STAADPREP_PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(
    SKETCHUP_SDK_ROOT
    "${STAADPREP_PROJECT_ROOT}/vendor/sketchup-sdk"
    CACHE PATH
    "Project-local staging directory for the official SketchUp SDK"
)
set(SKP_READER_OUTPUT_DIR "${STAADPREP_PROJECT_ROOT}/build/native/skp_reader")

add_executable(skp_reader src/main.cpp)
target_include_directories(skp_reader PRIVATE "${CMAKE_CURRENT_LIST_DIR}/include")

if(EXISTS "${SKETCHUP_SDK_ROOT}")
    message(
        STATUS
        "SketchUp SDK staging directory found at ${SKETCHUP_SDK_ROOT}; "
        "Task 15 must verify exact headers/libraries before enabling native reading."
    )
else()
    message(
        STATUS
        "SketchUp SDK not staged at ${SKETCHUP_SDK_ROOT}; building capability-only stub."
    )
endif()

set_target_properties(
    skp_reader
    PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${SKP_READER_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${SKP_READER_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${SKP_READER_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${SKP_READER_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${SKP_READER_OUTPUT_DIR}"
)
