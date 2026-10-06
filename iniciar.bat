@echo off
title PostulaPro - Generador de CVs ATS y Gestor de Postulaciones
color 0B
echo ===================================================================
echo     Iniciando PostulaPro - Gestor de Postulaciones y CVs ATS
echo     Candidato: Ing. Javier Viveros Huesca
echo     Base de Datos: MariaDB 12.3
echo ===================================================================
echo.

cd /d "%~dp0"

:: Ejecutar la aplicacion
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La aplicacion se cerro con errores.
    echo Presiona cualquier tecla para cerrar esta ventana...
    pause >nul
)
