@echo off
echo Activating TRINETRA AI virtual environment...
call trinetra_env\Scripts\activate.bat
echo Virtual environment activated!
echo Python version:
python --version
echo Pip version:
pip --version
echo.
echo Ready to install packages with: pip install -r requirements.txt
echo Ready to run the application with: python main.py