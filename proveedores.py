import customtkinter as ctk
from tkinter import messagebox  # Mantenemos messagebox temporalmente
from db import Database

class Proveedores(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")
        self.db = Database()
        self.widgets()

    def widgets(self):
        # Configuración principal
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title = ctk.CTkLabel(
            self, 
            text="Proveedores", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10)

        # Campos del formulario
        campos = [
            ("RFC:", "entry_rfc"),
            ("Nombre:", "entry_nombre"),
            ("Direccion:", "entry_direccion"),
            ("Telefono:", "entry_telefono")
        ]

        for i, (texto, nombre_var) in enumerate(campos):
            ctk.CTkLabel(
                form_frame, 
                text=texto
            ).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            
            entry = ctk.CTkEntry(
                form_frame,
                width=250
            )
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, nombre_var, entry)

        # Frame de botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        # Botones
        btn_agregar = ctk.CTkButton(
            btn_frame, 
            text="Agregar", 
            command=self.agregar_proveedor,
            width=100
        )
        btn_agregar.grid(row=0, column=0, padx=5)

        btn_eliminar = ctk.CTkButton(
            btn_frame, 
            text="Eliminar", 
            command=self.eliminar_proveedor,
            width=100,
            fg_color="#FF5555",
            hover_color="#FF3333"
        )
        btn_eliminar.grid(row=0, column=1, padx=5)

        btn_editar = ctk.CTkButton(
            btn_frame, 
            text="Editar", 
            command=self.editar_proveedor,
            width=100,
            fg_color="#FFAA00",
            hover_color="#FF8800"
        )
        btn_editar.grid(row=0, column=2, padx=5)

        # Tabla (Treeview - mantenemos temporalmente el de ttk)
        from tkinter import ttk
        self.tree = ttk.Treeview(
            self, 
            columns=("RFC", "Nombre", "Direccion", "Telefono"), 
            show="headings",
            height=15
        )
        
        # Configurar columnas
        for col in ("RFC", "Nombre", "Direccion", "Telefono"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        # Scrollbars
        scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side="bottom", fill="x")

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.mostrar_proveedores()

    # Métodos de funcionalidad (se mantienen igual)
    def mostrar_proveedores(self):
        self.tree.delete(*self.tree.get_children())
        consulta = "SELECT * FROM proveedor ORDER BY nombre ASC"
        resultado = self.db.obtener_datos(consulta)
        for row in resultado:
            self.tree.insert("", "end", values=row)

    def agregar_proveedor(self):
        rfc = self.entry_rfc.get().strip()
        nombre = self.entry_nombre.get().strip()
        direccion = self.entry_direccion.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not (rfc and nombre and direccion and telefono):
            messagebox.showwarning("Campos vacios", "Rellena todos los campos.")
            return
        
        consulta = "INSERT INTO proveedor (RFC, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)"
        try:
            self.db.ejecutar_query(consulta, (rfc, nombre, direccion, telefono))
            self.mostrar_proveedores()
            # Limpiar campos después de agregar
            self.entry_rfc.delete(0, "end")
            self.entry_nombre.delete(0, "end")
            self.entry_direccion.delete(0, "end")
            self.entry_telefono.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar proveedor: {e}")    

    def eliminar_proveedor(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar proveedor", "Selecciona un proveedor para eliminar.")
            return
        rfc = self.tree.item(seleccionado)['values'][0]
        consulta = "DELETE FROM proveedor WHERE RFC = %s"
        try:
            self.db.ejecutar_query(consulta, (rfc,))
            self.mostrar_proveedores()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar proveedor: {e}")
    
    def editar_proveedor(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar proveedor", "Selecciona un proveedor para editar.")
            return
        
        # Obtener datos del proveedor seleccionado
        datos = self.tree.item(seleccionado)['values']
        rfc_original = datos[0]
        
        # Crear ventana de edición
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Editar Proveedor")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Modal

        # Campos de edición
        campos_edicion = [
            ("RFC:", "entry_rfc_edit", datos[0]),
            ("Nombre:", "entry_nombre_edit", datos[1]),
            ("Dirección:", "entry_direccion_edit", datos[2]),
            ("Teléfono:", "entry_telefono_edit", datos[3])
        ]

        for i, (texto, _, valor) in enumerate(campos_edicion):
            ctk.CTkLabel(
                edit_window, 
                text=texto
            ).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            entry = ctk.CTkEntry(
                edit_window,
                width=250
            )
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, valor)
            setattr(edit_window, _, entry)

        def guardar_cambios():
            nuevo_rfc = edit_window.entry_rfc_edit.get().strip()
            nombre = edit_window.entry_nombre_edit.get().strip()
            direccion = edit_window.entry_direccion_edit.get().strip()
            telefono = edit_window.entry_telefono_edit.get().strip()

            if not (nuevo_rfc and nombre and direccion and telefono):
                messagebox.showwarning("Campos vacios", "Rellena todos los campos.")
                return
            
            consulta = """
                UPDATE proveedor 
                SET RFC = %s, nombre = %s, direccion = %s, telefono = %s
                WHERE RFC = %s
            """
            try:
                self.db.ejecutar_query(consulta, (nuevo_rfc, nombre, direccion, telefono, rfc_original))
                self.mostrar_proveedores()
                edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar proveedor: {e}")

        btn_guardar = ctk.CTkButton(
            edit_window,
            text="Guardar Cambios",
            command=guardar_cambios,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        btn_guardar.grid(row=len(campos_edicion), column=0, columnspan=2, pady=15)