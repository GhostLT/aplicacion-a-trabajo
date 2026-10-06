import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import profile_data

class TabPerfil(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.perfil = profile_data.load_user_profile()
        self._crear_interfaz()

    def _crear_interfaz(self):
        # Frame contenedor con scroll para soportar pantallas de diferentes tamaños
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

        # 1. DATOS PERSONALES Y CONTACTO
        datos_box = ttk.LabelFrame(scrollable_frame, text=" 👤 Datos de Contacto y Perfil Base ", padding=10)
        datos_box.pack(fill=tk.X, pady=(0, 10))

        p = self.perfil.get("datos_personales", {})

        grid = ttk.Frame(datos_box)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Nombre Completo:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_nombre = ttk.Entry(grid, width=45)
        self.entry_nombre.insert(0, p.get("nombre", ""))
        self.entry_nombre.grid(row=0, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Título Principal:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_titulo = ttk.Entry(grid, width=45)
        self.entry_titulo.insert(0, p.get("titulo_principal", ""))
        self.entry_titulo.grid(row=1, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Teléfono / WhatsApp:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.entry_tel = ttk.Entry(grid, width=45)
        self.entry_tel.insert(0, p.get("telefono", ""))
        self.entry_tel.grid(row=2, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Correo Electrónico:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.entry_email = ttk.Entry(grid, width=45)
        self.entry_email.insert(0, p.get("email", ""))
        self.entry_email.grid(row=3, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Ubicación:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.entry_ubicacion = ttk.Entry(grid, width=45)
        self.entry_ubicacion.insert(0, p.get("ubicacion", ""))
        self.entry_ubicacion.grid(row=4, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Perfil GitHub:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.entry_github = ttk.Entry(grid, width=45)
        self.entry_github.insert(0, p.get("github", ""))
        self.entry_github.grid(row=5, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Idiomas:").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.entry_idiomas = ttk.Entry(grid, width=45)
        self.entry_idiomas.insert(0, p.get("idiomas", ""))
        self.entry_idiomas.grid(row=6, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid, text="Disponibilidad:").grid(row=7, column=0, sticky=tk.W, pady=3)
        self.entry_disp = ttk.Entry(grid, width=45)
        self.entry_disp.insert(0, p.get("disponibilidad", ""))
        self.entry_disp.grid(row=7, column=1, sticky=tk.W, pady=3, padx=6)

        # 2. CREDENCIALES CLAVE Y LICENCIAS
        cred_box = ttk.LabelFrame(scrollable_frame, text=" 📜 Licencias y Certificaciones Clave (Texas TDLR, OSHA 30...) ", padding=10)
        cred_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(cred_box, text="Ingresa una credencial por línea:", font=("Segoe UI", 8, "italic")).pack(anchor=tk.W, pady=(0, 4))
        self.txt_credenciales = scrolledtext.ScrolledText(cred_box, height=5, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_credenciales.pack(fill=tk.X)
        self.txt_credenciales.insert("1.0", "\n".join(self.perfil.get("credenciales_clave", [])))

        # 3. RESUMEN PROFESIONAL PREDETERMINADO
        res_box = ttk.LabelFrame(scrollable_frame, text=" 📝 Resumen Profesional Base ", padding=10)
        res_box.pack(fill=tk.X, pady=(0, 10))

        aut_prof = self.perfil.get("perfiles_especializados", {}).get("automatizacion", {})
        self.txt_resumen = scrolledtext.ScrolledText(res_box, height=4, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_resumen.pack(fill=tk.X)
        self.txt_resumen.insert("1.0", aut_prof.get("resumen_es", ""))

        # BOTÓN GUARDAR PERFIL
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_guardar = tk.Button(
            btn_frame,
            text="💾 Guardar Cambios en Mi Perfil Base",
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

            res = self.txt_resumen.get("1.0", tk.END).strip()
            if "automatizacion" in self.perfil.get("perfiles_especializados", {}):
                self.perfil["perfiles_especializados"]["automatizacion"]["resumen_es"] = res

            profile_data.save_user_profile(self.perfil)
            messagebox.showinfo("Perfil Guardado", "✅ Los datos de tu perfil base han sido actualizados y guardados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el perfil:\n\n{str(e)}")
