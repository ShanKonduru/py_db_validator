@echo off
echo Running Database Validation Framework...

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Error: Virtual environment not activated. Please run scripts\002_activate.bat first.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "examples\sample_tests.csv" (
    echo Error: Sample tests CSV not found. Please ensure examples\sample_tests.csv exists.
    pause
    exit /b 1
)

if not exist "examples\db_profiles.json" (
    echo Error: Database profiles not found. Please ensure examples\db_profiles.json exists.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Warning: .env file not found. Please copy examples\.env.template to .env and configure your credentials.
    echo Continuing with example run...
)

REM Run the database validation framework
python main.py --csv examples\sample_tests.csv --profiles examples\db_profiles.json --output reports --log-level INFO

echo.
echo Validation completed. Check the reports\ directory for results.
pause