import wave
import json
import vosk
import os
import mono
import record

import toml
try:
    if os.path.exists("./tmp"):
        os.makedirs("./tmp")
except:
    pass
class STT():
    def __init__(self) -> None:
        with open("config.toml", "r", encoding="utf-8") as f:
            self.config = toml.load(f)
        # 使用配置中的模型路径
        model_path = self.config["record"]["DEFAULT_SPT_MODEL_PATH"]
        self.model = vosk.Model(model_path)
        
    def Speech_to_Text(self, file_path: str = None, model_path: str = None, use_mono: bool = True, use_record: bool = False):
        # 处理录音情况
        if use_record or file_path is None:
            file_path = record.record_wav()
        
        # 处理模型路径
        if model_path is not None:
            self.model = vosk.Model(model_path)
        
        # 处理单声道转换
        actual_file_path = file_path
        if use_mono:
            actual_file_path = mono.convert_to_mono_16k(file_path)
        
        # 打开音频文件并验证格式
        wf = wave.open(str(actual_file_path), "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("音频文件必须是16位单声道WAV格式")
            wf.close()
            return None
        
        # 初始化识别器
        rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
        results = []
        
        # 读取并处理音频数据
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                results.append(result.get("text", ""))
        
        # 获取最终结果
        final_result = json.loads(rec.FinalResult())
        results.append(final_result.get("text", ""))
        
        # 关闭文件
        wf.close()
        
        # 清理临时文件（如果是转换后的）
        if use_mono and actual_file_path != file_path:
            try:
                os.remove(actual_file_path)
            except:
                pass
        
        # 组合并返回结果
        full_text = " ".join([r for r in results if r])
        return full_text.strip()

if __name__ == "__main__":
    stt = STT()
    print(stt.Speech_to_Text())
