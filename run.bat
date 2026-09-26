@echo off
REM Stegora - Run script for Windows
echo Starting Stegora...
call .venv\Scripts\activate
streamlit run app.py
