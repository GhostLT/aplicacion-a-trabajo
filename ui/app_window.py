import tkinter as tk
from tkinter import ttk
import config
import database
from ui.tab_nueva_postulacion import TabNuevaPostulacion
from ui.tab_historial import TabHistorial
from ui.tab_perfil import TabPerfil
from ui.tab_configuracion import TabConfiguracion

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PostulaPro - Generador de CVs ATS & Gestor de Postulaciones")
        self.geometry("1180x760")
        self.minsize(980, 640)

        # Configuración visual
        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_pestanas()
        self._crear_barra_estado()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Colores principales
        style.configure("TNotebook", background="#f8fafc", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[14, 7], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab",
            background=[("selected", "#0f3460"), ("active", "#e2e8f0")],
            foreground=[("selected", "#ffffff"), ("active", "#0f3460")]
        )

        style.configure("TLabelFrame", font=("Segoe UI", 9, "bold"), foreground="#0f3460")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0", foreground="#0f3460")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    def _crear_encabezado(self):
        header_frame = tk.Frame(self, bg="#0f3460", padx=16, pady=10)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="💼 PostulaPro - Generador de CVs ATS & Gestor de Postulaciones",
            font=("Segoe UI", 14, "bold"),
            fg="#ffffff",
            bg="#0f3460"
        )
        title_lbl.pack(anchor=tk.W)

        sub_lbl = tk.Label(
            header_frame,
            text="Javier Viveros Huesca | Base de Datos MariaDB | Adaptación Inteligente & Control de Fases",
            font=("Segoe UI", 8),
            fg="#93c5fd",
            bg="#0f3460"
        )
        sub_lbl.pack(anchor=tk.W)

    def _crear_pestanas(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Pestaña 2 primero para tener referencia para el callback
        self.tab_historial = TabHistorial(self.notebook)

        # Pestaña 1: Nueva Postulación
        self.tab_nueva = TabNuevaPostulacion(self.notebook, on_guardado_callback=self._on_postulacion_guardada)
        self.notebook.add(self.tab_nueva, text=" ➕ Nueva Postulación ")

        # Añadir Historial al notebook
        self.notebook.add(self.tab_historial, text=" 📊 Historial & Fases de Contratación ")

        # Pestaña 3: Perfil Base
        self.tab_perfil = TabPerfil(self.notebook)
        self.notebook.add(self.tab_perfil, text=" 👤 Mi Perfil Base ")

        # Pestaña 4: Configuración & DB
        self.tab_config = TabConfiguracion(self.notebook)
        self.notebook.add(self.tab_config, text=" ⚙️ Configuración & Base de Datos ")

        # Evento al cambiar de pestaña para refrescar datos
        self.notebook.bind("<<NotebookTabChanged>>", self._on_cambio_pestana)

    def _on_postulacion_guardada(self):
        """Al guardar una nueva postulación, refrescar historial y cambiar a la pestaña de historial."""
        self.tab_historial.recargar_datos()
        self.notebook.select(self.tab_historial)

    def _on_cambio_pestana(self, event):
        tab_actual = self.notebook.select()
        if tab_actual == str(self.tab_historial):
            self.tab_historial.recargar_datos()
        elif tab_actual == str(self.tab_nueva):
            self.tab_nueva.sincronizar_con_perfil()

    def _crear_barra_estado(self):
        self.status_bar = tk.Frame(self, bg="#e2e8f0", padx=10, pady=4)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        ok_db, msg_db = database.probar_conexion()
        db_text = f"🐬 MariaDB: {config.DB_NAME} (Conectado)" if ok_db else "🐬 MariaDB: Desconectado"

        self.lbl_status_db = tk.Label(self.status_bar, text=db_text, font=("Segoe UI", 8), bg="#e2e8f0", fg="#16a34a" if ok_db else "#dc2626")
        self.lbl_status_db.pack(side=tk.LEFT, padx=6)

        ai_status = f"🤖 IA: {config.GEMINI_MODEL}" if config.GEMINI_API_KEY else "🤖 IA: Modo Local"
        self.lbl_status_ai = tk.Label(self.status_bar, text=ai_status, font=("Segoe UI", 8), bg="#e2e8f0", fg="#475569")
        self.lbl_status_ai.pack(side=tk.LEFT, padx=12)

        ruta_info = f"📁 {config.BASE_DIR}"
        lbl_dir = tk.Label(self.status_bar, text=ruta_info, font=("Segoe UI", 8), bg="#e2e8f0", fg="#64748b")
        lbl_dir.pack(side=tk.RIGHT, padx=6)
