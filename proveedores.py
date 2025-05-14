# proveedores.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import Database

class Proveedores(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.db = Database()
        self.pack()
        self.widgets()

    def widgets(self):
        title = tk.Label(self, text="Proveedores", font="sans 24 bold")
        title.pack(pady=10)
        # Entradas
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="RFC:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_rfc = tk.Entry(form_frame)
        self.entry_rfc.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(form_frame)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Direccion:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_direccion = tk.Entry(form_frame)
        self.entry_direccion.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Telefono:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_telefono = tk.Entry(form_frame)
        self.entry_telefono.grid(row=3, column=1, padx=5, pady=5)

        #Botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_agregar = tk.Button(btn_frame, text="Agregar", command=self.agregar_proveedor)
        btn_agregar.grid(row=0, column=0, padx=5, pady=5)

        btn_eliminar = tk.Button(btn_frame, text="Eliminar", command=self.eliminar_proveedor)
        btn_eliminar.grid(row=0, column=1, padx=5, pady=5)

        btn_editar = tk.Button(btn_frame, text="Editar", command=self.editar_proveedor)
        btn_editar.grid(row=0, column=2, padx=5, pady=5)

        #Tabla
        self.tree = ttk.Treeview(self, columns=("RFC","Nombre", "Direccion", "Telefono"), show="headings")
        for col in ("RFC", "Nombre", "Direccion", "Telefono"):
            self.tree.heading(col , text=col)
        self.tree.pack(fill=tk.BOTH, expand = True)

        self.mostrar_proveedores()

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
        rfc_original = self.tree.item(seleccionado)['values'][0]
        nuevo_rfc = self.entry_rfc.get().strip()
        nombre = self.entry_nombre.get().strip()
        direccion = self.entry_direccion.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not (nuevo_rfc and nombre and direccion and telefono):
            messagebox.showwarning("Campos vacios", "Rellena todos los campos.")
            return
        consulta = """
            Update proveedor 
            SET RFC = %s, nombre = %s, direccion = %s, telefono = %s
            WHERE RFC = %s
            """
        try:
            self.db.ejecutar_query(consulta, (nuevo_rfc, nombre, direccion, telefono, rfc_original))
            self.mostrar_proveedores()
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar proveedor: {e}")