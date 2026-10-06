import re
import json
from pathlib import Path
import config
from profile_data import load_user_profile
from pdf_engine import generar_pdf_desde_html

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def extraer_datos_de_imagen_oferta(ruta_imagen: str) -> dict:
    """
    Lee una imagen o captura de pantalla de una oferta laboral utilizando visión multimodal
    de Google Gemini y extrae estructuradamente la empresa, puesto, ubicación y descripción completa.
    """
    if not HAS_PIL:
        raise ImportError("Se requiere la librería Pillow (PIL) para procesar imágenes.")
    if not (HAS_GENAI and config.GEMINI_API_KEY):
        raise ValueError("Se requiere configurar la API Key de Google Gemini para leer texto desde imágenes.")

    try:
        img = Image.open(ruta_imagen)
        client = genai.Client(api_key=config.GEMINI_API_KEY)

        prompt = """
Analiza minuciosamente esta captura de pantalla o imagen de una oferta de empleo o vacante laboral y extrae toda la información técnica.

Responde ÚNICAMENTE un objeto JSON válido con las siguientes claves exactas:
{
  "empresa": "Nombre de la empresa que contrata (o 'Empresa Confidencial' si no se menciona)",
  "titulo_puesto": "Título exacto de la vacante o puesto",
  "ubicacion": "Ciudad / Estado / Modalidad de trabajo",
  "descripcion_completa": "Transcripción clara y detallada de todas las responsabilidades, requisitos técnicos, experiencia solicitada, certificaciones, herramientas y beneficios de la vacante."
}
No incluyas texto antes ni después del JSON.
"""
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[img, prompt]
        )

        texto_limpio = response.text.strip()
        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:]
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio[:-3]

        datos = json.loads(texto_limpio.strip())
        return datos
    except Exception as e:
        raise RuntimeError(f"Error procesando la imagen de la oferta con IA: {str(e)}")

def detectar_idioma(texto: str) -> str:
    """Detecta si el texto está principalmente en inglés o español."""
    texto_l = texto.lower()
    palabras_en = ["responsibilities", "requirements", "experience", "skills", "qualifications", "apply", "engineer", "technician", "must have", "full time", "job description"]
    palabras_es = ["responsabilidades", "requisitos", "experiencia", "conocimientos", "postulación", "ingeniero", "técnico", "disponibilidad", "prestaciones", "vacante"]

    puntos_en = sum(1 for p in palabras_en if p in texto_l)
    puntos_es = sum(1 for p in palabras_es if p in texto_l)

    return "en" if puntos_en > puntos_es else "es"

def detectar_perfil_optimo(texto: str) -> str:
    """Detecta el perfil técnico que mejor se adapta a la oferta pegada."""
    t = texto.lower()
    scores = {
        "automatizacion": 0,
        "electrico": 0,
        "fullstack_ai": 0,
        "telecom_redes": 0,
        "gerente_mantenimiento": 0
    }

    # Automatización
    for kw in ["plc", "allen-bradley", "siemens", "neumática", "pneumatic", "commissioning", "automatiz", "electromec", "loto", "jha", "fsr", "field service", "robot"]:
        if kw in t: scores["automatizacion"] += 2

    # Eléctrico
    for kw in ["electric", "conduit", "emt", "tableros", "subestacion", "media tension", "baja tension", "480v", "trifas", "cadweld", "nom-001", "nec", "nfpa 70e", "electricista"]:
        if kw in t: scores["electrico"] += 2

    # Full-Stack & AI
    for kw in ["python", "react", "typescript", "django", "fastapi", "ai", "ia", "llm", "rag", "desarrollador", "developer", "fullstack", "software", "backend", "frontend", "api", "sql"]:
        if kw in t: scores["fullstack_ai"] += 2

    # Telecomunicaciones & Redes
    for kw in ["fibra", "fiber", "ont", "telecom", "gpon", "otdr", "cisco", "redes", "network", "rf", "radiofrecuencia", "antenna", "spectrum", "cableado"]:
        if kw in t: scores["telecom_redes"] += 2

    # Gerente Mantenimiento
    for kw in ["mantenimiento", "chiller", "hvac", "hotel", "facility", "cuarto de maquinas", "opex", "capex", "gerente", "climatizacion", "albercas"]:
        if kw in t: scores["gerente_mantenimiento"] += 2

    perfil_ganador = max(scores, key=scores.get)
    # Si ningún puntaje superó 1, sugerir automatización o eléctrico por defecto
    if scores[perfil_ganador] == 0:
        return "automatizacion"
    return perfil_ganador

