from tkinter import filedialog
from scipy.io import wavfile
import numpy as np
import customtkinter
import pickle
import os
import matplotlib.pyplot as plt
from tkinter import messagebox
import sys

sys.path.append("Code")
from Classes.analizador import Analizador

class Upload_WAV_UI():
    _instance = None

    save_button_color = "#03fc6b"
    save_button_hover_color = "#016b2d"
    save_button_text_color = "#000000"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Upload_WAV_UI, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, window):
        super().__init__()
        # set classes
        self.analizer_instance = Analizador()

        # create frame
        self.main_window = window
        
        self.wav_frame = customtkinter.CTkFrame(window, width=1000, corner_radius=0, fg_color = "transparent")
        self.wav_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.wav_frame.grid_rowconfigure(0, weight=1)
        self.wav_frame.grid_columnconfigure(0, weight=1)

        # Buttons
        self.upload_wav_button = customtkinter.CTkButton(self.wav_frame, text="Subir archivo WAV", command=self.upload_wav)
        self.upload_wav_button.grid(row=0, column=0, padx=0, pady=0)

    def get_upload_wav_frame(self):
        return self.wav_frame

    def upload_wav(self):
        file_path = filedialog.askopenfilename(title="Seleccione un archivo wav", filetypes=[("Archivos de audio", "*.wav"), ("Todos los archivos", "*.*")])
        if file_path:
            self.analizer_instance.load_wav(file_path)
            while (self.analizer_instance.done_reading_wav is False):
                print("archivo no wav")
                break
            self.analizer_instance.set_done_reading_wav(False)
            samplerate, data = wavfile.read(file_path)
            data = data / max(abs(data))
            desktop_path = os.path.expanduser("~")
            audio_file_name = 'audio_data.atm'
            save_path = os.path.join(desktop_path, 'Desktop', audio_file_name)


            atm_data = {'audio': data, 'sample_rate': samplerate}
            with open(save_path, 'wb') as f:
                pickle.dump(atm_data, f)
            messagebox.showinfo("Audio Guardado", "El audio se generó exitosamente.")


            # Generar datos para gráficos en dominio de frecuencia
            fft_freq = np.fft.fftfreq(len(data), d=1/samplerate)
            fft_data = np.abs(np.fft.fft(data))

            # Crear y guardar los gráficos
            t = np.linspace(0, len(data) / samplerate, len(data))
            plt.subplot(2, 1, 1)
            plt.plot(t, data)
            plt.title('Audio en el dominio del tiempo')

            plt.subplot(2, 1, 2)
            plt.plot(fft_freq, fft_data)
            plt.title('Espectro de frecuencia')
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Amplitud')

            plt.tight_layout()
            plt.savefig('audio_graphs.png')
            plt.show()

    