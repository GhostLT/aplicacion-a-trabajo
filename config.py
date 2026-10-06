import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Cargar variables de entorno
load_dotenv(dotenv_path=ENV_PATH)

# Configuración de Base de Datos MariaDB
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "postulaciones_db")

# Configuración de Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Rutas de carpetas
OUTPUT_DIR = BASE_DIR / "output_pdfs"
TEMPLATES_DIR = BASE_DIR / "templates"
PROFILE_DATA_FILE = BASE_DIR / "user_profile.json"

# Ruta para Microsoft Edge
DEFAULT_EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(DEFAULT_EDGE_PATH):
    alt_edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(alt_edge):
        DEFAULT_EDGE_PATH = alt_edge

EDGE_PATH = os.getenv("EDGE_PATH", DEFAULT_EDGE_PATH)

# Asegurar directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

def reload_config():
    """Recarga las variables desde el archivo .env."""
    global DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, GEMINI_API_KEY, GEMINI_MODEL, EDGE_PATH
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "postulaciones_db")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EDGE_PATH = os.getenv("EDGE_PATH", DEFAULT_EDGE_PATH)

def update_env_variable(key: str, value: str):
    """Actualiza o agrega una clave en el archivo .env."""
    lines = []
    found = False
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    reload_config()
