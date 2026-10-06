import os
import threading
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pyperclip

import generator
import database
from pdf_engine import abrir_pdf_en_sistema, descargar_pdf_a_ruta

class TabNuevaPostulacion(ttk.Frame):
    def __init__(self, parent, on_guardado_callback=None):
        super().__init__(parent)
        self.on_guardado_callback = on_guardado_callback
        self.resultado_actual = None

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

        # Pegar descripción de la oferta
        ttk.Label(frame_izq, text="Pega aquí la descripción completa de la vacante (LinkedIn, OCC, Indeed...):", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W, pady=(4, 2))
        self.txt_oferta = scrolledtext.ScrolledText(frame_izq, height=12, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_oferta.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Opciones y Botón de procesamiento
        btn_frame = ttk.Frame(frame_izq)
        btn_frame.pack(fill=tk.X, pady=4)

        self.var_usar_ia = tk.BooleanVar(value=True)
        self.chk_ia = ttk.Checkbutton(btn_frame, text="Usar IA de Gemini para maximizar ATS", variable=self.var_usar_ia)
        self.chk_ia.pack(side=tk.LEFT)

        self.btn_generar = tk.Button(
            btn_frame,
            text="⚡ Analizar Oferta y Generar CV + Correo",
            bg="#1a56db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=self._iniciar_generacion_thread,
            cursor="hand2"
        )
        self.btn_generar.pack(side=tk.RIGHT)

        # Barra de progreso / Estado
        self.lbl_status = ttk.Label(frame_izq, text="Listo para procesar oferta.", font=("Segoe UI", 8, "italic"), foreground="#4a5568")
        self.lbl_status.pack(anchor=tk.W, pady=(4, 0))
        self.prog_bar = ttk.Progressbar(frame_izq, mode="indeterminate")

        # --- CONTENIDO COLUMNA DERECHA ---
        notebook_res = ttk.Notebook(frame_der)
        notebook_res.pack(fill=tk.BOTH, expand=True)

        # Pestaña Correo
        tab_correo = ttk.Frame(notebook_res, padding=8)
        notebook_res.add(tab_correo, text=" ✉️ Correo de Postulación ")

        # Asunto
        asunto_frame = ttk.Frame(tab_correo)
        asunto_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(asunto_frame, text="Asunto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.entry_asunto = ttk.Entry(asunto_frame, font=("Segoe UI", 9))
        self.entry_asunto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(asunto_frame, text="📋 Copiar", width=9, command=self._copiar_asunto).pack(side=tk.RIGHT)

        # Cuerpo del correo
        ttk.Label(tab_correo, text="Cuerpo del Correo (Listo para enviar):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        self.txt_correo = scrolledtext.ScrolledText(tab_correo, height=12, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_correo.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # Botones de acción del correo
        acciones_correo = ttk.Frame(tab_correo)
        acciones_correo.pack(fill=tk.X)
        ttk.Button(acciones_correo, text="📋 Copiar Cuerpo del Correo", command=self._copiar_correo).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(acciones_correo, text="📨 Abrir en Cliente de Correo", command=self._abrir_en_correo).pack(side=tk.LEFT)

        # Pestaña CV PDF
        tab_pdf = ttk.Frame(notebook_res, padding=10)
        notebook_res.add(tab_pdf, text=" 📄 CV PDF Generado ")

        info_box = ttk.LabelFrame(tab_pdf, text=" Estado del Documento PDF ", padding=10)
        info_box.pack(fill=tk.X, pady=(0, 10))

        self.lbl_pdf_ruta = ttk.Label(info_box, text="Aún no se ha generado ningún PDF.", wraplength=420, font=("Segoe UI", 9))
        self.lbl_pdf_ruta.pack(anchor=tk.W, pady=4)

        self.lbl_pdf_detalles = ttk.Label(info_box, text="", font=("Segoe UI", 8, "italic"), foreground="#4a5568")
        self.lbl_pdf_detalles.pack(anchor=tk.W)

        # Botones para el PDF
        pdf_btns = ttk.Frame(tab_pdf)
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
            messagebox.showwarning("Atención", "Por favor pega la descripción de la oferta laboral antes de generar.")
            return

        self.btn_generar.config(state=tk.DISABLED)
        self.lbl_status.config(text="Procesando oferta, adaptando perfil y renderizando PDF...")
        self.prog_bar.pack(fill=tk.X, pady=(2, 6))
        self.prog_bar.start(10)

        t = threading.Thread(target=self._generar_cv_proceso, daemon=True)
        t.start()

    def _generar_cv_proceso(self):
        try:
            datos_oferta = {
                "empresa": self.entry_empresa.get().strip() or "Empresa Confidencial",
                "titulo_puesto": self.entry_puesto.get().strip() or "Especialista Técnico",
                "ubicacion": self.entry_ubicacion.get().strip(),
                "url_oferta": self.entry_url.get().strip(),
                "descripcion_oferta": self.txt_oferta.get("1.0", tk.END).strip(),
                "perfil_aplicado": self.perfiles_map[self.combo_perfil.get()],
                "idioma": self.idiomas_map[self.combo_idioma.get()]
            }

            usar_ia = self.var_usar_ia.get()
            resultado = generator.procesar_postulacion_completa(datos_oferta, usar_ia=usar_ia)

            # Actualizar GUI en el hilo principal
            self.after(0, lambda: self._mostrar_resultados(resultado))
        except Exception as e:
            self.after(0, lambda: self._manejar_error(str(e)))

    def _mostrar_resultados(self, resultado):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_generar.config(state=tk.NORMAL)
        self.resultado_actual = resultado

        # Cargar correo
        self.entry_asunto.delete(0, tk.END)
        self.entry_asunto.insert(0, resultado["asunto_correo"])

        self.txt_correo.delete("1.0", tk.END)
        self.txt_correo.insert("1.0", resultado["cuerpo_correo"])

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

        self.lbl_status.config(text="✅ CV y correo generados con éxito.", foreground="#16a34a")

    def _manejar_error(self, error_msg):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.btn_generar.config(state=tk.NORMAL)
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
            "notas": self.entry_notas.get().strip()
        }

        try:
            nuevo_id = database.guardar_aplicacion(datos_guardar)
            messagebox.showinfo(
                "Guardado en MariaDB",
                f"✅ Postulación guardada con éxito en la base de datos (ID #{nuevo_id}).\n\n"
                f"Fase: {datos_guardar['estado']}\n"
                f"Empresa: {datos_guardar['empresa']}"
            )
            self.btn_guardar_bd.config(state=tk.DISABLED)

            if self.on_guardado_callback:
                self.on_guardado_callback()
        except Exception as e:
            messagebox.showerror("Error en MariaDB", f"No se pudo guardar en la base de datos:\n\n{str(e)}")
