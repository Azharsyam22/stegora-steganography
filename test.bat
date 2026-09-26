@echo off
REM Stegora - Test script for Windows
echo Running tests...
call .venv\Scripts\activate
pytest -v
