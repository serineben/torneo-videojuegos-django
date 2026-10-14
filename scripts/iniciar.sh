#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || {
    echo "Error: no se pudo localizar la carpeta del script." >&2
    exit 1
}
cd "$SCRIPT_DIR/.." || {
    echo "Error: no se pudo acceder a la carpeta del proyecto." >&2
    exit 1
}

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python no está instalado o no se encuentra en PATH." >&2
    echo "Instala Python y vuelve a ejecutar este script." >&2
    exit 1
fi

if [ ! -x "venv/bin/python" ]; then
    echo "Creando el entorno virtual..."
    if ! "$PYTHON" -m venv venv; then
        echo "Error: no se pudo crear el entorno virtual." >&2
        exit 1
    fi
fi

echo "Activando el entorno virtual..."
if ! source venv/bin/activate; then
    echo "Error: no se pudo activar el entorno virtual." >&2
    exit 1
fi

echo "Instalando dependencias..."
if ! python -m pip install -r requirements.txt; then
    echo "Error: falló la instalación de dependencias." >&2
    exit 1
fi

if [ ! -f ".env" ]; then
    if [ ! -f ".env.example" ]; then
        echo "Error: no existe .env.example para crear la configuración .env." >&2
        exit 1
    fi
    if ! cp ".env.example" ".env"; then
        echo "Error: no se pudo crear el archivo .env." >&2
        exit 1
    fi
    echo "Se ha creado .env desde .env.example."
    echo "Aviso: cambia SECRET_KEY en .env antes de usar el proyecto."
fi

echo "Aplicando migraciones de la base de datos..."
if ! python manage.py migrate; then
    echo "Error: falló la aplicación de migraciones." >&2
    exit 1
fi

URL="http://127.0.0.1:8000"
echo "Abriendo $URL en el navegador..."
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 &
elif grep -qi microsoft /proc/version 2>/dev/null && command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start "" "$URL" >/dev/null 2>&1 &
else
    echo "Aviso: abre $URL manualmente en el navegador."
fi

echo "Iniciando el servidor. Pulsa Ctrl+C para detenerlo."
exec python manage.py runserver