def _generar_con_gemini(datos_oferta: dict, perfil_base: dict, perfil_clave: str, idioma: str) -> dict:
    """Usa la API de Google Gemini para adaptar el CV y el correo de manera ultra personalizada."""
    if not (HAS_GENAI and config.GEMINI_API_KEY):
        return None

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        datos_p = perfil_base["datos_personales"]
        especialidad = perfil_base["perfiles_especializados"].get(perfil_clave, {})

        prompt = f"""
Actúa como un experto en redacción de CVs para contratación técnica internacional (ATS friendly) y reclutamiento de alto nivel.
Adapta el perfil profesional de Javier Viveros Huesca para la siguiente oferta laboral:

--- DATOS DE LA OFERTA ---
Empresa: {datos_oferta.get('empresa', '')}
Puesto: {datos_oferta.get('titulo_puesto', '')}
Ubicación: {datos_oferta.get('ubicacion', '')}
Idioma deseado: {"Inglés" if idioma == 'en' else "Español"}
Descripción de la Oferta:
{datos_oferta.get('descripcion_oferta', '')[:4000]}

--- DATOS REALES DEL CANDIDATO (NO INVENTAR NUEVOS TÍTULOS O LICENCIAS) ---
Nombre: {datos_p['nombre']}
Grados: Título de Ingeniero en Electrónica (Cédula Profesional) | MBA en Gestión Estratégica
Credenciales Clave: Texas TDLR Electrical License #702789 | Certificación OSHA 30 Horas #26-607426714 | Elegibilidad Visa TN (4 años de experiencia en EE. UU.) | Licencia de conducir vigente
Experiencia de referencia: {especialidad.get('nombre', '')}
Resumen base: {especialidad.get('resumen_es', '')}
Habilidades base: {', '.join(especialidad.get('habilidades_clave', []))}

--- INSTRUCCIONES DE SALIDA ---
Genera un objeto JSON EXACTO con las siguientes claves:
{{
  "titulo_objetivo": "Título profesional adaptado al puesto",
  "resumen_adaptado": "Párrafo conciso (4-5 líneas) resaltando las fortalezas del candidato directamente aplicables a la vacante",
  "habilidades_clave": ["Habilidad 1", "Habilidad 2", "Habilidad 3", "Habilidad 4", "Habilidad 5", "Habilidad 6"],
  "logros_experiencia": ["Logro 1 adaptado con métricas y palabras clave ATS", "Logro 2", "Logro 3", "Logro 4"],
  "asunto_correo": "Línea de asunto atractiva para el correo de postulación",
  "cuerpo_correo": "Cuerpo completo del correo de postulación listo para enviar, formal, destacando la disponibilidad, licencias TDLR/OSHA si aplican, y llamada a entrevista"
}}
Responde ÚNICAMENTE el JSON válido, sin bloques ```json adicionales.
"""
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt
        )

        texto_limpio = response.text.strip()
        # Limpiar posibles delimitadores markdown
        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:]
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio[:-3]

        return json.loads(texto_limpio.strip())
    except Exception as e:
        print(f"Aviso: Generación con Gemini no disponible ({e}), usando motor semántico local.")
        return None

