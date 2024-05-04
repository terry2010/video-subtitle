import os
import time
import torch
from faster_whisper import WhisperModel
import ctranslate2
from transformers import AutoTokenizer


def transcribe_audio_to_subtitle(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
    audio_time_start = time.time()

    model = WhisperModel(model_size,
                         device=device,
                         compute_type=compute_type,
                         download_root=os.path.join("models", "Whisper", "faster-whisper"))
    segments, info = model.transcribe(audio_path, beam_size=1, no_speech_threshold=0.6, best_of=5, patience=1)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai." + info.language + ".srt"

    srt_dict = {}

    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:
            print(
                f"{segment.id}\n"
                f"{segment.start} --> {segment.end}\n"
                f"{segment.text.strip()}\n",
                file=srt,
                flush=True,
            )
            srt_dict[segment.id] = {"id": segment.id, "start": segment.start, "end": segment.end,
                                    "text": segment.text.strip()}
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    time_taken = time.time() - audio_time_start
    print(f"原生字幕已保存到: {output_path},花费时间：{time_taken}")

    output_path = audio_path + ".ai.srt"

    del model
    torch.cuda.empty_cache()

    trans_time_start = time.time()

    # 指定本地模型路径
    model_path1 = "F:\\ai\\models\\facebook\\nllb-200-distilled-1.3B"
    model_path = "F:\\code\\video-subtitle\\models\\ctranslate2\\facebook\\nllb-200-distilled-1.3B"
    # model_path = os.path.join("models", "translate2", "facebook", "nllb-200-distilled-1.3B")

    # 设置源语言和目标语言 (根据您的模型支持的语言进行调整)
    src_lang = map_whisper_lang_to_nllb(info.language)
    tgt_lang = "zho_Hans"

    # 初始化ctranslate2模型
    translator = ctranslate2.Translator(model_path, device="cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_path1, src_lang=src_lang)

    print("Detected src nllb language '%s' , to language '%s'" % (src_lang, tgt_lang))

    with open(output_path, "w", encoding="utf-8") as srt:
        for k in srt_dict:
            # translation, elapsed_time = translate_text(translate_model, segment.text.strip(), src_lang, tgt_lang)
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
    time_taken = time.time() - audio_time_start
    time_taken_str = "{:.2f}".format(time_taken)  # 格式化时间为带两位小数的字符串
    print(f"字幕已保存到: {output_path}，花费时间：{time_taken_str}秒")


def map_whisper_lang_to_nllb(lang):
    lang_map = {
        "en": "eng_Latn",
        "zh": "zho_Hans",
        "de": "deu_Latn",
        "es": "spa_Latn",
        "ru": "rus_Cyrl",
        "ko": "kor_Hang",
        "fr": "fra_Latn",
        "ja": "jpn_Jpan",
        "pt": "por_Latn",
        "tr": "tur_Latn",
        "pl": "pol_Latn",
        "ca": "cat_Latn",
        "nl": "nld_Latn",
        "ar": "ara_Arab",
        "sv": "swe_Latn",
        "it": "ita_Latn",
        "id": "ind_Latn",
        "hi": "hin_Deva",
        "fi": "fin_Latn",
        "vi": "vie_Latn",
        "iw": "heb_Hebr",
        "uk": "ukr_Cyrl",
        "el": "ell_Grek",
        "ms": "zsm_Latn",
        "cs": "ces_Latn",
        "ro": "ron_Latn",
        "da": "dan_Latn",
        "hu": "hun_Latn",
        "ta": "tam_Taml",
        "no": "nob_Latn",
        "th": "tha_Thai",
        "ur": "urd_Arab",
        "hr": "hrv_Latn",
        "bg": "bul_Cyrl",
        "lt": "lit_Latn",
        "la": "lat_Latn",
        "mi": "mri_Latn",
        "ml": "mal_Mlym",
        "cy": "cym_Latn",
        "sk": "slk_Latn",
        "te": "tel_Telu",
        "fa": "fas_Arab",
        "lv": "lav_Latn",
        "bn": "ben_Beng",
        "sr": "srp_Cyrl",
        "az": "azj_Latn",
        "sl": "slv_Latn",
        "kn": "kan_Knda",
        "et": "est_Latn",
        "mk": "mkd_Cyrl",
        "br": "bre_Latn",
        "eu": "eus_Latn",
        "is": "isl_Latn",
        "hy": "hye_Armn",
        "ne": "npi_Deva",
        "bs": "bos_Latn",
        "kk": "kaz_Cyrl",
        "sq": "als_Latn",
        "sw": "swh_Latn",
        "gl": "glg_Latn",
        "mr": "mar_Deva",
        "pa": "pan_Guru",
        "si": "sin_Sinh",
        "km": "khm_Khmr",
        "sn": "sna_Latn",
        "yo": "yor_Latn",
        "so": "som_Latn",
        "af": "afr_Latn",
        "oc": "oci_Latn",
        "ka": "kat_Geor",
        "be": "bel_Cyrl",
        "tg": "tgk_Cyrl",
        "sd": "snd_Arab",
        "gu": "guj_Gujr",
        "am": "amh_Ethi",
        "yi": "ydd_Hebr",
        "lo": "lao_Laoo",
        "uz": "uzn_Latn",
        "fo": "fao_Latn",
        "ht": "hat_Latn",
        "ps": "pbu_Arab",
        "tk": "tuk_Latn",
        "nn": "nno_Latn",
        "mt": "mlt_Latn",
        "sa": "san_Deva",
        "lb": "ltz_Latn",
        "my": "mya_Mymr",
        "bo": "bod_Tibt",
        "tl": "tgl_Latn",
        "mg": "plt_Latn",
        "as": "asm_Beng",
        "tt": "tat_Cyrl",
        "haw": "haw_Latn",
        "ln": "lin_Latn",
        "ha": "hau_Latn",
        "ba": "bak_Cyrl",
        "jw": "jav_Latn",
        "su": "sun_Latn",
    }
    return lang_map.get(lang, lang)
