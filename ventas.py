from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime
import sys
import os

#El rollo aqui es que se esta seleccionando al producto por su nombre y no por el id que pondre nuevo con un codigo de identificacion unico para el producto
class Ventas(tk.Frame): #Hereda de Frame para crear la ventana de ventas
    def __init__(self, parent):
        super().__init__(parent) #Llamada al constructor de la clase padre tk.Frame
        self.db = Database() #instancia de la conexion a la base de datos
        self.numero_factura_actual = self.obtener_numero_factura_actual()
        ids = self.db.ids_mesas() #Obteniendo los ids de las mesas desde la base de datos
        self.mesas_dic = {f"Mesa {id_}": id_ for (id_,) in ids} #PEndiente definir!!
        self.widgets()
        self.mostrar_numero_factura()

    def widgets(self):

        frame1 = tk.Frame(self, bg = "#dddddd", highlightbackground="gray", highlightthickness=1)
        frame1.pack()
        frame1.place(x=0, y=0, width= 1100, height=100)

        titulo = tk.Label(self, text = "VENTAS", bg= "#dddddd", font="sans 30 bold", anchor="center")
        titulo.pack()
        titulo.place(x=5,y=0, width= 1090,height=90)

        frame2 = tk.Frame(self, bg="#C6D9E3", highlightbackground="gray", highlightthickness=1)
        frame2.place(x=0,y=100, width= 1100, height=550)

        lblframe = LabelFrame(frame2, text="Informacion de la venta", bg="#C6D9E3", font= "sans 16 bold")
        lblframe.place(x=10,y=10,width=1060, height=80)
        # Numero de factura

        label_numero_factura = tk.Label(lblframe, text= "Numero de \nfactura", bg="#C6D9E3", font= "sans 12 bold")
        label_numero_factura.place(x=10,y=5,)
        self.numero_factura = tk.StringVar()

        self.entry_numero_factura = ttk.Entry(lblframe, textvariable=self.numero_factura, state="readonly",font= "sans 12 bold" )
        self.entry_numero_factura.place(x=100,y=5, width=80)
          #Productos
        label_nombre = tk.Label(lblframe, text="productos: ",bg="#C6D9E3", font= "sans 12 bold")
        label_nombre.place(x=200,y=12)
        self.entry_nombre = ttk.Combobox(lblframe, font="sans 12 bold", state= "readonly")
        self.entry_nombre.place(x=280, y=10, width=180)

        
          #Precio
        label_valor = tk.Label(lblframe, text="Precio",bg="#C6D9E3", font="sans 12 bold")
        label_valor.place(x=470,y=12)
        self.entry_valor= ttk.Entry(lblframe, font="sans 12 bold", state= "readonly")
        self.entry_valor.place(x=540, y=10, width=180)

        
          #Cantidad
        label_cantidad = tk.Label(lblframe, text="Cantidad: ",bg="#C6D9E3", font="sans 12 bold")
        label_cantidad.place(x=730, y=12)
        self.entry_cantidad = ttk.Entry(lblframe, font="sans 12 bold")
        self.entry_cantidad.place(x=820, y=10, width=180)

        #Mesa
        label_mesa = tk.Label(lblframe, text="Mesa: ",bg="#C6D9E3", font= "sans 12 bold")
        label_mesa.place(x=730, y=60)
        self.entry_mesa = ttk.Combobox(lblframe, font="sans 12 bold", state= "readonly")
        self.entry_mesa.place(x=920, y=60, width=180)
        #Eventos y cargas iniciales
        self.entry_nombre.bind("<<ComboboxSelected>>", self.actualizar_precio) #Mover a eventos y cargas iniciales
        self.cargar_productos() # Carga los productos desde la base de datos
        self.cargar_mesas() # Carga las mesas desde la base de datos
          #Treeview de productos agregados
        treFrame = tk.Frame(frame2,bg="#C6D9E3")
        treFrame.place(x=150, y=120, width=800, height=200)

        scrol_y = ttk.Scrollbar(treFrame, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame,orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        self.tree = ttk.Treeview(treFrame, columns=("Producto", "Precio", "Cantidad", "Subtotal", "MesaID"), show="headings", height=10, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)

        self.tree.heading("#1", text="Producto")
        self.tree.heading("#2", text="Precio")
        self.tree.heading("#3", text="Cantidad")
        self.tree.heading("#4", text="Subtotal")
        self.tree.heading("#5", text="Mesa") #Nuevo
        
        self.tree.column("Producto", anchor="center")
        self.tree.column("Precio", anchor="center")
        self.tree.column("Cantidad", anchor="center")
        self.tree.column("Subtotal", anchor="center")
        self.tree.column("MesaID", anchor="center")#Nuevo

        self.tree.pack(expand=True, fill=BOTH)

        lblframe1 = LabelFrame(frame2, text="Opciones",bg="#C6D9E3", font= "sans 12 bold")
        lblframe1.place(x=10, y=380, width=1060, height=100)

        boton_agregar = tk.Button(lblframe1, text="Agregar Articulo",bg="#dddddd", font= "sans 12 bold",command= self.registrar)
        boton_agregar.place(x=50, y=10, width=240, height=50)

        boton_pagar = tk.Button(lblframe1, text="Pagar",bg="#dddddd", font= "sans 12 bold", command=self.abrir_ventana_pago)
        boton_pagar.place(x=400, y=10, width=240, height=50)

        boton_ver_facturas = tk.Button(lblframe1, text="Ver Facturas",bg="#dddddd", font= "sans 12 bold", command=self.abrir_ventana_factura)
        boton_ver_facturas.place(x=750, y=10, width=240, height=50)

        self.label_suma_total = tk.Label(frame2, text="Total a pagar: ",bg="#C6D9E3", font= "sans 25 bold" )
        self.label_suma_total.place(x=360, y=335)

    def cargar_productos(self): #carga los nombres desde la tabla inventario
            try: 
                query = "SELECT id, nombre FROM inventario"  #Aqui esta bien selecciona los valores unicos de la BD 
                productos = self.db.obtener_datos(query)
                self.productos_dic = {nombre: id for id,nombre in productos} #Diccionario para almacenar los nombres y ids de los productos}
                self.entry_nombre["values"] = list(self.productos_dic.keys()) #
                if not productos:
                    print("No se encontraron productos en la base de datos.")
            except Exception as e:
                print("Error al cargar el producto desde la base de datos:", e)
        
    def actualizar_precio(self, event):
            #actualiza el precio del producto seleccionado en el combobox
            nombre_producto = self.entry_nombre.get()
            try:
                #Consulta para obtener el precio del producto seleccionado
                query = "SELECT precio FROM inventario WHERE nombre = %s"
                resultado = self.db.obtener_datos(query, (nombre_producto,))
                if resultado:
                    precio = resultado[0][0]
                    self.entry_valor.config(state="normal")
                    self.entry_valor.delete(0, tk.END)
                    self.entry_valor.insert(0, precio)
                    self.entry_valor.config(state="readonly")
                else:
                    self.entry_valor.config(state="normal")
                    self.entry_valor.delete(0, tk.END)
                    self.entry_valor.insert(0,"Precio no disponible")
                    self.entry_valor.config(state="readonly")
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener el precio: {e}")
            
    def actualizar_total(self):
         total = 0.0
         for child in self.tree.get_children():
              subtotal = float(self.tree.item(child, "values") [3])
              total += subtotal
         self.label_suma_total.config(text=f"Total a pagar: ${total}")

    def registrar(self):
         producto = self.entry_nombre.get()
         precio = self.entry_valor.get()
         cantidad = self.entry_cantidad.get()
         mesa_nombre = self.entry_mesa.get() #Editando par que guarde el id de la mesa seleccionada
         if not mesa_nombre:
              messagebox.showerror("Error", "Debe seleccionar una mesa")
              return
         mesa_id = self.mesas_dic[mesa_nombre] #Obteniendo el id de la mesa seleccionada
         #Actualizar el estado de la mesa a ocupada
         if producto and precio and cantidad and mesa_id:
            try:
                 cantidad = int(cantidad)
                 if not self.verificar_stock(producto, cantidad):
                      messagebox.showerror("Error", "Stock insuficiente para el producto seleccionado")
                      return
                 precio = float(precio)
                 subtotal = cantidad * precio

                 self.tree.insert("","end", values=(producto,precio, cantidad, subtotal, mesa_id))

                 self.entry_nombre.set("")
                 self.entry_valor.config(state="normal")
                 self.entry_valor.delete(0, tk.END)
                 self.entry_valor.config(state="readonnly")
                 self.entry_cantidad.delete(0, tk.END)

                 self.actualizar_total()
            except ValueError:
                 messagebox.showerror("Error," "Cantidad o precio no valido")
         else:
              messagebox.showerror("Error", "Debe completar todos los campos")

    def verificar_stock(self, nombre_producto, cantidad):
         try:
             query = "SELECT stock FROM inventario WHERE nombre = %s"
             params = (nombre_producto,)
             resultado = self.db.obtener_datos(query, params)
             if resultado and resultado[0][0] >= cantidad:
                   return True
             return False
         except Exception as e:
              messagebox.showerror("Error", f"Error al verificar el stock: {e}")
              return False

    def obtener_total(self):
         total = 0.0
         for child in self.tree.get_children():
              subtotal = float(self.tree.item(child, "values") [3])
              total += subtotal
         return total
    
    def abrir_ventana_pago(self):
         if not self.tree.get_children():
              messagebox.showerror("Error", "no hay articulos para pagar")
              return 
         ventana_pago = Toplevel(self)
         ventana_pago.title("Realizar pago")
         ventana_pago.geometry("400x400")
         ventana_pago.config(bg="#C6D9E3")
         ventana_pago.resizable(False, False)

         label_total = tk.Label(ventana_pago, bg="#C6D9E3", text=f"Total a pagar: ${self.obtener_total()}", font="sans 18 bold")
         label_total.place(x=70, y=20)

         label_cantidad_pagada = tk.Label(ventana_pago, bg="#C6D9E3", text="Cantidad pagada:", font="sans 14 bold")
         label_cantidad_pagada.place(x=100, y=90)
         entry_cantidad_pagada = ttk.Entry(ventana_pago, font= "sans 14 bold")
         entry_cantidad_pagada.place(x=100 ,y=130)

         label_cambio = tk.Label(ventana_pago, bg="#C6D9E3", text="", font="sans 14 bold")
         label_cambio.place(x=100, y=190)

         def calcular_cambio():
              try:
                   cantidad_pagada = float(entry_cantidad_pagada.get())
                   total = self.obtener_total()
                   cambio = cantidad_pagada - total
                   if cambio < 0:
                        messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                        return
                   label_cambio.config(text=f"Vuelto: ${cambio}")
              except ValueError: 
                   messagebox.showerror("Error", "Cantidad pagada no valida")
         boton_calcular = tk.Button(ventana_pago, text ="Calcular Vuelto", bg="white",font="sans 12 bold", command=calcular_cambio)
         boton_calcular.place(x=100, y=240, width=240, height=40)

         boton_pagar = tk.Button(ventana_pago, text ="Pagar", bg="white",font="sans 12 bold", command=lambda: self.pagar(ventana_pago, entry_cantidad_pagada, label_cambio))
         boton_pagar.place(x=100, y=300, width=240, height=40)


    def pagar(self, ventana_pago, entry_cantidad_pagada, label_cambio):
         try:
            #obtener la cantidad pagada desde el entry
              cantidad_pagada = float(entry_cantidad_pagada.get())
              total = self.obtener_total()
              cambio = cantidad_pagada - total
              if cambio < 0:
                   messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                   return
              
              try:
                   productos = []
                   mesa_id = None
                   mesa_nombre = self.entry_mesa.get()
                   if not mesa_nombre:
                        messagebox.showerror("Error", "Debe seleccionar una mesa")
                        return
                   #obtenere id
                   mesa_id = self.mesas_dic[mesa_nombre] #FALTA INICIALIZAR A mesas_dic
                   if not mesa_id:
                        messagebox.showerror("Error", "Mesa no seleccionada")
                        return
                   #obtener los valores del producto vendido desde el arbol
                   for child in self.tree.get_children():
                        item = self.tree.item(child, "values")
                        producto = item[0]
                        precio = item[1]
                        cantidad_vendida = int(item[2])
                        subtotal = float(item[3])
                        productos.append([producto, precio, cantidad_vendida, subtotal])
                        #Verificar el stock del producto
                        if not self.verificar_stock(producto, cantidad_vendida):
                             messagebox.showerror("Error", f"Stock insuficiente para el producto: {producto}")
                             return
                        #insertar la venta en la tabla ventas
                        query_venta = """
                         INSERT INTO ventas (factura, nombre_articulo, valor_articulo, cantidad, subtotal, id_mesa) 
                         VALUES (%s, %s, %s, %s, %s, %s)
                         RETURNING id
                           """
                        params_venta = (
                             self.numero_factura_actual,
                             producto,
                             float(precio),
                             cantidad_vendida,
                             subtotal,
                             mesa_id
                        )
                        id_venta = self.db.ejecutar_query(query_venta, params_venta, return_id=True) #nueva funcion que devuelve el id de la venta para asignar el folio
                        query_factura = "INSERT INTO factura (id_venta, folio) VALUES (%s, %s)"
                        params_factura = (id_venta, self.numero_factura_actual)
                        self.db.ejecutar_query(query_factura, params_factura) #Asociar el folio a la venta
                        #Actualizar el stock del producto en la tabla inventario
                        query_stock = "UPDATE inventario SET stock = stock - %s WHERE nombre = %s"
                        params_stock = (cantidad_vendida, producto)
                        self.db.ejecutar_query(query_stock, params_stock)
                   messagebox.showinfo("Excito", "Venta registrada exitosamente") #Confirmar venta
                   self.numero_factura_actual += 1
                   self.mostrar_numero_factura()
                    #Limpiar la interfaz
                   for child in self.tree.get_children():
                        self.tree.delete(child)
                   self.label_suma_total.config(text="Total a pagar: $0")
                   #Cerrar la venta de pago
                   ventana_pago.destroy()
                   fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                   #self.generar_factura_pdf(productos, total, self.numero_factura_actual - 1,fecha, mesa_id )
              except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar la venta: {e}")
         except ValueError:
              messagebox.showerror("Error", "Cantidad pagada no válida")
     
    def generar_factura_pdf(self, productos, total, factura_numero, fecha, mesa_id=None):
         archivo_pdf = f"facturas/factura_{factura_numero}.pdf"

         c = canvas.Canvas(archivo_pdf, pagesize=letter)
         width, height = letter
         mesa_info =""
         #Informacion de la mesa si esta disponible
         if mesa_id:
              try:
                   resultado = self.db.obtener_mesa_por_id(mesa_id)
                   if resultado:
                        mesa_data = resultado[0]
              except Exception as e:
                   print(f"Error al obtener la mesa: {e}")
         #Configuracion de margenes
         margin_left = 50
         margin_top = 50
          #Encabezado de la factura
         c.setFont("Helvetica-Bold", 18)
         c.drwaCenteredString(width/2, height-50, f"FACTURA #{factura_numero}")
         #INformacion de fecha y meas
         c.setFont("Helvetica", 12)
         y_position = height - margin_top - 30
         c.drawString(margin_left,y_position, f"Fecha: {fecha}")
         if mesa_data:
              y_position -=20
              mesa_info = f"Mesa: {mesa_data[0]} ({mesa_data[1]} sillas)"
              c.drawString(margin_left, y_position, mesa_info)
          #Linea separadora
         y_position -= 10
         c.setFont("Helvetica-Bold", 14)
         c.drawString(margin_left, y_position, "Detalle de productos:")
         #Prepara datos para la tabla
         data = [["Producto", "Precio", "Cantidad", "Subtotal"]]
         for producto in productos:
              data.append([producto[0], f"${producto[1]:.2f}", producto[2], f"${producto[3]:.2f}"])
         #Estilo de la tabla
         style = [
          ('BACKGROUND', (0, 0), (-1, 0), '#EEEEEE'),
          ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), '#FFFFFF'),
          ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC'),
         ]
         #Crear y dibujar tabla
         table = Table(data, colWidths=[200, 80, 60, 80], style=style)
         table.wrapOn(c, width - 2*margin_left, height)
         table.drawOn(c, margin_left, y_position - 20 - len(productos)*20)
         #Total
         y_total = y_position - 40 - len(productos)*20
         c.setFont("Helvetica-Bold", 14)
         c.drawString(margin_left, y_total, f"Total: ${total:.2f}")
         #Pie de pagina
         c.setFont("Helvetica-Oblique", 10)
         c.drwaCenteredString(width/2, 30, "Gracias por su preferencia - Vuelva pronto")
         #Guardar PDF
         c.save()
         messagebox.showinfo("Factura generada", f"Factura #{factura_numero} guardada como {archivo_pdf}")
              

    #importante revisar como se obtiene el numero de la factura por que esta vulnerable a ser cambiada
    def obtener_numero_factura_actual(self):
         try:
              query = "SELECT MAX(factura) FROM ventas"
              resultado = self.db.obtener_datos(query)

              max_factura = resultado[0][0]
              if max_factura:
                   return max_factura + 1
              else:
                   return 1
         except Exception as e:
              messagebox.showerror("Error", f"Error al obtener el numero de factura: {e}")
              return 1
              
    def mostrar_numero_factura(self):
         self.numero_factura.set(self.numero_factura_actual)

    def abrir_ventana_factura(self):
         ventana_facturas = Toplevel(self)
         ventana_facturas.title("Factura")
         ventana_facturas.geometry("800x500")
         ventana_facturas.config(bg="#C6D9E3")
         ventana_facturas.resizable(False, False)
         
         facturas = Label(ventana_facturas, bg="#C6D9E3", text = "facturas registradas", font = "sans 36 bold")
         facturas.place(x=150, y=15)

         treFrame = tk.Frame(ventana_facturas, bg="#C6D9E3")
         treFrame.place(x=10, y=100, width=780, height=380)

         scrol_y = ttk.Scrollbar(treFrame, orient=VERTICAL)
         scrol_y.pack(side=RIGHT, fill=Y)

         scrol_x = ttk.Scrollbar(treFrame,orient=HORIZONTAL)
         scrol_x.pack(side=BOTTOM, fill=X)

         tree_facturas = ttk.Treeview(treFrame, columns=("ID", "Factura", "Producto", "Precio", "Cantidad", "Subtotal"), show="headings", height=10, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
         scrol_y.config(command=tree_facturas.yview)
         scrol_x.config(command=tree_facturas.xview)

         tree_facturas.heading("#1", text="ID")
         tree_facturas.heading("#2", text="Factura")
         tree_facturas.heading("#3", text="Producto")
         tree_facturas.heading("#4", text="Precio")
         tree_facturas.heading("#5", text="Cantidad")
         tree_facturas.heading("#6", text="Subtotal")
        
         tree_facturas.column("ID",width=70, anchor="center")
         tree_facturas.column("Factura",width=100, anchor="center")
         tree_facturas.column("Producto",width=200, anchor="center")
         tree_facturas.column("Precio",width=130, anchor="center")
         tree_facturas.column("Cantidad",width=130, anchor="center")
         tree_facturas.column("Subtotal",width=130, anchor="center")

         tree_facturas.pack(expand=True, fill=BOTH)

         self.cargar_facturas(tree_facturas)

    def cargar_facturas(self, tree):
         try:
              query = "SELECT * FROM ventas"
              facturas = self.db.obtener_datos(query)
              for factura in facturas:
                   tree.insert("","end", values=factura)
                
         except Exception as e:
              messagebox.showerror("Error", f"Error al cargar las facturas: {e}")

    def cargar_mesas(self):
        try:
             # Usa las claves del diccionario self.mesas_dic
             nombres_mesas = list(self.mesas_dic.keys())
             self.entry_mesa['values'] = nombres_mesas
             if nombres_mesas:
                  self.entry_mesa.current(0)
        except Exception as e:
             print("Error al cargar las mesas:", e)
         