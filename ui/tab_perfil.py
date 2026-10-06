import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import profile_data

class TabPerfil(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.perfil = profile_data.load_user_profile()
        self._crear_interfaz()

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
            self.perfil["opciones_visibilidad"] = {
                "usar_titulo_fijo": self.var_usar_titulo_fijo.get(),
                "mostrar_ubicacion": self.var_mostrar_ubicacion.get(),
                "mostrar_github": self.var_mostrar_github.get(),
                "mostrar_disponibilidad": self.var_mostrar_disponibilidad.get(),
                "mostrar_licencias": self.var_mostrar_licencias.get(),
                "usar_resumen_fijo": self.var_usar_resumen_fijo.get()
            }

            profile_data.save_user_profile(self.perfil)
            messagebox.showinfo("Perfil Guardado", "✅ Preferencias y datos de perfil base guardados exitosamente en user_profile.json.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el perfil:\n\n{str(e)}")
