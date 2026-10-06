# 💼 PostulaPro - Generador de CVs ATS y Gestor de Postulaciones

Aplicación de escritorio desarrollada en **Python** con interfaz gráfica moderna en **Tkinter**, diseñada para acelerar y profesionalizar la búsqueda de empleo técnico. Permite copiar y pegar ofertas laborales de cualquier portal de empleo (LinkedIn, OCC Mundial, Indeed, CompuTrabajo, Glassdoor, etc.), generar automáticamente un **Currículum Vitae en PDF de alto impacto compatible con filtros ATS** adaptado a la vacante con los datos del candidato (**Ing. Javier Viveros Huesca**), redactar un **correo formal de postulación listo para enviar**, registrar todo el historial en **MariaDB** y gestionar el ciclo de contratación a través de sus diferentes fases.

---

## 🌟 Características Principales

1. **📋 Cargar o Pegar Ofertas de Empleo (Texto o Imagen/Captura):**
   - **Carga de Capturas de Pantalla / Imágenes:** Botón para cargar fotos o capturas de ofertas (LinkedIn, portales web, WhatsApp, redes sociales) y botón naranja destacado **`✨ Extraer Datos con IA (OCR)`** para analizar y extraer automáticamente con **Inteligencia Artificial Multimodal (Gemini Vision)** el nombre de la empresa, puesto, ubicación y transcripción completa de los requisitos.
   - **Pegado Manual:** Campo de texto amplio para pegar descripciones copiadas de cualquier portal de empleo.
   - **Detección Automática o Manual de Perfil:**
     - *Automatización & Field Service (Houston / PLC)*
     - *Oficial Eléctrico & Instalaciones (Media y Baja Tensión / Texas TDLR)*
     - *Ingeniero Senior Full-Stack & Inteligencia Artificial*
     - *Telecomunicaciones, Fibra Óptica & Redes*
     - *Gerente de Mantenimiento / Facility Management*
   - Detección inteligente de idioma (Español o Inglés).

