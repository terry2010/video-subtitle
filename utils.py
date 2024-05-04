import os

def check_file_exists(filepath):
    return os.path.exists(filepath)

def parse_audio_info(info):
    audio_list = []
    for stream in info['streams']:
        if stream['codec_type'] == 'audio':
            index = stream['index']
            language = stream.get('tags', {}).get('language', 'unknown')
            codec = stream['codec_name']
            audio_list.append({'index': index, 'language': language, 'codec': codec})
    return audio_list

def parse_subtitle_info(info):
    subtitle_list = []
    for stream in info['streams']:
        if stream['codec_type'] == 'subtitle':
            index = stream['index']
            language = stream.get('tags', {}).get('language', 'unknown')
            codec = stream['codec_name']
            tags = stream.get('tags', {})  # 获取所有标签信息
            subtitle_list.append({'index': index, 'language': language, 'codec': codec, 'tags': tags})
    return subtitle_list

def print_audio_subtitle_info(audio_list, grouped_subtitles):
    print("文件中存在的音轨:")
    for audio in audio_list:
        print(f"- {audio['language']}.{audio['codec']}")

    print("\n文件中存在的字幕:")
    for (language, title), subtitles in grouped_subtitles.items():
        subtitle_name = f"{language}_{title}" if title else language
        print(f"- {subtitle_name}")



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
