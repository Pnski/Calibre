@echo off
setlocal

echo ==========================
echo Creating virtual environment
echo ==========================

if not exist ".venv" (
    pymanager exec -3.14 -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo.
echo ==========================
echo Upgrading pip
echo ==========================

".venv\Scripts\python.exe" -m pip install --upgrade pip

echo.
echo ==========================
echo Installing requirements
echo ==========================

".venv\Scripts\python.exe" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo ==========================
echo Starting application
echo ==========================

".venv\Scripts\python.exe" start.py -op -v

popd
pause