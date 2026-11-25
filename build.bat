@echo off
REM Windows, Python 3.10+ (64-bit), internet needed. Result: PhononTranscribe_Package\
REM    PhononTranscribe.exe, _internal\ (libraries), models\ (Phonon-2 weights)

python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt || goto :fail

set COLLECT=
for /f "delims=" %%A in ('python collect_args.py') do set COLLECT=%%A
if not defined COLLECT goto :nopkg
echo Collecting: %COLLECT%

REM Use the logo files if they exist and are not empty
set ICONARGS=
if exist WT.ico for %%F in (WT.ico) do if %%~zF GTR 0 set ICONARGS=--icon WT.ico --add-data "WT.ico;."
if exist WT.png for %%F in (WT.png) do if %%~zF GTR 0 set ICONARGS=%ICONARGS% --add-data "WT.png;."
if not defined ICONARGS echo WARNING: WT.ico / WT.png missing or empty - building without a logo.

echo.
echo === Building exe (this takes a few minutes: torch is large) ===
pyinstaller --noconfirm --onedir --console --name PhononTranscribe %ICONARGS% ^
  --copy-metadata fermion-research %COLLECT% ^
  --collect-all soundfile --collect-data _soundfile_data ^
  --collect-all sounddevice --collect-data _sounddevice_data ^
  --hidden-import safetensors --hidden-import scipy.signal --hidden-import zstandard ^
  app.py || goto :fail

echo.
echo === Downloading Phonon-2 beside the exe (164 MB) ===
python app.py --prepare dist\PhononTranscribe || goto :fail

if exist PhononTranscribe_Package rmdir /s /q PhononTranscribe_Package
xcopy /e /i /y /q dist\PhononTranscribe PhononTranscribe_Package >nul

echo.
echo Done. Copy the whole folder PhononTranscribe_Package to any Windows PC.
echo Run PhononTranscribe.exe inside it and keep the folder together.
pause
exit /b 0

:nopkg
echo Could not find the fermion-research package files.
:fail
echo.
echo BUILD FAILED. Copy the error above and send it to me.
pause
exit /b 1
