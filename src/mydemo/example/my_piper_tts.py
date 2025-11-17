from piper import PiperVoice, SynthesisConfig
import wave
import os

# 加载模型
voice = PiperVoice.load(
    model_path="/Users/jiaxiaopeng/pyhub/piper-models/zh/zh_CN-huayan-medium.onnx",
    config_path="/Users/jiaxiaopeng/pyhub/piper-models/zh/zh_CN-huayan-medium.onnx.json",
    use_cuda=False
)

text = "今天天气真不错，适合出去散步。我是中国人。"

# 生成音频（返回 bytes）
audio_bytes = voice.synthesize(text)

out_path = "/Users/jiaxiaopeng/pyhub"
fine_name = os.path.join(out_path, "out.wav");

syn_config = SynthesisConfig(
    volume=0.5,  # half as loud
    length_scale=2.0,  # twice as slow
    noise_scale=1.0,  # more audio variation
    noise_w_scale=1.0,  # more speaking variation
    normalize_audio=False,  # use raw audio from voice
)

# 保存为 WAV
with wave.open(fine_name, "wb") as wav_file:
    voice.synthesize_wav(text, wav_file, syn_config=syn_config)

print(f"converted done:{fine_name}")
