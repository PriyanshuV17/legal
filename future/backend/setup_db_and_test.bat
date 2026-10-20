@echo off
REM Setup Database and Initialize with Lawyer Data

cd /d D:\legal\backend

echo.
echo ================================================================
echo LEGAL SYSTEM - COMPLETE SETUP
echo ================================================================

echo.
echo Step 1: Activating conda environment...
call conda activate verma

echo.
echo Step 2: Running database initialization...
python setup_database.py

echo.
echo Step 3: Database setup complete!
echo.
echo ================================================================
echo Next steps:
echo 1. Open another terminal
echo 2. Run: conda activate verma
echo 3. Run: python main.py
echo 4. Open another terminal for Streamlit UI
echo ================================================================

pause