def _generar_con_motor_local(datos_oferta: dict, perfil_base: dict, perfil_clave: str, idioma: str) -> dict:
    """Motor de generación local 100% offline y determinista."""
    datos_p = perfil_base["datos_personales"]
    especialidad = perfil_base["perfiles_especializados"].get(perfil_clave, perfil_base["perfiles_especializados"]["automatizacion"])

    titulo_puesto = datos_oferta.get("titulo_puesto", especialidad["nombre"])
    empresa = datos_oferta.get("empresa", "Equipo de Selección")
    ubicacion = datos_oferta.get("ubicacion", "la posición indicada")

    if idioma == "en":
        resumen = especialidad.get("resumen_en", especialidad["resumen_es"])
        titulo_obj = f"{titulo_puesto} | Electronics Engineer (Texas TDLR & OSHA 30)"
        asunto_correo = f"Application: {titulo_puesto} - {ubicacion} | Javier Viveros Huesca (B.S. Electronics Eng | Texas TDLR #702789 & OSHA 30)"
        cuerpo_correo = f"""Dear Hiring Team at {empresa},

I hope this email finds you well. I am writing to formally submit my application for the {titulo_puesto} position at {empresa}.

I hold a Bachelor's Degree in Electronics Engineering and have over 10 years of hands-on technical field experience. Notably, I have 4 years of proven field work experience across the United States under TN Visa status.

Key qualifications aligned with your requirements include:
1. Active Texas TDLR Electrical License (US License #702789).
2. OSHA 30-Hour Construction & Industrial Safety Certification (US #26-607426714).
3. Immediate TN Visa eligibility (Engineer category under USMCA/T-MEC) with valid passport and clean record.
4. Professional English proficiency (C1) and valid driver's license.
5. Direct expertise in: {", ".join(especialidad.get("habilidades_clave", [])[:4])}.

Attached to this email you will find my updated Resume (PDF) tailored to this position.

I would welcome the opportunity to discuss how my technical background and readiness can bring immediate value to {empresa}. Thank you for your time and consideration.

Sincerely,

Javier Viveros Huesca
Electronics Engineer | Technical Specialist
Phone / WhatsApp: {datos_p['telefono']}
Email: {datos_p['email']}
Location: {datos_p['ubicacion']}
Credentials: Texas TDLR #702789 | OSHA 30 #26-607426714 | TN Visa Ready
"""
    else:
        resumen = especialidad.get("resumen_es")
        titulo_obj = f"{titulo_puesto} | Ing. Electrónica (Licencia Texas TDLR & OSHA 30)"
        asunto_correo = f"Postulación: {titulo_puesto} - {empresa} | Javier Viveros Huesca (Ing. Electrónica | Licencia Texas TDLR & OSHA 30)"
        cuerpo_correo = f"""Estimado equipo de Selección y Reclutamiento de {empresa},

Es un gusto saludarlos. Me pongo en contacto con ustedes para presentar mi postulación formal a la vacante de {titulo_puesto}{f' en {ubicacion}' if ubicacion else ''}.

Cuento con formación como Ingeniero en Electrónica (Título y Cédula Profesional), Maestría en Administración de Empresas (MBA) y más de 10 años de experiencia técnica comprobada en campo, con un respaldo de 4 años continuos de trabajo en Estados Unidos bajo estatus de Visa TN.

Aspectos clave de mi perfil que aportan valor inmediato a {empresa}:
1. Licencia Eléctrica de Texas TDLR activa (US License #702789).
2. Certificación oficial OSHA 30 Horas en Seguridad en la Construcción e Industrial (#26-607426714).
3. Elegibilidad inmediata para Visa TN (profesión Ingeniero bajo T-MEC), con pasaporte vigente y récord impecable.
4. Licencia de conducir vigente e inglés técnico avanzado (C1 fluido).
5. Especialización en: {", ".join(especialidad.get("habilidades_clave", [])[:4])}.

Adjunto a este correo encontrarán mi Currículum Vitae en formato PDF descargable y optimizado para este puesto.

Agradezco de antemano su atención y tiempo. Quedo a su entera disposición para coordinar una entrevista y profundizar en cómo mi perfil se alinea con sus metas operativas.

Atentamente,

Ing. Javier Viveros Huesca
Ingeniero en Electrónica | Especialista Técnico
Teléfono / WhatsApp: {datos_p['telefono']}
Correo: {datos_p['email']}
Ubicación: {datos_p['ubicacion']}
Credenciales: Licencia Texas TDLR #702789 | OSHA 30 Horas #26-607426714
"""

    return {
        "titulo_objetivo": titulo_obj,
        "resumen_adaptado": resumen,
        "habilidades_clave": especialidad.get("habilidades_clave", []),
        "logros_experiencia": [
            "Ejecución rigurosa de comisionamiento, diagnóstico de fallas y pruebas funcionales.",
            "Cumplimiento normativo estricto bajo estándares de seguridad LOTO, JHA y OSHA.",
            "Gestión técnica orientada a cero paros no programados y alta confiabilidad de equipo.",
            "Elaboración de reportes técnicos detallados y comunicación directa con clientes y supervisores."
        ],
        "asunto_correo": asunto_correo,
        "cuerpo_correo": cuerpo_correo
    }

