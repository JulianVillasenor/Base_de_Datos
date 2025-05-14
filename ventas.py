import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import Database


class Ventas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.numero_factura_actual = self.obtener_numero_folio()
        ids = self.db.ids_mesas()
        self.mesas_dic = {f"Mesa {id_}": id_ for (id_,) in ids}
        self.productos = self.obtener_productos()
        self.items_venta = []
        self.widgets()
        self.mostrar_numero_factura()
        
    def obtener_numero_folio(self):
        """Obtiene el próximo número de folio disponible"""
        query = "SELECT COALESCE(MAX(numero_folio), 0) + 1 FROM folio"
        resultado = self.db.obtener_datos(query)
        return resultado[0][0] if resultado else 1
        
    def obtener_productos(self):
        """Obtiene todos los productos disponibles con stock"""
        query = "SELECT num_id, nombre, precio FROM inventario WHERE stock > 0"
        productos = self.db.obtener_datos(query)
        return {nombre: (num_id, precio) for num_id, nombre, precio in productos}
        
    def widgets(self):
        # Frame principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de selección
        self.selection_frame = tk.LabelFrame(self.main_frame, text="Nueva Venta")
        self.selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Folio
        tk.Label(self.selection_frame, text="Folio:").grid(row=0, column=0, sticky="w")
        self.folio_label = tk.Label(self.selection_frame, text=str(self.numero_factura_actual))
        self.folio_label.grid(row=0, column=1, sticky="w", padx=5)
        
        # Mesa
        tk.Label(self.selection_frame, text="Mesa:").grid(row=1, column=0, sticky="w")
        self.mesa_var = tk.StringVar()
        self.mesa_combobox = ttk.Combobox(
            self.selection_frame, 
            textvariable=self.mesa_var,
            values=list(self.mesas_dic.keys()),
            state="readonly"
        )
        self.mesa_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Producto
        tk.Label(self.selection_frame, text="Producto:").grid(row=2, column=0, sticky="w")
        self.producto_var = tk.StringVar()
        self.producto_combobox = ttk.Combobox(
            self.selection_frame,
            textvariable=self.producto_var,
            values=list(self.productos.keys()),
            state="readonly"
        )
        self.producto_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Cantidad
        tk.Label(self.selection_frame, text="Cantidad:").grid(row=3, column=0, sticky="w")
        self.cantidad_var = tk.IntVar(value=1)
        self.cantidad_spinbox = tk.Spinbox(
            self.selection_frame,
            from_=1,
            to=100,
            textvariable=self.cantidad_var
        )
        self.cantidad_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Botón agregar
        self.add_button = tk.Button(
            self.selection_frame,
            text="Agregar a Venta",
            command=self.agregar_producto,
            bg="#4CAF50",
            fg="white"
        )
        self.add_button.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Frame de la venta actual
        self.venta_frame = tk.LabelFrame(self.main_frame, text="Detalle de Venta")
        self.venta_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para los items
        columns = ("producto", "cantidad", "precio", "subtotal")
        self.venta_tree = ttk.Treeview(
            self.venta_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configurar columnas
        self.venta_tree.heading("producto", text="Producto")
        self.venta_tree.heading("cantidad", text="Cantidad")
        self.venta_tree.heading("precio", text="Precio Unitario")
        self.venta_tree.heading("subtotal", text="Subtotal")
        
        # Ajustar anchos de columnas
        self.venta_tree.column("producto", width=200, anchor="w")
        self.venta_tree.column("cantidad", width=80, anchor="center")
        self.venta_tree.column("precio", width=100, anchor="e")
        self.venta_tree.column("subtotal", width=120, anchor="e")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.venta_frame, orient="vertical", command=self.venta_tree.yview)
        self.venta_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.venta_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Total
        self.total_var = tk.DoubleVar(value=0.0)
        self.total_label = tk.Label(
            self.venta_frame, 
            textvariable=self.total_var,
            text="Total: $0.00", 
            font=("Arial", 12, "bold")
        )
        self.total_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Botones de acción
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cancelar_button = tk.Button(
            self.button_frame,
            text="Cancelar Venta",
            command=self.cancelar_venta,
            bg="#f44336",
            fg="white"
        )
        self.cancelar_button.pack(side=tk.LEFT, padx=5)
        
        self.eliminar_button = tk.Button(
            self.button_frame,
            text="Eliminar Item",
            command=self.eliminar_item,
            bg="#FF9800",
            fg="white"
        )
        self.eliminar_button.pack(side=tk.LEFT, padx=5)
        
        self.pagar_button = tk.Button(
            self.button_frame,
            text="Finalizar Venta",
            command=self.finalizar_venta,
            bg="#2196F3",
            fg="white"
        )
        self.pagar_button.pack(side=tk.RIGHT, padx=5)
    
    def agregar_producto(self):
        mesa = self.mesa_var.get()
        producto_nombre = self.producto_var.get()
        cantidad = self.cantidad_var.get()
        
        # Validaciones
        if not mesa:
            messagebox.showerror("Error", "Seleccione una mesa")
            return
        if not producto_nombre:
            messagebox.showerror("Error", "Seleccione un producto")
            return
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a cero")
            return
        
        try:
            num_id, precio = self.productos[producto_nombre]
            subtotal = precio * cantidad
            
            # Verificar stock disponible
            query_stock = "SELECT stock FROM inventario WHERE num_id = %s"
            stock_actual = self.db.obtener_datos(query_stock, (num_id,))[0][0]
            
            if cantidad > stock_actual:
                messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {stock_actual}")
                return
            
            # Agregar al Treeview
            self.venta_tree.insert("", "end", values=(
                producto_nombre, 
                cantidad, 
                f"${precio:.2f}", 
                f"${subtotal:.2f}"
            ))
            
            # Guardar en lista temporal
            self.items_venta.append({
                "id_mesa": self.mesas_dic[mesa],
                "num_id_producto": num_id,
                "producto_nombre": producto_nombre,
                "valor_articulo": precio,
                "cantidad": cantidad,
                "subtotal": subtotal
            })
            if len(self.items_venta) == 1:
                self.mesa_combobox.config(state="disabled")
            # Actualizar total
            self.actualizar_total()
            
            # Limpiar selección
            self.producto_var.set("")
            self.cantidad_var.set(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
    
    def eliminar_item(self):
        seleccionado = self.venta_tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un item para eliminar")
            return
            
        try:
            # Obtener índice del item seleccionado
            index = self.venta_tree.index(seleccionado[0])
            
            # Eliminar de la lista
            self.items_venta.pop(index)
            
            # Eliminar del Treeview
            self.venta_tree.delete(seleccionado)
            
            # Actualizar total
            self.actualizar_total()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar item: {str(e)}")
    
    def actualizar_total(self):
        total = sum(item["subtotal"] for item in self.items_venta)
        self.total_var.set(total)
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def finalizar_venta(self):
     if not self.items_venta:
          messagebox.showerror("Error", "No hay items en la venta")
          return
     if not messagebox.askyesno("Confirmar", "¿Desea finalizar la venta?"):
          return
     try:
          # 1. Insertar el folio y obtener el ID
          query_folio = "INSERT INTO folio (numero_folio) VALUES (%s) RETURNING id"
          folio_id_result = self.db.obtener_datos(query_folio, (self.numero_factura_actual,))
          if not folio_id_result:
               raise Exception("No se pudo crear el folio")
          id_folio = folio_id_result[0][0]

          # 2. Preparamos las operaciones para insertar ventas y actualizar stock
          operaciones = []
          for item in self.items_venta:
               # Registrar venta
               operaciones.append((
                    """
                    INSERT INTO ventas (
                         id_mesa, num_id_producto, valor_articulo, cantidad, subtotal, id_folio
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                         item["id_mesa"],
                         item["num_id_producto"],
                         item["valor_articulo"],
                         item["cantidad"],
                         item["subtotal"],
                         id_folio  # Usamos el id del folio real
                    )
               ))

               # Actualizar stock
               operaciones.append((
                    "UPDATE inventario SET stock = stock - %s WHERE num_id = %s",
                    (item["cantidad"], item["num_id_producto"])
               ))

          # 3. Ejecutamos la transacción
          if not self.db.ejecutar_transaccion(operaciones):
               raise Exception("Error al realizar la transacción")

          # 4. Mostrar resumen
          fecha_venta = self.db.obtener_datos(
               "SELECT fecha_creacion FROM folio WHERE numero_folio = %s",
               (self.numero_factura_actual,)
          )[0][0]
          resumen = (
               f"Venta finalizada con éxito \n\n"
               f"Folio: {self.numero_factura_actual}\n"
               f"Fecha: {fecha_venta}\n\n"
               f"Total: ${sum(item['subtotal'] for item in self.items_venta):.2f}\n\n"
          )
          if messagebox.askyesno("Venta exitosa", resumen):
               self.imprimir_ticket(self.numero_factura_actual)
          self.cancelar_venta()

     except Exception as e:
          messagebox.showerror("Error", f"No se pudo finalizar la venta: {str(e)}")


    def imprimir_ticket(self, folio_id):
        """Función para generar el ticket de venta"""
        try:
            # Obtener datos del folio
            query = """
                SELECT f.numero_folio, f.fecha_creacion, 
                       m.id as mesa_id, SUM(v.subtotal) as total
                FROM folio f
                JOIN ventas v ON f.id = v.id_folio
                JOIN mesas m ON v.id_mesa = m.id
                WHERE f.id = %s
                GROUP BY f.id, m.id
            """
            datos_folio = self.db.obtener_datos(query, (folio_id,))[0]
            
            # Obtener items de la venta
            query_items = """
                SELECT i.nombre, v.cantidad, v.valor_articulo, v.subtotal
                FROM ventas v
                JOIN inventario i ON v.num_id_producto = i.num_id
                WHERE v.id_folio = %s
            """
            items = self.db.obtener_datos(query_items, (folio_id,))
            
            # Aquí iría el código para generar el ticket (PDF, impresora, etc.)
            # Por ahora solo mostramos un mensaje
            messagebox.showinfo("Ticket", "Ticket generado (simulación)")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ticket: {str(e)}")
    
    def cancelar_venta(self):
        
        # Limpiar todo
        self.venta_tree.delete(*self.venta_tree.get_children())
        self.items_venta = []
        self.total_var.set(0.0)
        self.mesa_var.set("")
        self.producto_var.set("")
        self.cantidad_var.set(1)
        
        # Generar nuevo folio
        self.numero_factura_actual = self.obtener_numero_folio()
        self.mostrar_numero_factura()
        self.mesa_combobox.config(state="readonly")
    
    def mostrar_numero_factura(self):
        self.folio_label.config(text=str(self.numero_factura_actual))