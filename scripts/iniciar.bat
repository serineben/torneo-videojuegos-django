@echo off
setlocal
chcp 65001 >nul

pushd "%~dp0.." || (
    echo Error: no se pudo acceder a la carpeta del proyecto.
    pause
    exit /b 1
)

set "PYTHON="
where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON=py -3"
)

if not defined PYTHON (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version >nul 2>&1
        if not errorlevel 1 set "PYTHON=python"
    )
)

if not defined PYTHON (
    echo Error: Python no esta instalado o no se encuentra en PATH.
    echo Instala Python y vuelve a ejecutar este archivo.
    goto error
)

if not exist "venv\Scripts\python.exe" (
    echo Creando el entorno virtual...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo Error: no se pudo crear el entorno virtual.
        goto error
    )
)

echo Activando el entorno virtual...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: no se pudo activar el entorno virtual.
    goto error
)

echo Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: fallo la instalacion de dependencias.
    goto error
)

if not exist ".env" (
    if not exist ".env.example" (
        echo Error: no existe .env.example para crear la configuracion .env.
        goto error
    )
    copy ".env.example" ".env" >nul
    if errorlevel 1 (
        echo Error: no se pudo crear el archivo .env.
        goto error
    )
    echo Se ha creado .env desde .env.example.
    echo Aviso: cambia SECRET_KEY en .env antes de usar el proyecto.
)

echo Aplicando migraciones de la base de datos...
python manage.py migrate
if errorlevel 1 (
    echo Error: fallo la aplicacion de migraciones.
    goto error
)

echo Abriendo http://127.0.0.1:8000 en el navegador...
start "" "http://127.0.0.1:8000"
if errorlevel 1 echo Aviso: no se pudo abrir el navegador automaticamente.

echo Iniciando el servidor. Pulsa Ctrl+C para detenerlo.
python manage.py runserver
set "SERVER_EXIT=%ERRORLEVEL%"
popd
exit /b %SERVER_EXIT%

:error
popd
pause
exit /b 1
