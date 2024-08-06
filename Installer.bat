@echo off
setlocal EnableDelayedExpansion

@REM cd C:\

:: URLs for the installers
@REM set GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe
set PYTHON_URL=https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe
@REM set GIT_REPO_URL=https://github.com/R3tr0gh057/LibraryManagementSystem.git
@REM set Arduino_Driver=https://www.silabs.com/documents/public/software/CP210x_Windows_Drivers.zip

@REM :: File names
@REM set GIT_INSTALLER=Git-2.45.2-64-bit.exe
set PYTHON_INSTALLER=python-3.11.4-amd64.exe

@REM :: Download Git installer
@REM echo Downloading Git...
@REM powershell -Command "Invoke-WebRequest -Uri %GIT_URL% -OutFile %GIT_INSTALLER%"
@REM if not exist %GIT_INSTALLER% (
@REM     echo Failed to download Git installer.
@REM )
@REM echo Installing Git...
@REM start /wait %GIT_INSTALLER% /VERYSILENT
@REM if %errorlevel% neq 0 (
@REM     echo Failed to install Git.
@REM )

@REM :: Add Git to PATH
@REM set PATH=%PATH%;C:\Program Files\Git\cmd

@REM :: Clone Git repository
@REM echo Cloning Git repository...
@REM git clone %GIT_REPO_URL%
@REM if %errorlevel% neq 0 (
@REM     echo Failed to clone Git repository.
@REM )
@REM cd LibraryManagementSystem

:: Download Python installer
echo Downloading Python...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"
if not exist %PYTHON_INSTALLER% (
    echo Failed to download Python installer.
)
echo Installing Python...
start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
if %errorlevel% neq 0 (
    echo Failed to install Python.
)

:: Add Python to PATH
set PATH=%PATH%;C:\Program Files\Python311\Scripts

:: Check if pip is installed
echo Checking for pip...
pip --version
if %errorlevel% neq 0 (
    echo pip not found.
)

:: Install Python requirements
echo Installing Python requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python requirements.
)

:: Installation successful
echo Installation successful!
echo Installed Python packages:
pip list

endlocal
pause