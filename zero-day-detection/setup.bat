@echo off
REM Setup script for Zero-Day Network Attack Detection System (Windows)

echo ================================================
echo Zero-Day Network Attack Detection System Setup
echo ================================================
echo.

REM Create necessary directories
echo Creating directories...
if not exist "models" mkdir models
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo Directories created
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM Train models
echo Training machine learning models...
echo This may take a few minutes...
python train_models.py

if %errorlevel% neq 0 (
    echo Model training failed
    exit /b 1
)

echo Models trained successfully
echo.

echo ================================================
echo Setup complete!
echo.
echo To start the dashboard, run:
echo    streamlit run app.py
echo.
echo The dashboard will be available at:
echo    http://localhost:8501
echo ================================================
pause
