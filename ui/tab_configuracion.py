import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import config
import database

class TabConfiguracion(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
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

        # 1. BASE DE DATOS MARIADB
        db_box = ttk.LabelFrame(scrollable_frame, text=" 🐬 Conexión a Base de Datos MariaDB ", padding=10)
        db_box.pack(fill=tk.X, pady=(0, 12))

        grid_db = ttk.Frame(db_box)
        grid_db.pack(fill=tk.X)

        ttk.Label(grid_db, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_host = ttk.Entry(grid_db, width=30)
        self.entry_host.insert(0, config.DB_HOST)
        self.entry_host.grid(row=0, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid_db, text="Puerto:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_port = ttk.Entry(grid_db, width=30)
        self.entry_port.insert(0, str(config.DB_PORT))
        self.entry_port.grid(row=1, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid_db, text="Usuario:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.entry_user = ttk.Entry(grid_db, width=30)
        self.entry_user.insert(0, config.DB_USER)
        self.entry_user.grid(row=2, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid_db, text="Contraseña:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.entry_pass = ttk.Entry(grid_db, width=30, show="*")
        self.entry_pass.insert(0, config.DB_PASSWORD)
        self.entry_pass.grid(row=3, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Label(grid_db, text="Base de Datos:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.entry_dbname = ttk.Entry(grid_db, width=30)
        self.entry_dbname.insert(0, config.DB_NAME)
        self.entry_dbname.grid(row=4, column=1, sticky=tk.W, pady=3, padx=6)

        btn_db_frame = ttk.Frame(db_box)
        btn_db_frame.pack(fill=tk.X, pady=(10, 4))

        self.btn_probar_db = ttk.Button(btn_db_frame, text="🔌 Probar Conexión MariaDB", command=self._probar_conexion_db)
        self.btn_probar_db.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_init_db = ttk.Button(btn_db_frame, text="🔄 Crear / Verificar Tablas", command=self._inicializar_tablas_db)
        self.btn_init_db.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_guardar_db = ttk.Button(btn_db_frame, text="💾 Guardar Cambios DB en .env", command=self._guardar_credenciales_db)
        self.btn_guardar_db.pack(side=tk.LEFT)

        self.lbl_db_status = ttk.Label(db_box, text="Estado: No comprobado.", font=("Segoe UI", 8, "italic"))
        self.lbl_db_status.pack(anchor=tk.W, pady=(6, 0))

        # 2. GOOGLE GEMINI API
        ai_box = ttk.LabelFrame(scrollable_frame, text=" 🤖 Inteligencia Artificial (Google Gemini API) ", padding=10)
        ai_box.pack(fill=tk.X, pady=(0, 12))

        grid_ai = ttk.Frame(ai_box)
        grid_ai.pack(fill=tk.X)

        ttk.Label(grid_ai, text="Clave API (GEMINI_API_KEY):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_gemini_key = ttk.Entry(grid_ai, width=50, show="*")
        self.entry_gemini_key.insert(0, config.GEMINI_API_KEY)
        self.entry_gemini_key.grid(row=0, column=1, sticky=tk.W, pady=3, padx=6)

        self.var_show_key = tk.BooleanVar(value=False)
        chk_show = ttk.Checkbutton(grid_ai, text="Mostrar clave", variable=self.var_show_key, command=self._toggle_ver_key)
        chk_show.grid(row=0, column=2, padx=4)

        ttk.Label(grid_ai, text="Modelo de Gemini:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.combo_model = ttk.Combobox(
            grid_ai,
            values=["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
            width=28,
            state="readonly"
        )
        self.combo_model.set(config.GEMINI_MODEL)
        self.combo_model.grid(row=1, column=1, sticky=tk.W, pady=3, padx=6)

        btn_ai_frame = ttk.Frame(ai_box)
        btn_ai_frame.pack(fill=tk.X, pady=(10, 4))

        self.btn_guardar_ai = ttk.Button(btn_ai_frame, text="💾 Guardar Clave y Modelo en .env", command=self._guardar_gemini_config)
        self.btn_guardar_ai.pack(side=tk.LEFT)

        # 3. CONVERSIÓN DE PDF (MICROSOFT EDGE)
        edge_box = ttk.LabelFrame(scrollable_frame, text=" 🌐 Motor de Conversión de PDF (Microsoft Edge) ", padding=10)
        edge_box.pack(fill=tk.X, pady=(0, 12))

        grid_edge = ttk.Frame(edge_box)
        grid_edge.pack(fill=tk.X)

        ttk.Label(grid_edge, text="Ruta de msedge.exe:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_edge = ttk.Entry(grid_edge, width=50)
        self.entry_edge.insert(0, config.EDGE_PATH)
        self.entry_edge.grid(row=0, column=1, sticky=tk.W, pady=3, padx=6)

        ttk.Button(grid_edge, text="Examinar...", command=self._examinar_edge).grid(row=0, column=2, padx=4)

        ttk.Button(edge_box, text="💾 Guardar Ruta Edge", command=self._guardar_edge_config).pack(anchor=tk.W, pady=(8, 0))

    def _toggle_ver_key(self):
        if self.var_show_key.get():
            self.entry_gemini_key.config(show="")
        else:
            self.entry_gemini_key.config(show="*")

    def _probar_conexion_db(self):
        ok, msg = database.probar_conexion()
        if ok:
            self.lbl_db_status.config(text=f"✅ {msg}", foreground="#16a34a")
            messagebox.showinfo("Conexión Exitosa", msg)
        else:
            self.lbl_db_status.config(text=f"❌ {msg}", foreground="#dc2626")
            messagebox.showerror("Error de Conexión", msg)

    def _inicializar_tablas_db(self):
        ok, msg = database.inicializar_base_datos()
        if ok:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def _guardar_credenciales_db(self):
        try:
            config.update_env_variable("DB_HOST", self.entry_host.get().strip())
            config.update_env_variable("DB_PORT", self.entry_port.get().strip())
            config.update_env_variable("DB_USER", self.entry_user.get().strip())
            config.update_env_variable("DB_PASSWORD", self.entry_pass.get().strip())
            config.update_env_variable("DB_NAME", self.entry_dbname.get().strip())
            messagebox.showinfo("Configuración Guardada", "Credenciales de MariaDB guardadas en .env y recargadas.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")

    def _guardar_gemini_config(self):
        try:
            config.update_env_variable("GEMINI_API_KEY", self.entry_gemini_key.get().strip())
            config.update_env_variable("GEMINI_MODEL", self.combo_model.get().strip())
            messagebox.showinfo("Configuración Guardada", "Clave y modelo de Gemini guardados en .env.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la clave: {e}")

    def _examinar_edge(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de Microsoft Edge o Chrome",
            filetypes=[("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")]
        )
        if ruta:
            self.entry_edge.delete(0, tk.END)
            self.entry_edge.insert(0, ruta)

    def _guardar_edge_config(self):
        try:
            config.update_env_variable("EDGE_PATH", self.entry_edge.get().strip())
            messagebox.showinfo("Configuración Guardada", "Ruta de Microsoft Edge guardada en .env.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la ruta: {e}")
