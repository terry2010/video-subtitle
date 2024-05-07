import os
import ctranslate2
from transformers import AutoTokenizer


def load_srt_to_dict(srt_file_path):
    """
    从SRT文件加载字幕到字典。
    """
    print(f"Load srt file:{srt_file_path}")
    srt_dict = {}
    with open(srt_file_path, "r", encoding="utf-8") as srt_file:
        segment_text = ""
        start_time = ""
        end_time = ""
        for line_num, line in enumerate(srt_file, start=1):
            line = line.strip()
            if line.isdigit():
                if segment_text:
                    srt_dict[line_num] = {'start': start_time, 'end': end_time, 'text': segment_text}
                    segment_text = ""
            elif '-->' in line:
                start_time, end_time = line.split(' --> ')
            else:
                if start_time and end_time:
                    segment_text += '\n' if segment_text else ''
                    segment_text += line
        # 添加最后一段
        if segment_text:
            srt_dict[line_num + 1] = {'start': start_time, 'end': end_time, 'text': segment_text}
    return srt_dict


def translate_subtitle(srt_file, src_lang, tgt_lang):
    model_path = os.path.join("models", "Ctranslate2", "facebook", "nllb-200-distilled-1.3B")
    translator = ctranslate2.Translator(model_path, device="cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_path, src_lang=src_lang)

    # 加载SRT文件到字典
    srt_dict = load_srt_to_dict(srt_file)

    output_path = f"{os.path.splitext(srt_file)[0]}.{src_lang}.ai.{tgt_lang}.srt"

    with open(output_path, "w", encoding="utf-8") as srt:
        for seg_num, seg in srt_dict.items():
            source = tokenizer.convert_ids_to_tokens(tokenizer.encode(seg['text'].strip()))
            target_prefix = [tgt_lang]
            results = translator.translate_batch([source], target_prefix=[target_prefix])
            target = results[0].hypotheses[0][1:]
            translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))

            # 对时间戳进行格式化，保留两位小数
            formatted_start = f"{float(seg['start']):.2f}"
            formatted_end = f"{float(seg['end']):.2f}"

            print(f"{seg_num}\n{formatted_start} --> {formatted_end}\n{translation}\n{seg['text']}\n", file=srt,flush=True)
            print(f"{seg_num}\n{formatted_start} --> {formatted_end}\n{translation}\n{seg['text']}\n")

    print(f"翻译后的字幕已保存到: {output_path}")

# 示例调用（在实际使用中，应确保此调用在适当的上下文中）
# src_lang = 'auto'  # 如果模型支持自动检测
# tgt_lang = 'zho_Hans'
# srt_file = 'your_subtitle_file.srt'
# translate_subtitle(srt_file, src_lang, tgt_lang)