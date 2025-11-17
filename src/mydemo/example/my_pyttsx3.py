import pyttsx3
### pyttsx3
engine = pyttsx3.init()

# 获取当前语速并修改
rate = engine.getProperty('rate')
print(f"默认语速: {rate}")
engine.setProperty('rate', 150)  # 设置语速（字/分钟）

# 获取并设置音量（0.0 到 1.0）
volume = engine.getProperty('volume')
print(f"默认音量: {volume}")
engine.setProperty('volume', 0.9)

# 获取可用的语音列表
voices = engine.getProperty('voices')
for voice in voices:
    print(f"ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")

# 设置语音（例如选择中文）
# com.apple.voice.compact.zh-TW.Meijia
# com.apple.voice.compact.zh-HK.Sinji
# com.apple.voice.compact.zh - CN.Tingting
engine.setProperty('voice', 'com.apple.voice.compact.zh - CN.Tingting')  # 根据系统支持情况选择合适的 voice id

engine.say("现在语速和音量都已调整。今天天气真不错，适合出去散步。我是中国人。")
engine.runAndWait()