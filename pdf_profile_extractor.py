import os
import re
import json
import shutil
from pathlib import Path
import pypdf

import config

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

CARPETA_CV_BASE = config.BASE_DIR / "uploads" / "cv_base"

def guardar_copia_cv_base(ruta_pdf_origen: str) -> str:
    CARPETA_CV_BASE.mkdir(parents=True, exist_ok=True)
    nombre_archivo = os.path.basename(ruta_pdf_origen)
    nombre_seguro = "".join(c for c in nombre_archivo if c.isalnum() or c in (" ", "_", "-", ".")).strip()
    if not nombre_seguro.lower().endswith(".pdf"):
        nombre_seguro += ".pdf"

    ruta_destino = CARPETA_CV_BASE / nombre_seguro
    shutil.copy2(ruta_pdf_origen, ruta_destino)
    return str(ruta_destino.resolve())

def extraer_texto_de_pdf(ruta_pdf: str) -> str:
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo PDF en: {ruta_pdf}")

    texto_total = []
    try:
        reader = pypdf.PdfReader(ruta_pdf)
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            texto_total.append(f"--- PÁGINA {idx + 1} ---\n{txt}")
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo PDF con pypdf: {str(e)}")

    return "\n\n".join(texto_total).strip()

def estructurar_perfil_con_ia(texto_pdf: str, ruta_pdf: str = None) -> dict:
    if HAS_GENAI and config.GEMINI_API_KEY:
        try:
            return _analizar_con_gemini(texto_pdf, ruta_pdf)
        except Exception as e:
            print(f"[ADVERTENCIA] Falló análisis con Gemini ({e}). Usando parser local de respaldo.")

    return analizar_perfil_local(texto_pdf)

def _analizar_con_gemini(texto_pdf: str, ruta_pdf: str = None) -> dict:
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    prompt = '''
Eres un especialista en Recursos Humanos y Reclutamiento Técnico Internacional.
A continuación se proporciona el texto extraído de un Currículum Vitae (CV) profesional en PDF.
Analiza detenidamente toda la información y extrae estructuradamente el perfil profesional del candidato.

Debes responder ÚNICAMENTE con un objeto JSON válido (sin comentarios ni texto introductorio) con las siguientes claves exactas:
{
  "datos_personales": {
    "nombre": "Nombre completo del candidato",
    "titulo_principal": "Título profesional principal del candidato",
    "telefono": "Teléfono o celular de contacto",
    "email": "Correo electrónico",
    "ubicacion": "Ciudad, Estado, País",
    "linkedin": "Enlace o usuario de LinkedIn",
    "github": "Enlace o usuario de GitHub (si existe en el CV)",
    "idiomas": "Idiomas y niveles especificados",
    "disponibilidad": "Disponibilidad especificada, estatus de visa (ej. Visa TN) o disponibilidad de viaje/reubicación"
  },
  "resumen_base_fijo": "Resumen profesional o perfil ejecutivo completo redactado en un párrafo sólido destacando años de experiencia y especialidad",
  "credenciales_clave": [
    "Licencia, certificación, título o acreditación relevante 1",
    "Licencia, certificación, título o acreditación relevante 2"
  ],
  "educacion": [
    {
      "grado": "Nombre del título o grado",
      "especialidad": "Área de estudio o especialidad",
      "institucion": "Universidad o Instituto",
      "periodo": "Años o periodo"
    }
  ],
  "habilidades_clave": [
    "Habilidad técnica 1",
    "Habilidad técnica 2",
    "Habilidad técnica 3"
  ]
}

TEXTO EXTRAÍDO DEL CV EN PDF:
''' + texto_pdf[:8000]

    contents = []
    if len(texto_pdf.strip()) < 80 and ruta_pdf and os.path.exists(ruta_pdf):
        with open(ruta_pdf, "rb") as f:
            pdf_bytes = f.read()
        contents.append(types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))
        contents.append(prompt)
    else:
        contents.append(prompt)

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=contents
    )

    texto_resp = response.text.strip()
    if texto_resp.startswith("`json"):
        texto_resp = texto_resp[7:]
    if texto_resp.startswith("`"):
        texto_resp = texto_resp[3:]
    if texto_resp.endswith("`"):
        texto_resp = texto_resp[:-3]

    datos = json.loads(texto_resp.strip())
    return datos

def analizar_perfil_local(texto: str) -> dict:
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
    email = email_match.group(0) if email_match else ""

    tel_match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}', texto)
    telefono = tel_match.group(0) if tel_match else ""

    gh_match = re.search(r'github\.com/[\w\d-]+', texto, re.IGNORECASE)
    github = f"https://{gh_match.group(0)}" if gh_match else ""

    li_match = re.search(r'linkedin\.com/in/[\w\d-]+', texto, re.IGNORECASE)
    linkedin = f"https://{li_match.group(0)}" if li_match else ""

    credenciales = []
    for line in texto.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        if "linkedin.com" in line_clean.lower() or "github.com" in line_clean.lower():
            continue
        if any(term in line_clean.lower() for term in ["tdlr", "osha", "licencia", "license", "certific", "cédula", "visa"]):
            if len(line_clean) < 130 and line_clean not in credenciales:
                credenciales.append(line_clean)

    lineas_no_vacias = [l.strip() for l in texto.splitlines() if l.strip() and not l.startswith("---")]
    nombre = lineas_no_vacias[0] if lineas_no_vacias else "Candidato"
    titulo = lineas_no_vacias[1] if len(lineas_no_vacias) > 1 else "Profesional Técnico"

    return {
        "datos_personales": {
            "nombre": nombre,
            "titulo_principal": titulo,
            "telefono": telefono,
            "email": email,
            "ubicacion": "México / EE. UU.",
            "linkedin": linkedin,
            "github": github,
            "idiomas": "Español | Inglés",
            "disponibilidad": "Disponibilidad Inmediata / Elegible Visa TN"
        },
        "resumen_base_fijo": texto[:500].strip(),
        "credenciales_clave": credenciales[:8],
        "educacion": [],
        "habilidades_clave": []
    }
