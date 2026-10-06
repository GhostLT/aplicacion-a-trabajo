import json
from pathlib import Path
from config import PROFILE_DATA_FILE

DEFAULT_PROFILE = {
    "datos_personales": {
        "nombre": "Javier Viveros Huesca",
        "titulo_principal": "Ingeniero en Electrónica | MBA | Especialista Técnico",
        "telefono": "+52 (669) 533-0508",
        "email": "viverosjavier86@gmail.com",
        "ubicacion": "Mazatlán, Sinaloa, México / Houston, Texas, EE. UU.",
        "linkedin": "linkedin.com/in/javier-viveros",
        "github": "https://github.com/GhostLT",
        "idiomas": "Español (Nativo) | Inglés (C1 Profesional Fluido)",
        "disponibilidad": "Inmediata para proyectos locales, viajes o reubicación en EE. UU. (Elegible Visa TN)"
    },
    "opciones_visibilidad": {
        "usar_titulo_fijo": False,         # False: usa el nombre del perfil de la postulación; True: usa titulo_principal
        "mostrar_ubicacion": True,         # True: muestra ubicación en el PDF; False: se omite
        "mostrar_github": True,            # True: muestra GitHub en el PDF; False: se omite
        "mostrar_disponibilidad": True,    # True: muestra disponibilidad en el PDF; False: se omite
        "mostrar_licencias": True,         # True: incluye la sección de licencias; False: se omite en el PDF
        "usar_resumen_fijo": True,         # True: usa por defecto lo escrito en resumen base; False: lo crea acorde al perfil
        "idioma_predeterminado": "auto"    # "auto": según vacante, "es": 100% Español, "en": 100% Inglés
    },
    "ruta_cv_base_pdf": "",
    "texto_cv_base_extraido": "",
    "fecha_carga_cv_base": "",
    "resumen_base_fijo": "Ingeniero en Electrónica y Técnico Especialista con más de 10 años de experiencia técnica en comisionamiento, instalación electromecánica, diagnóstico sistemático de fallas (eléctricas 24VDC/120V/480V, neumáticas y mecánicas) y mantenimiento correctivo/preventivo de maquinaria industrial automatizada. Con 4 años de experiencia de campo en Estados Unidos con Visa TN, Licencia Eléctrica de Texas TDLR (#702789) y Certificación OSHA 30 Horas. Dominio fluido de inglés técnico (C1).",
    "credenciales_clave": [
        "Licencia Eléctrica de Texas TDLR (US #702789)",
        "Certificación OSHA 30 Horas en Seguridad de la Construcción e Industrial (US #26-607426714)",
        "Título y Cédula Profesional de Ingeniero en Electrónica",
        "Maestría en Administración de Empresas (MBA) - Gestión Estratégica y Liderazgo Operativo",
        "Elegibilidad inmediata para Visa TN (4 años de experiencia previa trabajando en EE. UU.)",
        "Licencia de conducir vigente (vehículos estándar y automáticos)"
    ],
    "educacion": [
        {
            "grado": "Maestría en Administración de Empresas (MBA)",
            "especialidad": "Gestión Estratégica y Liderazgo Operativo",
            "institucion": "Universidad TecMilenio",
            "periodo": "2018 - 2020"
        },
        {
            "grado": "Ingeniería en Electrónica",
            "especialidad": "Control, Telecomunicaciones y Sistemas Digitales",
            "institucion": "Instituto Tecnológico",
            "periodo": "2006 - 2011"
        }
    ],
    "perfiles_especializados": {
        "automatizacion": {
            "nombre": "Técnico de Servicio en Automatización / Field Service Engineer",
            "resumen_es": "Ingeniero en Electrónica y Técnico Especialista con más de 10 años de experiencia técnica en comisionamiento, instalación electromecánica, diagnóstico sistemático de fallas (eléctricas 24VDC/120V/480V, neumáticas y mecánicas) y mantenimiento correctivo/preventivo de maquinaria industrial automatizada. Con 4 años de experiencia de campo en Estados Unidos con Visa TN, Licencia Eléctrica de Texas TDLR (#702789) y Certificación OSHA 30 Horas. Dominio fluido de inglés técnico (C1).",
            "resumen_en": "Electronics Engineer and Field Service Specialist with 10+ years of technical experience in commissioning, electromechanical assembly, pneumatic troubleshooting, 24VDC/120V/480V power systems, and OEM industrial maintenance. 4 years of hands-on field experience across the US under TN Visa status. Active Texas TDLR Electrical License (#702789), OSHA 30-Hour Construction Safety Certification (#26-607426714), and professional English proficiency (C1).",
            "habilidades_clave": [
                "Comisionamiento y puesta en marcha de líneas de automatización",
                "Neumática industrial (electroválvulas, cilindros, unidades FRL, manifolds)",
                "Lectura experta de diagramas esquemáticos eléctricos y neumáticos DTI/P&ID",
                "Diagnóstico con multímetro Fluke, amperímetro y pruebas de lazo punto a punto",
                "Seguridad LOTO (Lockout/Tagout), JHA y cumplimiento de normas OSHA / NFPA 70E",
                "Elaboración de Field Service Reports (FSR) y gestión técnica con clientes"
            ],
            "experiencia": [
                {
                    "puesto": "Field Service & Automation Technician",
                    "empresa": "Proyectos Industriales & Contratistas EE. UU. / México",
                    "periodo": "2020 - Actual",
                    "logros": [
                        "Ejecución de comisionamiento y verificación funcional de líneas automatizadas y celdas electromecánicas.",
                        "Diagnóstico de fallas en lazos de control de 24VDC, sensores inductivos/ópticos y actuadores neumáticos.",
                        "Aplicación estricta de protocolos de seguridad LOTO y análisis diario de riesgos (JHA).",
                        "Elaboración de reportes de servicio en campo (FSR) y entrega técnica formal a supervisores y clientes."
                    ]
                }
            ]
        },
        "electrico": {
            "nombre": "Oficial Eléctrico / Especialista en Media y Baja Tensión",
            "resumen_es": "Oficial Eléctrico e Ingeniero en Electrónica con amplia trayectoria en instalaciones eléctricas de baja y media tensión (120V, 220V, 440V/480V trifásica y corriente directa), armado y peinado de tableros de distribución, canalizaciones conduit EMT/PVC cédula 40, charolas portacables, plantas de emergencia diésel, transferencias automáticas (ATS), bancos de baterías y sistemas de tierras físicas con soldadura exotérmica (Cadweld). Licencia TDLR Texas y certificación OSHA 30.",
            "resumen_en": "Journeyman-level Electrician and Electronics Engineer experienced in low and medium voltage industrial/commercial installations (120V, 208V, 240V, 480V 3-phase). Expert in distribution panel wiring, EMT/PVC conduit bending and threading, cable tray routing, diesel generators, automatic transfer switches (ATS), battery banks, and grounding systems. Active Texas TDLR License and OSHA 30-Hour card.",
            "habilidades_clave": [
                "Instalación en baja y media tensión (120V / 220V / 480V trifásica)",
                "Doblado y roscado de tubería conduit EMT y PVC de hasta 2 pulgadas",
                "Armado, peinado y conexionado de tableros de control y centros de carga",
                "Sistemas de respaldo de energía: Plantas diésel, transferencias ATS y UPS",
                "Mallas de tierras físicas y soldadura exotérmica (Cadweld)",
                "Normativas NOM-001-SEDE, NEC / NFPA 70E y OSHA de construcción"
            ],
            "experiencia": [
                {
                    "puesto": "Oficial Eléctrico / Encargado de Instalaciones",
                    "empresa": "Infraestructura Eléctrica y Telecomunicaciones",
                    "periodo": "2019 - Actual",
                    "logros": [
                        "Tendido de conductores de potencia calibres AWG y MCM en charolas y canalizaciones subterráneas.",
                        "Conexión y balanceo de cargas en tableros de distribución principales y secundarios.",
                        "Instalación de bancos de baterías de respaldo y mantenimiento a generadores diésel de emergencia.",
                        "Pruebas de aislamiento con megóhmetro y resistencia de tierras físicas bajo normas vigentes."
                    ]
                }
            ]
        },
        "fullstack_ai": {
            "nombre": "Ingeniero Senior Full-Stack con IA / Python Developer",
            "resumen_es": "Ingeniero en Electrónica y Desarrollador Full-Stack especializado en Python, FastAPI, Django, React, TypeScript y arquitecturas con Inteligencia Artificial generativa. Experiencia sólida integrando modelos de lenguaje (LLMs, RAG, embeddings vectoriales), bases de datos SQL (MariaDB, PostgreSQL) y automatizaciones de flujos de trabajo con agentes autónomos.",
            "resumen_en": "Full-Stack Software and AI Engineer with deep expertise in Python, FastAPI, Django, React, TypeScript, and Generative AI workflows. Experienced in implementing LLM agents, Retrieval-Augmented Generation (RAG), vector databases, relational database design (MariaDB/MySQL, PostgreSQL), and scalable microservices.",
            "habilidades_clave": [
                "Desarrollo backend con Python (FastAPI, Django, Flask)",
                "Desarrollo frontend con React, TypeScript, HTML5/CSS3 y Tkinter",
                "Bases de datos: MariaDB, MySQL, PostgreSQL, Supabase, SQLite",
                "Integración de IA: APIs Gemini/OpenAI, modelos open-source (Ollama, vLLM), RAG",
                "Arquitectura de APIs RESTful, WebSockets y automatización de procesos",
                "Control de versiones Git, Docker, CI/CD y despliegue en la nube"
            ],
            "experiencia": [
                {
                    "puesto": "Senior AI & Full-Stack Developer",
                    "empresa": "Desarrollo de Soluciones Tecnológicas y Startups",
                    "periodo": "2021 - Actual",
                    "logros": [
                        "Diseño e implementación de plataformas con asistentes virtuales inteligentes y RAG corporativo.",
                        "Creación de pipelines de datos y automatización de procesos operativos en Python.",
                        "Optimización de consultas SQL y modelado relacional en MariaDB y PostgreSQL.",
                        "Construcción de interfaces de usuario modernas, interactivas y altamente responsivas."
                    ]
                }
            ]
        },
        "telecom_redes": {
            "nombre": "Ingeniero de Telecomunicaciones, Fibra Óptica & Redes",
            "resumen_es": "Ingeniero en Electrónica con especialidad en infraestructura de telecomunicaciones, tendido y conectorización de fibra óptica monomodo, configuración de ONTs/módems/routers, cableado estructurado Cat6, soporte de redes nivel 2/NOC y pruebas de radiofrecuencia (RF). Experiencia en despliegue en campo y monitoreo continuo.",
            "resumen_en": "Electronics & Telecommunications Engineer specialized in fiber optic deployment (single-mode), NAP closures, ONT/router provisioning, structured cabling, Network Operations Center (NOC) Tier 2 support, and RF hardware validation. Hands-on experience with OTDR measurements and carrier-grade network equipment.",
            "habilidades_clave": [
                "Tendido, fusión y pruebas de fibra óptica monomodo (OTDR, VFL, medidor de potencia)",
                "Instalación y aprovisionamiento de ONTs, GPON, routers y switches",
                "Cableado estructurado Cat5e/Cat6, racks de telecomunicaciones y gabinetes",
                "Protocolos de red IP, VLANs, subnetting, enrutamiento estático y dinámico",
                "Pruebas de RF, análisis de espectro y validación de hardware inalámbrico",
                "Gestión de incidentes, SLAs y soporte técnico de campo 24/7"
            ],
            "experiencia": [
                {
                    "puesto": "Técnico Especialista en Telecomunicaciones y Fibra Óptica",
                    "empresa": "Redes de Telecomunicaciones & Infraestructura de Conectividad",
                    "periodo": "2018 - Actual",
                    "logros": [
                        "Instalación y puesta en servicio de enlaces de fibra óptica y terminales de red óptica (ONT).",
                        "Medición de reflectometría y atenuación óptica garantizando estándares de calidad de enlace.",
                        "Configuración de equipos CPE y verificación de ancho de banda y conectividad del abonado.",
                        "Resolución de fallas de capa física y enlace en infraestructura de telecomunicaciones."
                    ]
                }
            ]
        },
        "gerente_mantenimiento": {
            "nombre": "Gerente de Mantenimiento / Facility Management",
            "resumen_es": "Ingeniero en Electrónica con Maestría en Administración de Empresas (MBA) en Gestión Estratégica. Especialista en la dirección integral de operaciones de mantenimiento en infraestructura hotelera e industrial. Amplio dominio de sistemas HVAC (chillers, UMAs, fan & coils), cuartos de máquinas, subestaciones eléctricas, plantas de emergencia, calderas, sistemas hidroneumáticos, gestión presupuestal OPEX/CAPEX y liderazgo de cuadrillas multidisciplinarias 24/7.",
            "resumen_en": "Maintenance Manager & Facilities Director with Electronics Engineering degree and MBA in Strategic Management. Proven track record leading 24/7 multidisciplinary technical teams, managing HVAC chilled water plants, boilers, pumping stations, electrical substations, diesel generators, and comprehensive PM programs with full budget control (OPEX/CAPEX).",
            "habilidades_clave": [
                "Gestión integral de mantenimiento hotelero e industrial (Facility Management)",
                "Sistemas HVAC centrales: Chillers de agua helada, manejadoras de aire y fan & coils",
                "Plantas de emergencia diésel, transferencias automáticas y subestaciones eléctricas",
                "Sistemas hidráulicos: Hidroneumáticos de presión constante, calderas y calentadores",
                "Control presupuestal OPEX y CAPEX, negociación con contratistas y compras",
                "Cumplimiento de normativas de Protección Civil, Distintivo H y seguridad industrial"
            ],
            "experiencia": [
                {
                    "puesto": "Gerente de Mantenimiento e Infraestructura",
                    "empresa": "Sector Hotelero y Complejos Inmobiliarios",
                    "periodo": "2018 - Actual",
                    "logros": [
                        "Liderazgo de cuadrillas técnicas multidisciplinarias cubriendo turnos 24/7 en operación continua.",
                        "Reducción de paros imprevistos de climatización mediante mantenimiento predictivo en chillers.",
                        "Optimización del consumo energético y de agua en cuartos de máquinas e instalaciones generales.",
                        "Implementación de planes de mantenimiento preventivo a habitaciones e instalaciones comunes."
                    ]
                }
            ]
        }
    }
}

