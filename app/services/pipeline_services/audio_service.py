import numpy as np
import librosa 
import matplotlib.pyplot as plt 
from app.models.audio import Audio

import logging

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class AudioUtils() : 

    def __init__(self , array , sampling_rate , language , job_id) : 

        self.array =  array
        self.sampling_rate = sampling_rate
        self.language = language
        self.job_id = job_id

    @classmethod
    def load_resample_audio(cls , audio : Audio)  : 

        array , sampling_rate = librosa.load(audio.audio_filepath , sr=None)

        language = audio.language 

        job_id = audio.job_id

        instance = cls(
            array = array , 
            sampling_rate = sampling_rate , 
            language = language , 
            job_id = job_id
        )


        instance.resample()
        instance.reduce_noise()

        return instance


    def resample(self , target_sr = 16_000) : 
        resmpled_audio = librosa.resample(self.array , orig_sr=self.sampling_rate , target_sr=target_sr) 
        self.array = resmpled_audio
        self.sampling_rate = target_sr
        logger.info("Audio was resmapled successfully")
    
    def audio_stats(self) : 
        stats = {}
        stats["size_MB"] = np.round((self.array.size * self.array.itemsize) * 1 / (1024 * 1024) , decimals=2) 
        stats["smapling_rate"] = self.sampling_rate
        stats["total_samples"] = float(np.size(self.array))
        stats["mean"] = float(np.mean(self.array))
        stats["max"] = float(np.max(self.array))
        stats["min"] = float(np.min(self.array))
        stats["std"] = float(np.std(self.array))

        return stats
    

    def reduce_noise(self) : 
        pass

    def visualize_waveform(self , output_dir : str ,figure_width : int = 12 ) : 
        
        plt.figure().set_figwidth(figure_width) 

        plt.xlabel("time [s]") 

        plt.ylabel("amplitude")
 
        librosa.display.waveshow(y = self.array , sr = self.sampling_rate)

        plt.tight_layout() 

        plt.savefig(output_dir + "/waveform.png") 


        plt.close()

    def visualize_freq_spectrum(self , output_dir : str ,figure_width : int = 12 , db_amplitudes : bool = True , log_scale : bool = True) : 
        
        # calculate the dft : 
        window = np.hanning(len(self.array)) 
        windowed_input = window * self.array 
        dft = np.fft.rfftn(windowed_input) 

        # get teh amplitudes : 
        amplitudes = np.abs(dft)

        if db_amplitudes :
            amplitudes = librosa.amplitude_to_db(amplitudes , ref=np.max)

        # get the frequencies : 
        frequencies = librosa.fft_frequencies(sr=self.sampling_rate , n_fft=len(self.array))

        plt.figure().set_figwidth(figure_width)
        plt.plot(frequencies , amplitudes)  
        plt.title("Frequecy Spectrum")
        plt.xlabel("frequency [Hz]") 
        plt.ylabel("amplitude [Db]") 

        if log_scale :
            plt.xscale("log") 


        plt.savefig(output_dir + "/freq.png") 

        plt.close()

    def visualize_mel_diagram(self ,output_dir : str  ,figure_width : int = 12 , cmap : str = "viridis") : 

        stft = librosa.stft(self.array)

        scale_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

        plt.figure().set_figwidth(figure_width)

        librosa.display.specshow(scale_db, x_axis="time", y_axis="hz" , cmap =  cmap)

        plt.title("Spectrogram")

        plt.colorbar()

        plt.savefig(output_dir + "/mel.png") 

        plt.close()