import os
import ctranslate2
from transformers import AutoTokenizer
import pysubs2
from langdetect import detect
import time


def detect_language(text):
    return detect(text)


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


def translate_subtitle(subtitle_file, src_lang, tgt_lang,model_name = "ct2fast-nllb-200-distilled-1.3B", device="cuda",compute_type="int8"):
    model_path = os.path.join("models", "ctranslate2", "facebook", model_name)
    translator = ctranslate2.Translator(model_path, device=device,compute_type=compute_type)
    audio_time_start = time.time()

    # 如果没有指定源语言或源语言为auto,则自动检测语言
    if src_lang is None or src_lang == 'auto':
        # 加载字幕文件到字典
        subtitle_dict = load_subtitle_to_dict(subtitle_file)
        # 取第一条字幕文本进行语言检测
        text = list(subtitle_dict.values())[0]['text']
        src_lang = detect_language(text)
        print(f"Detected source language: {src_lang}")

    print(f"source language: {src_lang},target language: {tgt_lang}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, src_lang=src_lang)

    # 加载字幕文件到字典
    subtitle_dict = load_subtitle_to_dict(subtitle_file)

    srt_output_path = f"{os.path.splitext(subtitle_file)[0]}.{src_lang}.ai.{tgt_lang}.srt"
    ass_output_path = f"{os.path.splitext(subtitle_file)[0]}.{src_lang}.ai.{tgt_lang}.ass"

    srt_subs = pysubs2.SSAFile()
    ass_subs = pysubs2.SSAFile()

    # 定义ass字幕样式
    style_top = pysubs2.SSAStyle(fontsize=24)  # 上面一行字幕的样式,默认大小
    style_bottom = pysubs2.SSAStyle(fontsize=8, primarycolor=pysubs2.Color(255, 165, 0))  # 下面一行字幕的样式,三分之一大小,橘黄色

    # 添加字幕样式到ass字幕文件中
    ass_subs.styles["Default"] = style_top
    ass_subs.styles["BottomStyle"] = style_bottom  # 为下面一行字幕的样式指定一个名称

    style_with_border = pysubs2.SSAStyle(fontsize=24, borderstyle=1, outline=1,
                                         primarycolor=pysubs2.Color(255, 255, 255),
                                         backcolor=pysubs2.Color(0, 0, 0))  # 白色文字,黑色边框
    style_bottom_with_border = pysubs2.SSAStyle(fontsize=8, borderstyle=1, outline=1,
                                                primarycolor=pysubs2.Color(255, 165, 0),
                                                backcolor=pysubs2.Color(0, 0, 0))  # 橘黄色文字,黑色边框
    # 添加样式到ass字幕文件
    ass_subs.styles["DefaultWithBorder"] = style_with_border
    ass_subs.styles["BottomStyleWithBorder"] = style_bottom_with_border

    for seg_num, seg in subtitle_dict.items():
        source = tokenizer.convert_ids_to_tokens(tokenizer.encode(seg['text'].strip()))
        target_prefix = [tgt_lang]
        results = translator.translate_batch([source], target_prefix=[target_prefix])
        target = results[0].hypotheses[0][1:]
        translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))

        srt_event = pysubs2.SSAEvent(start=seg['start'], end=seg['end'], text=translation)
        srt_subs.append(srt_event)

        ass_event = pysubs2.SSAEvent(start=seg['start'], end=seg['end'])
        ass_event.text = f"{translation}{{\\rDefaultWithBorder}}\\N{{\\rBottomStyleWithBorder}}{seg['text']}"
        ass_subs.append(ass_event)

        print("[%.2fs -> %.2fs] %s >> %s" % (seg['start'], seg['end'], seg['text'],translation))

    srt_subs.save(srt_output_path, encoding="utf-8")
    print(f"翻译后的srt字幕已保存到: {srt_output_path}")

    ass_subs.save(ass_output_path, encoding="utf-8")
    print(f"翻译后的双语ass字幕已保存到: {ass_output_path}")

    time_taken = time.time() - audio_time_start
    print(f"花费时间：{time_taken}")