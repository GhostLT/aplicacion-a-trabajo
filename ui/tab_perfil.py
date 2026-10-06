import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import profile_data
from pdf_engine import abrir_pdf_en_sistema
import pdf_profile_extractor

class TabPerfil(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.perfil = profile_data.load_user_profile()
        self._cola_tareas = queue.Queue()
        self._crear_interfaz()
        self._verificar_cola_tareas()

    def _crear_interfaz(self):
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=12)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        p = self.perfil.get("datos_personales", {})
        opc = self.perfil.get("opciones_visibilidad", {})

        # Variables de control para las opciones de selección/omisión
        self.var_usar_titulo_fijo = tk.BooleanVar(value=opc.get("usar_titulo_fijo", False))
        self.var_mostrar_ubicacion = tk.BooleanVar(value=opc.get("mostrar_ubicacion", True))
        self.var_mostrar_github = tk.BooleanVar(value=opc.get("mostrar_github", True))
        self.var_mostrar_disponibilidad = tk.BooleanVar(value=opc.get("mostrar_disponibilidad", True))
        self.var_mostrar_licencias = tk.BooleanVar(value=opc.get("mostrar_licencias", True))
        self.var_usar_resumen_fijo = tk.BooleanVar(value=opc.get("usar_resumen_fijo", True))
        self.var_mostrar_maestria = tk.BooleanVar(value=opc.get("mostrar_maestria", True))
        id_pref_init = opc.get("idioma_predeterminado", "auto")
        es_en_init = (id_pref_init == "en") or bool(opc.get("en_ingles", False))
        self.var_en_ingles_default = tk.BooleanVar(value=es_en_init)
        self.var_idioma_default = tk.StringVar(value="en" if es_en_init else id_pref_init)

        # 0. SECCIÓN DESTACADA: SUBIR CV BASE EN PDF
        pdf_box = ttk.LabelFrame(scrollable_frame, text=" 📄 Cargar CV Base en PDF (Importar Perfil Automáticamente) ", padding=10)
        pdf_box.pack(fill=tk.X, pady=(0, 10))

        pdf_info_row = ttk.Frame(pdf_box)
        pdf_info_row.pack(fill=tk.X, pady=(0, 6))

        ruta_cv_existente = self.perfil.get("ruta_cv_base_pdf", "")
        self.ruta_pdf_cv_base = ruta_cv_existente if (ruta_cv_existente and os.path.exists(ruta_cv_existente)) else ""
        txt_inicial_pdf = f"📄 Archivo actual: {os.path.basename(self.ruta_pdf_cv_base)}" if self.ruta_pdf_cv_base else "Ningún archivo PDF cargado como CV base."

        self.lbl_pdf_cv_base = ttk.Label(
            pdf_info_row,
            text=txt_inicial_pdf,
            font=("Segoe UI", 9, "bold" if self.ruta_pdf_cv_base else "normal"),
            foreground="#0f3460" if self.ruta_pdf_cv_base else "#64748b"
        )
        self.lbl_pdf_cv_base.pack(side=tk.LEFT, fill=tk.X, expand=True)

        pdf_btn_row = ttk.Frame(pdf_box)
        pdf_btn_row.pack(fill=tk.X, pady=2)

        self.btn_subir_pdf = ttk.Button(
            pdf_btn_row,
            text="📁 Seleccionar CV PDF...",
            command=self._seleccionar_pdf_base
        )
        self.btn_subir_pdf.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_extraer_pdf = tk.Button(
            pdf_btn_row,
            text="✨ Extraer y Cargar Perfil desde PDF",
            bg="#ea580c",
            fg="white",
            activebackground="#c2410c",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            command=self._iniciar_extraccion_pdf_thread,
            state=tk.NORMAL if self.ruta_pdf_cv_base else tk.DISABLED,
            cursor="hand2"
        )
        self.btn_extraer_pdf.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_ver_pdf_base = ttk.Button(
            pdf_btn_row,
            text="👁️ Ver PDF",
            command=self._abrir_pdf_base,
            state=tk.NORMAL if self.ruta_pdf_cv_base else tk.DISABLED
        )
        self.btn_ver_pdf_base.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_quitar_pdf_base = ttk.Button(
            pdf_btn_row,
            text="❌ Quitar",
            command=self._quitar_pdf_base,
            state=tk.NORMAL if self.ruta_pdf_cv_base else tk.DISABLED
        )
        self.btn_quitar_pdf_base.pack(side=tk.LEFT)

        self.lbl_status_pdf = ttk.Label(
            pdf_box,
            text="Sube tu CV en PDF para extraer tu experiencia y alimentar la creación de nuevos CVs descargables.",
            font=("Segoe UI", 8, "italic"),
            foreground="#475569"
        )
        self.lbl_status_pdf.pack(anchor=tk.W, pady=(4, 0))
        self.prog_bar_pdf = ttk.Progressbar(pdf_box, mode="indeterminate")

        # 1. DATOS PERSONALES Y CONTACTO
        datos_box = ttk.LabelFrame(scrollable_frame, text=" 👤 Datos de Contacto y Perfil Base ", padding=10)
        datos_box.pack(fill=tk.X, pady=(0, 10))

        grid = ttk.Frame(datos_box)
        grid.pack(fill=tk.X)

        # Nombre
        ttk.Label(grid, text="Nombre Completo:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_nombre = ttk.Entry(grid, width=45)
        self.entry_nombre.insert(0, p.get("nombre", ""))
        self.entry_nombre.grid(row=0, column=1, sticky=tk.W, pady=3, padx=6)

        # Título Principal con opción seleccionable
        ttk.Label(grid, text="Título Principal:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_titulo = ttk.Entry(grid, width=45)
        self.entry_titulo.insert(0, p.get("titulo_principal", ""))
        self.entry_titulo.grid(row=1, column=1, sticky=tk.W, pady=3, padx=6)
        chk_titulo = ttk.Checkbutton(
            grid,
            text="Usar este título fijo (si no se selecciona, muestra el nombre del perfil de la postulación)",
            variable=self.var_usar_titulo_fijo
        )
        chk_titulo.grid(row=2, column=1, sticky=tk.W, pady=(0, 5), padx=6)

        # Teléfono
        ttk.Label(grid, text="Teléfono / WhatsApp:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.entry_tel = ttk.Entry(grid, width=45)
        self.entry_tel.insert(0, p.get("telefono", ""))
        self.entry_tel.grid(row=3, column=1, sticky=tk.W, pady=3, padx=6)

        # Email
        ttk.Label(grid, text="Correo Electrónico:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.entry_email = ttk.Entry(grid, width=45)
        self.entry_email.insert(0, p.get("email", ""))
        self.entry_email.grid(row=4, column=1, sticky=tk.W, pady=3, padx=6)

        # Ubicación con opción seleccionable
        ttk.Label(grid, text="Ubicación:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.entry_ubicacion = ttk.Entry(grid, width=45)
        self.entry_ubicacion.insert(0, p.get("ubicacion", ""))
        self.entry_ubicacion.grid(row=5, column=1, sticky=tk.W, pady=3, padx=6)
        chk_ubicacion = ttk.Checkbutton(
            grid,
            text="Mostrar en el CV PDF descargable (si se desmarca, se omite por completo)",
            variable=self.var_mostrar_ubicacion
        )
        chk_ubicacion.grid(row=6, column=1, sticky=tk.W, pady=(0, 5), padx=6)

        # Perfil GitHub con opción seleccionable
        ttk.Label(grid, text="Perfil GitHub:").grid(row=7, column=0, sticky=tk.W, pady=3)
        self.entry_github = ttk.Entry(grid, width=45)
        self.entry_github.insert(0, p.get("github", ""))
        self.entry_github.grid(row=7, column=1, sticky=tk.W, pady=3, padx=6)
        chk_github = ttk.Checkbutton(
            grid,
            text="Mostrar en el CV PDF descargable (si se desmarca, se omite por completo)",
            variable=self.var_mostrar_github
        )
        chk_github.grid(row=8, column=1, sticky=tk.W, pady=(0, 5), padx=6)

        # Idiomas
        ttk.Label(grid, text="Idiomas:").grid(row=9, column=0, sticky=tk.W, pady=3)
        self.entry_idiomas = ttk.Entry(grid, width=45)
        self.entry_idiomas.insert(0, p.get("idiomas", ""))
        self.entry_idiomas.grid(row=9, column=1, sticky=tk.W, pady=3, padx=6)

        # Disponibilidad con opción seleccionable
        ttk.Label(grid, text="Disponibilidad:").grid(row=10, column=0, sticky=tk.W, pady=3)
        self.entry_disp = ttk.Entry(grid, width=45)
        self.entry_disp.insert(0, p.get("disponibilidad", ""))
        self.entry_disp.grid(row=10, column=1, sticky=tk.W, pady=3, padx=6)
        chk_disp = ttk.Checkbutton(
            grid,
            text="Mostrar en el CV PDF descargable (si se desmarca, se omite por completo)",
            variable=self.var_mostrar_disponibilidad
        )
        chk_disp.grid(row=11, column=1, sticky=tk.W, pady=(0, 5), padx=6)

        # 2. CREDENCIALES CLAVE Y LICENCIAS CON OPCIÓN SELECCIONABLE
        cred_box = ttk.LabelFrame(scrollable_frame, text=" 📜 Licencias y Certificaciones Clave (Texas TDLR, OSHA 30...) ", padding=10)
        cred_box.pack(fill=tk.X, pady=(0, 10))

        chk_licencias = ttk.Checkbutton(
            cred_box,
            text="Mostrar sección de Licencias en el CV PDF descargable (si se desmarca, se omite del documento)",
            variable=self.var_mostrar_licencias
        )
        chk_licencias.pack(anchor=tk.W, pady=(0, 6))

        ttk.Label(cred_box, text="Ingresa una credencial por línea (se mostrarán las que estén escritas aquí):", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W, pady=(0, 4))
        self.txt_credenciales = scrolledtext.ScrolledText(cred_box, height=5, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_credenciales.pack(fill=tk.X)
        self.txt_credenciales.insert("1.0", "\n".join(self.perfil.get("credenciales_clave", [])))

        # 3. RESUMEN PROFESIONAL BASE CON OPCIÓN POR DEFAULT O ACORDE AL PERFIL
        res_box = ttk.LabelFrame(scrollable_frame, text=" 📝 Resumen Profesional Base ", padding=10)
        res_box.pack(fill=tk.X, pady=(0, 10))

        chk_resumen = ttk.Checkbutton(
            res_box,
            text="Por default mostrar lo que está escrito aquí (si no se selecciona, crearlo acorde al perfil/oferta)",
            variable=self.var_usar_resumen_fijo
        )
        chk_resumen.pack(anchor=tk.W, pady=(0, 6))

        resumen_guardado = self.perfil.get("resumen_base_fijo")
        if not resumen_guardado:
            resumen_guardado = self.perfil.get("perfiles_especializados", {}).get("automatizacion", {}).get("resumen_es", "")

        self.txt_resumen = scrolledtext.ScrolledText(res_box, height=4, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_resumen.pack(fill=tk.X)
        self.txt_resumen.insert("1.0", resumen_guardado)

        # 4. FORMACIÓN ACADÉMICA Y MAESTRÍA (MBA) CON OPCIÓN SELECCIONABLE
        edu_box = ttk.LabelFrame(scrollable_frame, text=" 🎓 Formación Académica & Grados Universitarios (Maestría / MBA) ", padding=10)
        edu_box.pack(fill=tk.X, pady=(0, 10))

        chk_maestria = ttk.Checkbutton(
            edu_box,
            text="Incluir que tengo una Maestría en Administración de Empresas (MBA) en el CV PDF (desmarcar para omitirla por completo)",
            variable=self.var_mostrar_maestria
        )
        chk_maestria.pack(anchor=tk.W, pady=(0, 6))

        edu_info_frame = ttk.Frame(edu_box)
        edu_info_frame.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(edu_info_frame, text="Grados académicos registrados en tu perfil:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        for e in self.perfil.get("educacion", []):
            grado_txt = f"• {e.get('grado', '')} ({e.get('especialidad', '')}) — {e.get('institucion', '')} [{e.get('periodo', '')}]"
            ttk.Label(edu_info_frame, text=grado_txt, font=("Segoe UI", 8), foreground="#334155").pack(anchor=tk.W, padx=(10, 0), pady=1)

        # 5. IDIOMA PREDETERMINADO DEL CV PDF
        lang_box = ttk.LabelFrame(scrollable_frame, text=" 🌐 Idioma Predeterminado del CV PDF ", padding=10)
        lang_box.pack(fill=tk.X, pady=(0, 10))

        chk_en_ingles_base = ttk.Checkbutton(
            lang_box,
            text="En inglés (Generar por defecto el CV PDF 100% en inglés)",
            variable=self.var_en_ingles_default,
            command=self._on_check_en_ingles_default_changed
        )
        chk_en_ingles_base.pack(anchor=tk.W, pady=(0, 6))

        lang_row = ttk.Frame(lang_box)
        lang_row.pack(fill=tk.X)

        ttk.Label(lang_row, text="O seleccionar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            lang_row,
            text="🇲🇽 100% Español",
            value="es",
            variable=self.var_idioma_default,
            command=self._on_radio_idioma_default_changed
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            lang_row,
            text="🇺🇸 100% Inglés (English)",
            value="en",
            variable=self.var_idioma_default,
            command=self._on_radio_idioma_default_changed
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            lang_row,
            text="🤖 Auto-detectar según la vacante",
            value="auto",
            variable=self.var_idioma_default,
            command=self._on_radio_idioma_default_changed
        ).pack(side=tk.LEFT)

        # BOTÓN GUARDAR PERFIL
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_guardar = tk.Button(
            btn_frame,
            text="💾 Guardar Cambios y Preferencias en Mi Perfil Base",
            bg="#0f3460",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            command=self._guardar_perfil,
            cursor="hand2"
        )
        self.btn_guardar.pack(side=tk.RIGHT)

    def _on_check_en_ingles_default_changed(self):
        if self.var_en_ingles_default.get():
            self.var_idioma_default.set("en")
        else:
            self.var_idioma_default.set("es")

    def _on_radio_idioma_default_changed(self):
        self.var_en_ingles_default.set(self.var_idioma_default.get() == "en")

    def _guardar_perfil(self):
        try:
            self.perfil["datos_personales"]["nombre"] = self.entry_nombre.get().strip()
            self.perfil["datos_personales"]["titulo_principal"] = self.entry_titulo.get().strip()
            self.perfil["datos_personales"]["telefono"] = self.entry_tel.get().strip()
            self.perfil["datos_personales"]["email"] = self.entry_email.get().strip()
            self.perfil["datos_personales"]["ubicacion"] = self.entry_ubicacion.get().strip()
            self.perfil["datos_personales"]["github"] = self.entry_github.get().strip()
            self.perfil["datos_personales"]["idiomas"] = self.entry_idiomas.get().strip()
            self.perfil["datos_personales"]["disponibilidad"] = self.entry_disp.get().strip()

            creds = [c.strip() for c in self.txt_credenciales.get("1.0", tk.END).strip().splitlines() if c.strip()]
            self.perfil["credenciales_clave"] = creds

            resumen_texto = self.txt_resumen.get("1.0", tk.END).strip()
            self.perfil["resumen_base_fijo"] = resumen_texto

            # Guardar preferencias de visibilidad
            es_ingles = self.var_en_ingles_default.get() or (self.var_idioma_default.get() == "en")
            self.perfil["opciones_visibilidad"] = {
                "usar_titulo_fijo": self.var_usar_titulo_fijo.get(),
                "mostrar_ubicacion": self.var_mostrar_ubicacion.get(),
                "mostrar_github": self.var_mostrar_github.get(),
                "mostrar_disponibilidad": self.var_mostrar_disponibilidad.get(),
                "mostrar_licencias": self.var_mostrar_licencias.get(),
                "usar_resumen_fijo": self.var_usar_resumen_fijo.get(),
                "mostrar_maestria": self.var_mostrar_maestria.get(),
                "en_ingles": es_ingles,
                "idioma_predeterminado": "en" if es_ingles else self.var_idioma_default.get()
            }

            profile_data.save_user_profile(self.perfil)
            messagebox.showinfo("Perfil Guardado", "✅ Preferencias y datos de perfil base guardados exitosamente en user_profile.json.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el perfil:\n\n{str(e)}")

    def _seleccionar_pdf_base(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar Currículum Vitae en PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                ruta_copiada = pdf_profile_extractor.guardar_copia_cv_base(archivo)
                self.ruta_pdf_cv_base = ruta_copiada
                nombre = os.path.basename(ruta_copiada)
                self.lbl_pdf_cv_base.config(
                    text=f"📄 Archivo actual: {nombre}",
                    foreground="#0f3460",
                    font=("Segoe UI", 9, "bold")
                )
                self.btn_extraer_pdf.config(state=tk.NORMAL)
                self.btn_ver_pdf_base.config(state=tk.NORMAL)
                self.btn_quitar_pdf_base.config(state=tk.NORMAL)
                self.lbl_status_pdf.config(
                    text=f"PDF '{nombre}' cargado. Listo para extraer el perfil.",
                    foreground="#16a34a"
                )

                if messagebox.askyesno(
                    "CV PDF Cargado",
                    f"Se cargó '{nombre}'.\n\n¿Deseas que la Inteligencia Artificial analice y extraiga tu perfil desde este PDF ahora mismo?"
                ):
                    self._iniciar_extraccion_pdf_thread()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo PDF:\n\n{str(e)}")

    def _verificar_cola_tareas(self):
        """Revisa la cola de tareas en el hilo principal de Tkinter."""
        try:
            while not self._cola_tareas.empty():
                msg = self._cola_tareas.get_nowait()
                m_type = msg.get("tipo")
                if m_type == "exito_extraccion":
                    perfil_actualizado = msg.get("perfil")
                    self.prog_bar_pdf.stop()
                    self.prog_bar_pdf.pack_forget()
                    self.btn_subir_pdf.config(state=tk.NORMAL)
                    self.btn_extraer_pdf.config(state=tk.NORMAL)
                    self.btn_ver_pdf_base.config(state=tk.NORMAL)
                    self.btn_quitar_pdf_base.config(state=tk.NORMAL)

                    self._refrescar_formulario_con_perfil(perfil_actualizado)
                    self.lbl_status_pdf.config(
                        text="✅ Perfil extraído e importado exitosamente desde el PDF.",
                        foreground="#16a34a"
                    )
                    messagebox.showinfo(
                        "Extracción Exitosa",
                        "✅ ¡Tu perfil base se ha actualizado a partir del CV en PDF!\n\n"
                        "Todos los datos personales, licencias y resumen se han cargado en el formulario y guardado en user_profile.json.\n\n"
                        "Los nuevos CVs descargables se generarán tomando como base esta información."
                    )
                elif m_type == "error_extraccion":
                    err = msg.get("error", "Error desconocido")
                    self.prog_bar_pdf.stop()
                    self.prog_bar_pdf.pack_forget()
                    self.btn_subir_pdf.config(state=tk.NORMAL)
                    self.btn_extraer_pdf.config(state=tk.NORMAL)
                    self.btn_ver_pdf_base.config(state=tk.NORMAL)
                    self.btn_quitar_pdf_base.config(state=tk.NORMAL)
                    self.lbl_status_pdf.config(
                        text="❌ Error al extraer el perfil del PDF.",
                        foreground="#dc2626"
                    )
                    messagebox.showerror("Error de Extracción", f"No se pudo extraer el perfil del PDF:\n\n{err}")
        except Exception as e:
            print(f"Error procesando cola de tab_perfil: {e}")
        finally:
            self.after(80, self._verificar_cola_tareas)

    def _iniciar_extraccion_pdf_thread(self):
        if not self.ruta_pdf_cv_base:
            messagebox.showwarning("Atención", "Por favor selecciona primero un archivo PDF.")
            return

        self.btn_subir_pdf.config(state=tk.DISABLED)
        self.btn_extraer_pdf.config(state=tk.DISABLED)
        self.btn_ver_pdf_base.config(state=tk.DISABLED)
        self.btn_quitar_pdf_base.config(state=tk.DISABLED)

        self.lbl_status_pdf.config(
            text="Extrayendo texto y estructurando tu perfil con Inteligencia Artificial...",
            foreground="#ea580c"
        )
        self.prog_bar_pdf.pack(fill=tk.X, pady=(2, 6))
        self.prog_bar_pdf.start(10)

        ruta = self.ruta_pdf_cv_base
        t = threading.Thread(
            target=self._procesar_extraccion_pdf_worker,
            args=(ruta,),
            daemon=True
        )
        t.start()

    def _procesar_extraccion_pdf_worker(self, ruta_pdf):
        """Worker en hilo secundario. 100% libre de llamadas a Tkinter."""
        try:
            texto = pdf_profile_extractor.extraer_texto_de_pdf(ruta_pdf)
            datos_extraidos = pdf_profile_extractor.estructurar_perfil_con_ia(texto, ruta_pdf)
            perfil_actualizado = profile_data.actualizar_perfil_desde_datos_extraidos(
                datos_extraidos, ruta_pdf, texto
            )
            self._cola_tareas.put({
                "tipo": "exito_extraccion",
                "perfil": perfil_actualizado
            })
        except Exception as e:
            self._cola_tareas.put({
                "tipo": "error_extraccion",
                "error": str(e)
            })

    def _refrescar_formulario_con_perfil(self, perfil):
        self.perfil = perfil
        p = perfil.get("datos_personales", {})

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, p.get("nombre", ""))

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, p.get("titulo_principal", ""))

        self.entry_tel.delete(0, tk.END)
        self.entry_tel.insert(0, p.get("telefono", ""))

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, p.get("email", ""))

        self.entry_ubicacion.delete(0, tk.END)
        self.entry_ubicacion.insert(0, p.get("ubicacion", ""))

        self.entry_github.delete(0, tk.END)
        self.entry_github.insert(0, p.get("github", ""))

        self.entry_idiomas.delete(0, tk.END)
        self.entry_idiomas.insert(0, p.get("idiomas", ""))

        self.entry_disp.delete(0, tk.END)
        self.entry_disp.insert(0, p.get("disponibilidad", ""))

        self.txt_credenciales.delete("1.0", tk.END)
        self.txt_credenciales.insert("1.0", "\n".join(perfil.get("credenciales_clave", [])))

        self.txt_resumen.delete("1.0", tk.END)
        self.txt_resumen.insert("1.0", perfil.get("resumen_base_fijo", ""))

        opc = perfil.get("opciones_visibilidad", {})
        self.var_usar_titulo_fijo.set(opc.get("usar_titulo_fijo", False))
        self.var_mostrar_ubicacion.set(opc.get("mostrar_ubicacion", True))
        self.var_mostrar_github.set(opc.get("mostrar_github", True))
        self.var_mostrar_disponibilidad.set(opc.get("mostrar_disponibilidad", True))
        self.var_mostrar_licencias.set(opc.get("mostrar_licencias", True))
        self.var_usar_resumen_fijo.set(opc.get("usar_resumen_fijo", True))
        self.var_idioma_default.set(opc.get("idioma_predeterminado", "auto"))

    def _abrir_pdf_base(self):
        if self.ruta_pdf_cv_base and os.path.exists(self.ruta_pdf_cv_base):
            abrir_pdf_en_sistema(self.ruta_pdf_cv_base)
        else:
            messagebox.showwarning("Aviso", "No se encontró el archivo PDF para abrir.")

    def _quitar_pdf_base(self):
        if messagebox.askyesno("Quitar PDF Base", "¿Deseas desvincular el archivo PDF del perfil base?"):
            self.ruta_pdf_cv_base = ""
            self.perfil["ruta_cv_base_pdf"] = ""
            self.perfil["texto_cv_base_extraido"] = ""
            profile_data.save_user_profile(self.perfil)
            self.lbl_pdf_cv_base.config(
                text="Ningún archivo PDF cargado como CV base.",
                foreground="#64748b",
                font=("Segoe UI", 9, "normal")
            )
            self.btn_extraer_pdf.config(state=tk.DISABLED)
            self.btn_ver_pdf_base.config(state=tk.DISABLED)
            self.btn_quitar_pdf_base.config(state=tk.DISABLED)
            self.lbl_status_pdf.config(
                text="PDF desvinculado.",
                foreground="#475569"
            )
