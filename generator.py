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

HABILIDADES_EN = {
    "automatizacion": [
        "Automated assembly lines commissioning and startup",
        "Industrial pneumatics (solenoid valves, cylinders, FRL units, manifolds)",
        "Expert reading of electrical and pneumatic schematic diagrams (P&ID)",
        "Diagnostics with Fluke multimeter, clamp meter, and point-to-point loop testing",
        "LOTO safety procedures (Lockout/Tagout), JHA, and OSHA / NFPA 70E compliance",
        "Field Service Reports (FSR) preparation and technical client consultation"
    ],
    "electrico": [
        "Medium & Low Voltage electrical installations (24VDC, 120V, 277V, 480V 3-Phase)",
        "Conduit bending and routing (EMT, Rigid, PVC-coated) per NEC standards",
        "Distribution panelboards, switchgear, transformers, and motor control centers (MCC)",
        "Grounding systems, bonding, and Cadweld exothermic welding",
        "Substation maintenance, cable tray assembly, and megohmmeter insulation testing",
        "Strict adherence to NFPA 70E, OSHA 30, and Texas TDLR Electrical Code"
    ],
    "fullstack_ai": [
        "Full-Stack Python, TypeScript, React, and Django / FastAPI architecture",
        "RESTful APIs, microservices, and MariaDB / PostgreSQL database design",
        "Applied Artificial Intelligence (Gemini API, LLMs, RAG, automated pipelines)",
        "DevOps, Docker containers, Kubernetes, CI/CD pipelines, and Linux administration",
        "Cloud Infrastructure (AWS, Google Cloud Platform, Azure)",
        "Version control (Git / GitHub) and agile software development methodologies"
    ],
    "telecom_redes": [
        "Fiber optic splicing, testing, and troubleshooting (OTDR, Optical Power Meter)",
        "FTTx / GPON architectures, Optical Network Terminals (ONT), and OLT integration",
        "Radio Frequency (RF) optimization, antenna alignment, and spectrum analysis",
        "5G / LTE mobile network access (C-RAN, Wireless Access, Network Slicing)",
        "Cisco routing & switching, VLANs, TCP/IP protocols, and network monitoring",
        "Telecom tower and rooftop safety (DC3 / Working at Heights certified)"
    ],
    "gerente_mantenimiento": [
        "Comprehensive facility management and preventive/corrective maintenance plans",
        "Industrial HVAC systems, chillers, cooling towers, and mechanical rooms",
        "Operational Budgeting (OPEX / CAPEX) and vendor/contractor management",
        "Key Performance Indicators (KPIs), MTTR, MTBF, and maintenance software (CMMS)",
        "Compliance with local safety regulations, fire protection, and environmental audits",
        "Leadership of multi-disciplinary technical teams and crisis management"
    ]
}

LOGROS_EN = [
    "Rigorous execution of commissioning, systematic diagnostics, and functional testing on industrial equipment.",
    "Strict regulatory compliance adhering to LOTO safety protocols, daily JHA risk assessments, and OSHA standards.",
    "Technical management focused on zero unscheduled downtime, root-cause troubleshooting, and high equipment reliability.",
    "Preparation of comprehensive Field Service Reports (FSR) and direct technical consultation with clients and engineering supervisors."
]