def construir_html_cv(datos_cv: dict, perfil_base: dict, idioma: str, opciones: dict = None) -> str:
    """Rellena la plantilla templates/cv_template.html respetando las opciones de visibilidad."""
    template_path = config.TEMPLATES_DIR / "cv_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    p_data = perfil_base["datos_personales"]
    if opciones is None:
        opciones = perfil_base.get("opciones_visibilidad", {})

    # Título Principal: Si usar_titulo_fijo es True, se usa el de datos_personales.
    # Si es False (desmarcado), se usa el nombre del puesto/perfil de la postulación.
    if opciones.get("usar_titulo_fijo", False):
        titulo_final = p_data.get("titulo_principal", "Especialista Técnico")
    else:
        titulo_final = datos_cv.get("titulo_objetivo", p_data.get("titulo_principal", "Especialista Técnico"))

    # Resumen Profesional: Si usar_resumen_fijo es True, se muestra literalmente lo escrito ahí.
    # Si es False (desmarcado), se genera y adapta acorde al perfil y la oferta.
    if opciones.get("usar_resumen_fijo", True):
        resumen_final = perfil_base.get("resumen_base_fijo") or datos_cv.get("resumen_adaptado", "")
    else:
        resumen_final = datos_cv.get("resumen_adaptado", "")

    # Ubicación: Si mostrar_ubicacion es True, se muestra. Si es False, se omite.
    if opciones.get("mostrar_ubicacion", True) and p_data.get("ubicacion"):
        ubicacion_item = f'<div class="contact-item"><strong>📍 Ubicación:</strong> {p_data["ubicacion"]}</div>'
    else:
        ubicacion_item = ""

    # GitHub: Si mostrar_github es True, se muestra. Si es False, se omite.
    if opciones.get("mostrar_github", True) and p_data.get("github"):
        github_item = f'<div class="contact-item"><strong>🌐 GitHub:</strong> {p_data["github"]}</div>'
    else:
        github_item = ""

    # Badges y Disponibilidad
    badges_items = []
    if opciones.get("mostrar_licencias", True):
        badges_items.append("Texas TDLR Electrical License (#702789)")
        badges_items.append("OSHA 30-Hour Safety (#26-607426714)")
    badges_items.append("B.S. Electronics Engineer")

    # Disponibilidad: Si mostrar_disponibilidad es True, se muestra en los badges. Si es False, se omite.
    if opciones.get("mostrar_disponibilidad", True) and p_data.get("disponibilidad"):
        badges_items.append("TN Visa Eligible" if idioma == "en" else "Elegible Visa TN")
    badges_items.append("Bilingual (C1)" if idioma == "en" else "Bilingüe (C1)")

    if badges_items:
        badges_str = " &bull; ".join(badges_items)
        badges_bar = f'<div class="badges-bar"><strong>Credenciales Clave:</strong> {badges_str}</div>'
    else:
        badges_bar = ""

    # Sección Licencias y Certificaciones: Si mostrar_licencias es True, se incluye.
    # Si es False (desmarcado), se omite por completo del CV PDF.
    if opciones.get("mostrar_licencias", True) and perfil_base.get("credenciales_clave"):
        cred_items = [f"<li>{cred}</li>" for cred in perfil_base.get("credenciales_clave", [])]
        seccion_licencias = f"""
<div class="section-title">Certificaciones & Licencias Profesionales</div>
<ul class="credentials-list">
    {''.join(cred_items)}
</ul>
"""
    else:
        seccion_licencias = ""

    # Habilidades técnicas
    habilidades_html = "".join([f'<div class="skill-item">{h}</div>' for h in datos_cv.get("habilidades_clave", [])])

    # Experiencia profesional
    logros_list = "".join([f'<li>{l}</li>' for l in datos_cv.get("logros_experiencia", [])])
    experiencia_html = f"""
    <div class="job-block">
        <div class="job-header">
            <div>
                <span class="job-title">{titulo_final}</span> &bull; 
                <span class="job-company">Experiencia en Campo & Proyectos Industriales</span>
            </div>
            <div class="job-meta">2018 - Presente | México & EE. UU.</div>
        </div>
        <ul class="bullet-list">
            {logros_list}
        </ul>
    </div>
    """

    # Educación
    edu_items = []
    for edu in perfil_base.get("educacion", []):
        edu_items.append(f"""
        <div class="edu-block">
            <div><span class="edu-degree">{edu['grado']}</span> - <span class="edu-school">{edu['institucion']} ({edu['especialidad']})</span></div>
            <div class="edu-period">{edu['periodo']}</div>
        </div>
        """)
    educacion_html = "".join(edu_items)

    # Reemplazar variables
    reemplazos = {
        "{{LANG}}": idioma,
        "{{NOMBRE}}": p_data["nombre"],
        "{{TITULO}}": titulo_final,
        "{{TELEFONO}}": p_data["telefono"],
        "{{EMAIL}}": p_data["email"],
        "{{UBICACION_ITEM}}": ubicacion_item,
        "{{GITHUB_ITEM}}": github_item,
        "{{BADGES_BAR}}": badges_bar,
        "{{RESUMEN}}": resumen_final,
        "{{HABILIDADES_HTML}}": habilidades_html,
        "{{EXPERIENCIA_HTML}}": experiencia_html,
        "{{EDUCACION_HTML}}": educacion_html,
        "{{SECCION_LICENCIAS}}": seccion_licencias
    }

    for k, v in reemplazos.items():
        html = html.replace(k, str(v))

    return html

