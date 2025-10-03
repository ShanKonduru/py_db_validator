#!/bin/bash
# Run Database Validation Framework

echo "Running Database Validation Framework..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment not activated. Please run 'source scripts/002_activate.sh' first."
    exit 1
fi

# Check if required files exist
if [ ! -f "examples/sample_tests.csv" ]; then
    echo "Error: Sample tests CSV not found. Please ensure examples/sample_tests.csv exists."
    exit 1
fi

if [ ! -f "examples/db_profiles.json" ]; then
    echo "Error: Database profiles not found. Please ensure examples/db_profiles.json exists."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please copy examples/.env.template to .env and configure your credentials."
    echo "Continuing with example run..."
fi

# Run the database validation framework
python3 main.py --csv examples/sample_tests.csv --profiles examples/db_profiles.json --output reports --log-level INFO

echo ""
echo "Validation completed. Check the reports/ directory for results."