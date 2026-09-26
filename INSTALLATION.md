# Stegora - Installation Guide

## Prerequisites
- Python 3.10 or higher
- pip package manager
- Git (for cloning repository)

## Step-by-Step Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd stegora-steganography
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
# Run tests
pytest -v

# Check Python syntax
python -m compileall .
```

## Running the Application

### Option 1: Using helper scripts (Windows)
```bash
run.bat
```

### Option 2: Direct command
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Running Tests

### Option 1: Using helper script (Windows)
```bash
test.bat
```

### Option 2: Direct command
```bash
pytest -v
```

## Troubleshooting

### Issue: Python version error
**Solution:** Ensure Python 3.10+ is installed
```bash
python --version
```

### Issue: Module not found
**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: Port 8501 already in use
**Solution:** Stop other Streamlit instances or use different port
```bash
streamlit run app.py --server.port 8502
```

## Development Setup

### Install development dependencies
```bash
pip install -r requirements.txt
pip install pytest-cov black flake8
```

### Run with coverage
```bash
pytest --cov=stegora --cov-report=html
```

## Environment Variables
Stegora does not require environment variables for basic usage.

## Notes
- Never commit `.venv/` directory
- Never commit test images with sensitive data
- Never commit actual keys or passwords
