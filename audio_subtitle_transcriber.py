import os
from audio_transcriber import transcribe_audio  # 假设这是您用来转录音频为文本的函数
from subtitle_translator import translate_subtitle
from utils import map_whisper_lang_to_nllb


def transcribe_audio_to_subtitle(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
    """
    将音频转换为字幕文件并返回SRT文件路径。
    """
    src_path, srt_dict, detected_lang = transcribe_audio(audio_path, model_size, device, compute_type)
    print(f"src_path:{src_path},detected_lang:{detected_lang}")
    return src_path, detected_lang
    # # 使用srt_dict的值（即字幕段落）来生成或重写SRT文件，这里假设我们只需要写入一次
    # base_name = os.path.splitext(os.path.basename(audio_path))[0]
    # srt_file_path = f"{base_name}_transcribed.srt"
    # srt_file_path = f"{base_name}.ai.{detected_lang}.srt"
    #
    # # 将字幕内容写入SRT文件，这里直接使用srt_dict的值
    # with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
    #     for seg_num, seg_info in enumerate(srt_dict.values(), start=1):
    #         srt_file.write(f"{seg_num}\n{seg_info['start']} --> {seg_info['end']}\n{seg_info['text']}\n\n")
    #
    # print(f"字幕文件已保存至: {srt_file_path}")
    # return srt_file_path, detected_lang


# 注意：这个函数在您提供的上下文中并未直接使用，但提供完整性
def translate_audio_to_subtitle(audio_path, model_size, device, src_lang, tgt_lang):
    """
    一体化功能：转录音频为字幕并翻译。
    """
    # 这里假设调用transcribe_audio_to_subtitle后直接进行翻译
    srt_file_path = transcribe_audio_to_subtitle(audio_path, model_size, device)[0]
    translate_subtitle(srt_file_path, src_lang, tgt_lang)
    # 注意：实际使用时，可能需要处理或返回翻译后的文件路径或状态信息
