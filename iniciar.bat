@echo off
setlocal EnableExtensions
title DesignMatch - Iniciar
cd /d "%~dp0"
cls

echo ==================================================
echo               DesignMatch
echo        Inicio automatico del sistema
echo ==================================================
echo.
echo Este proceso puede tardar unos minutos la primera vez.
echo No cierre esta ventana mientras el sistema este abierto.
echo.

set "PYTHON_CMD="

echo [1/5] Buscando Python...
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo.
    echo ERROR: No se encontro Python en este computador.
    echo Instale Python 3.11 o superior desde https://www.python.org/downloads/windows/
    echo Durante la instalacion marque la opcion "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo Python detectado: %PYTHON_VERSION%

echo.
echo [2/5] Preparando entorno...
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual por primera vez...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: No fue posible crear el entorno virtual.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Entorno virtual encontrado.
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

echo.
echo [3/5] Verificando pip...
"%VENV_PYTHON%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no esta disponible en el entorno virtual.
    pause
    exit /b 1
)

echo.
echo [4/5] Instalando o actualizando dependencias...
if not exist "requirements.txt" (
    echo ERROR: No se encontro el archivo requirements.txt
    pause
    exit /b 1
)

"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Fallo la instalacion de dependencias.
    echo Revise su conexion a internet e intente de nuevo.
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Iniciando DesignMatch...
echo.
echo En unos segundos se abrira el navegador.
echo Si no se abre solo, copie esta direccion:
echo http://localhost:5000
echo.
echo Para cerrar el sistema, vuelva a esta ventana y presione CTRL+C.
echo.

start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 5; Start-Process 'http://localhost:5000'"
"%VENV_PYTHON%" app.py

echo.
echo DesignMatch se ha detenido.
pause
