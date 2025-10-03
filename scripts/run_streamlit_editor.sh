#!/bin/bash
echo "================================================"
echo "Database Configuration Editor - Streamlit App"
echo "================================================"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install required packages if not already installed
echo "Checking and installing required packages..."
python -m pip install streamlit pandas --quiet

# Run the Streamlit application
echo "Starting Streamlit Database Configuration Editor..."
echo ""
echo "The application will open in your default web browser."
echo "Press Ctrl+C to stop the application."
echo ""

streamlit run streamlit_db_config_editor.py --server.port 8501