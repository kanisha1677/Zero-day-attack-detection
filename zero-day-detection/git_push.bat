@echo off
REM Git Push Script for Zero-Day Attack Detection System

echo ======================================================
echo Pushing Zero-Day Attack Detection System to GitHub
echo ======================================================
echo.

REM Check git status
echo Checking git status...
git status

echo.
echo Staging all files...
git add .

echo.
echo Creating commit...
git commit -m "Add Zero-Day Network Attack Detection System - Features: ML detection (IF, AE, RF, XGB), Streamlit dashboard, SHAP explainability, ensemble voting - Components: Feature extraction, anomaly detection, attack classification, real-time visualization - Documentation: README, quickstart, requirements checklist, project summary"

if %errorlevel% equ 0 (
    echo.
    echo Commit created successfully!
    echo.
    echo Pushing to GitHub...
    git push
    
    if %errorlevel% equ 0 (
        echo.
        echo ======================================================
        echo Successfully pushed to GitHub!
        echo ======================================================
        echo.
        echo Your code is now on GitHub!
        echo Check your repository to see the changes
        echo.
        echo Next steps:
        echo 1. View your repo on GitHub
        echo 2. Install dependencies: pip install -r requirements.txt
        echo 3. Train models: python train_models.py
        echo 4. Run dashboard: streamlit run app.py
        echo.
    ) else (
        echo.
        echo Push failed. Error details above.
        echo.
        echo Try manually: git push
        exit /b 1
    )
) else (
    echo.
    echo No changes to commit or commit failed
    echo.
    echo Check 'git status' to see current state
)

echo ======================================================
pause