def procesar_postulacion_completa(datos_oferta: dict, usar_ia: bool = True) -> dict:
    """
    Función principal que:
    1. Analiza y detecta idioma y perfil óptimo.
    2. Adapta el CV y redacta el correo con Gemini o motor local.
    3. Construye el HTML final ATS respetando las opciones de visibilidad.
    4. Compila el PDF descargable mediante Edge Headless.
    5. Retorna toda la información lista para visualizar y guardar en MariaDB.
    """
    perfil_base = load_user_profile()
    desc_oferta = datos_oferta.get("descripcion_oferta", "")

    # Opciones de visibilidad combinadas
    opciones = dict(perfil_base.get("opciones_visibilidad", {}))
    if "opciones_visibilidad" in datos_oferta and datos_oferta["opciones_visibilidad"]:
        opciones.update(datos_oferta["opciones_visibilidad"])

    # Idioma
    idioma = datos_oferta.get("idioma", "auto")
    if idioma == "auto" or not idioma:
        idioma = detectar_idioma(desc_oferta)

    # Perfil técnico
    perfil_clave = datos_oferta.get("perfil_aplicado", "auto")
    if perfil_clave == "auto" or not perfil_clave:
        perfil_clave = detectar_perfil_optimo(desc_oferta)

    # Generación de contenidos (con Gemini o fallback local)
    resultado_ia = None
    if usar_ia:
        resultado_ia = _generar_con_gemini(datos_oferta, perfil_base, perfil_clave, idioma)

    if not resultado_ia:
        resultado_ia = _generar_con_motor_local(datos_oferta, perfil_base, perfil_clave, idioma)

    # Generar HTML con opciones
    html_content = construir_html_cv(resultado_ia, perfil_base, idioma, opciones=opciones)

    # Generar PDF
    empresa_limpia = re.sub(r'[^a-zA-Z0-9]', '_', datos_oferta.get("empresa", "Empresa")).strip('_')
    puesto_limpio = re.sub(r'[^a-zA-Z0-9]', '_', datos_oferta.get("titulo_puesto", "Puesto")).strip('_')
    nombre_archivo = f"CV_Javier_Viveros_{empresa_limpia}_{puesto_limpio}"

    pdf_path = generar_pdf_desde_html(html_content, nombre_archivo)

    return {
        "empresa": datos_oferta.get("empresa", "Empresa no especificada"),
        "titulo_puesto": datos_oferta.get("titulo_puesto", "Puesto no especificado"),
        "ubicacion": datos_oferta.get("ubicacion", ""),
        "url_oferta": datos_oferta.get("url_oferta", ""),
        "descripcion_oferta": desc_oferta,
        "perfil_aplicado": perfil_clave,
        "idioma": idioma,
        "asunto_correo": resultado_ia.get("asunto_correo", ""),
        "cuerpo_correo": resultado_ia.get("cuerpo_correo", ""),
        "ruta_pdf": pdf_path,
        "html_content": html_content
    }
