import os
import subprocess
import time
import shutil
from pathlib import Path
import config

def generar_pdf_desde_html(html_content: str, nombre_base: str) -> str:
    """
    Guarda el contenido HTML temporalmente y lo compila a PDF utilizando
    Microsoft Edge en modo headless (renderizado nativo de alta calidad ATS).
    Retorna la ruta absoluta del PDF generado.
    """
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Limpiar nombre de archivo para evitar caracteres inválidos
    nombre_seguro = "".join(c for c in nombre_base if c.isalnum() or c in (" ", "_", "-")).rstrip()
    nombre_seguro = nombre_seguro.replace(" ", "_")
    if not nombre_seguro:
        nombre_seguro = f"CV_Javier_Viveros_{int(time.time())}"

    html_path = config.OUTPUT_DIR / f"{nombre_seguro}.html"
    pdf_path = config.OUTPUT_DIR / f"{nombre_seguro}.pdf"

    # Guardar HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_abs = str(html_path.resolve())
    pdf_abs = str(pdf_path.resolve())

    # Ejecutar Microsoft Edge para compilar a PDF
    edge_exe = config.EDGE_PATH
    if not os.path.exists(edge_exe):
        # Buscar en rutas comunes si no está configurado
        for alt in [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]:
            if os.path.exists(alt):
                edge_exe = alt
                break

    if not os.path.exists(edge_exe):
        raise FileNotFoundError(f"No se encontró el ejecutable de Microsoft Edge en: {config.EDGE_PATH}")

    file_uri = f"file:///{html_abs.replace(os.sep, '/')}"

    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_abs}",
        file_uri
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Esperar hasta que el archivo PDF esté completamente escrito
    for _ in range(12):
        if os.path.exists(pdf_abs) and os.path.getsize(pdf_abs) > 0:
            return pdf_abs
        time.sleep(0.4)

    if os.path.exists(pdf_abs) and os.path.getsize(pdf_abs) > 0:
        return pdf_abs

    raise RuntimeError(f"No se pudo generar el archivo PDF en {pdf_abs}")

def abrir_pdf_en_sistema(pdf_path: str):
    """Abre el archivo PDF en el visor predeterminado del sistema operativo Windows."""
    if pdf_path and os.path.exists(pdf_path):
        os.startfile(pdf_path)
        return True
    return False

def descargar_pdf_a_ruta(pdf_path_origen: str, ruta_destino: str):
    """Copia el PDF generado a la ubicación seleccionada por el usuario (ej. Escritorio, Descargas)."""
    if pdf_path_origen and os.path.exists(pdf_path_origen):
        shutil.copy2(pdf_path_origen, ruta_destino)
        return True
    return False
