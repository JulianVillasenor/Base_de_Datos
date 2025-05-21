import customtkinter as ctk
from container import Container

class Manager(ctk.CTk):  # Ahora hereda de CTk en lugar de Tk
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración inicial de la ventana
        self.title("Caja registradora versión 1.02")
        self.resizable(False, False)
        self.geometry("800x400+120+20")
        
        # Configuración del tema (reemplaza ttkthemes)
        ctk.set_appearance_mode("light")  # Opciones: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"
        
        # Contenedor principal
        self.container = ctk.CTkFrame(
            self, 
            fg_color="#C6D9E3"  # Equivalente a bg en CustomTkinter
        )
        self.container.pack(fill="both", expand=True)

        # Diccionario de frames
        self.frames = {
            Container: None  # Aquí irían otros frames si los tuvieras
        }

        self.load_frames()
        self.show_frame(Container)

    def load_frames(self):
        for FrameClass in self.frames.keys():
            frame = FrameClass(self.container, self)
            self.frames[FrameClass] = frame
            frame.pack(fill="both", expand=True)  # Mejor manejo de geometría

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()


def main():
    app = Manager()
    app.mainloop()


if __name__ == "__main__":
    main()