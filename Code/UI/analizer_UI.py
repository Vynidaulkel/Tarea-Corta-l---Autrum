from matplotlib.figure import Figure
import matplotlib.style as plt_style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
import customtkinter
import sys

sys.path.append("Code")
from Classes.analizador import Analizador
from Classes.reproductor import Playback


class Analizer_UI():
    _instance = None

    save_button_color = "#03fc6b"
    save_button_hover_color = "#016b2d"
    save_button_text_color = "#000000"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Analizer_UI, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, window):
        super().__init__()
        # set classes
        self.analizer_instance = Analizador()
        self.playback_instance = Playback()

        # create frame
        self.main_window = window

        self.analizer_frame = customtkinter.CTkFrame(window, width=1000, corner_radius=0, fg_color = "transparent")
        self.analizer_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.analizer_frame.grid_rowconfigure(1, weight=1)
        self.analizer_frame.grid_columnconfigure(0, weight=1)

        # Frame for graphs
        self.analizer_plot_frame = customtkinter.CTkFrame(self.analizer_frame, width=1000, corner_radius=0, fg_color = "transparent")
        self.analizer_plot_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.analizer_plot_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Graphs
        plt_style.use("Code//UI//theme.mplstyle")

        self.time_analizer_fig = Figure(figsize=(6, 6), dpi=100)
        self.time_analizer_plot = self.time_analizer_fig.add_subplot(1, 1, 1)
        self.time_analizer_canvas = FigureCanvasTkAgg(self.time_analizer_fig, master=self.analizer_plot_frame)
        self.time_analizer_canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=(20, 10))

        self.time_analizer_toolbar = NavigationToolbar2Tk(self.time_analizer_canvas, self.analizer_plot_frame, pack_toolbar=False)
        self.time_analizer_toolbar.update()
        self.time_analizer_toolbar.grid(row=0, column=0, sticky="sw", pady=10, padx=30)

        self.time_analizer_line, = self.time_analizer_plot.plot([])
        self.time_analizer_plot.set_title("Gráfica del Tiempo")
        self.time_analizer_plot.set_xlabel("Tiempo (s)", loc="right")
        self.time_analizer_plot.set_ylabel("Amplitud")
        self.time_analizer_plot.set_ylim(-1.2, 1.2)
        self.time_analizer_canvas.draw()
        self.time_n_points = 0
        
        self.frequency_analizer_fig = Figure(figsize=(6, 6), dpi=100)
        self.frequency_analizer_plot = self.frequency_analizer_fig.add_subplot(1, 1, 1)
        self.frequency_analizer_canvas = FigureCanvasTkAgg(self.frequency_analizer_fig, master=self.analizer_plot_frame)
        self.frequency_analizer_canvas.get_tk_widget().grid(row=0, column=1, padx=0, pady=(20, 10))

        self.frequency_analizer_toolbar = NavigationToolbar2Tk(self.frequency_analizer_canvas, self.analizer_plot_frame, pack_toolbar=False)
        self.frequency_analizer_toolbar.update()
        self.frequency_analizer_toolbar.grid(row=0, column=1, sticky="sw", pady=10, padx=30)

        self.frequency_analizer_line, = self.frequency_analizer_plot.plot([])
        self.frequency_analizer_plot.set_title("Gráfica de Frecuencia")
        self.frequency_analizer_plot.set_xlabel("Frecuencia", loc="right")
        self.frequency_analizer_plot.set_ylabel("Magnitud")
        self.frequency_analizer_plot.set_ylim(-0.5, 100)
        self.frequency_analizer_canvas.draw()
        self.freq_n_points = 0

        # Frame for Buttons
        self.analizer_buttons_frame = customtkinter.CTkFrame(self.analizer_frame, width=1000, corner_radius=0, fg_color = "transparent")
        self.analizer_buttons_frame.grid(row=2, column=0, pady=(0, 50), rowspan=4, sticky="nsew")
        self.analizer_buttons_frame.grid_columnconfigure((0, 5), weight=1)
        
        # Buttons for audio control
        self.analizador_start_button = customtkinter.CTkButton(self.analizer_buttons_frame, text="Start", command=self.analizer_instance.start_audio)
        self.analizador_pause_button = customtkinter.CTkButton(self.analizer_buttons_frame, text="Pause", command=self.analizer_instance.pause_audio)
        self.analizador_resume_button = customtkinter.CTkButton(self.analizer_buttons_frame, text="Resume", command=self.analizer_instance.resume_audio)
        self.analizador_save_button = customtkinter.CTkButton(self.analizer_buttons_frame, text="Stop & Save", fg_color=Analizer_UI.save_button_color, text_color=Analizer_UI.save_button_text_color, hover_color=Analizer_UI.save_button_hover_color, command=self.analizer_instance.save_audio)
        
        #blit
        self.time_analizer_bg = self.time_analizer_canvas.copy_from_bbox(self.time_analizer_plot.bbox)
        self.frequency_analizer_bg = self.frequency_analizer_canvas.copy_from_bbox(self.frequency_analizer_plot.bbox)

        # Place buttons
        buttons = [self.analizador_start_button, self.analizador_pause_button, self.analizador_resume_button, self.analizador_save_button]

        for i, button in enumerate(buttons):
            button.grid(row=0, column=i+1, padx=5, pady=(0, 0))
    
    def get_analizer_frame(self):
        return self.analizer_frame

    def update_time_graph_analizer(self, data, rate):
        n_points = len(data)
        if (n_points == 0):
            return

        x = np.arange(n_points)
        y = data
        self.time_analizer_line.set_data(x,y)

        if self.time_n_points != n_points:
            self.time_n_points = n_points
            self.time_analizer_plot.set_xlim(0, n_points)
            self.time_analizer_fig.canvas.resize_event()

        self.time_analizer_fig.canvas.restore_region(self.time_analizer_bg)
        self.time_analizer_plot.draw_artist(self.time_analizer_line)
        # fill in the axes rectangle
        self.time_analizer_fig.canvas.blit(self.time_analizer_plot.bbox)
    
    def update_frequency_graph_analizer(self, data, rate, audio):
        n_points = len(data)
        if (n_points == 0):
            return

        y = data 
        x = rate*np.arange(0, len(data))/len(data)
        self.frequency_analizer_line.set_data(x,y)
        if self.freq_n_points != round(max(x)):
            self.freq_n_points = round(max(x))
            self.frequency_analizer_plot.set_xlim(0, max(x))
            self.frequency_analizer_fig.canvas.resize_event()

        self.frequency_analizer_fig.canvas.restore_region(self.frequency_analizer_bg)
        self.frequency_analizer_plot.draw_artist(self.frequency_analizer_line)

        # fill in the axes rectangle
        self.frequency_analizer_fig.canvas.blit(self.frequency_analizer_plot.bbox)