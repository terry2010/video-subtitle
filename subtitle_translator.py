import os
import time
import ctranslate2
from transformers import AutoTokenizer

def translate_subtitle(srt_dict, src_lang, tgt_lang):
    # 指定本地模型路径
    model_path1 = "F:\\ai\\models\\facebook\\nllb-200-distilled-1.3B"
    # model_path = "F:\\code\\video-subtitle\\models\\ctranslate2\\facebook\\nllb-200-distilled-1.3B"
    model_path = os.path.join("models", "Ctranslate2", "facebook", "nllb-200-distilled-1.3B")

    trans_time_start = time.time()

    # 初始化ctranslate2模型
    translator = ctranslate2.Translator(model_path, device="cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_path1, src_lang=src_lang)

    print("Detected src nllb language '%s' , to language '%s'" % (src_lang, tgt_lang))

    output_path = tgt_lang + ".ai.srt"

    with open(output_path, "w", encoding="utf-8") as srt:
        for k in srt_dict:
            seg = srt_dict[k]
            segment_id = "{:.2f}".format(srt_dict[k]['id'])  # 格式化时间为带两位小数的字符串

            print(f"{srt_dict[k]['id']}-{srt_dict[k]['text']}")
            source = tokenizer.convert_ids_to_tokens(tokenizer.encode(srt_dict[k]['text'].strip()))
            target_prefix = [tgt_lang]
            results = translator.translate_batch([source], target_prefix=[target_prefix])
            target = results[0].hypotheses[0][1:]
            translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))
            print(
                f"{srt_dict[k]['id']}\n"
                f"{srt_dict[k]['start']} --> {srt_dict[k]['end']}\n"
                f"{translation}\n",
                f"{srt_dict[k]['text'].strip()}\n",
                file=srt,
                flush=True,
            )
            print("[%.2fs -> %.2fs] %s" % (srt_dict[k]['start'], srt_dict[k]['end'], srt_dict[k]['text']))
            print(f"{translation}")
    time_taken = time.time() - trans_time_start
    time_taken_str = "{:.2f}".format(time_taken)  # 格式化时间为带两位小数的字符串
    print(f"字幕已保存到: {output_path}，花费时间：{time_taken_str}秒")