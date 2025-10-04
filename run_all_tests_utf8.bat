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

python run_all_enabled_tests.py

echo.
echo Press any key to exit...
pause > nul