def _generar_con_gemini(datos_oferta: dict, perfil_base: dict, perfil_clave: str, idioma: str) -> dict:
    """Usa la API de Google Gemini para adaptar el CV y el correo de manera ultra personalizada."""
    if not (HAS_GENAI and config.GEMINI_API_KEY):
        return None

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        datos_p = perfil_base["datos_personales"]
        especialidad = perfil_base["perfiles_especializados"].get(perfil_clave, {})
        credenciales_str = " | ".join(perfil_base.get("credenciales_clave", []))
        resumen_base_cand = perfil_base.get("resumen_base_fijo") or especialidad.get("resumen_es", "")
        texto_cv_pdf = perfil_base.get("texto_cv_base_extraido", "")
        bloque_cv_pdf = f"\n--- INFORMACIÓN ÍNTEGRA EXTRAÍDA DEL CV BASE EN PDF DEL CANDIDATO ---\n{texto_cv_pdf[:4000]}\n" if texto_cv_pdf else ""

        is_en = (idioma == "en")
        instruccion_idioma = f"""
*** EXIGENCIA ESTRICTA DE IDIOMA ***
El idioma seleccionado para este documento es: {"INGLÉS (ENGLISH)" if is_en else "ESPAÑOL"}.
{"Todo el contenido generado en el JSON (titulo_objetivo, resumen_adaptado, habilidades_clave, logros_experiencia, asunto_correo, cuerpo_correo) DEBE ESTAR 100% EN INGLÉS PROFESIONAL FLUIDO (US STANDARD). No mezcles palabras en español." if is_en else "Todo el contenido generado en el JSON DEBE ESTAR 100% EN ESPAÑOL PROFESIONAL FORMAL."}
"""

        prompt = f"""
Actúa como un experto en redacción de CVs para contratación técnica internacional (ATS friendly) y reclutamiento de alto nivel.
Adapta el perfil profesional del candidato para la siguiente oferta laboral:

--- DATOS DE LA OFERTA ---
Empresa: {datos_oferta.get('empresa', '')}
Puesto: {datos_oferta.get('titulo_puesto', '')}
Ubicación: {datos_oferta.get('ubicacion', '')}
Idioma deseado: {"Inglés (US Standard)" if is_en else "Español"}
Descripción de la Oferta:
{datos_oferta.get('descripcion_oferta', '')[:4000]}

--- DATOS REALES DEL CANDIDATO (TOMADOS DE SU PERFIL Y CV BASE EN PDF) ---
Nombre: {datos_p.get('nombre', 'Javier Viveros Huesca')}
Título Base: {datos_p.get('titulo_principal', '')}
Credenciales y Licencias Clave: {credenciales_str}
Resumen profesional base: {resumen_base_cand}
Habilidades base: {', '.join(especialidad.get('habilidades_clave', []))}
{bloque_cv_pdf}

{instruccion_idioma}

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
    """Motor de generación local 100% offline y determinista con soporte íntegro para inglés y español."""
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
5. Direct expertise in: {", ".join(HABILIDADES_EN.get(perfil_clave, HABILIDADES_EN["automatizacion"])[:4])}.

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
        habilidades_finales = HABILIDADES_EN.get(perfil_clave, HABILIDADES_EN["automatizacion"])
        logros_finales = LOGROS_EN
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
        habilidades_finales = especialidad.get("habilidades_clave", [])
        logros_finales = [
            "Ejecución rigurosa de comisionamiento, diagnóstico de fallas y pruebas funcionales.",
            "Cumplimiento normativo estricto bajo estándares de seguridad LOTO, JHA y OSHA.",
            "Gestión técnica orientada a cero paros no programados y alta confiabilidad de equipo.",
            "Elaboración de reportes técnicos detallados y comunicación directa con clientes y supervisores."
        ]

    return {
        "titulo_objetivo": titulo_obj,
        "resumen_adaptado": resumen,
        "habilidades_clave": habilidades_finales,
        "logros_experiencia": logros_finales,
        "asunto_correo": asunto_correo,
        "cuerpo_correo": cuerpo_correo
    }

def construir_html_cv(datos_cv: dict, perfil_base: dict, idioma: str, opciones: dict = None) -> str:
    """Rellena la plantilla templates/cv_template.html respetando las opciones de visibilidad e idioma (100% EN o 100% ES)."""
    template_path = config.TEMPLATES_DIR / "cv_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    p_data = perfil_base["datos_personales"]
    if opciones is None:
        opciones = perfil_base.get("opciones_visibilidad", {})

    is_en = (idioma == "en")

    # Etiquetas de encabezados según idioma
    label_tel = "📞 Phone" if is_en else "📞 Tel"
    label_email = "✉️ Email" if is_en else "✉️ Correo"
    titulo_resumen = "Professional Summary" if is_en else "Perfil Profesional"
    titulo_habilidades = "Core Technical Skills & Key Competencies" if is_en else "Habilidades & Competencias Técnicas Clave"
    titulo_experiencia = "Relevant Professional Experience" if is_en else "Experiencia Profesional Relevante"
    titulo_educacion = "Education & Academic Background" if is_en else "Educación & Formación Académica"
    titulo_licencias = "Professional Certifications & Licenses" if is_en else "Certificaciones & Licencias Profesionales"

    # Título Principal
    if opciones.get("usar_titulo_fijo", False):
        titulo_final = p_data.get("titulo_principal", "Especialista Técnico")
    else:
        titulo_final = datos_cv.get("titulo_objetivo", p_data.get("titulo_principal", "Especialista Técnico"))

    # Resumen Profesional
    if opciones.get("usar_resumen_fijo", True):
        if is_en and not perfil_base.get("resumen_base_fijo_en"):
            resumen_final = datos_cv.get("resumen_adaptado") or perfil_base.get("resumen_base_fijo", "")
        else:
            resumen_final = perfil_base.get("resumen_base_fijo") or datos_cv.get("resumen_adaptado", "")
    else:
        resumen_final = datos_cv.get("resumen_adaptado", "")

    # Ubicación
    if opciones.get("mostrar_ubicacion", True) and p_data.get("ubicacion"):
        ubicacion_txt = p_data["ubicacion"]
        if is_en:
            ubicacion_txt = ubicacion_txt.replace("México", "Mexico").replace("Remoto", "Remote")
        ubicacion_label = "📍 Location:" if is_en else "📍 Ubicación:"
        ubicacion_item = f'<div class="contact-item"><strong>{ubicacion_label}</strong> {ubicacion_txt}</div>'
    else:
        ubicacion_item = ""

    # GitHub
    if opciones.get("mostrar_github", True) and p_data.get("github"):
        github_item = f'<div class="contact-item"><strong>🌐 GitHub:</strong> {p_data["github"]}</div>'
    else:
        github_item = ""

    # Badges y Disponibilidad
    badges_items = []
    if opciones.get("mostrar_licencias", True):
        badges_items.append("Texas TDLR Electrical License (#702789)")
        badges_items.append("OSHA 30-Hour Safety (#26-607426714)")
    badges_items.append("B.S. Electronics Engineer" if is_en else "Ingeniero en Electrónica")

    if opciones.get("mostrar_disponibilidad", True) and p_data.get("disponibilidad"):
        badges_items.append("TN Visa Eligible (US Work Authorized)" if is_en else "Elegible Visa TN (Permiso de Trabajo EE. UU.)")
    badges_items.append("Bilingual (English C1 / Native Spanish)" if is_en else "Bilingüe (Inglés C1 / Español Nativo)")

    if badges_items:
        badges_str = " &bull; ".join(badges_items)
        badges_label = "Key Credentials:" if is_en else "Credenciales Clave:"
        badges_bar = f'<div class="badges-bar"><strong>{badges_label}</strong> {badges_str}</div>'
    else:
        badges_bar = ""

    # Sección Licencias y Certificaciones
    if opciones.get("mostrar_licencias", True) and perfil_base.get("credenciales_clave"):
        if is_en:
            traducciones_cred = {
                "Competente en Maniobras en Alturas y Certificado DC3": "Fall Protection Competent Person & DC3 Safety Certified (Heights)",
                "Red Hat Certified System Administrator (RHCSA / RH199)": "Red Hat Certified System Administrator (RHCSA / RH199)",
                "Certificaciones Mpirical en 5G (Acceso Wireless, C-RAN, Network Slicing, VoNR)": "Mpirical 5G Certifications (Wireless Access, C-RAN, Network Slicing, VoNR)",
                "Certificaciones técnicas de fabricantes (Ericsson LTE, Huawei WCDMA RAN, NEC iPasolink)": "OEM Manufacturer Telecom Certifications (Ericsson LTE, Huawei WCDMA RAN, NEC iPasolink)",
                "Electricista de Texas Licencia TDLR Id # 702789": "Active Texas TDLR Electrical License (#702789)",
                "OSHA 30 Licencia 26-607426714": "OSHA 30-Hour Construction Safety Certification (#26-607426714)"
            }
            cred_items = [f"<li>{traducciones_cred.get(cred, cred)}</li>" for cred in perfil_base.get("credenciales_clave", [])]
        else:
            cred_items = [f"<li>{cred}</li>" for cred in perfil_base.get("credenciales_clave", [])]

        seccion_licencias = f"""
