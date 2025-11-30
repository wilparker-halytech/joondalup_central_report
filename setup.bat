@echo off
REM Setup Script for Illuminator Billing Processor (Windows)
REM This creates a virtual environment and installs dependencies

echo Setting up Illuminator Billing Processor...
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
if exist venv (
    echo Virtual environment already exists
    set /p RECREATE="Delete and recreate? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing old venv...
        rmdir /s /q venv
    ) else (
        echo Using existing venv
    )
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded
echo.

REM Install requirements
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt --quiet
    echo Dependencies installed
    echo.
    
    echo Installed packages:
    pip list | findstr /i "streamlit pandas"
    echo.
) else (
    echo requirements.txt not found
    echo Creating default requirements.txt...
    (
        echo streamlit^>=1.28.0
        echo pandas^>=2.0.0
    ) > requirements.txt
    pip install -r requirements.txt --quiet
    echo Default dependencies installed
    echo.
)

REM Create .vscode directory
if not exist .vscode (
    echo Creating .vscode directory...
    mkdir .vscode
    echo .vscode created
    echo.
)

REM Check for main files
echo Checking project files...
if exist streamlit_app.py (
    echo   [OK] streamlit_app.py found
) else (
    echo   [!] streamlit_app.py not found - you need to download this
)

if exist requirements.txt (
    echo   [OK] requirements.txt found
)

if exist .gitignore (
    echo   [OK] .gitignore found
) else (
    echo   [!] .gitignore not found - recommended to add one
)
echo.

REM Initialize git
if not exist .git (
    echo Initializing git repository...
    git init
    echo Git initialized
    echo.
)

echo Setup complete!
echo.
echo Next steps:
echo.
echo 1. Make sure you have these files:
echo    - streamlit_app.py
echo    - requirements.txt
echo    - .gitignore
echo.
echo 2. To run the app:
echo    venv\Scripts\activate
echo    streamlit run streamlit_app.py
echo.
echo 3. To deactivate when done:
echo    deactivate
echo.
echo 4. VS Code will automatically use this venv
echo    Just open the folder: code .
echo.
echo The virtual environment is in .\venv\
echo It is excluded from git by .gitignore
echo.

pause