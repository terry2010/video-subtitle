import os
from audio_transcriber import transcribe_audio
from subtitle_translator import translate_subtitle
from utils import map_whisper_lang_to_nllb
import json

def transcribe_audio_to_subtitle(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
    # 转录音频为字幕
    output_path, srt_dict, detected_lang = transcribe_audio(audio_path, model_size, device, compute_type)

    # 将字典转换为JSON字符串
    json_str = json.dumps(srt_dict, ensure_ascii=False, indent=4)

    # 打印JSON字符串
    print(json_str)

    # 如果需要将JSON字符串写入文件
    with open('srt_dict.json', 'w', encoding='utf-8') as json_file:
         json.dump(srt_dict, json_file, ensure_ascii=False, indent=4)
    srt_dict = {}
    with open('srt_dict.json', 'r', encoding='utf-8') as json_file:
             srt_dict = json.load(json_file)
    # 设置源语言和目标语言
    detected_lang = 'ja'
    src_lang = map_whisper_lang_to_nllb(detected_lang)
    tgt_lang = "zho_Hans"

    print("Detected src nllb language '%s' , to language '%s'" % (src_lang, tgt_lang))

    # 翻译字幕
    translate_subtitle(srt_dict, src_lang, tgt_lang)