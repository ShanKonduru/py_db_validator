@echo off
REM Run tests and generate HTML report
pytest --html=test_reports\report.html --self-contained-html tests\