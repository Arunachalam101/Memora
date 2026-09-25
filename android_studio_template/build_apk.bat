@echo off
setlocal

REM MEMORA Build Script using Android Studio's Gradle

set ANDROID_HOME=C:\Users\chala\AppData\Local\Android\Sdk
set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
set PROJECT_DIR=C:\Users\chala\Memora\android_studio_template

echo.
echo ========================================
echo MEMORA APK Build Script
echo ========================================
echo Android SDK: %ANDROID_HOME%
echo Java Home: %JAVA_HOME%
echo Project: %PROJECT_DIR%
echo.

cd /d %PROJECT_DIR%

REM Try to find gradle executable
if exist "%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" (
    echo Found Android SDK command-line tools
) else (
    echo Warning: Android SDK command-line tools not found
)

REM Set environment
set PATH=%JAVA_HOME%\bin;%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools;%PATH%

echo.
echo Attempting to build APK...
echo.

REM Try using gradle.bat if available in system
where gradle.bat >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found gradle in PATH
    call gradle.bat assembleDebug
    goto :end
)

REM Try running through Java directly
echo Running gradle via Java...
java -cp "C:\Program Files\Android\Android Studio\plugins\gradle\lib\*" org.gradle.cli.Main assembleDebug

:end
echo.
if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo.
    echo ========================================
    echo SUCCESS! APK created
    echo ========================================
    dir app\build\outputs\apk\debug\app-debug.apk
) else (
    echo.
    echo ========================================
    echo APK not found - build may have failed
    echo ========================================
)
endlocal
