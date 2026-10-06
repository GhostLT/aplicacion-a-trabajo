import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import pyperclip

import database
from pdf_engine import abrir_pdf_en_sistema, descargar_pdf_a_ruta

class TabHistorial(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.aplicaciones_cargadas = []
        self._crear_interfaz()
        self.recargar_datos()

    def _crear_interfaz(self):
        # 1. TARJETAS DE ESTADÍSTICAS (KPIs)
        kpi_frame = ttk.LabelFrame(self, text=" 📊 Métricas por Fase de Contratación ", padding=8)
        kpi_frame.pack(fill=tk.X, padx=10, pady=(8, 4))

        self.kpi_labels = {}
        estados_kpi = [
            ("Total", "#0f3460"),
            ("Sin aplicar", "#64748b"),
            ("En proceso (enviado)", "#2563eb"),
            ("En entrevista", "#7c3aed"),
            ("Rechazado", "#dc2626"),
            ("Oferta recibida", "#16a34a")
        ]

        for idx, (nombre, color) in enumerate(estados_kpi):
            card = tk.Frame(kpi_frame, bg="#f1f5f9", padx=10, pady=6, relief=tk.GROOVE, bd=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            lbl_title = tk.Label(card, text=nombre, font=("Segoe UI", 8, "bold"), fg=color, bg="#f1f5f9")
            lbl_title.pack()

            lbl_val = tk.Label(card, text="0", font=("Segoe UI", 13, "bold"), fg="#1e293b", bg="#f1f5f9")
            lbl_val.pack()
            self.kpi_labels[nombre] = lbl_val

        # 2. BARRA DE FILTROS Y BÚSQUEDA
        toolbar = ttk.Frame(self, padding=6)
        toolbar.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(toolbar, text="Filtrar por Fase:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_filtro_estado = ttk.Combobox(
            toolbar,
            values=["Todos", "Sin aplicar", "En proceso (enviado)", "En entrevista", "Rechazado", "Oferta recibida"],
            state="readonly",
            width=20
        )
        self.combo_filtro_estado.current(0)
        self.combo_filtro_estado.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_filtro_estado.bind("<<ComboboxSelected>>", lambda e: self.recargar_datos())

        ttk.Label(toolbar, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_busqueda = ttk.Entry(toolbar, width=25)
        self.entry_busqueda.pack(side=tk.LEFT, padx=(0, 6))
        self.entry_busqueda.bind("<Return>", lambda e: self.recargar_datos())

        ttk.Button(toolbar, text="🔍 Buscar", command=self.recargar_datos).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(toolbar, text="❌ Limpiar", command=self._limpiar_busqueda).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(toolbar, text="🔄 Refrescar", command=self.recargar_datos).pack(side=tk.RIGHT)

        # 3. TABLA DE APLICACIONES (Treeview)
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        columnas = ("id", "fecha", "empresa", "puesto", "ubicacion", "estado", "perfil", "pdf")
        self.tree = ttk.Treeview(table_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("empresa", text="Empresa")
        self.tree.heading("puesto", text="Puesto")
        self.tree.heading("ubicacion", text="Ubicación")
        self.tree.heading("estado", text="Fase Actual")
        self.tree.heading("perfil", text="Perfil")
        self.tree.heading("pdf", text="Archivo PDF")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("fecha", width=110, anchor=tk.CENTER)
        self.tree.column("empresa", width=140, anchor=tk.W)
        self.tree.column("puesto", width=180, anchor=tk.W)
        self.tree.column("ubicacion", width=120, anchor=tk.W)
        self.tree.column("estado", width=140, anchor=tk.CENTER)
        self.tree.column("perfil", width=110, anchor=tk.CENTER)
        self.tree.column("pdf", width=180, anchor=tk.W)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self._ver_detalle_seleccionado())
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        # 4. BARRA DE ACCIONES PARA EL REGISTRO SELECCIONADO
        action_bar = ttk.LabelFrame(self, text=" Acciones sobre la Postulación Seleccionada ", padding=8)
        action_bar.pack(fill=tk.X, padx=10, pady=(4, 8))

        # Cambiar fase
        fase_box = ttk.Frame(action_bar)
        fase_box.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(fase_box, text="Cambiar Fase:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.combo_cambiar_fase = ttk.Combobox(
            fase_box,
            values=["Sin aplicar", "En proceso (enviado)", "En entrevista", "Rechazado", "Oferta recibida"],
            state="readonly",
            width=18
        )
        self.combo_cambiar_fase.current(1)
        self.combo_cambiar_fase.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_cambiar_fase = ttk.Button(fase_box, text="Actualizar Fase", command=self._actualizar_fase, state=tk.DISABLED)
        self.btn_cambiar_fase.pack(side=tk.LEFT)

        # Botones de visualización y archivos
        self.btn_ver_detalle = ttk.Button(action_bar, text="👁️ Ver Correo & Detalle", command=self._ver_detalle_seleccionado, state=tk.DISABLED)
        self.btn_ver_detalle.pack(side=tk.LEFT, padx=4)

        self.btn_abrir_pdf = ttk.Button(action_bar, text="📂 Abrir PDF", command=self._abrir_pdf_seleccionado, state=tk.DISABLED)
        self.btn_abrir_pdf.pack(side=tk.LEFT, padx=4)

        self.btn_descargar_pdf = ttk.Button(action_bar, text="📥 Descargar PDF", command=self._descargar_pdf_seleccionado, state=tk.DISABLED)
        self.btn_descargar_pdf.pack(side=tk.LEFT, padx=4)

        self.btn_editar_notas = ttk.Button(action_bar, text="📝 Notas", command=self._editar_notas_seleccionado, state=tk.DISABLED)
        self.btn_editar_notas.pack(side=tk.LEFT, padx=4)

        self.btn_eliminar = tk.Button(
            action_bar,
            text="🗑️ Eliminar",
            bg="#ef4444",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=3,
            command=self._eliminar_seleccionado,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.btn_eliminar.pack(side=tk.RIGHT)

    def _limpiar_busqueda(self):
        self.entry_busqueda.delete(0, tk.END)
        self.combo_filtro_estado.current(0)
        self.recargar_datos()

    def recargar_datos(self):
        """Carga las aplicaciones desde MariaDB y actualiza la tabla y las métricas."""
        filtro = self.combo_filtro_estado.get()
        busqueda = self.entry_busqueda.get().strip()

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Obtener datos de BD
            self.aplicaciones_cargadas = database.obtener_todas_aplicaciones(
                filtro_estado=filtro,
                busqueda=busqueda
            )

            # Insertar en treeview
            for app in self.aplicaciones_cargadas:
                fecha_str = str(app["fecha_creacion"])[:10] if app.get("fecha_creacion") else ""
                pdf_name = os.path.basename(app["ruta_pdf"]) if app.get("ruta_pdf") else "Sin PDF"

                self.tree.insert("", tk.END, iid=str(app["id"]), values=(
                    app["id"],
                    fecha_str,
                    app["empresa"],
                    app["titulo_puesto"],
                    app.get("ubicacion", ""),
                    app["estado"],
                    app.get("perfil_aplicado", ""),
                    pdf_name
                ))

            # Actualizar KPIs
            stats = database.obtener_estadisticas_fases()
            for k, lbl in self.kpi_labels.items():
                lbl.config(text=str(stats.get(k, 0)))

        except Exception as e:
            messagebox.showerror("Error al Cargar Datos", f"No se pudo consultar MariaDB:\n\n{str(e)}")

        self._deshabilitar_acciones()

    def _on_select_row(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            self._deshabilitar_acciones()
            return

        app_id = int(seleccion[0])
        app = self._buscar_app_por_id(app_id)
        if not app:
            return

        self.combo_cambiar_fase.set(app["estado"])
        self.btn_cambiar_fase.config(state=tk.NORMAL)
        self.btn_ver_detalle.config(state=tk.NORMAL)
        self.btn_abrir_pdf.config(state=tk.NORMAL if app.get("ruta_pdf") and os.path.exists(app["ruta_pdf"]) else tk.DISABLED)
        self.btn_descargar_pdf.config(state=tk.NORMAL if app.get("ruta_pdf") and os.path.exists(app["ruta_pdf"]) else tk.DISABLED)
        self.btn_editar_notas.config(state=tk.NORMAL)
        self.btn_eliminar.config(state=tk.NORMAL)

    def _deshabilitar_acciones(self):
        self.btn_cambiar_fase.config(state=tk.DISABLED)
        self.btn_ver_detalle.config(state=tk.DISABLED)
        self.btn_abrir_pdf.config(state=tk.DISABLED)
        self.btn_descargar_pdf.config(state=tk.DISABLED)
        self.btn_editar_notas.config(state=tk.DISABLED)
        self.btn_eliminar.config(state=tk.DISABLED)

    def _buscar_app_por_id(self, app_id: int):
        for app in self.aplicaciones_cargadas:
            if app["id"] == app_id:
                return app
        return database.obtener_aplicacion_por_id(app_id)

    def _actualizar_fase(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        app_id = int(seleccion[0])
        nueva_fase = self.combo_cambiar_fase.get()

        try:
            database.actualizar_estado_aplicacion(app_id, nueva_fase)
            messagebox.showinfo("Fase Actualizada", f"La postulación #{app_id} ahora está en fase: '{nueva_fase}'.")
            self.recargar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la fase:\n\n{str(e)}")

    def _abrir_pdf_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        app = self._buscar_app_por_id(int(seleccion[0]))
        if app and app.get("ruta_pdf"):
            if not abrir_pdf_en_sistema(app["ruta_pdf"]):
                messagebox.showwarning("Archivo no encontrado", f"No se encontró el archivo PDF en:\n{app['ruta_pdf']}")

    def _descargar_pdf_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        app = self._buscar_app_por_id(int(seleccion[0]))
        if not app or not app.get("ruta_pdf") or not os.path.exists(app["ruta_pdf"]):
            messagebox.showwarning("Aviso", "No existe un archivo PDF asociado.")
            return

        pdf_orig = app["ruta_pdf"]
        destino = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=os.path.basename(pdf_orig),
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            title="Guardar copia del CV PDF en..."
        )
        if destino:
            if descargar_pdf_a_ruta(pdf_orig, destino):
                messagebox.showinfo("Descarga Exitosa", f"Copia guardada en:\n{destino}")

    def _editar_notas_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        app = self._buscar_app_por_id(int(seleccion[0]))
        if not app:
            return

        nota_actual = app.get("notas", "") or ""
        nueva_nota = simpledialog.askstring("Notas de Seguimiento", "Notas sobre la postulación (entrevistas, feedback, contacto):", initialvalue=nota_actual, parent=self)
        if nueva_nota is not None:
            database.actualizar_notas_aplicacion(app["id"], nueva_nota)
            messagebox.showinfo("Notas Guardadas", "Notas actualizadas con éxito.")
            self.recargar_datos()

    def _eliminar_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        app_id = int(seleccion[0])
        app = self._buscar_app_por_id(app_id)
        empresa = app["empresa"] if app else f"#{app_id}"

        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar permanentemente el registro de '{empresa}' de MariaDB?",
            icon="warning"
        )
        if confirm:
            database.eliminar_aplicacion(app_id)
            messagebox.showinfo("Eliminado", "Registro eliminado correctamente.")
            self.recargar_datos()

    def _ver_detalle_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        app = self._buscar_app_por_id(int(seleccion[0]))
        if not app:
            return

        # Ventana modal de detalle
        top = tk.Toplevel(self)
        top.title(f"Detalle de Postulación #{app['id']} - {app['empresa']}")
        top.geometry("750x600")
        top.minsize(600, 450)

        # Encabezado
        header_f = ttk.Frame(top, padding=10)
        header_f.pack(fill=tk.X)

        ttk.Label(header_f, text=f"🏢 {app['empresa']} - {app['titulo_puesto']}", font=("Segoe UI", 12, "bold"), foreground="#0f3460").pack(anchor=tk.W)
        ttk.Label(header_f, text=f"📍 Ubicación: {app.get('ubicacion', 'N/A')} | Fase: {app['estado']} | Fecha: {app.get('fecha_creacion', '')}").pack(anchor=tk.W, pady=2)

        notebook = ttk.Notebook(top)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Pestaña Correo
        tab_email = ttk.Frame(notebook, padding=8)
        notebook.add(tab_email, text=" ✉️ Asunto y Cuerpo del Correo ")

        ttk.Label(tab_email, text=f"Asunto: {app.get('asunto_correo', '')}", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        
        txt_mail = scrolledtext.ScrolledText(tab_email, wrap=tk.WORD, font=("Segoe UI", 9))
        txt_mail.pack(fill=tk.BOTH, expand=True, pady=4)
        txt_mail.insert("1.0", app.get("cuerpo_correo", "") or "Sin cuerpo de correo registrado.")
        txt_mail.config(state=tk.DISABLED)

        btn_copy_mail = ttk.Button(
            tab_email,
            text="📋 Copiar Correo Completo",
            command=lambda: (pyperclip.copy(app.get("cuerpo_correo", "")), messagebox.showinfo("Copiado", "Cuerpo del correo copiado."))
        )
        btn_copy_mail.pack(anchor=tk.E, pady=4)

        # Pestaña Descripción de la Vacante
        tab_desc = ttk.Frame(notebook, padding=8)
        notebook.add(tab_desc, text=" 📋 Vacante Original Pegada ")

        txt_v = scrolledtext.ScrolledText(tab_desc, wrap=tk.WORD, font=("Consolas", 9))
        txt_v.pack(fill=tk.BOTH, expand=True)
        txt_v.insert("1.0", app.get("descripcion_oferta", "") or "Sin descripción registrada.")
        txt_v.config(state=tk.DISABLED)

        # Pestaña Notas
        tab_notas = ttk.Frame(notebook, padding=8)
        notebook.add(tab_notas, text=" 📝 Notas de Seguimiento ")

        txt_n = scrolledtext.ScrolledText(tab_notas, wrap=tk.WORD, font=("Segoe UI", 9))
        txt_n.pack(fill=tk.BOTH, expand=True)
        txt_n.insert("1.0", app.get("notas", "") or "Sin notas registradas.")
        txt_n.config(state=tk.DISABLED)

        # Si tiene captura/imagen asociada
        if app.get("ruta_imagen") and os.path.exists(app["ruta_imagen"]):
            img_bar = ttk.Frame(top, padding=6)
            img_bar.pack(fill=tk.X, side=tk.BOTTOM)
            ttk.Label(img_bar, text=f"📷 Captura guardada: {os.path.basename(app['ruta_imagen'])}", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=6)
            ttk.Button(img_bar, text="👁️ Abrir Imagen Original", command=lambda: os.startfile(app["ruta_imagen"])).pack(side=tk.RIGHT, padx=6)
