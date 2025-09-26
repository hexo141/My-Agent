# mono.py 备选方案
import librosa
import soundfile as sf
import toml
import pathlib
import random
with open("config.toml", "r",encoding="utf-8") as f:
    config = toml.load(f)

def convert_to_mono_16k(file_path):
    signal, sample_rate = librosa.load(file_path, sr=16000, mono=True)
    temp_path = pathlib.Path(config["record"]["mono_save_path"]) / f"{random.randint(0, 10000)}.wav"
    sf.write(temp_path, signal, 16000)
    return temp_path
