import os
import ctranslate2
from transformers import AutoTokenizer
import pysubs2


def load_subtitle_to_dict(subtitle_file_path):
    """
    从字幕文件（SRT或ASS）加载字幕到字典。
    """
    print(f"Load subtitle file: {subtitle_file_path}")
    subtitle_dict = {}
    if subtitle_file_path.endswith(".srt"):
        subs = pysubs2.load(subtitle_file_path, encoding="utf-8")
        for line_num, event in enumerate(subs, start=1):
            subtitle_dict[line_num] = {'start': event.start, 'end': event.end, 'text': event.text}
    elif subtitle_file_path.endswith(".ass"):
        subs = pysubs2.load(subtitle_file_path, format="ass")
        for line_num, event in enumerate(subs, start=1):
            subtitle_dict[line_num] = {'start': event.start, 'end': event.end, 'text': event.text}
    else:
        raise ValueError("Unsupported subtitle format. Only SRT and ASS formats are supported.")
    return subtitle_dict


def translate_subtitle(subtitle_file, src_lang, tgt_lang, output_format):
    model_path = os.path.join("models", "Ctranslate2", "facebook", "nllb-200-distilled-1.3B")
    translator = ctranslate2.Translator(model_path, device="cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_path, src_lang=src_lang)

    # 加载字幕文件到字典
    subtitle_dict = load_subtitle_to_dict(subtitle_file)

    output_path = f"{os.path.splitext(subtitle_file)[0]}.{src_lang}.ai.{tgt_lang}.{output_format}"

    subs = pysubs2.SSAFile()
    for seg_num, seg in subtitle_dict.items():
        source = tokenizer.convert_ids_to_tokens(tokenizer.encode(seg['text'].strip()))
        target_prefix = [tgt_lang]
        results = translator.translate_batch([source], target_prefix=[target_prefix])
        target = results[0].hypotheses[0][1:]
        translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))

        event = pysubs2.SSAEvent(start=seg['start'], end=seg['end'])
        if output_format == "ass":
            event.text = f"{translation}\\N{{\\fs{int(subs.styles['Default'].fontsize / 3)}}}{seg['text']}"
        else:
            event.text = f"{translation}\n{seg['text']}"
        print(event.text)
        subs.append(event)

    subs.save(output_path, encoding="utf-8")
    print(f"翻译后的字幕已保存到: {output_path}")

# 示例调用（在实际使用中，应确保此调用在适当的上下文中）
# src_lang = 'auto'  # 如果模型支持自动检测
# tgt_lang = 'zho_Hans'
# subtitle_file = 'your_subtitle_file.srt'  # 支持 SRT 和 ASS 格式
# output_format = 'ass'  # 可选 'srt' 或 'ass'
# translate_subtitle(subtitle_file, src_lang, tgt_lang, output_format)