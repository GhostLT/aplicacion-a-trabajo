import os
import threading
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pyperclip

import generator
import database
import profile_data
from pdf_engine import abrir_pdf_en_sistema, descargar_pdf_a_ruta

class TabNuevaPostulacion(ttk.Frame):
    def __init__(self, parent, on_guardado_callback=None):
        super().__init__(parent)
        self.on_guardado_callback = on_guardado_callback
        self.resultado_actual = None
        self.ruta_imagen_actual = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Contenedor principal con dos columnas (PanedWindow para redimensionar)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Columna Izquierda: Entradas de la oferta
        frame_izq = ttk.LabelFrame(paned, text=" 📋 1. Datos de la Oferta Laboral ", padding=10)
        paned.add(frame_izq, weight=1)

        # Columna Derecha: Resultados (CV PDF y Correo)
        frame_der = ttk.LabelFrame(paned, text=" 🚀 2. CV Adaptado y Correo Generado ", padding=10)
        paned.add(frame_der, weight=1)

        # --- CONTENIDO COLUMNA IZQUIERDA ---
        # Barra superior con botón de Nueva Postulación
        top_bar = ttk.Frame(frame_izq)
        top_bar.pack(fill=tk.X, pady=(0, 6))

        self.btn_nueva_postulacion = tk.Button(
            top_bar,
            text="✨ Iniciar Nueva Postulación (Limpiar Formulario)",
            bg="#0f3460",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            command=self.limpiar_para_nueva_postulacion,
            cursor="hand2"
        )
        self.btn_nueva_postulacion.pack(side=tk.LEFT)

        grid_frame = ttk.Frame(frame_izq)
        grid_frame.pack(fill=tk.X, pady=(0, 8))

        # Empresa
        ttk.Label(grid_frame, text="Empresa:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_empresa = ttk.Entry(grid_frame, font=("Segoe UI", 9))
        self.entry_empresa.grid(row=0, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        # Título del Puesto
        ttk.Label(grid_frame, text="Puesto:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_puesto = ttk.Entry(grid_frame, font=("Segoe UI", 9))
        self.entry_puesto.grid(row=1, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        # Ubicación
        ttk.Label(grid_frame, text="Ubicación:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.entry_ubicacion = ttk.Entry(grid_frame, font=("Segoe UI", 9))
        self.entry_ubicacion.grid(row=2, column=1, sticky=tk.EW, pady=3, padx=(5, 0))
        self.entry_ubicacion.insert(0, "Houston, TX / Remoto / México")

        # URL de la oferta
        ttk.Label(grid_frame, text="URL / Enlace:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.entry_url = ttk.Entry(grid_frame, font=("Segoe UI", 9))
        self.entry_url.grid(row=3, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        # Perfil Técnico
        ttk.Label(grid_frame, text="Perfil Técnico:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.perfiles_map = {
            "Auto-detectar según la oferta": "auto",
            "Automatización & Field Service (Houston / PLC)": "automatizacion",
            "Oficial Eléctrico & Instalaciones (Media/Baja Tensión)": "electrico",
            "Ingeniero Full-Stack & Inteligencia Artificial": "fullstack_ai",
            "Telecomunicaciones, Fibra Óptica & Redes": "telecom_redes",
            "Gerente de Mantenimiento / Facility Management": "gerente_mantenimiento"
        }
        self.combo_perfil = ttk.Combobox(grid_frame, values=list(self.perfiles_map.keys()), state="readonly")
        self.combo_perfil.current(0)
        self.combo_perfil.grid(row=4, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        # Idioma
        ttk.Label(grid_frame, text="Idioma del CV:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.idiomas_map = {
            "Auto-detectar (según la vacante)": "auto",
            "Español": "es",
            "Inglés (US Standard)": "en"
        }
        self.combo_idioma = ttk.Combobox(grid_frame, values=list(self.idiomas_map.keys()), state="readonly")
        self.combo_idioma.current(0)
        self.combo_idioma.grid(row=5, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        grid_frame.columnconfigure(1, weight=1)

        # Barra para Cargar Imagen de la Oferta (Captura de pantalla / foto)
        img_frame = ttk.LabelFrame(frame_izq, text=" 📷 Cargar Imagen / Captura de la Vacante (Opcional) ", padding=6)
        img_frame.pack(fill=tk.X, pady=(0, 6))

        img_ctrls = ttk.Frame(img_frame)
        img_ctrls.pack(fill=tk.X)

        self.btn_cargar_img = ttk.Button(
            img_ctrls,
            text="📁 Seleccionar Imagen...",
            command=self._cargar_imagen_oferta
        )
        self.btn_cargar_img.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_leer_img = tk.Button(
            img_ctrls,
            text="✨ Extraer Datos con IA (OCR)",
            bg="#ea580c",
            fg="white",
            activebackground="#c2410c",
            activeforeground="white",
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=2,
            command=self._iniciar_extraccion_imagen_thread,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.btn_leer_img.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_quitar_img = ttk.Button(
            img_ctrls,
            text="❌ Quitar",
            command=self._quitar_imagen_oferta,
            state=tk.DISABLED
        )
        self.btn_quitar_img.pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_info_img = ttk.Label(img_frame, text="Sin imagen seleccionada.", font=("Segoe UI", 8, "italic"), foreground="#64748b")
        self.lbl_info_img.pack(anchor=tk.W, pady=(3, 0))

        # Pegar descripción de la oferta
        ttk.Label(frame_izq, text="Descripción completa de la vacante (extraída de la imagen o pegada manualmente):", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W, pady=(4, 2))
        self.txt_oferta = scrolledtext.ScrolledText(frame_izq, height=11, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_oferta.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Opciones de personalización del CV PDF para esta postulación
        p_init = profile_data.load_user_profile()
        opc_init = p_init.get("opciones_visibilidad", {})

        opts_frame = ttk.LabelFrame(frame_izq, text=" ⚙️ Personalización del CV PDF (Seleccionar / Omitir) ", padding=6)
        opts_frame.pack(fill=tk.X, pady=(0, 6))

        row1 = ttk.Frame(opts_frame)
        row1.pack(fill=tk.X, pady=1)

        self.var_opt_ubicacion = tk.BooleanVar(value=opc_init.get("mostrar_ubicacion", True))
        ttk.Checkbutton(row1, text="Ubicación", variable=self.var_opt_ubicacion).pack(side=tk.LEFT, padx=(0, 10))

        self.var_opt_github = tk.BooleanVar(value=opc_init.get("mostrar_github", True))
        ttk.Checkbutton(row1, text="GitHub", variable=self.var_opt_github).pack(side=tk.LEFT, padx=(0, 10))

        self.var_opt_disp = tk.BooleanVar(value=opc_init.get("mostrar_disponibilidad", True))
        ttk.Checkbutton(row1, text="Disponibilidad", variable=self.var_opt_disp).pack(side=tk.LEFT, padx=(0, 10))

        self.var_opt_licencias = tk.BooleanVar(value=opc_init.get("mostrar_licencias", True))
        ttk.Checkbutton(row1, text="Licencias/Cert.", variable=self.var_opt_licencias).pack(side=tk.LEFT)

        row2 = ttk.Frame(opts_frame)
        row2.pack(fill=tk.X, pady=2)

        self.var_opt_resumen = tk.BooleanVar(value=opc_init.get("usar_resumen_fijo", True))
        ttk.Checkbutton(row2, text="Resumen Base Fijo (desmarcar para adaptar)", variable=self.var_opt_resumen).pack(side=tk.LEFT, padx=(0, 10))

        self.var_opt_titulo = tk.BooleanVar(value=opc_init.get("usar_titulo_fijo", False))
        ttk.Checkbutton(row2, text="Título Fijo (desmarcar para usar puesto de vacante)", variable=self.var_opt_titulo).pack(side=tk.LEFT)

        # Sección Destacada: Generar CV PDF
        acciones_frame = ttk.LabelFrame(frame_izq, text=" 🚀 Generación de CV PDF ", padding=8)
        acciones_frame.pack(fill=tk.X, pady=(4, 6))

        self.var_usar_ia = tk.BooleanVar(value=True)
        self.chk_ia = ttk.Checkbutton(
            acciones_frame,
            text="Usar IA de Gemini para maximizar ATS y adaptar perfil",
            variable=self.var_usar_ia
        )
        self.chk_ia.pack(anchor=tk.W, pady=(0, 6))

        # Botón PRINCIPAL y PROMINENTE: Generar CV PDF
        self.btn_generar = tk.Button(
            acciones_frame,
            text="📄 Generar CV PDF",
            bg="#1d4ed8",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=9,
            command=self._iniciar_generacion_thread,
            cursor="hand2",
            activebackground="#1e40af",
            activeforeground="white"
        )
        self.btn_generar.pack(fill=tk.X, pady=(0, 4))

        # Botón secundario: Generar y Descargar directo
        self.btn_generar_descargar = tk.Button(
            acciones_frame,
            text="📥 Generar y Descargar PDF Directo a Carpeta...",
            bg="#0f766e",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self._generar_y_descargar_directo,
            cursor="hand2",
            activebackground="#115e59",
            activeforeground="white"
        )
        self.btn_generar_descargar.pack(fill=tk.X)

        # Barra de progreso / Estado
        self.lbl_status = ttk.Label(frame_izq, text="Listo para procesar oferta.", font=("Segoe UI", 8, "italic"), foreground="#4a5568")
        self.lbl_status.pack(anchor=tk.W, pady=(4, 0))
        self.prog_bar = ttk.Progressbar(frame_izq, mode="indeterminate")

        # --- CONTENIDO COLUMNA DERECHA ---
        self.notebook_res = ttk.Notebook(frame_der)
        self.notebook_res.pack(fill=tk.BOTH, expand=True)

        # 1. Pestaña CV PDF (Primera pestaña por defecto)
        self.tab_pdf = ttk.Frame(self.notebook_res, padding=10)
        self.notebook_res.add(self.tab_pdf, text=" 📄 CV PDF Generado ")

        # Botón destacado dentro de la pestaña para generar el CV PDF
        self.btn_generar_cv_pdf_tab = tk.Button(
            self.tab_pdf,
            text="📄 Generar CV PDF con los Datos de la Vacante",
            bg="#1d4ed8",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=9,
            command=self._iniciar_generacion_thread,
            cursor="hand2",
            activebackground="#1e40af",
            activeforeground="white"
        )
        self.btn_generar_cv_pdf_tab.pack(fill=tk.X, pady=(0, 10))

        info_box = ttk.LabelFrame(self.tab_pdf, text=" Estado del Documento PDF ", padding=10)
        info_box.pack(fill=tk.X, pady=(0, 10))

        self.lbl_pdf_ruta = ttk.Label(info_box, text="Aún no se ha generado ningún PDF.", wraplength=420, font=("Segoe UI", 9))
        self.lbl_pdf_ruta.pack(anchor=tk.W, pady=4)

        self.lbl_pdf_detalles = ttk.Label(info_box, text="", font=("Segoe UI", 8, "italic"), foreground="#4a5568")
        self.lbl_pdf_detalles.pack(anchor=tk.W)

        # Botones para el PDF
        pdf_btns = ttk.Frame(self.tab_pdf)
        pdf_btns.pack(fill=tk.X, pady=10)

        self.btn_descargar_pdf = tk.Button(
            pdf_btns,
            text="📥 Descargar / Guardar PDF como...",
            bg="#0f3460",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self._descargar_pdf,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.btn_descargar_pdf.pack(fill=tk.X, pady=4)

        self.btn_abrir_pdf = tk.Button(
            pdf_btns,
            text="👁️ Abrir PDF en Visor de Windows",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self._abrir_pdf,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.btn_abrir_pdf.pack(fill=tk.X, pady=4)

        # 2. Pestaña Correo (Segunda pestaña)
        self.tab_correo = ttk.Frame(self.notebook_res, padding=8)
        self.notebook_res.add(self.tab_correo, text=" ✉️ Correo de Postulación ")

        # Asunto
        asunto_frame = ttk.Frame(self.tab_correo)
        asunto_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(asunto_frame, text="Asunto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.entry_asunto = ttk.Entry(asunto_frame, font=("Segoe UI", 9))
        self.entry_asunto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(asunto_frame, text="📋 Copiar", width=9, command=self._copiar_asunto).pack(side=tk.RIGHT)

        # Cuerpo del correo
        ttk.Label(self.tab_correo, text="Cuerpo del Correo (Listo para enviar):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        self.txt_correo = scrolledtext.ScrolledText(self.tab_correo, height=12, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_correo.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # Botones de acción del correo
        acciones_correo = ttk.Frame(self.tab_correo)
        acciones_correo.pack(fill=tk.X)
        ttk.Button(acciones_correo, text="📋 Copiar Cuerpo del Correo", command=self._copiar_correo).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(acciones_correo, text="📨 Abrir en Cliente de Correo", command=self._abrir_en_correo).pack(side=tk.LEFT)

        # Barra inferior de Guardado en MariaDB
        save_box = ttk.LabelFrame(frame_der, text=" 💾 Guardar en Base de Datos MariaDB ", padding=8)
        save_box.pack(fill=tk.X, pady=(10, 0))

        save_row = ttk.Frame(save_box)
        save_row.pack(fill=tk.X, pady=3)

        ttk.Label(save_row, text="Fase Inicial:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.combo_fase_inicial = ttk.Combobox(
            save_row,
            values=["Sin aplicar", "En proceso (enviado)", "En entrevista"],
            state="readonly",
            width=20
        )
        self.combo_fase_inicial.current(1) # Por defecto: En proceso (enviado)
        self.combo_fase_inicial.pack(side=tk.LEFT, padx=8)

        self.btn_guardar_bd = tk.Button(
            save_row,
            text="💾 Guardar en MariaDB",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._guardar_en_mariadb,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.btn_guardar_bd.pack(side=tk.RIGHT)

        self.btn_crear_otra = tk.Button(
            save_row,
            text="✨ Crear Nueva Postulación",
            bg="#334155",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self.limpiar_para_nueva_postulacion,
            cursor="hand2"
        )
        self.btn_crear_otra.pack(side=tk.RIGHT, padx=(0, 6))

        # Notas rápidas
        notas_row = ttk.Frame(save_box)
        notas_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(notas_row, text="Notas:").pack(side=tk.LEFT)
        self.entry_notas = ttk.Entry(notas_row, font=("Segoe UI", 8))
        self.entry_notas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.entry_notas.insert(0, "Postulación generada desde el sistema.")

    def _iniciar_generacion_thread(self):
        desc = self.txt_oferta.get("1.0", tk.END).strip()
        if not desc:
            resp = messagebox.askyesno(
                "Generar CV PDF",
                "No has ingresado la descripción de una vacante específica.\n\n¿Deseas generar el CV PDF profesional con los datos base de tu perfil seleccionado?"
            )
            if resp:
                desc = "Perfil profesional general y trayectoria técnica de Javier Viveros Huesca."
                self.txt_oferta.insert("1.0", desc)
            else:
                self.txt_oferta.focus_set()
                return

        self.btn_generar.config(state=tk.DISABLED)
        self.btn_generar_descargar.config(state=tk.DISABLED)
        if hasattr(self, "btn_generar_cv_pdf_tab"):
            self.btn_generar_cv_pdf_tab.config(state=tk.DISABLED)

        self.lbl_status.config(text="Procesando oferta, adaptando perfil y renderizando PDF...", foreground="#1d4ed8")
        self.prog_bar.pack(fill=tk.X, pady=(2, 6))
        self.prog_bar.start(10)

        t = threading.Thread(target=self._generar_cv_proceso, daemon=True)
        t.start()

    def sincronizar_con_perfil(self):
        """Actualiza los valores de los checkboxes según lo guardado en user_profile.json."""
        p = profile_data.load_user_profile()
        opc = p.get("opciones_visibilidad", {})
        self.var_opt_ubicacion.set(opc.get("mostrar_ubicacion", True))
        self.var_opt_github.set(opc.get("mostrar_github", True))
        self.var_opt_disp.set(opc.get("mostrar_disponibilidad", True))
        self.var_opt_licencias.set(opc.get("mostrar_licencias", True))
        self.var_opt_resumen.set(opc.get("usar_resumen_fijo", True))
        self.var_opt_titulo.set(opc.get("usar_titulo_fijo", False))

    def _generar_cv_proceso(self):
        try:
            datos_oferta = {
                "empresa": self.entry_empresa.get().strip() or "Empresa Confidencial",
                "titulo_puesto": self.entry_puesto.get().strip() or "Especialista Técnico",
                "ubicacion": self.entry_ubicacion.get().strip(),
                "url_oferta": self.entry_url.get().strip(),
                "descripcion_oferta": self.txt_oferta.get("1.0", tk.END).strip(),
                "perfil_aplicado": self.perfiles_map[self.combo_perfil.get()],
                "idioma": self.idiomas_map[self.combo_idioma.get()],
                "opciones_visibilidad": {
                    "mostrar_ubicacion": self.var_opt_ubicacion.get(),
                    "mostrar_github": self.var_opt_github.get(),
                    "mostrar_disponibilidad": self.var_opt_disp.get(),
                    "mostrar_licencias": self.var_opt_licencias.get(),
                    "usar_resumen_fijo": self.var_opt_resumen.get(),
                    "usar_titulo_fijo": self.var_opt_titulo.get()
                }
            }

            usar_ia = self.var_usar_ia.get()
            resultado = generator.procesar_postulacion_completa(datos_oferta, usar_ia=usar_ia)

            # Actualizar GUI en el hilo principal
            self.after(0, lambda: self._mostrar_resultados(resultado))
        except Exception as e:
            self.after(0, lambda: self._manejar_error(str(e)))

    def limpiar_para_nueva_postulacion(self):
        """Limpia todos los campos, textos, imágenes y estados para iniciar una nueva postulación desde cero."""
        self.entry_empresa.delete(0, tk.END)
        self.entry_puesto.delete(0, tk.END)
        self.entry_ubicacion.delete(0, tk.END)
        self.entry_ubicacion.insert(0, "Houston, TX / Remoto / México")
        self.entry_url.delete(0, tk.END)
        self.combo_perfil.current(0)
        self.combo_idioma.current(0)

        self._quitar_imagen_oferta()

        self.txt_oferta.delete("1.0", tk.END)

        # Limpiar resultados
        self.entry_asunto.delete(0, tk.END)
        self.txt_correo.delete("1.0", tk.END)

        self.lbl_pdf_ruta.config(text="Aún no se ha generado ningún PDF.")
        self.lbl_pdf_detalles.config(text="")

        self.btn_descargar_pdf.config(state=tk.DISABLED)
        self.btn_abrir_pdf.config(state=tk.DISABLED)
        self.btn_guardar_bd.config(state=tk.DISABLED)

        self.entry_notas.delete(0, tk.END)
        self.entry_notas.insert(0, "Postulación generada desde el sistema.")
        self.combo_fase_inicial.current(1)

        self.resultado_actual = None
        self.lbl_status.config(text="Listo para procesar una nueva oferta.", foreground="#4a5568")
        self.sincronizar_con_perfil()
        self.notebook_res.select(self.tab_pdf)
        self.entry_empresa.focus_set()

    def _generar_y_descargar_directo(self):
        """Genera el CV PDF alimentado con los datos de la postulación y abre inmediatamente el diálogo para descargarlo."""
        desc = self.txt_oferta.get("1.0", tk.END).strip()
        if not desc:
            resp = messagebox.askyesno(
                "Generar y Descargar CV PDF",
                "No has ingresado la descripción de una vacante específica.\n\n¿Deseas generar y descargar el CV PDF profesional con los datos base de tu perfil seleccionado?"
            )
            if resp:
                desc = "Perfil profesional general y trayectoria técnica de Javier Viveros Huesca."
                self.txt_oferta.insert("1.0", desc)
            else:
                self.txt_oferta.focus_set()
                return

        # Si ya está generado el resultado actual, descargar directamente
        if self.resultado_actual and self.resultado_actual.get("ruta_pdf"):
            self._descargar_pdf()
            return

        # Si aún no está generado, generar en hilo y luego descargar
        self.btn_generar.config(state=tk.DISABLED)
        self.btn_generar_descargar.config(state=tk.DISABLED)
        if hasattr(self, "btn_generar_cv_pdf_tab"):
            self.btn_generar_cv_pdf_tab.config(state=tk.DISABLED)

        self.lbl_status.config(text="Generando CV PDF alimentado con los datos de la vacante...", foreground="#0f766e")
        self.prog_bar.pack(fill=tk.X, pady=(2, 6))
        self.prog_bar.start(10)

        t = threading.Thread(target=self._generar_cv_proceso_y_descargar, daemon=True)
        t.start()

    def _generar_cv_proceso_y_descargar(self):
        try:
            datos_oferta = {
                "empresa": self.entry_empresa.get().strip() or "Empresa Confidencial",
                "titulo_puesto": self.entry_puesto.get().strip() or "Especialista Técnico",
                "ubicacion": self.entry_ubicacion.get().strip(),
                "url_oferta": self.entry_url.get().strip(),
                "descripcion_oferta": self.txt_oferta.get("1.0", tk.END).strip(),
                "perfil_aplicado": self.perfiles_map[self.combo_perfil.get()],
                "idioma": self.idiomas_map[self.combo_idioma.get()],
                "opciones_visibilidad": {
                    "mostrar_ubicacion": self.var_opt_ubicacion.get(),
                    "mostrar_github": self.var_opt_github.get(),
                    "mostrar_disponibilidad": self.var_opt_disp.get(),
                    "mostrar_licencias": self.var_opt_licencias.get(),
                    "usar_resumen_fijo": self.var_opt_resumen.get(),
                    "usar_titulo_fijo": self.var_opt_titulo.get()
                }
            }

            usar_ia = self.var_usar_ia.get()
            resultado = generator.procesar_postulacion_completa(datos_oferta, usar_ia=usar_ia)

            def callback_final():
                self._mostrar_resultados(resultado)
                self.btn_generar_descargar.config(state=tk.NORMAL)
                self._descargar_pdf()

            self.after(0, callback_final)
        except Exception as e:
            def err_cb():
                self.btn_generar.config(state=tk.NORMAL)
                self.btn_generar_descargar.config(state=tk.NORMAL)
                if hasattr(self, "btn_generar_cv_pdf_tab"):
                    self.btn_generar_cv_pdf_tab.config(state=tk.NORMAL)
                self._manejar_error(str(e))
            self.after(0, err_cb)

    def _mostrar_resultados(self, resultado):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_generar.config(state=tk.NORMAL)
        self.btn_generar_descargar.config(state=tk.NORMAL)
        if hasattr(self, "btn_generar_cv_pdf_tab"):
            self.btn_generar_cv_pdf_tab.config(state=tk.NORMAL)
        self.resultado_actual = resultado

        # Seleccionar inmediatamente la pestaña del CV PDF para que el usuario lo vea
        self.notebook_res.select(self.tab_pdf)

        # Cargar datos de PDF
        pdf_path = resultado["ruta_pdf"]
        self.lbl_pdf_ruta.config(text=f"📄 {pdf_path}")
        size_kb = os.path.getsize(pdf_path) / 1024 if os.path.exists(pdf_path) else 0
        self.lbl_pdf_detalles.config(
            text=f"Tamaño: {size_kb:.1f} KB | Idioma: {resultado['idioma'].upper()} | Perfil: {resultado['perfil_aplicado']}"
        )

        self.btn_descargar_pdf.config(state=tk.NORMAL)
        self.btn_abrir_pdf.config(state=tk.NORMAL)
        self.btn_guardar_bd.config(state=tk.NORMAL)

        # Cargar correo
        self.entry_asunto.delete(0, tk.END)
        self.entry_asunto.insert(0, resultado["asunto_correo"])

        self.txt_correo.delete("1.0", tk.END)
        self.txt_correo.insert("1.0", resultado["cuerpo_correo"])

        self.lbl_status.config(text="✅ CV PDF y correo generados con éxito.", foreground="#16a34a")

    def _manejar_error(self, error_msg):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_generar.config(state=tk.NORMAL)
        self.btn_generar_descargar.config(state=tk.NORMAL)
        if hasattr(self, "btn_generar_cv_pdf_tab"):
            self.btn_generar_cv_pdf_tab.config(state=tk.NORMAL)
        self.lbl_status.config(text="❌ Error durante la generación.", foreground="#dc2626")
        messagebox.showerror("Error al Generar", f"Ocurrió un error al procesar la postulación:\n\n{error_msg}")

    def _copiar_asunto(self):
        asunto = self.entry_asunto.get().strip()
        if asunto:
            pyperclip.copy(asunto)
            messagebox.showinfo("Copiado", "Asunto copiado al portapapeles.")

    def _copiar_correo(self):
        cuerpo = self.txt_correo.get("1.0", tk.END).strip()
        if cuerpo:
            pyperclip.copy(cuerpo)
            messagebox.showinfo("Copiado", "Cuerpo del correo copiado al portapapeles.")

    def _abrir_en_correo(self):
        asunto = urllib.parse.quote(self.entry_asunto.get().strip())
        cuerpo = urllib.parse.quote(self.txt_correo.get("1.0", tk.END).strip())
        mailto_url = f"mailto:?subject={asunto}&body={cuerpo}"
        try:
            os.startfile(mailto_url)
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudo abrir el cliente predeterminado: {e}")

    def _abrir_pdf(self):
        if self.resultado_actual and self.resultado_actual.get("ruta_pdf"):
            abrir_pdf_en_sistema(self.resultado_actual["ruta_pdf"])

    def _descargar_pdf(self):
        if not self.resultado_actual or not self.resultado_actual.get("ruta_pdf"):
            return

        pdf_orig = self.resultado_actual["ruta_pdf"]
        nombre_def = os.path.basename(pdf_orig)

        destino = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=nombre_def,
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            title="Guardar CV PDF en..."
        )

        if destino:
            if descargar_pdf_a_ruta(pdf_orig, destino):
                messagebox.showinfo("Descarga Exitosa", f"CV guardado exitosamente en:\n{destino}")

    def _cargar_imagen_oferta(self):
        """Permite al usuario seleccionar una captura o foto de la postulación."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar captura o imagen de la postulación",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if archivo:
            self.ruta_imagen_actual = archivo
            nombre = os.path.basename(archivo)
            self.lbl_info_img.config(text=f"📷 {nombre}", foreground="#1e293b")
            self.btn_leer_img.config(state=tk.NORMAL)
            self.btn_quitar_img.config(state=tk.NORMAL)
            
            # Preguntar si desea extraer automáticamente
            if messagebox.askyesno(
                "Imagen Seleccionada",
                f"Se cargó '{nombre}'.\n\n¿Deseas que la Inteligencia Artificial analice la imagen ahora y llene automáticamente los datos de la vacante?"
            ):
                self._iniciar_extraccion_imagen_thread()

    def _quitar_imagen_oferta(self):
        """Quita la imagen seleccionada."""
        self.ruta_imagen_actual = None
        self.lbl_info_img.config(text="Sin imagen seleccionada.", foreground="#64748b")
        self.btn_leer_img.config(state=tk.DISABLED)
        self.btn_quitar_img.config(state=tk.DISABLED)

    def _iniciar_extraccion_imagen_thread(self):
        """Inicia el análisis de la imagen en un hilo de fondo."""
        if not self.ruta_imagen_actual:
            return

        self.btn_leer_img.config(state=tk.DISABLED)
        self.lbl_status.config(text="Leyendo y transcribiendo oferta desde la imagen con IA...", foreground="#ea580c")
        self.prog_bar.pack(fill=tk.X, pady=(2, 6))
        self.prog_bar.start(10)

        t = threading.Thread(target=self._procesar_imagen_extraccion, daemon=True)
        t.start()

    def _procesar_imagen_extraccion(self):
        try:
            datos = generator.extraer_datos_de_imagen_oferta(self.ruta_imagen_actual)
            self.after(0, lambda: self._aplicar_datos_extraidos_imagen(datos))
        except Exception as e:
            self.after(0, lambda: self._manejar_error_extraccion_imagen(str(e)))

    def _aplicar_datos_extraidos_imagen(self, datos):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_leer_img.config(state=tk.NORMAL)

        if datos.get("empresa") and datos["empresa"] != "Empresa Confidencial":
            self.entry_empresa.delete(0, tk.END)
            self.entry_empresa.insert(0, datos["empresa"])

        if datos.get("titulo_puesto"):
            self.entry_puesto.delete(0, tk.END)
            self.entry_puesto.insert(0, datos["titulo_puesto"])

        if datos.get("ubicacion"):
            self.entry_ubicacion.delete(0, tk.END)
            self.entry_ubicacion.insert(0, datos["ubicacion"])

        if datos.get("descripcion_completa"):
            self.txt_oferta.delete("1.0", tk.END)
            self.txt_oferta.insert("1.0", datos["descripcion_completa"])

        self.lbl_status.config(text="✅ Datos de la vacante extraídos exitosamente desde la imagen.", foreground="#16a34a")
        messagebox.showinfo(
            "Extracción Completa",
            "✅ Se analizaron con éxito los datos de la vacante a partir de la imagen.\n\n"
            "Puedes revisarlos en el formulario y pulsar '⚡ Analizar Oferta y Generar CV + Correo'."
        )

    def _manejar_error_extraccion_imagen(self, error_msg):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_leer_img.config(state=tk.NORMAL)
        self.lbl_status.config(text="❌ Error al analizar la imagen.", foreground="#dc2626")
        messagebox.showerror("Error al Leer Imagen", f"No se pudo extraer la información de la imagen:\n\n{error_msg}")

    def _guardar_en_mariadb(self):
        if not self.resultado_actual:
            messagebox.showwarning("Atención", "Genera primero el CV y correo antes de guardar.")
            return

        datos_guardar = {
            "empresa": self.entry_empresa.get().strip() or self.resultado_actual.get("empresa"),
            "titulo_puesto": self.entry_puesto.get().strip() or self.resultado_actual.get("titulo_puesto"),
            "ubicacion": self.entry_ubicacion.get().strip(),
            "url_oferta": self.entry_url.get().strip(),
            "descripcion_oferta": self.txt_oferta.get("1.0", tk.END).strip(),
            "perfil_aplicado": self.resultado_actual.get("perfil_aplicado"),
            "idioma": self.resultado_actual.get("idioma"),
            "estado": self.combo_fase_inicial.get(),
            "asunto_correo": self.entry_asunto.get().strip(),
            "cuerpo_correo": self.txt_correo.get("1.0", tk.END).strip(),
            "ruta_pdf": self.resultado_actual.get("ruta_pdf"),
            "ruta_imagen": self.ruta_imagen_actual or "",
            "notas": self.entry_notas.get().strip()
        }

        try:
            nuevo_id = database.guardar_aplicacion(datos_guardar)
            if messagebox.askyesno(
                "Guardado en MariaDB",
                f"✅ Postulación guardada con éxito en la base de datos (ID #{nuevo_id}).\n\n"
                f"Fase: {datos_guardar['estado']}\n"
                f"Empresa: {datos_guardar['empresa']}\n\n"
                "¿Deseas limpiar el formulario para iniciar una nueva postulación ahora?"
            ):
                self.limpiar_para_nueva_postulacion()
            elif self.on_guardado_callback:
                self.on_guardado_callback()
        except Exception as e:
            messagebox.showerror("Error en MariaDB", f"No se pudo guardar en la base de datos:\n\n{str(e)}")
