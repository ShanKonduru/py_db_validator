@echo off
REM ============================================================
REM COMPREHENSIVE TEST SUITE RUNNER - WINDOWS BATCH FILE
REM ============================================================
REM This script runs all enabled tests from the unified Excel workbook
REM Usage: run_all_tests.bat

echo.
echo ============================================================
echo COMPREHENSIVE TEST SUITE RUNNER
echo ============================================================
echo Starting comprehensive test execution...
echo Excel File: enhanced_unified_sdm_test_suite.xlsx
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the Excel file exists
if not exist "enhanced_unified_sdm_test_suite.xlsx" (
    echo ERROR: enhanced_unified_sdm_test_suite.xlsx not found
    echo Please ensure the Excel file is in the current directory
    pause
    exit /b 1
)

REM Check if the test runner exists
if not exist "run_all_enabled_tests.py" (
    echo ERROR: run_all_enabled_tests.py not found
    echo Please ensure the test runner script is in the current directory
    pause
    exit /b 1
)

REM Run the comprehensive test suite
echo Running comprehensive test suite...
echo.
python run_all_enabled_tests.py enhanced_unified_sdm_test_suite.xlsx

REM Check the exit code
if errorlevel 1 (
    echo.
    echo ============================================================
    echo TEST EXECUTION COMPLETED WITH ISSUES
    echo ============================================================
    echo Some tests may have failed or been skipped.
    echo Review the detailed output above for more information.
) else (
    echo.
    echo ============================================================
    echo TEST EXECUTION COMPLETED SUCCESSFULLY
    echo ============================================================
    echo All enabled tests passed successfully.
)

echo.
echo Press any key to exit...
pause >nul