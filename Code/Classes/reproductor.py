import sounddevice as sd
from tkinter.filedialog import askopenfilename
import pickle
import numpy as np
import scipy.fft as fourier
import threading
import time
import time as time_module

class Playback():
    _instance = None
    done_reading_atm = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Playback, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance
    
    def initialize(self, window):
        self.app = window
        self.audio_data_queue = np.array([])
        self.sample_rate = 44100
        self.refresh_rate = 10
        self.time_data = np.array([])
        self.frequency_data = np.array([])
        self.paused = False
        self.playing = False
        self.framenums = 0
        self.frame_skip = 10
        self.frame_skip_value = 0

    def set_UI(self, playback_ui):
        self.playback_ui = playback_ui
    
    def reset_playback(self):
        # Reset the audio and graph data
        self.time_data = np.array([])
        self.frequency_data = np.array([])
        self.audio_data_queue = np.array([])

        # Update the graphs with empty data
        self.playback_ui.update_time_graph_playback(self.time_data, self.sample_rate)
        self.playback_ui.update_frequency_graph_playback(self.frequency_data, self.sample_rate, self.time_data)

        # Reset other states if needed
        self.playing = False
        self.paused = False
        self.framenums = 0

        print("Playback and graphs reset.")
    
    @staticmethod
    def set_done_reading_wav(bool):
        Playback.done_reading_atm = bool

    def audio_g(self, segundos):
        self.total_iteraciones = int(self.audio_data_queue.size / 1136)
        tiempo_por_iteracion = (segundos  - 0.5)/ self.total_iteraciones
        for _ in range(self.total_iteraciones):
            start_index=self.framenums*1137
            end_index=(self.framenums+1)*1137

            frame_data=self.audio_data_queue[start_index:end_index]
            if end_index >= self.audio_data_queue.size:
                break

            audio_data = frame_data.reshape(-1, 1)
            self.framenums += 1

            self.time_data = audio_data
            self.frequency_data = self.fast_fourier(audio_data)
            # Espera el tiempo calculado para asegurarte de que el loop tome N segundos en total
            time.sleep(tiempo_por_iteracion)
    
    def set_config(self, sample_rate = -1, refresh_rate = -1):
        if (sample_rate > 0):
            self.sample_rate = sample_rate
        if (refresh_rate > 0):
            self.refresh_rate = refresh_rate

    def save_config(self):
        with open("Code\\UI\\Assets\\parameters.txt", "w") as f:
            f.write(f"Sample Rate: {self.sample_rate}\n")
            f.write(f"Refresh Data: {self.refresh_rate}\n")
    
    def update_graphs(self):
        self.playback_ui.update_time_graph_playback(self.time_data, self.sample_rate)
        self.playback_ui.update_frequency_graph_playback(self.frequency_data, self.sample_rate, self.time_data)
        if self.playing: 
            self.playback_ui.get_playback_frame().after(self.refresh_rate, self.update_graphs)
    
    def fast_fourier(self, audio_data):
        audio_data = audio_data.flatten()
        freq = fourier.fft(audio_data)
        freq = abs(freq)
        freq = freq[0: len(freq)//2]
        return freq
    
    def output_callback(self, outdata, frames, time, status):
        if not self.playing:
            raise sd.CallbackStop
        while self.paused:
            time_module.sleep(0.1)
        start_index=self.framenums*frames
        end_index=(self.framenums+1)*frames
        frame_data=self.audio_data_queue[start_index:end_index]

        if end_index >= self.audio_data_queue.size:
            self.playing = False
            raise sd.CallbackStop

        audio_data = frame_data.reshape(-1, 1)
        outdata[:]= audio_data
        self.framenums += 1
        self.time_data = audio_data
        self.frequency_data = self.fast_fourier(audio_data)

    def start_audio_stream(self):
        self.playing = True
        self.update_graphs()
        with sd.OutputStream(samplerate=self.sample_rate, channels=1, callback=self.output_callback):
            while self.playing:
                while self.paused:
                    time.sleep(0.1)
                time.sleep(0.1)

    def upload_audio(self):
        archivo_atm = askopenfilename()

        with open(archivo_atm, 'rb') as f:
            datos = pickle.load(f)

        audio_data = datos['audio']
        audio_data = np.array(audio_data)
        audio_data = audio_data.astype(np.float32)
        self.audio_data_queue = (np.concatenate((self.audio_data_queue, audio_data))).astype(np.float32)
        self.sample_rate = datos['sample_rate']
        self.framenums = 0

        duracion_s = len(audio_data) / self.sample_rate
        print(f"La duración del audio es de {duracion_s} segundos.")

        t1 = threading.Thread(target=self.start_audio_stream)
        t1.start()

    def pause_audio(self):
        self.paused = True
        print("Audio paused.")

    def resume_audio(self):
        self.paused = False
        print("Audio resumed.")

    def stop_audio(self):
        self.playing = False
        self.paused = False
        self.framenums = 0
        print("Audio stopped.")
