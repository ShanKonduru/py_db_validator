@echo off
REM Run tests with code coverage and generate HTML report
pytest --cov=src --cov-report=html --cov-report=term-missing tests\