@echo off
REM Set UTF-8 code page for proper Unicode character handling
chcp 65001 > nul

echo.
echo ============================================================
echo COMPREHENSIVE TEST SUITE RUNNER
echo ============================================================
echo Starting comprehensive test execution...
echo Excel File: enhanced_unified_sdm_test_suite.xlsx
echo.

echo Running Smoke Tests...
python execute_unified_smoke_tests.py

echo.
echo Running Data Validation Tests...
python execute_enhanced_data_validation_tests.py

echo.
echo Test execution completed.