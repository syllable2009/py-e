from gtts import gTTS
import os
### gTTS（Google Text-to-Speech）支持保存音频的 TTS 库,缺点：需要网络，且 Google 服务在某些地区可能受限。


text = "今天天气真不错，适合出去散步。我是中国人。你好，这是通过 gTTS 生成的语音。"
tts = gTTS(text=text, lang='zh')  # lang='zh' 表示中文
out_path = "/Users/jiaxiaopeng/pyhub"
fine_name = os.path.join(out_path, "output.mp3");
tts.save(fine_name)
print(f"语音已保存为 {fine_name}")