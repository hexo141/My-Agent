import pyaudio
import wave
import toml
import numpy as np
import pathlib
import time
with open("config.toml", "r",encoding="utf-8") as f:
    config = toml.load(f)

def calculate_rms(data, sample_width=2):
    """计算音频数据的RMS（音量）"""
    audio_data = np.frombuffer(data, dtype=np.int16 if sample_width == 2 else np.int8)
    rms = np.sqrt(np.mean(audio_data ** 2))  # 计算 RMS
    return rms

def record_wav(
    FORMAT=eval(config["record"]["FORMAT"]),  # 修正拼写错误：ORMAT -> FORMAT
    CHANNELS=config["record"]["CHANNELS"],
    RATE=config["record"]["RATE"],
    CHUNK=config["record"]["CHUNK"],
    SILENCE_THRESHOLD=config["record"].get("SILENCE_THRESHOLD", 500),
    SILENCE_DURATION=config["record"].get("SILENCE_DURATION", 2.0),
    MAX_DURATION=config["record"].get("MAX_DURATION", 30.0),
    SAVE_PATH=config["record"].get("SAVE_PATH", "./")
):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("开始录音... (等待声音输入)")
    frames = []
    silent_frames = 0
    silence_limit = int(SILENCE_DURATION * RATE / CHUNK)
    max_frames = int(MAX_DURATION * RATE / CHUNK) if MAX_DURATION else None
    started = False

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.abs(audio_data)
            dB = 20 * np.log10(np.max(amplitude) if np.max(amplitude) > 0 else 1)
            # 调试信息：打印当前音量（可选）
            print(f"当前音量 dB: {dB}", end="\r")  # 动态显示
            # 检测是否开始录音（有声音输入）
            if not started:
                if dB > SILENCE_THRESHOLD:
                    started = True
                    print("\n检测到声音，开始录音...")
                else:
                    continue
            
            frames.append(data)
            
            # 检测静音
            if dB < SILENCE_THRESHOLD:
                silent_frames += 1
                if silent_frames > silence_limit:
                    print(f"\n检测到{SILENCE_DURATION}秒静音，停止录音。")
                    break
            else:
                silent_frames = 0
            
            # 检查最大录音时长
            if max_frames and len(frames) >= max_frames:
                print(f"\n达到最大录音时长{MAX_DURATION}秒，停止录音。")
                break

    except KeyboardInterrupt:
        print("\n用户手动停止录音。")
    finally:
        # 确保资源释放
        stream.stop_stream()
        stream.close()
        p.terminate()

    # 保存录音文件
    save_path = pathlib.Path(SAVE_PATH) / f"{time.strftime('%Y%m%d%H%M%S')}.wav"
    with wave.open(str(save_path), 'wb') as wave_file:
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(p.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))

    print(f"录音文件已保存为 {save_path}")
    return save_path

if __name__ == "__main__":
    record_wav()
