@echo off
setlocal enabledelayedexpansion

:: Path to the Python installer
set pythonInstaller=C:\TODO\LMS-nosql\Dependencies\python-3.11.0-amd64.exe

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    start /wait "" "%pythonInstaller%" /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo Failed to install Python.
        exit /b 1
    )
) else (
    echo Python is already installed.
)

:: Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not installed. Installing pip...
    python -m ensurepip --upgrade >nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to install pip.
        exit /b 1
    )
) else (
    echo Pip is already installed.
)

:: Install the required Python packages
echo Installing required Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    set install_status=failed
) else (
    set install_status=success
)

:: Verify the installation of each package
echo Verifying package installations...
set "failures="
for /f "tokens=*" %%i in (requirements.txt) do (
    pip show %%i >nul 2>&1
    if %errorlevel% neq 0 (
        echo %%i failed to install.
        set "failures=!failures! %%i"
    ) else (
        echo %%i successfully installed.
    )
)

:: Provide installation feedback
if "%install_status%"=="failed" (
    echo.
    echo Installation completed with errors.
    if defined failures (
        echo The following packages failed to install: %failures%
    )
    echo Please check the errors above.
) else (
    echo.
    echo Installation successful, press any key to continue...
    pause >nul
)
