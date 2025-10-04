# ============================================================
# COMPREHENSIVE TEST SUITE RUNNER - POWERSHELL SCRIPT
# ============================================================
# This script runs all enabled tests from the unified Excel workbook
# Usage: .\run_all_tests.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE TEST SUITE RUNNER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting comprehensive test execution..." -ForegroundColor Green
Write-Host "Excel File: enhanced_unified_sdm_test_suite.xlsx" -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the Excel file exists
if (-not (Test-Path "enhanced_unified_sdm_test_suite.xlsx")) {
    Write-Host "ERROR: enhanced_unified_sdm_test_suite.xlsx not found" -ForegroundColor Red
    Write-Host "Please ensure the Excel file is in the current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the test runner exists
if (-not (Test-Path "run_all_enabled_tests.py")) {
    Write-Host "ERROR: run_all_enabled_tests.py not found" -ForegroundColor Red
    Write-Host "Please ensure the test runner script is in the current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the comprehensive test suite
Write-Host "Running comprehensive test suite..." -ForegroundColor Green
Write-Host ""

try {
    # Execute the Python script and capture the exit code
    python run_all_enabled_tests.py enhanced_unified_sdm_test_suite.xlsx
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "TEST EXECUTION COMPLETED SUCCESSFULLY" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "All enabled tests passed successfully." -ForegroundColor Green
    } else {
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host "TEST EXECUTION COMPLETED WITH ISSUES" -ForegroundColor Yellow
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host "Some tests may have failed or been skipped." -ForegroundColor Yellow
        Write-Host "Review the detailed output above for more information." -ForegroundColor Yellow
        Write-Host "Exit code: $exitCode" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to execute test suite" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Write-Host "Test execution finished." -ForegroundColor Cyan
Read-Host "Press Enter to exit"
exit $exitCode