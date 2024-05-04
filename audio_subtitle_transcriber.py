import os
from audio_transcriber import transcribe_audio
from subtitle_translator import translate_subtitle
from utils import map_whisper_lang_to_nllb

def transcribe_audio_to_subtitle(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
    # 转录音频为字幕
    output_path, srt_dict, detected_lang = transcribe_audio(audio_path, model_size, device, compute_type)

    # 指定本地模型路径
    model_path1 = "F:\\ai\\models\\facebook\\nllb-200-distilled-1.3B"
    model_path = "F:\\code\\video-subtitle\\models\\ctranslate2\\facebook\\nllb-200-distilled-1.3B"
    # model_path = os.path.join("models", "translate2", "facebook", "nllb-200-distilled-1.3B")

    # 设置源语言和目标语言
    src_lang = map_whisper_lang_to_nllb(detected_lang)
    tgt_lang = "zho_Hans"

    # 翻译字幕
    translate_subtitle(srt_dict, src_lang, tgt_lang, model_path1, model_path)