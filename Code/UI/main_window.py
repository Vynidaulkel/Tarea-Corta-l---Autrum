from PIL import Image
from tkinter import messagebox
import customtkinter
import sys

# Code from classes
sys.path.append("Code")

from Classes.analizador import Analizador
from Classes.reproductor import Playback
# Other frames
from UI.analizer_UI import Analizer_UI
from UI.upload_wav_UI import Upload_WAV_UI
from UI.playback_UI import Playback_UI

class Main_Window(customtkinter.CTk):
    _instance = None
    
    exit_button_color = "#eb2f2f"
    exit_button_hover_color = "#6b0101"

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Main_Window, cls).__new__(cls)
        return cls._instance

    def __init__(self, size=(1600, 800), espaciado=20):
        super().__init__()
        # set classes
        self.analizer_instance = Analizador(self)
        self.playback_instance = Playback(self)

        # create app
        self.title("Autrum")
        self.geometry(f"{size[0]}x{size[1]}")
        self.width, self.height = size
        self.espaciado = espaciado

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        # create sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Left panel buttons and app name
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Autrum", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create Buttons
        self.create_buttons()

        self.frames_list = []
        # Create Analizer Frame
        self.analizer_UI = Analizer_UI(self)
        self.analizer_frame = self.analizer_UI.get_analizer_frame()
        self.analizer_instance.set_UI(self.analizer_UI)

        # Create upload wav frame
        self.wav_frame_UI = Upload_WAV_UI(self)
        self.wav_frame = self.wav_frame_UI.get_upload_wav_frame()
        
        # Create playback frame
        self.playback_UI = Playback_UI(self)
        self.playback_frame = self.playback_UI.get_playback_frame()
        self.playback_instance.set_UI(self.playback_UI)

        self.analizador()
        customtkinter.set_widget_scaling(1.5)

        self.load_parameters()
        
    def create_buttons(self):
        self.checkimage = customtkinter.CTkImage(light_image=Image.open("Code\\UI\\Assets\\checkmark.png"),
                                  dark_image=Image.open("Code\\UI\\Assets\\checkmark.png"),
                                  size=(20, 20))
        self.analizador_button = customtkinter.CTkButton(self.sidebar_frame, text="Analizador", command=self.analizador)
        self.analizar_wav_button = customtkinter.CTkButton(self.sidebar_frame, text="Analizar wav", command=self.analizar_wav)
        self.reproductor_button = customtkinter.CTkButton(self.sidebar_frame, text="Reproductor", command=self.reproductor)
        
        # Center buttons
        buttons = [self.analizador_button, self.analizar_wav_button, self.reproductor_button]

        for i, button in enumerate(buttons):
            button.grid(row=i+1, column=0, padx=20, pady=10)

        # Sample frame, label and button
        self.sampleRateLabel = customtkinter.CTkLabel(self.sidebar_frame, text="Sample rate (Hz)", anchor="w")
        self.sampleRateLabel.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.sampleRateFrame = customtkinter.CTkFrame(self.sidebar_frame, width=140, corner_radius=0, fg_color = "transparent")
        self.sampleRateFrame.grid(row=6, column=0, sticky="nsew")
        self.sampleRateFrame.columnconfigure(0, weight=1)

        self.sampleRateEntry = customtkinter.CTkEntry(self.sampleRateFrame, placeholder_text="44100")
        self.sampleRateEntry.grid(row=0, column=0, padx=5, pady=0)
        self.sampleRateEntry.bind("<Return>", self.save_sample_rate)
        self.sampleRate_button = customtkinter.CTkButton(self.sampleRateFrame, image=self.checkimage, text="", command=self.save_sample_rate, width=20, height=20)
        self.sampleRate_button.grid(row=0, column=1, padx=0, pady=0)

        # refresh rate frame, label and button
        self.refreshRateLabel = customtkinter.CTkLabel(self.sidebar_frame, text="Refresh rate (ms)", anchor="w")
        self.refreshRateLabel.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.refreshRateFrame = customtkinter.CTkFrame(self.sidebar_frame, width=140, corner_radius=0, fg_color = "transparent")
        self.refreshRateFrame.grid(row=8, column=0, sticky="nsew")
        self.refreshRateFrame.columnconfigure(0, weight=1)

        self.refreshRateEntry = customtkinter.CTkEntry(self.refreshRateFrame, placeholder_text="10")
        self.refreshRateEntry.grid(row=0, column=0, padx=5, pady=0)
        self.refreshRateEntry.bind("<Return>", self.save_refresh_rate)
        self.refreshRate_button = customtkinter.CTkButton(self.refreshRateFrame, image=self.checkimage, text="", command=self.save_refresh_rate, width=20, height=20)
        self.refreshRate_button.grid(row=0, column=1, padx=0, pady=0)

        # Change apperance button
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(0, 0))
        self.appearance_mode_optionemenu.set("System")

        # Close button
        self.salir_button = customtkinter.CTkButton(self.sidebar_frame, text="Salir", fg_color=Main_Window.exit_button_color, hover_color=Main_Window.exit_button_hover_color, command=self.destroy)
        self.salir_button.grid(row=11, column=0, padx=20, pady=(10, 20))

    def analizador(self):
        self.analizer_instance.reset_analizer()
        self.analizer_frame.tkraise()
    
    def analizar_wav(self):
        self.analizer_instance.reset_analizer()
        self.wav_frame.tkraise()
    
    def reproductor(self):
        self.playback_instance.reset_playback()
        self.playback_frame.tkraise()

    def save_sample_rate(self, event = None):
        try:
            sample_rate = int(self.sampleRateEntry.get())
            self.analizer_instance.set_config(sample_rate=sample_rate)
            self.analizer_instance.save_config()
            self.focus_set()
        except:
            messagebox.showinfo("Error", "sample_rate: Solo se permiten ints")

    def save_refresh_rate(self, event = None):
        try:
            refresh_rate = int(self.refreshRateEntry.get())
            self.analizer_instance.set_config(refresh_rate=refresh_rate)
            self.analizer_instance.save_config()

            self.playback_instance.set_config(refresh_rate=refresh_rate)
            self.playback_instance.save_config()
            self.focus_set()
        except:
            messagebox.showinfo("Error", "refresh_rate: Solo se permiten ints")
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def load_parameters(self):
        try:
            with open("Code\\UI\\Assets\\parameters.txt", "r") as f:
                lines = f.readlines()
                sample_rate = int(lines[0].split(":")[1].strip())
                refresh_rate = int(lines[1].split(":")[1].strip())
                self.analizer_instance.set_config(sample_rate, refresh_rate)
                self.playback_instance.set_config(sample_rate, refresh_rate)
                self.sampleRateEntry.insert(0, str(sample_rate))
                self.refreshRateEntry.insert(0, str(refresh_rate))

        except FileNotFoundError:
            print("Archivo no encontrado. Los parámetros no se han cargado.")
        except ValueError:
            print("Error al leer el archivo. Los parámetros no se han cargado.")
        except IndexError:
            print("El archivo no tiene el formato esperado. Los parámetros no se han cargado.")

if __name__ == "__main__":
    app = Main_Window()
    app.mainloop()