from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from proveedores import Proveedores

class Inventario(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.db = Database() #instancia de la conexion a la base de datos
        self.pack()
        self.widgets()
    
    def widgets(self):

        frame1 = tk.Frame(self, bg = "#dddddd", highlightbackground="gray", highlightthickness=1)
        frame1.pack()
        frame1.place(x=0, y=0, width= 1100, height=100)

        titulo = tk.Label(self, text = "INVENTARIO", bg="#dddddd", font="sans 30 bold", anchor="center")
        titulo.pack()
        titulo.place(x=5,y=0,width=1090,height=90)

        frame2 = tk.Frame(self, bg="#C6D9E3", highlightbackground="gray", highlightthickness=1)
        frame2.place(x=0,y=100, width=1100, height=600)

        labelframe = LabelFrame(frame2, text="Productos", font= "sans 22 bold", bg="#C6D9E3")
        labelframe.place(x=20, y=30, width=400, height=550)
        #poner el entry de id para capturar el codigo de barras dentro de labelframe
        #Pendiendte revisar como se muestra
        lblid = Label(labelframe, text="ID (EAN-13)", font="sans 14 bold", bg="#C6D9E3")
        lblid.place(x=10, y=20)
        self.num_id = ttk.Entry(labelframe, font="sans 14 bold")
        self.num_id.place(x=140, y=20, width=240, height=40)

        lblnombre = Label(labelframe, text="Nombre", font="sans 14 bold", bg="#C6D9E3")
        lblnombre.place(x=10, y=80)
        self.nombre = ttk.Entry(labelframe, font="sans 14 bold")
        self.nombre.place(x=140, y=80, width=240, height=40)

        lblproveedor = Label(labelframe, text="Proveedor", font="sans 14 bold",bg="#C6D9E3")
        lblproveedor.place(x=10,y=140)
        self.proveedor = ttk.Entry(labelframe, font="sans 14 bold")
        self.proveedor.place(x=140,y=140,width=240,height=40)

        lblprecio = Label(labelframe, text="Precio", font="sans 14 bold",bg="#C6D9E3")
        lblprecio.place(x=10,y=200)
        self.precio = ttk.Entry(labelframe, font="sans 14 bold")
        self.precio.place(x=140,y=200,width=240,height=40)

        lblcosto = Label(labelframe, text="Costo", font="sans 14 bold",bg="#C6D9E3")
        lblcosto.place(x=10,y=260)
        self.costo = ttk.Entry(labelframe, font="sans 14 bold")
        self.costo.place(x=140,y=260,width=240,height=40)

        lblstock = Label(labelframe, text="Stock", font="sans 14 bold",bg="#C6D9E3")
        lblstock.place(x=10,y=320)
        self.stock = ttk.Entry(labelframe, font="sans 14 bold")
        self.stock.place(x=140,y=320,width=240,height=40)

        boton_agregar = tk.Button(labelframe, text="Ingresa", font="sans 14 bold", bg="#dddddd", command=self.registrar)
        boton_agregar.place(x=80, y=380, width=240, height=40)

        boton_editar = tk.Button(labelframe, text="Editar", font="sans 14 bold", bg="#dddddd", command=self.editar_producto)
        boton_editar.place(x=80, y=440, width=240, height=40)

        #Tabla 
        treFrame = Frame(frame2, bg="white")
        treFrame.place(x=440,y=50,width=620, height=400)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM,fill=X )

        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40,
                                columns=("ID", "PRODUCTO", "PROVEEDOR", "PRECIO", "COSTO", "STOCK"), show="headings")
        self.tre.pack(expand=True, fill=BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        self.tre.heading("ID", text="Id")
        self.tre.heading("PRODUCTO", text="Producto")
        self.tre.heading("PROVEEDOR", text="Proveedor")
        self.tre.heading("PRECIO", text="Precio")
        self.tre.heading("COSTO", text="Costo")
        self.tre.heading("STOCK", text="Stock")

        self.tre.column("ID", width=70, anchor="center")
        self.tre.column("PRODUCTO", width=100, anchor="center")
        self.tre.column("PROVEEDOR", width=100, anchor="center")
        self.tre.column("PRECIO", width=100, anchor="center")
        self.tre.column("COSTO", width=100, anchor="center")
        self.tre.column("STOCK", width=70, anchor="center")

        self.mostrar()

        btn_actualizar = Button(frame2, text="Actualizar Inventario", font = "sans 14 bold", command=self.actualizar_inventario)
        btn_actualizar.place(x=440, y=480, width=260, height=50)
        #El boton que llame al tk.Frame para mostrar a proveedor
        """
        elcommand del boton debe llamar al frame proveedor
        def proveedores(self):
          self.show_frames(Proveedor) #se va abrir desde el archivo ventas la clase Proveedor
        """
        btn_proveedores = Button(frame2, text="Proveedores", font = "sans 14 bold", command=self.proveedores)
        btn_proveedores.place(x=740, y=480, width=260, height=50)

    def eje_consulta(self, consulta, parametros=()):
        try:
            cursor = self.db.cursor #Obten el cursor de la conexion
            cursor.execute(consulta, parametros) #Ejecuta la consulta con los parametros
            self.db.connection.commit() #Confirma los cambios
            #Verifica si la consulta es un SELECT
            if consulta.strip().lower().startswith("select"):
              return cursor.fetchall() #retorna los datos del select
            return None #no hay resultados para otras consultas
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando consulta: {e}")
            return None #Asegura retornar algo en caso de error
    
    def validacion(self,num_id, nombre, prov, precio, costo, stock):
        if not (num_id and nombre and prov and precio and costo and stock):
            return False
        if not (num_id.isdigit() and len(num_id) == 13):
            return False #se añadio a id como parametro a la funcion
        try:
            float(precio)
            float(costo)
            int(stock)
        except ValueError:
            return False
        return True
    
    def mostrar(self):
        try:
            #Aqui habra una edicion para que muestre un JOIN con la tabla proveedor con la llave foranea RFC
            consulta = """
            SELECT
                i.num_id,
                i.nombre,
                p.nombre AS proveedor,
                i.precio,
                i.costo,
                i.stock
            FROM inventario AS i
            JOIN proveedor AS p ON i.proveedor = p.RFC
            ORDER BY i.nombre ASC
            """
            result = self.eje_consulta(consulta)
            #insertar los datos a la tabla
            for elem in result:
                self.tre.insert("", 0, values=(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5]))
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar datos: {e}")

    def actualizar_inventario(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.mostrar()
        messagebox.showinfo("Actualizacion", "El inventario ha sido actualizado correctamente.")

    def registrar(self):
        result = self.tre.get_children()
        for i in result:
            self.tre.delete(i)
        num_id = self.num_id.get() #modificacion
        nombre = self.nombre.get()
        prov = self.proveedor.get()
        precio = self.precio.get()
        costo = self.costo.get()
        stock = self.stock.get()
        if self.validacion(num_id, nombre, prov, precio, costo, stock):
            try:
                consulta =  "INSERT INTO inventario (num_id, nombre, proveedor, precio, costo, stock) VALUES (%s, %s, %s, %s, %s, %s)"
                parametros = (int(num_id), nombre, prov, precio, costo, stock)
                self.eje_consulta(consulta, parametros)
                self.mostrar()
                self.id.delete(0, END) #Limpiar los campos de entrada
                self.nombre.delete(0, END)
                self.proveedor.delete(0, END)
                self.precio.delete(0, END)
                self.costo.delete(0, END)
                self.stock.delete(0, END)
            except Exception as e:
                messagebox.showwarning(title="Error", message=f"Error al registrar el producto: {e}")
        else:
            messagebox.showwarning(title="Error", message="Rellene todos los campos correctamente.")
            self.mostrar()

    def editar_producto(self):
        seleccion = self.tre.selection()
        if not seleccion:
            messagebox.showwarning("Editar productio", "Seleccione un producto para editar")
            return
        item_id = self.tre.item(seleccion)["values"][0]
        item_values = self.tre.item(seleccion)["values"]

        ventana_editar = Toplevel(self)
        ventana_editar.title("Editar producto")
        ventana_editar.geometry("400x500")
        ventana_editar.config(bg="#C6D9E3")

        #ID (EAN-13)
        lbl_id = Label(ventana_editar, text="ID (EAN-13): ", font="sans 14 bold", bg="#C6D9E3")
        lbl_id.grid(row=0,column=0, padx=10, pady=10)
        entry_id = Entry(ventana_editar, font="sans 14 bold")
        entry_id.grid(row=0, columns=1, padx=10, pady=10)
        entry_id.insert(0,item_values[0])

        lbl_nombre = Label(ventana_editar, text="Nombre: ", font="sans 14 bold", bg="#C6D9E3")
        lbl_nombre.grid(row=0,column=0, padx=10, pady=10)
        entry_nombre = Entry(ventana_editar, font = "sans 14 bold")
        entry_nombre.grid(row=0, columns=1, padx=10, pady=10)
        entry_nombre.insert(0,item_values[1])

        lbl_proveedor = Label(ventana_editar, text="Proveedor: ", font="sans 14 bold", bg="#C6D9E3")
        lbl_proveedor.grid(row=1,column=0, padx=10, pady=10)
        entry_proveedor = Entry(ventana_editar, font = "sans 14 bold")
        entry_proveedor.grid(row=1, columns=1, padx=10, pady=10)
        entry_proveedor.insert(0,item_values[2])

        lbl_precio = Label(ventana_editar, text="Precio: ", font="sans 14 bold", bg="#C6D9E3")
        lbl_precio.grid(row=2,column=0, padx=10, pady=10)
        entry_precio = Entry(ventana_editar, font = "sans 14 bold")
        entry_precio.grid(row=2, columns=1, padx=10, pady=10)
        entry_precio.insert(0,item_values[3])

        lbl_costo = Label(ventana_editar, text="Costo: ", font="sans 14 bold", bg="#C6D9E3")
        lbl_costo.grid(row=3,column=0, padx=10, pady=10)
        entry_costo = Entry(ventana_editar, font = "sans 14 bold")
        entry_costo.grid(row=3, columns=1, padx=10, pady=10)
        entry_costo.insert(0,item_values[4])

        lbl_stock = Label(ventana_editar, text="Stock: ", font="sans 14 bold", bg="#C6D9E3")
        lbl_stock.grid(row=4,column=0, padx=10, pady=10)
        entry_stock = Entry(ventana_editar, font = "sans 14 bold")
        entry_stock.grid(row=4, columns=1, padx=10, pady=10)
        entry_stock.insert(0,item_values[5])

        def guardar_cambios():
             #Recuperar el nuevo ID del prodcuto de codigo de barras
             nuevo_id = entry_id.get()
             nombre = entry_nombre.get()
             proveedor = entry_proveedor.get()
             precio = entry_precio.get()
             costo = entry_costo.get()
             stock = entry_stock.get()

             if not (nombre and proveedor and precio and costo and stock):
                messagebox.showwarning("Guardar cambios", "Rellene todos los campos.")
                return
             """
             try:
              precio = float(precio.replace(",", ""))
              costo = float(costo.replace(",", ""))
             except ValueError:
                messagebox.showwarning("Guardar cambios", "Ingrese valores numericos validos para precio y costo.")
                return
            """
             consulta = "UPDATE inventario SET num_id =%s ,nombre= %s,proveedor= %s, precio=%s, costo= %s, stock=%s WHERE id=%s"
             parametros =(nuevo_id, nombre, proveedor, precio, costo, stock, item_id)
             self.eje_consulta(consulta, parametros)

             self.actualizar_inventario()

             ventana_editar.destroy()

        btn_guardar = Button(ventana_editar, text="Guardar cambios", font="sans 14 bold", command=guardar_cambios)
        btn_guardar.place(x=80,y=250, width=240, height=40)

    def show_frames(self, container):
      top_level = tk.Toplevel(self) #se crea una ventana independiente a la pantalla inicial que se abre
      frame = container(top_level) #es el top level que se abre
      frame.config(bg="#C6D9E3")
      frame.pack(fill="both", expand=True) #es para que se expanda en toda la ventana
      top_level.geometry("1100x650+120+20")
      top_level.resizable(False, False)

      top_level.transient(self.master)
      top_level.grab_set()

      top_level.focus_set()
      top_level.lift()


    def proveedores(self):
            self.show_frames(Proveedores)


 