# CMakeLists.txt — KMDF filter driver qurilishi uchun
#
# Talab qilinadi:
#   - Visual Studio 2019/2022
#   - Windows Driver Kit (WDK) 10.x
#   - WDK Visual Studio Extension
#
# Qurilish:
#   Visual Studio'da "Kernel Mode Driver (KMDF)" loyihasi ochib,
#   Driver.c faylini qo'shing va quyidagi sozlamalarni o'rnating:
#
#   Project Properties:
#     Driver Settings > Target OS: Windows 10
#     Driver Settings > Target Platform: Desktop
#     C/C++ > Code Generation > Runtime Library: /MT (Multi-threaded)
#
# Yoki WDK build tools bilan:
#   msbuild UsbFilter.vcxproj /p:Configuration=Release /p:Platform=x64

cmake_minimum_required(VERSION 3.20)
project(UsbFilter LANGUAGES C)

# WDK yo'lini aniqlash
if(NOT DEFINED WDK_ROOT)
    set(WDK_ROOT "C:/Program Files (x86)/Windows Kits/10")
endif()

set(WDK_VERSION "10.0.22621.0")
set(WDK_INC "${WDK_ROOT}/Include/${WDK_VERSION}")
set(WDK_LIB "${WDK_ROOT}/Lib/${WDK_VERSION}")
set(KMDF_VERSION "1.33")
set(KMDF_INC "${WDK_ROOT}/Include/wdf/kmdf/${KMDF_VERSION}")
set(KMDF_LIB "${WDK_ROOT}/Lib/wdf/kmdf/x64/${KMDF_VERSION}")

add_library(UsbFilter MODULE
    Driver.c
)

target_include_directories(UsbFilter PRIVATE
    "${WDK_INC}/km"
    "${WDK_INC}/shared"
    "${WDK_INC}/um"
    "${KMDF_INC}"
)

target_link_libraries(UsbFilter
    "${WDK_LIB}/km/x64/ntoskrnl.lib"
    "${WDK_LIB}/km/x64/hal.lib"
    "${WDK_LIB}/km/x64/wdm.lib"
    "${KMDF_LIB}/WdfDriverStubum.lib"
    "${KMDF_LIB}/WdfLdr.lib"
)

set_target_properties(UsbFilter PROPERTIES
    SUFFIX ".sys"
    LINK_FLAGS "/DRIVER /SUBSYSTEM:NATIVE /ENTRY:DriverEntry /NODEFAULTLIB /MANIFEST:NO"
)
