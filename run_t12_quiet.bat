@echo off
REM Run T12 tests without verbose mode (to avoid Windows hang issue)
echo ========================================
echo T12 Core Round-Trip Tests
echo Running without -v flag to avoid hang
echo ========================================
.venv\Scripts\python.exe -m pytest tests/test_core_roundtrip.py -q --tb=short
pause
