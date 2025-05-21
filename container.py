import customtkinter as ctk
from ventas import Ventas
from inventario import Inventario
from mesas import Mesas
from PIL import Image

# Configuración de apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Container(ctk.CTkFrame):
    def __init__(self, padre, controlador):
        super().__init__(
            padre, 
            width=800,  # Definir tamaño aquí
            height=400
        )
        self.controlador = controlador
        self.pack(fill="both", expand=True)
        self.configure(fg_color="#C6D9E3")
        self.widgets()

    def show_frames(self, container):
        top_level = ctk.CTkToplevel(self)
        top_level.geometry("1100x650+120+20")
        top_level.resizable(False, False)
        top_level.transient(self.master)
        top_level.grab_set()
        top_level.focus_set()
        top_level.lift()
        
        frame = container(top_level)
        frame.configure(fg_color="#C6D9E3")
        frame.pack(fill="both", expand=True)

    def ventas(self):
        self.show_frames(Ventas)

    def inventario(self):
        self.show_frames(Inventario)

    def mesas(self):
        self.show_frames(Mesas)

    def widgets(self):
        frame1 = ctk.CTkFrame(
            self, 
            fg_color="#C6D9E3",
            width=800,  # Tamaño definido en constructor
            height=400
        )
        frame1.pack(fill="both", expand=True)
        
        # Botón de Ventas
        imagen_ventas = ctk.CTkImage(Image.open("icono/carrito.png"), size=(50, 50))
        btnventas = ctk.CTkButton(
            frame1,
            text="Ir a ventas",
            font=ctk.CTkFont(family="sans serif", size=18, weight="bold"),
            fg_color="#f4b400",
            text_color="white",
            command=self.ventas,
            image=imagen_ventas,
            compound="left",
            corner_radius=10,
            width=240,  # Tamaño en constructor
            height=60
        )
        btnventas.place(x=500, y=30)

        # Botón de Inventario
        imagen_inventario = ctk.CTkImage(Image.open("icono/inventario.png"), size=(50, 50))
        btninventario = ctk.CTkButton(
            frame1,
            text="Ir a inventario",
            font=ctk.CTkFont(family="sans serif", size=18, weight="bold"),
            fg_color="#c62e26",
            text_color="white",
            command=self.inventario,
            image=imagen_inventario,
            compound="left",
            corner_radius=10,
            width=240,
            height=60
        )
        btninventario.place(x=500, y=130)

        # Botón de Mesas
        imagen_mesas = ctk.CTkImage(Image.open("icono/mesa-circular.png"), size=(50, 50))
        btnmesas = ctk.CTkButton(
            frame1,
            text="Mesas",
            font=ctk.CTkFont(family="sans serif", size=18, weight="bold"),
            fg_color="#0F9D58",
            text_color="white",
            command=self.mesas,
            image=imagen_mesas,
            compound="left",
            corner_radius=10,
            width=240,
            height=60
        )
        btnmesas.place(x=500, y=230)

        # Logo
        self.logo_image = ctk.CTkImage(Image.open("imagenes/Piedra.png"), size=(280, 280))
        self.logo_label = ctk.CTkLabel(frame1, image=self.logo_image, text="")
        self.logo_label.place(x=100, y=30)

        # Copyright
        copyright_label = ctk.CTkLabel(
            frame1,
            text="© 2022 Piedra Romana. Todos los derechos reservados",
            font=ctk.CTkFont(family="sans serif", size=12, weight="bold"),
            text_color="gray"
        )
        copyright_label.place(x=180, y=350)