def load_user_profile():
    """Carga el perfil del usuario desde JSON o genera el predeterminado asegurando las opciones de visibilidad."""
    if PROFILE_DATA_FILE.exists():
        try:
            with open(PROFILE_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Asegurar que existan las nuevas opciones de visibilidad
                if "opciones_visibilidad" not in data:
                    data["opciones_visibilidad"] = DEFAULT_PROFILE["opciones_visibilidad"]
                else:
                    for k, v in DEFAULT_PROFILE["opciones_visibilidad"].items():
                        if k not in data["opciones_visibilidad"]:
                            data["opciones_visibilidad"][k] = v
                
                if "resumen_base_fijo" not in data:
                    data["resumen_base_fijo"] = DEFAULT_PROFILE["resumen_base_fijo"]
                if "ruta_cv_base_pdf" not in data:
                    data["ruta_cv_base_pdf"] = ""
                if "texto_cv_base_extraido" not in data:
                    data["texto_cv_base_extraido"] = ""
                if "fecha_carga_cv_base" not in data:
                    data["fecha_carga_cv_base"] = ""

                return data
        except Exception:
            pass
    
    # Si no existe, guardar el predeterminado
    save_user_profile(DEFAULT_PROFILE)
    return DEFAULT_PROFILE

def save_user_profile(profile_dict):
    """Guarda el perfil del usuario en user_profile.json."""
    with open(PROFILE_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_dict, f, ensure_ascii=False, indent=2)

def actualizar_perfil_desde_datos_extraidos(datos_extraidos: dict, ruta_pdf_origen: str, texto_extraido: str) -> dict:
    """
    Actualiza el perfil del usuario con los datos extraídos de un CV en PDF,
    preservando las preferencias de visibilidad y estructura del sistema.
    """
    import time
    perfil = load_user_profile()

    dp = datos_extraidos.get("datos_personales", {})
    if "datos_personales" not in perfil:
        perfil["datos_personales"] = {}

    for k in ["nombre", "titulo_principal", "telefono", "email", "ubicacion", "linkedin", "github", "idiomas", "disponibilidad"]:
        val = dp.get(k)
        if val and str(val).strip():
            perfil["datos_personales"][k] = str(val).strip()

    if datos_extraidos.get("resumen_base_fijo"):
        perfil["resumen_base_fijo"] = str(datos_extraidos["resumen_base_fijo"]).strip()

    if datos_extraidos.get("credenciales_clave"):
        perfil["credenciales_clave"] = [c.strip() for c in datos_extraidos["credenciales_clave"] if c.strip()]

    if datos_extraidos.get("educacion"):
        perfil["educacion"] = datos_extraidos["educacion"]

    perfil["ruta_cv_base_pdf"] = ruta_pdf_origen or ""
    perfil["texto_cv_base_extraido"] = texto_extraido or ""
    perfil["fecha_carga_cv_base"] = time.strftime("%Y-%m-%d %H:%M:%S")

    save_user_profile(perfil)
    return perfil
