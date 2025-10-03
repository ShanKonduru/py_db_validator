@echo off
echo ================================================
echo Database Configuration Editor - Streamlit App
echo ================================================

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Install required packages if not already installed
echo Checking and installing required packages...
python -m pip install streamlit pandas --quiet

REM Run the Streamlit application
echo Starting Streamlit Database Configuration Editor...
echo.
echo The application will open in your default web browser.
echo Press Ctrl+C to stop the application.
echo.

streamlit run streamlit_db_config_editor.py --server.port 8501

pause