2. **📄 Generación de CV en PDF Descargable:**
   - **Botón Destacado `📄 Generar CV PDF con los Datos de la Vacante`:** Botón principal de alta visibilidad en azul rey ubicado en el panel de control y dentro de la pestaña de visualización del documento. Genera al instante el currículum vitae profesional en PDF adaptado con las palabras clave de la vacante (con opción inteligente de generar el CV base si aún no se ha pegado una vacante específica).
   - **Arquitectura Multihilo Thread-Safe y Libre de Bloqueos:** Procesamiento en segundo plano desacoplado mediante colas `queue.Queue`. La interfaz recolecta de forma segura los datos en el hilo principal de Tkinter y comunica los resultados mediante sondeo asíncrono, garantizando que el botón de generación nunca quede inhabilitado o trabado y evitando excepciones por manipulación de hilos en Python 3.12 (`RuntimeError: main thread is not in main loop`).
   - **Pestaña Predeterminada `📄 CV PDF Generado`:** La pestaña de visualización y control del PDF se presenta como la vista principal al abrir la aplicación y se enfoca automáticamente tras cada generación para acceder a la descarga y apertura inmediata.
   - **Botón `📥 Generar y Descargar PDF Directo a Carpeta...`:** Genera y abre directamente el explorador de archivos para guardar el PDF en la ruta de tu elección (Escritorio, Descargas, etc.).
   - Botón **📥 Descargar / Guardar PDF como...** y botón **👁️ Abrir PDF en Visor de Windows** para visualización instantánea.
   - Compilación con renderizado tipográfico de precisión mediante motor headless de **Microsoft Edge**.
   - Formato optimizado para sistemas de seguimiento de candidatos (**ATS**).
   - Inclusión automática de credenciales clave:
     - ⚡ **Licencia Eléctrica de Texas TDLR (US #702789)**
     - 🛡️ **Certificación OSHA 30 Horas en Construcción e Industria (#26-607426714)**
     - 🎓 **Título y Cédula Profesional de Ingeniero en Electrónica**
     - 📈 **Maestría en Administración de Empresas (MBA)**
     - 🇺🇸 **Elegibilidad inmediata para Visa TN (4 años de experiencia en EE. UU.)**

3. **✉️ Redacción de Correos de Postulación (Cover Letter):**
   - Asuntos estructurados de alto impacto (con certificaciones y disponibilidad).
   - Cuerpo de correo personalizado en español o inglés alineado a los requerimientos de la oferta.
   - Botones de **📋 Copiar Asunto**, **📋 Copiar Cuerpo** y **📨 Abrir en Cliente de Correo**.

4. **🐬 Base de Datos MariaDB:**
   - Registro automático y persistente de cada postulación:
     - Empresa, puesto, ubicación, URL de la oferta y descripción original.
     - Cuerpo del correo generado y asunto.
     - Ruta absoluta del PDF compilado.
     - Notas de seguimiento y fechas de registro y actualización.
   - Creación automática de la base de datos `postulaciones_db` y tablas al iniciar la aplicación.

5. **📊 Seguimiento de Fases de Contratación (Pipeline de Empleo):**
   - Control de estados:
     - ⚪ **Sin aplicar**
     - 🔵 **En proceso (enviado)**
     - 🟣 **En entrevista**
     - 🔴 **Rechazado**
     - 🟢 **Oferta recibida**
   - Panel de métricas con tarjetas KPI en tiempo real.
   - Filtro por estado y barra de búsqueda interactiva por empresa o puesto.
   - Actualización de estado en 1 clic desde la tabla.

6. **🤖 Motor Dual (Gemini AI + Motor Semántico Local):**
   - Soporte opcional para **Google Gemini API** (`gemini-3.5-flash-lite` / `gemini-3.8-flash`) para sintetizar resúmenes y viñetas con palabras clave exactas.
   - Motor local por reglas 100% offline que garantiza funcionamiento continuo sin conexión o sin clave de API.

7. **🎛️ Opciones Avanzadas de Personalización y Omisión en el CV PDF:**
   - **Título Principal Dinámico:** Opción seleccionable para fijar un título manual o, si se desmarca, usar automáticamente el **nombre del puesto/perfil de la postulación**.
   - **Resumen Profesional Base:** Opción para mostrar por defecto lo redactado en el campo fijo o, si se desmarca, generar un resumen adaptativo acorde al perfil y requerimientos específicos de la vacante.
   - **Licencias y Certificaciones Clave:** Opción para incluir la sección completa en el CV PDF o desmarcarla para **omitirla por completo**.
   - **Ubicación:** Opción para mostrar u **omitir la ubicación** del encabezado del documento.
   - **Perfil de GitHub:** Opción para mostrar u **omitir el enlace de GitHub** en el CV PDF.
   - **Disponibilidad:** Opción para mostrar u **omitir el estatus de disponibilidad / Visa TN** en los distintivos del encabezado.
   - **🎓 Incluir u Omitir Maestría (MBA):** Campo seleccionable en **Mi Perfil Base** y en **Nueva Postulación** que permite agregar u **omitir por completo tener una Maestría en Administración de Empresas (MBA)** en el CV PDF descargable y en la carta de presentación. Al desmarcarlo, se eliminan las menciones de MBA en el bloque de educación, credenciales clave, título profesional y correo, evitando aparecer como "sobrecalificado" para puestos técnicos, de campo u operativos que requieren un enfoque 100% práctico.
   - **🇺🇸 Campo Seleccionable "En inglés" (CV PDF 100% en Inglés):** Campo seleccionable directo etiquetado como **`En inglés`** en la pestaña **Nueva Postulación** (junto al formulario y opciones de personalización) y en **Mi Perfil Base**. Al seleccionarlo (marcarlo), garantiza que el CV PDF creado salga **completamente en inglés** (encabezados, datos de contacto, resumen, competencias, educación y carta de presentación). Al desmarcarlo, el CV se genera en español.
   - *Estas opciones se guardan de forma permanente en `user_profile.json` desde la pestaña **Mi Perfil Base** y también se pueden ajustar al instante para cada vacante desde la pestaña **Nueva Postulación**.*

8. **🔄 Flujo Continuo de Nuevas Postulaciones (Sin Reiniciar la Aplicación):**
   - **Botón `✨ Iniciar Nueva Postulación (Limpiar Formulario)`:** Ubicado en la barra superior izquierda para vaciar los campos, remover capturas cargadas y restablecer el estado inicial en 1 solo clic.
   - **Botón `✨ Crear Nueva Postulación`:** Disponible directamente en la barra de guardado de MariaDB.
   - Diálogo automático tras guardar exitosamente en la base de datos que te ofrece limpiar el formulario para iniciar la siguiente postulación de inmediato sin tener que cerrar y abrir la aplicación.

9. **📄 Carga de CV Base en PDF e Importación Automática del Perfil:**
   - **Campo en "Mi Perfil Base":** Permite subir tu Currículum Vitae actual en formato **PDF** para que el sistema tome de ahí directamente tu perfil profesional.
   - **Extracción Inteligente:** Combina `pypdf` y **Google Gemini AI** (con respaldo local offline) para extraer automáticamente tu nombre, título, datos de contacto, licencias (TDLR, OSHA 30), certificaciones, resumen profesional y educación.
   - **Alimentación de Nuevos CVs:** El texto y datos extraídos se guardan en `user_profile.json` y se inyectan automáticamente en el motor generador para crear los CVs en PDF descargables adaptados a las vacantes de forma 100% fidedigna a tu experiencia real.
   - **Controles Intuitivos:** Botón **`📁 Seleccionar CV PDF...`**, botón naranja destacado **`✨ Extraer y Cargar Perfil desde PDF`**, visor rápido **`👁️ Ver PDF`** y opción para desvincular con **`❌ Quitar`**.

10. **📜 Scroll Vertical Completo y Soporte de Rueda del Ratón (MouseWheel):**
   - **Navegación Fluida y Adaptable:** Incorporación de un contenedor `tk.Canvas` con `ttk.Scrollbar` vertical reactivo en la ventana principal de **Nueva Postulación** y en **Mi Perfil Base**.
   - **Acceso Total a Todos los Campos:** Permite desplazarse fácilmente hacia abajo en cualquier tamaño de pantalla o resolución (e.g. laptops 1366x768, pantallas con escala DPI del 125% o 150%) para seleccionar cómodamente los checkboxes inferiores (Maestría/MBA, En inglés, Resumen, Título, etc.) y los botones de acción principales ("📄 Generar CV PDF", "💾 Guardar en MariaDB").
   - **Desplazamiento Inteligente con Rueda del Ratón:** Al posicionar el cursor sobre el formulario se activa el scroll vertical con la rueda del ratón (`<MouseWheel>`). Si el cursor se sitúa dentro de las cajas de texto de descripción o correo, respeta el scroll interno del texto sin interferencias.
   - **Dimensionamiento Dinámico:** Detección de la resolución de pantalla al iniciar la aplicación para ajustar las dimensiones de la ventana y dimensiones mínimas adaptativas.

---

## 🏗️ Arquitectura del Proyecto

```
aplicacion a trabajo/
│
├── main.py                     # Punto de entrada de la aplicación
├── config.py                   # Carga de variables de entorno (.env) y rutas
├── database.py                 # Conexión MariaDB, creación de esquema y consultas CRUD
├── profile_data.py             # Datos maestros del candidato y persistencia en user_profile.json
├── pdf_profile_extractor.py    # Extracción de texto y estructuración de perfil desde CV PDF
├── generator.py                # Analizador de vacantes, lógica de CV y redactor de correos
├── pdf_engine.py               # Renderizador HTML -> PDF mediante Edge Headless
│
├── ui/
│   ├── __init__.py
│   ├── app_window.py           # Ventana principal Tkinter con pestañas modernas
│   ├── tab_nueva_postulacion.py# Pestaña para pegar vacante y generar CV/correo
│   ├── tab_historial.py        # Pestaña con tabla, métricas y cambio de fases
│   ├── tab_perfil.py           # Pestaña para editar perfil y cargar CV base en PDF
│   └── tab_configuracion.py    # Configuración de MariaDB, Gemini y rutas
│
├── templates/
│   └── cv_template.html        # Plantilla HTML/CSS profesional y ATS-friendly
│
├── uploads/                    # Almacenamiento local del CV base en PDF cargado
├── output_pdfs/                # Almacenamiento local de los PDFs generados
├── user_profile.json           # Datos editables del perfil guardados en JSON
├── .env                        # Variables de entorno y credenciales locales
├── .env.example                # Plantilla de variables de entorno
├── requirements.txt            # Dependencias de Python
└── README.md                   # Documentación técnica y manual de usuario
```

---

## 🛠️ Requisitos Previos

- **Sistema Operativo:** Windows 10 u 11 (recomendado para renderizado directo con Edge).
- **Python:** Versión `3.10` o superior (probado en Python `3.12.10`).
- **MariaDB:** Versión `10.5` o superior (probado en MariaDB `12.3` en puerto `3306`).
- **Microsoft Edge:** Incluido por defecto en Windows.

---

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/GhostLT/aplicacion-a-trabajo.git
cd "aplicacion a trabajo"
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno (`.env`)
El archivo `.env` se crea automáticamente con valores predeterminados. Puedes verificar o editar las credenciales:
```env
# Conexión MariaDB
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=postulaciones_db

# Google Gemini API (Opcional)
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-3.5-flash-lite

# Ruta de Microsoft Edge
EDGE_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

---

## 🖥️ Ejecución de la Aplicación

Para iniciar el sistema, ejecuta:
```bash
python main.py
```

La aplicación verificará la conexión a MariaDB, inicializará la base de datos `postulaciones_db` si aún no existe, cargará tu perfil base y abrirá la ventana gráfica.

---

## 📖 Manual de Uso Paso a Paso

### Paso 1: Crear una Nueva Postulación
1. Ve a la pestaña **➕ Nueva Postulación**.
2. Escribe la **Empresa**, el **Puesto** y la **Ubicación** (ej. *Houston, TX*).
3. Pega la descripción completa del trabajo en el área de texto.
4. Selecciona el **Perfil Técnico** (o déjalo en *Auto-detectar*) y el **Idioma** deseado.
5. Haz clic en **⚡ Analizar Oferta y Generar CV + Correo**.

### Paso 2: Descargar el CV y Enviar el Correo
1. En la pestaña **✉️ Correo de Postulación**, copia el asunto y el cuerpo del correo con un solo clic.
2. En la pestaña **📄 CV PDF Generado**, haz clic en:
   - **👁️ Abrir PDF** para revisarlo de inmediato.
   - **📥 Descargar / Guardar PDF como...** para guardar tu copia en el Escritorio.

### Paso 3: Registrar en MariaDB
1. Selecciona la fase inicial (ej. *En proceso (enviado)*).
2. Haz clic en **💾 Guardar en MariaDB**. La aplicación registrará la oferta y te redirigirá a la pestaña de historial.

### Paso 4: Seguimiento del Embudo de Contratación
1. Ve a la pestaña **📊 Historial & Fases de Contratación**.
2. Consulta el número total de vacantes en cada etapa.
3. Al recibir una respuesta o llamada de un reclutador, selecciona la fila, elige la nueva fase (ej. *En entrevista*) y haz clic en **Actualizar Fase**.
4. Agrega notas de seguimiento (preguntas hechas en la entrevista, fechas de feedback) con el botón **📝 Notas**.

---

## 🐬 Estructura de la Base de Datos

```sql
CREATE TABLE `aplicaciones` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `empresa` VARCHAR(255) NOT NULL,
    `titulo_puesto` VARCHAR(255) NOT NULL,
    `ubicacion` VARCHAR(255) DEFAULT '',
    `url_oferta` TEXT,
    `descripcion_oferta` LONGTEXT,
    `perfil_aplicado` VARCHAR(100) DEFAULT '',
    `idioma` VARCHAR(20) DEFAULT 'es',
    `estado` VARCHAR(50) DEFAULT 'Sin aplicar',
    `asunto_correo` VARCHAR(500) DEFAULT '',
    `cuerpo_correo` LONGTEXT,
    `ruta_pdf` VARCHAR(500) DEFAULT '',
    `ruta_imagen` VARCHAR(500) DEFAULT '',
    `notas` TEXT,
    `fecha_creacion` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `fecha_actualizacion` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_estado (`estado`),
    INDEX idx_empresa (`empresa`),
    INDEX idx_fecha (`fecha_creacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 👤 Autor

**Ing. Javier Viveros Huesca**  
- ✉️ Correo: [viverosjavier86@gmail.com](mailto:viverosjavier86@gmail.com)  
- 📞 Tel / WhatsApp: +52 (669) 533-0508  
- 🌐 GitHub: [@GhostLT](https://github.com/GhostLT)  
- ⚡ Credenciales: Licencia Eléctrica de Texas TDLR (#702789) | Certificación OSHA 30 Horas (#26-607426714) | Elegible Visa TN
