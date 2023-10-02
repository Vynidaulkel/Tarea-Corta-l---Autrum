from matplotlib.figure import Figure
import matplotlib.style as plt_style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
import customtkinter
import sys

sys.path.append("Code")
from Classes.reproductor import Playback

class Playback_UI():
    _instance = None

    stop_button_color = "#eb2f2f"
    stop_button_hover_color = "#6b0101"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Playback_UI, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, window):
        super().__init__()
        # set classes
        self.playback_instance = Playback()

        # create frame
        self.main_window = window
        
        self.playback_frame = customtkinter.CTkFrame(window, width=1000, corner_radius=0, fg_color = "transparent")
        self.playback_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.playback_frame.grid_rowconfigure(0, weight=1)
        self.playback_frame.grid_columnconfigure(0, weight=1)
    
        # Frame for graphs
        self.playback_plot_frame = customtkinter.CTkFrame(self.playback_frame, width=1000, corner_radius=0, fg_color = "transparent")
        self.playback_plot_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.playback_plot_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Graphs
        plt_style.use("Code//UI//theme.mplstyle")

        self.time_playback_fig = Figure(figsize=(6, 6), dpi=100)
        self.time_playback_plot = self.time_playback_fig.add_subplot(1, 1, 1)
        self.time_playback_canvas = FigureCanvasTkAgg(self.time_playback_fig, master=self.playback_plot_frame)
        self.time_playback_canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=(20, 10))

        self.time_playback_toolbar = NavigationToolbar2Tk(self.time_playback_canvas, self.playback_plot_frame, pack_toolbar=False)
        self.time_playback_toolbar.update()
        self.time_playback_toolbar.grid(row=0, column=0, sticky="sw", pady=10, padx=30)

        self.time_playback_line, = self.time_playback_plot.plot([])
        self.time_playback_plot.set_title("Gráfica del Tiempo")
        self.time_playback_plot.set_xlabel("Tiempo (s)", loc="right")
        self.time_playback_plot.set_ylabel("Amplitud")
        self.time_playback_plot.set_ylim(-1.2, 1.2)
        self.time_playback_canvas.draw()
        self.time_n_points = 0
        
        self.frequency_playback_fig = Figure(figsize=(6, 6), dpi=100)
        self.frequency_playback_plot = self.frequency_playback_fig.add_subplot(1, 1, 1)
        self.frequency_playback_canvas = FigureCanvasTkAgg(self.frequency_playback_fig, master=self.playback_plot_frame)
        self.frequency_playback_canvas.get_tk_widget().grid(row=0, column=1, padx=0, pady=(20, 10))

        self.frequency_playback_toolbar = NavigationToolbar2Tk(self.frequency_playback_canvas, self.playback_plot_frame, pack_toolbar=False)
        self.frequency_playback_toolbar.update()
        self.frequency_playback_toolbar.grid(row=0, column=1, sticky="sw", pady=10, padx=30)

        self.frequency_playback_line, = self.frequency_playback_plot.plot([])
        self.frequency_playback_plot.set_title("Gráfica de Frecuencia")
        self.frequency_playback_plot.set_xlabel("Frecuencia", loc="right")
        self.frequency_playback_plot.set_ylabel("Magnitud")
        self.frequency_playback_plot.set_ylim(-0.5, 100)
        self.frequency_playback_canvas.draw()
        self.freq_n_points = 0

        # Frame for Buttons
        self.playback_buttons_frame = customtkinter.CTkFrame(self.playback_frame, width=1000, corner_radius=0, fg_color = "transparent")
        self.playback_buttons_frame.grid(row=2, column=0, pady=(0, 50), rowspan=4, sticky="nsew")
        self.playback_buttons_frame.grid_columnconfigure((0, 5), weight=1)
        self.playback_uploadFile = customtkinter.CTkButton(self.playback_buttons_frame, text="Subir .atm", command=self.playback_instance.upload_audio)
        self.playback_pause_button = customtkinter.CTkButton(self.playback_buttons_frame, text="Pause", command=self.playback_instance.pause_audio)
        self.playback_resume_button = customtkinter.CTkButton(self.playback_buttons_frame, text="Resume", command=self.playback_instance.resume_audio)
        self.playback_stop_button = customtkinter.CTkButton(self.playback_buttons_frame, text="Stop", fg_color=Playback_UI.stop_button_color, hover_color=Playback_UI.stop_button_hover_color, command=self.playback_instance.stop_audio)
        
        #blit
        self.time_playback_bg = self.time_playback_canvas.copy_from_bbox(self.time_playback_plot.bbox)
        self.frequency_playback_bg = self.frequency_playback_canvas.copy_from_bbox(self.frequency_playback_plot.bbox)

        buttons = [self.playback_uploadFile, self.playback_pause_button, self.playback_resume_button, self.playback_stop_button]
        #self.playback_uploadFile.grid(row=0, column=1, padx=6, pady=(0,0))
        for i, button in enumerate(buttons):
            button.grid(row=0, column=i+1, padx=5, pady=(0, 0))


    def get_playback_frame(self):
        return self.playback_frame

    def update_time_graph_playback(self, data, rate):
        n_points = len(data)
        if (n_points == 0):
            return
        x = np.arange(n_points)
        y = data
        self.time_playback_line.set_data(x,y)

        if self.time_n_points != n_points:
            self.time_n_points = n_points
            self.time_playback_plot.set_xlim(0, n_points)
            self.time_playback_fig.canvas.resize_event()

        self.time_playback_fig.canvas.restore_region(self.time_playback_bg)
        self.time_playback_plot.draw_artist(self.time_playback_line)

        # fill in the axes rectangle
        self.time_playback_fig.canvas.blit(self.time_playback_plot.bbox)

        #self.time_analizer_canvas.draw()
    
    def update_frequency_graph_playback(self, data, rate, audio):
        n_points = len(data)
        if (n_points == 0):
            return
        y = data 
        x = rate*np.arange(0, len(data))/len(data)
        self.frequency_playback_line.set_data(x,y)
        if self.freq_n_points != round(max(x)):
            self.freq_n_points = round(max(x))
            self.frequency_playback_plot.set_xlim(0, max(x))
            self.frequency_playback_fig.canvas.resize_event()
        self.frequency_playback_fig.canvas.restore_region(self.frequency_playback_bg)
        self.frequency_playback_plot.draw_artist(self.frequency_playback_line)

        # fill in the axes rectangle
        self.frequency_playback_fig.canvas.blit(self.frequency_playback_plot.bbox)