<div class="section-title">{titulo_licencias}</div>
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
    empresa_exp = "Field Engineering & Industrial Projects" if is_en else "Experiencia en Campo & Proyectos Industriales"
    meta_exp = "2018 - Present | US & Mexico" if is_en else "2018 - Presente | México & EE. UU."

    experiencia_html = f"""
    <div class="job-block">
        <div class="job-header">
            <div>
                <span class="job-title">{titulo_final}</span> &bull; 
                <span class="job-company">{empresa_exp}</span>
            </div>
            <div class="job-meta">{meta_exp}</div>
        </div>
        <ul class="bullet-list">
            {logros_list}
        </ul>
    </div>
    """

    # Educación
    edu_items = []
    for edu in perfil_base.get("educacion", []):
        grado = edu.get("grado", "")
        esp = edu.get("especialidad", "")
        inst = edu.get("institucion", "")
        periodo = edu.get("periodo", "")

        if is_en:
            if "Maestría" in grado or "MBA" in grado:
                grado_en = "Master of Business Administration (MBA)"
                esp_en = "Business Administration & Management"
            elif "Ingeniería" in grado:
                grado_en = "Bachelor of Science in Electronics Engineering"
                esp_en = "Electronics Engineering"
            elif "Técnico" in grado:
                grado_en = "Technical Diploma / Associate in Electronics"
                esp_en = "Electronics & Automation"
            else:
                grado_en = grado
                esp_en = esp

            edu_items.append(f"""
            <div class="edu-block">
                <div><span class="edu-degree">{grado_en}</span> - <span class="edu-school">{inst} ({esp_en})</span></div>
                <div class="edu-period">{periodo}</div>
            </div>
            """)
        else:
            edu_items.append(f"""
            <div class="edu-block">
                <div><span class="edu-degree">{grado}</span> - <span class="edu-school">{inst} ({esp})</span></div>
                <div class="edu-period">{periodo}</div>
            </div>
            """)
    educacion_html = "".join(edu_items)

    # Reemplazar variables
    reemplazos = {
        "{{LANG}}": idioma,
        "{{NOMBRE}}": p_data["nombre"],
        "{{TITULO}}": titulo_final,
        "{{LABEL_TEL}}": label_tel,
        "{{TELEFONO}}": p_data["telefono"],
        "{{LABEL_EMAIL}}": label_email,
        "{{EMAIL}}": p_data["email"],
        "{{UBICACION_ITEM}}": ubicacion_item,
        "{{GITHUB_ITEM}}": github_item,
        "{{BADGES_BAR}}": badges_bar,
        "{{TITULO_RESUMEN}}": titulo_resumen,
        "{{RESUMEN}}": resumen_final,
        "{{TITULO_HABILIDADES}}": titulo_habilidades,
        "{{HABILIDADES_HTML}}": habilidades_html,
        "{{TITULO_EXPERIENCIA}}": titulo_experiencia,
        "{{EXPERIENCIA_HTML}}": experiencia_html,
        "{{TITULO_EDUCACION}}": titulo_educacion,
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
