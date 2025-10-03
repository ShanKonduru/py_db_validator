@echo off
REM Run tests and generate HTML report
pytest --cov=src --cov-report=html --cov-report=term-missing --html=test_reports\report.html --self-contained-html tests\