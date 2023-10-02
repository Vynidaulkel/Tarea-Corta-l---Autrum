import numpy as np
import pickle
import sounddevice as sd
import os
from tkinter import messagebox
import scipy.fft as fourier
import matplotlib.pyplot as plt
from scipy.io import wavfile


class Analizador():
    _instance = None
    done_reading_wav = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Analizador, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance
    
    def initialize(self, window):
        self.app = window
        self.paused = False
        self.recording = False
        self.audio_data = np.array([])
        self.audio_data_queue = np.array([])
        self.frequency_data = np.array([])
        self.sample_rate = 44100
        self.refresh_rate = 1
        self.stream = None
        
    def set_UI(self, analizer_ui):
        self.analizer_ui = analizer_ui
    
    def reset_analizer(self):
        self.audio_data = np.array([])
        self.paused = False
        self.recording = False

    def set_config(self, sample_rate = -1, refresh_rate = -1):
        if (sample_rate > 0):
            self.sample_rate = sample_rate
        if (refresh_rate > 0):
            self.refresh_rate = refresh_rate

    def save_config(self):
        with open("Code\\UI\\Assets\\parameters.txt", "w") as f:
            f.write(f"Sample Rate: {self.sample_rate}\n")
            f.write(f"Refresh Data: {self.refresh_rate}\n")

    def load_wav(self, path):
        # TODO read and do stuff
        Analizador.set_done_reading_wav(True)

    @staticmethod
    def set_done_reading_wav(bool):
        Analizador.done_reading_wav = bool
    
    def update_graphs(self):
        self.analizer_ui.update_time_graph_analizer(self.audio_data_queue, self.sample_rate)
        self.analizer_ui.update_frequency_graph_analizer(self.frequency_data, self.sample_rate, self.audio_data)
        if self.recording and not self.paused: 
            self.analizer_ui.get_analizer_frame().after(self.refresh_rate, self.update_graphs)

    def start_audio(self):
        self.audio_data = np.array([])
        self.audio_data_queue = np.array([])
        self.frequency_data = np.array([])
        self.recording = True
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.callback)
        self.stream.start()
        self.update_graphs()
        print("Grabación iniciada.")
    
    def pause_audio(self):
        self.paused = True
        print("Grabación pausada.")

    def resume_audio(self):
        self.paused = False
        self.update_graphs()
        print("Grabación reanudada.")
    
    def fast_fourier(self, audio_data):
        audio_data = audio_data.flatten()
        freq = fourier.fft(audio_data)
        freq = abs(freq)
        freq = freq[0: len(freq)//2]
        return freq
        

    def callback(self, indata, frames, time, status):
        if self.recording and not self.paused:
            self.audio_data_queue = np.array(indata)
            self.audio_data = np.append(self.audio_data, self.audio_data_queue)
            self.frequency_data = self.fast_fourier(indata)

    def save_audio(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        desktop_path = os.path.expanduser("~")
        audio_file_name = 'audio_data.atm'
        save_path = os.path.join(desktop_path, 'Desktop', audio_file_name)


        atm_data = {'audio': self.audio_data, 'sample_rate': self.sample_rate}
        with open(save_path, 'wb') as f:
            pickle.dump(atm_data, f)
        messagebox.showinfo("Audio Guardado", "El audio se generó exitosamente.")

        # Generar datos para gráficos en dominio de frecuencia
        fft_freq = np.fft.fftfreq(len(self.audio_data), d=1/self.sample_rate)
        fft_data = np.abs(np.fft.fft(self.audio_data))
        
        # Crear y guardar los gráficos
        t = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
        plt.subplot(2, 1, 1)
        plt.plot(t, self.audio_data)
        plt.title('Audio en el dominio del tiempo')

        plt.subplot(2, 1, 2)
        plt.plot(fft_freq, fft_data)
        plt.title('Espectro de frecuencia')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Amplitud')

        plt.tight_layout()
        plt.savefig('audio_graphs.png')
        plt.show()
       

        