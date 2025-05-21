import customtkinter as ctk
from tkinter import messagebox
from db import Database

class Mesas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f0f0f0")
        self.db = Database()
        self.MAX_MESAS = 10
        self.ESTADOS = {
            0: {'nombre': 'Libre', 'color': '#0F9D58'},
            1: {'nombre': 'Ocupada', 'color': '#DB4437'},
            2: {'nombre': 'Reservada', 'color': '#F4B400'}
        }
        self.FORMAS = {
            'rectangular': {'aspecto': 'rectangle', 'ratio': 1.2},
            'circular': {'aspecto': 'oval', 'ratio': 1.0},
            'barra': {'aspecto': 'rectangle', 'ratio': 3.0}
        }
        self.mesa_seleccionada = None
        self.mesa_arrastrando = None
        self.mesa_id_arrastrando = None
        self.offset_x = 0
        self.offset_y = 0
        self.escala_plano = 1.0

        self.pack(fill="both", expand=True)
        self.widgets()
        self.cargar_mesas()

    def widgets(self):
        # Frame principal con dos secciones
        main_frame = ctk.CTkFrame(self, fg_color="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sección izquierda - Lista y controles
        left_frame = ctk.CTkFrame(main_frame, fg_color="#f0f0f0", width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        # Sección derecha - Mapa del salón
        right_frame = ctk.CTkFrame(main_frame, fg_color="#f0f0f0")
        right_frame.pack(side="right", fill="both", expand=True)

        # Canvas para el mapa del salón (usamos tk.Canvas temporalmente)
        from tkinter import Canvas
        self.canvas = Canvas(right_frame, bg="white", scrollregion=(0, 0, 2000, 1500))

        h_scroll = ctk.CTkScrollbar(right_frame, orientation="horizontal", command=self.canvas.xview)
        v_scroll = ctk.CTkScrollbar(right_frame, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame de propiedades
        prop_frame = ctk.CTkFrame(left_frame, fg_color="#f0f0f0")
        prop_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(prop_frame, text="Sillas:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_sillas = ctk.CTkEntry(prop_frame, font=ctk.CTkFont(size=12))
        self.entry_sillas.grid(row=0, column=1, pady=5)

        ctk.CTkLabel(prop_frame, text="Estado:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_estado = ctk.CTkComboBox(
            prop_frame, 
            values=[e['nombre'] for e in self.ESTADOS.values()],
            font=ctk.CTkFont(size=12)
        )
        self.combo_estado.grid(row=1, column=1, pady=5)

        ctk.CTkLabel(prop_frame, text="Forma:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.combo_forma = ctk.CTkComboBox(
            prop_frame, 
            values=list(self.FORMAS.keys()),
            font=ctk.CTkFont(size=12)
        )
        self.combo_forma.grid(row=2, column=1, pady=5)

        # Botones de acción
        btn_frame = ctk.CTkFrame(left_frame, fg_color="#f0f0f0")
        btn_frame.pack(fill="x", pady=10)

        self.btn_nueva = ctk.CTkButton(
            btn_frame, 
            text="Nueva Mesa", 
            command=self.nueva_mesa,
            fg_color="#4285F4"
        )
        self.btn_nueva.pack(fill="x", pady=5)

        self.btn_guardar = ctk.CTkButton(
            btn_frame, 
            text="Guardar", 
            command=self.guardar_mesa,
            fg_color="#0F9D58"
        )
        self.btn_guardar.pack(fill="x", pady=5)

        self.btn_eliminar = ctk.CTkButton(
            btn_frame, 
            text="Eliminar", 
            command=self.eliminar_mesa,
            fg_color="#DB4437"
        )
        self.btn_eliminar.pack(fill="x", pady=5)

        # Configurar eventos del canvas
        self.canvas.bind("<Button-1>", self.iniciar_arrastre)
        self.canvas.bind("<B1-Motion>", self.mover_mesa)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_arrastre)
        self.canvas.bind("<MouseWheel>", self.zoom_con_rueda)
        self.canvas.bind("<Control-plus>", self.zoom_in)
        self.canvas.bind("<Control-minus>", self.zoom_out)

    # Los métodos de funcionalidad se mantienen exactamente iguales
    def cargar_mesas(self):
        self.canvas.delete("all")
        mesas = self.db.obtener_mesas()
        
        if mesas:
            for mesa in mesas:
                id_mesa, sillas, estado, pos_x, pos_y, ancho, alto, forma = mesa
                aspecto = self.FORMAS.get(forma, self.FORMAS['rectangular'])['aspecto']
                color = self.ESTADOS.get(estado, self.ESTADOS[0])['color']
                
                if aspecto == "rectangle":
                    mesa_canvas = self.canvas.create_rectangle(
                        pos_x, pos_y, pos_x + ancho, pos_y + alto,
                        fill=color, tags=(f"mesa_{id_mesa}", "mesa")
                    )
                elif aspecto == "oval":
                    mesa_canvas = self.canvas.create_oval(
                        pos_x, pos_y, pos_x + ancho, pos_y + alto,
                        fill=color, tags=(f"mesa_{id_mesa}", "mesa")
                    )
                
                centro_x = pos_x + ancho / 2
                centro_y = pos_y + alto / 2
                self.canvas.create_text(
                    centro_x, centro_y,
                    text=str(id_mesa),
                    font=("Arial", 14, "bold"),
                    fill="white",
                    tags=(f"texto_{id_mesa}", "texto")
                )

                self.canvas.tag_bind(mesa_canvas, "<Button-1>", self.seleccionar_mesa_canvas)

    def seleccionar_mesa_canvas(self, event):
        item = self.canvas.find_withtag("current")
        tags = self.canvas.gettags(item)
        if tags:
            mesa_tag = tags[0]
            mesa_id = mesa_tag.split("_")[-1]
            self.cargar_propiedades_mesa(mesa_id)

    def cargar_propiedades_mesa(self, id_mesa):
        mesa = self.db.obtener_mesa_por_id(id_mesa)
        if mesa:
            id_mesa, sillas, estado, pos_x, pos_y, ancho, alto, forma = mesa
            self.entry_sillas.delete(0, "end")
            self.entry_sillas.insert(0, str(sillas))
            self.combo_estado.set(self.ESTADOS[estado]['nombre'])
            self.combo_forma.set(forma)
            self.mesa_seleccionada = id_mesa

    def nueva_mesa(self):
        try:
            sillas = int(self.entry_sillas.get())
            estado_idx = list(self.ESTADOS.keys())[self.combo_estado.current()]
            forma = self.combo_forma.get()

            if sillas <= 0:
                messagebox.showerror("Error", "El número de sillas debe ser mayor que 0.")
                return
            
            count_query = "SELECT COUNT(*) FROM mesas WHERE id !=0"
            count = self.db.obtener_datos(count_query)[0][0]
            if count >= self.MAX_MESAS:
                messagebox.showerror("Error", "No se pueden crear más mesas.")
                return
            
            id_query = "SELECT MAX(id) FROM mesas"
            max_id_result = self.db.obtener_datos(id_query)
            nuevo_id = max_id_result[0][0] + 1 if max_id_result[0][0] else 1

            ancho, alto = self.calcular_dimensiones(forma, sillas) 
            x, y = 400, 300
            
            insert_query = """
                INSERT INTO mesas (id, sillas, estado, pos_x, pos_y, ancho, alto, forma)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            parametros = (nuevo_id, sillas, estado_idx, x, y, ancho, alto, forma)
            self.db.ejecutar_query(insert_query, parametros)
            messagebox.showinfo("Éxito", "Mesa creada con éxito.")
            self.cargar_mesas()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de sillas.")

    def calcular_dimensiones(self, forma, sillas):
        base_area = sillas * 900
        if forma not in self.FORMAS:
            forma = 'rectangular'

        ratio = self.FORMAS[forma]['ratio']
        ancho = int((base_area * ratio) ** 0.5)
        alto = int((base_area / ratio) ** 0.5)
        ancho = max(40, min(ancho, 300))
        alto = max(40, min(alto, 300))
        return ancho, alto
    
    def guardar_mesa(self):
        if self.mesa_seleccionada is None:
            messagebox.showwarning("Advertencia", "No hay ninguna mesa seleccionada.")
            return

        try:
            sillas = int(self.entry_sillas.get())
            estado_idx = list(self.ESTADOS.keys())[self.combo_estado.current()]
            forma = self.combo_forma.get()

            if sillas <= 0:
                messagebox.showerror("Error", "El número de sillas debe ser mayor que 0.")
                return

            id_mesa = self.mesa_seleccionada
            coords = self.canvas.coords(f"mesa_{id_mesa}")
            if not coords or len(coords) < 4:
                messagebox.showerror("Error", "No se pudo obtener la posición de la mesa.")
                return
            
            x, y, x2, y2 = coords
            ancho, alto = self.calcular_dimensiones(forma, sillas)
            
            update_query = """
                UPDATE mesas
                SET sillas = %s, estado = %s, pos_x = %s, pos_y = %s, ancho = %s, alto = %s, forma = %s
                WHERE id = %s
            """
            parametros = (sillas, estado_idx, int(x), int(y), ancho, alto, forma, id_mesa)
            self.db.ejecutar_query(update_query, parametros)
            
            self.canvas.delete(f"mesa_{id_mesa}")
            color = self.ESTADOS[estado_idx]['color']
            aspecto = self.FORMAS[forma]['aspecto']
            
            if aspecto == 'oval':
                self.canvas.create_oval(
                    x, y, x + ancho, y + alto,
                    fill=color, tags=("mesa", f"mesa_{id_mesa}")
                )
            else:
                self.canvas.create_rectangle(
                    x, y, x + ancho, y + alto,
                    fill=color, tags=("mesa", f"mesa_{id_mesa}")
                )
            
            messagebox.showinfo("Éxito", "Mesa actualizada con éxito.")
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número válido de sillas.")    

    def eliminar_mesa(self):
        if self.mesa_seleccionada is None:
            messagebox.showwarning("Advertencia", "No hay ninguna mesa seleccionada.")
            return
        
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta mesa?")
        if not respuesta:
            return
        
        try:
            id_mesa = self.mesa_seleccionada
            delete_query = "DELETE FROM mesas WHERE id = %s"
            self.db.ejecutar_query(delete_query, (id_mesa,))
            self.canvas.delete(f"mesa_{id_mesa}")
            self.canvas.delete(f"texto_{id_mesa}")
            self.mesa_seleccionada = None
            self.cargar_mesas()
            messagebox.showinfo("Éxito", "Mesa eliminada con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar la mesa: {e}")
    
    def iniciar_arrastre(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
        
        tags = self.canvas.gettags(item[0])
        mesa_tag = next((tag for tag in tags if tag.startswith("mesa_")), None)
        if mesa_tag:
            self.mesa_arrastrando = item[0]
            self.mesa_id_arrastrando = int(mesa_tag.split("_")[-1])
            coords = self.canvas.coords(self.mesa_arrastrando)
            x, y = coords[0], coords[1]
            self.offset_x = event.x - x
            self.offset_y = event.y - y 

    def mover_mesa(self, event):
        if self.mesa_arrastrando:
            coords = self.canvas.coords(self.mesa_arrastrando)
            ancho = coords[2] - coords[0]
            alto = coords[3] - coords[1]

            nuevo_x1 = event.x - self.offset_x
            nuevo_y1 = event.y - self.offset_y
            nuevo_x2 = nuevo_x1 + ancho
            nuevo_y2 = nuevo_y1 + alto

            dx = nuevo_x1 - coords[0]
            dy = nuevo_y1 - coords[1]
            self.canvas.coords(
                self.mesa_arrastrando, nuevo_x1, nuevo_y1, nuevo_x2, nuevo_y2
            )
            self.canvas.move(f"texto_{self.mesa_id_arrastrando}", dx, dy)

    def finalizar_arrastre(self, event):
        if self.mesa_arrastrando:
            tags = self.canvas.gettags(self.mesa_arrastrando)
            mesa_tag = next((tag for tag in tags if tag.startswith("mesa_")), None)
            if mesa_tag:
                mesa_id = int(mesa_tag.split("_")[-1])
                coords = self.canvas.coords(self.mesa_arrastrando)
                x = coords[0] / self.escala_plano
                y = coords[1] / self.escala_plano
                ancho = (coords[2] - coords[0]) / self.escala_plano
                alto = (coords[3] - coords[1]) / self.escala_plano
                
                update_query = "UPDATE mesas SET pos_x = %s, pos_y = %s, ancho = %s, alto = %s WHERE id = %s"
                parametros = (x, y, ancho, alto, mesa_id)
                try:
                    self.db.ejecutar_query(update_query, parametros)
                except Exception as e:
                    print(f"Error actualizando posición de mesa {mesa_id}: {e}")
                
                self.mesa_arrastrando = None
                self.mesa_id_arrastrando = None

    def zoom_con_rueda(self, event):
        print("Zoom con rueda")
    
    def zoom_in(self, event):
        print("Zoom in")

    def zoom_out(self, event):
        print("Zoom out")

    def __del__(self):
        self.db.cerrar_conexion()
        print("Conexión cerrada con la base de datos.")