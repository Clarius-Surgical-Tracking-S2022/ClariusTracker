cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(Procrustean_PTLR)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/Procrustean_PTLR")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Chris Gibson (Robarts Research Institute), Elvis Chen (Robarts Research Institute), ")
set(EXTENSION_DESCRIPTION "This is a simple implementation of a Procrustean Point-To-Line registration algorithm for US probe calibration.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/Procrustean_PTLR.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/Procrustean_PTLR/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(PTL_Registration)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
