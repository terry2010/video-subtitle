import argparse
import os
import subprocess
import shutil
import json
import time
from collections import defaultdict
from faster_whisper import WhisperModel
import sys
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import ctranslate2
import time

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.add_dll_directory(r"C:\\Program Files\\NVIDIA\\CUDNN\\v8.8\\bin")


def parse_arguments():
    # python app.py --input=test.mkv --subtitle=jpn_SDH --audio=jpn.eac3

    parser = argparse.ArgumentParser(description='提取文件中的音轨和字幕,并按语言存储到同级目录')
    parser.add_argument('--input', type=str, required=True, help='输入的文件路径')
    parser.add_argument('--timeout', type=int, default=60, help='每个提取命令的超时时间(秒),默认为60秒')
    parser.add_argument('--subtitle', type=str, help='要提取的字幕名称')
    parser.add_argument('--audio', type=str, help='要提取的音轨名称')
    return parser.parse_args()


def check_file_exists(filepath):
    return os.path.exists(filepath)


def print_audio_subtitle_info(audio_list, grouped_subtitles):
    print("文件中存在的音轨:")
    for audio in audio_list:
        print(f"- {audio['language']}.{audio['codec']}")

    print("\n文件中存在的字幕:")
    for (language, title), subtitles in grouped_subtitles.items():
        subtitle_name = f"{language}_{title}" if title else language
        print(f"- {subtitle_name}")


def extract_audio_subtitle(input_file, timeout, target_subtitle=None, target_audio=None):
    if not shutil.which("ffmpeg"):
        print("请确保ffmpeg已安装")
        return

    input_dir = os.path.dirname(os.path.abspath(input_file))
    input_name = os.path.splitext(os.path.basename(input_file))[0]

    # 获取音轨和字幕信息，并按语言分组
    command_info = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_file]
    try:
        info_result = subprocess.run(command_info, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = json.loads(info_result.stdout.decode())

        audio_list = parse_audio_info(info)
        subtitle_list = parse_subtitle_info(info)

        # 按语言和标签分组字幕流
        grouped_subtitles = defaultdict(list)
        for subtitle in subtitle_list:
            language = subtitle['language']
            tags = subtitle.get('tags', {})
            title = tags.get('title', '')
            grouped_subtitles[(language, title)].append(subtitle)

        # 检查指定的字幕和音轨是否存在
        found_subtitle = False
        found_audio = False
        for (language, title), subtitles in grouped_subtitles.items():
            subtitle_name = f"{language}_{title}" if title else language
            if target_subtitle and subtitle_name == target_subtitle:
                found_subtitle = True
                break

        for audio in audio_list:
            audio_name = f"{audio['language']}.{audio['codec']}"
            if target_audio and audio_name == target_audio:
                found_audio = True
                break

        if target_subtitle and not found_subtitle:
            print("指定的字幕不存在。")
            print_audio_subtitle_info(audio_list, grouped_subtitles)
            return
        if (target_audio and not found_audio):
            print("指定的音轨不存在。")
            print_audio_subtitle_info(audio_list, grouped_subtitles)
            return

        print("开始提取音轨和字幕...")

        # 提取音轨
        if not target_audio or found_audio:
            for audio in audio_list:
                audio_name = f"{audio['language']}.{audio['codec']}"
                if not target_audio or audio_name == target_audio:
                    output_audio = os.path.join(input_dir, f"{input_name}_{audio_name}")
                    command_extract_audio = ['ffmpeg', '-i', input_file, '-map', f"0:{audio['index']}", '-c', 'copy',
                                             '-nostats', '-loglevel', '0', '-y', output_audio]
                    try:
                        process = subprocess.Popen(command_extract_audio, stderr=subprocess.PIPE)
                        while True:
                            output = process.stderr.readline().decode().strip()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                print(output, end='\r', flush=True)
                        process.wait(timeout=timeout)
                        print(f"已提取音轨: {output_audio}")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                        print(f"提取音轨失败: {output_audio}")
                        print("错误信息:", str(e))

        # 提取字幕
        subtitle_counts = defaultdict(int)
        for (language, title), subtitles in grouped_subtitles.items():
            subtitle_name = f"{language}_{title}" if title else language
            if not target_subtitle or subtitle_name == target_subtitle:
                if len(subtitles) > 1:
                    for subtitle in subtitles:
                        subtitle_counts[(language, title)] += 1
                        output_subtitle = os.path.join(input_dir,
                                                       f"{input_name}_{subtitle_name}_{subtitle_counts[(language, title)]}.srt")
                        command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}", '-c',
                                                    'srt', '-nostats', '-loglevel', '0', '-y', output_subtitle]
                        try:
                            process = subprocess.Popen(command_extract_subtitle, stderr=subprocess.PIPE)
                            while True:
                                output = process.stderr.readline().decode().strip()
                                if output == '' and process.poll() is not None:
                                    break
                                if output:
                                    print(output, end='\r', flush=True)
                            process.wait(timeout=timeout)
                            print(f"已提取字幕: {output_subtitle}")
                        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                            print(f"提取字幕失败: {output_subtitle}")
                            print("错误信息:", str(e))
                else:
                    output_subtitle = os.path.join(input_dir, f"{input_name}_{subtitle_name}.srt")
                    subtitle = subtitles[0]
                    command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}", '-c',
                                                'srt', '-nostats', '-loglevel', '0', '-y', output_subtitle]
                    try:
                        process = subprocess.Popen(command_extract_subtitle, stderr=subprocess.PIPE)
                        while True:
                            output = process.stderr.readline().decode().strip()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                print(output, end='\r', flush=True)
                        process.wait(timeout=timeout)
                        print(f"已提取字幕: {output_subtitle}")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                        print(f"提取字幕失败: {output_subtitle}")
                        print("错误信息:", str(e))

        print("提取完成")
    except subprocess.CalledProcessError as e:
        print("错误:", e.stderr.decode())


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


def transcribe_audio_to_subtitle(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
    model = WhisperModel(model_size,
                         device=device,
                         compute_type=compute_type,
                         download_root=os.path.join("models", "Whisper", "faster-whisper"))
    segments, info = model.transcribe(audio_path, beam_size=1, no_speech_threshold=0.6, best_of=5, patience=1)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai.srt"

    # 指定本地模型路径
    model_path1 = "F:\\ai\\models\\facebook\\nllb-200-distilled-1.3B"
    model_path = "F:\\code\\video-subtitle\\models\\ctranslate2\\facebook\\nllb-200-distilled-1.3B"
    # model_path = os.path.join("models", "translate2", "facebook", "nllb-200-distilled-1.3B")


    # 设置源语言和目标语言 (根据您的模型支持的语言进行调整)
    src_lang = map_whisper_lang_to_nllb(info.language)
    tgt_lang = "zho_Hans"

    # 初始化ctranslate2模型
    translator = ctranslate2.Translator(model_path,device="cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_path1, src_lang=src_lang)


    print("Detected src nllb language '%s' , to language '%s'" % (src_lang, tgt_lang))

    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:
            # translation, elapsed_time = translate_text(translate_model, segment.text.strip(), src_lang, tgt_lang)
            source = tokenizer.convert_ids_to_tokens(tokenizer.encode(segment.text.strip()))
            target_prefix = [tgt_lang]
            results = translator.translate_batch([source], target_prefix=[target_prefix])
            target = results[0].hypotheses[0][1:]
            translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))
            print(
                f"{segment.id}\n"
                f"{segment.start} --> {segment.end}\n"
                f"{translation}\n",
                f"{segment.text.strip()}\n",
                file=srt,
                flush=True,
            )
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            print(f"{translation}")

    print(f"字幕已保存到: {output_path}")


def translate_text(model, article, src_lang, tgt_lang):
    # 开始计时
    start_time = time.time()

    # 生成翻译
    translation = model.translate_batch([article], source_lang=src_lang, target_lang=tgt_lang)

    # 计算运行时间
    elapsed_time = time.time() - start_time

    return translation[0], elapsed_time


def map_whisper_lang_to_nllb(whisper_lang_code):
    lang_map = {
        'en': 'eng_Latn',
        'zh': 'zho_Hans',
        'de': 'deu_Latn',
        'es': 'spa_Latn',
        'ru': 'rus_Cyrl',
        'ko': 'kor_Hang',
        'fr': 'fra_Latn',
        'ja': 'jpn_Jpan',
        'pt': 'por_Latn',
        'tr': 'tur_Latn',
        'pl': 'pol_Latn',
        'ca': 'cat_Latn',
        'nl': 'nld_Latn',
        'ar': 'ara_Arab',
        'sv': 'swe_Latn',
        'it': 'ita_Latn',
        'id': 'ind_Latn',
        'hi': 'hin_Deva',
        'fi': 'fin_Latn',
        'vi': 'vie_Latn',
        'iw': 'heb_Hebr',
        'uk': 'ukr_Cyrl',
        'el': 'ell_Grek',
        'ms': 'msa_Latn',
        'cs': 'ces_Latn',
        'ro': 'ron_Latn',
        'da': 'dan_Latn',
        'hu': 'hun_Latn',
        'ta': 'tam_Taml',
        'no': 'nor_Latn',
        'th': 'tha_Thai',
        'ur': 'urd_Arab',
        'hr': 'hrv_Latn',
        'bg': 'bul_Cyrl',
        'lt': 'lit_Latn',
        'la': 'lat_Latn',
        'mi': 'mri_Latn',
        'ml': 'mal_Mlym',
        'cy': 'cym_Latn',
        'sk': 'slk_Latn',
        'te': 'tel_Telu',
        'fa': 'fas_Arab',
        'lv': 'lav_Latn',
        'bn': 'ben_Beng',
        'sr': 'srp_Cyrl',
        'az': 'azj_Latn',
        'sl': 'slv_Latn',
        'kn': 'kan_Knda',
        'et': 'est_Latn',
        'mk': 'mkd_Cyrl',
        'br': 'bre_Latn',
        'eu': 'eus_Latn',
        'is': 'isl_Latn',
        'hy': 'hye_Armn',
        'ne': 'nep_Deva',
        'mn': 'mon_Cyrl',
        'bs': 'bos_Latn',
        'kk': 'kaz_Cyrl',
        'sq': 'sqi_Latn',
        'sw': 'swh_Latn',
        'gl': 'glg_Latn',
        'mr': 'mar_Deva',
        'pa': 'pan_Guru',
        'si': 'sin_Sinh',
        'km': 'khm_Khmr',
        'sn': 'sna_Latn',
        'yo': 'yor_Latn',
        'am': 'amh_Ethi',
        'fy': 'fry_Latn',
        'xh': 'xho_Latn',
        'zu': 'zul_Latn',
        'gd': 'gla_Latn',
        'eo': 'epo_Latn',
        'mt': 'mlt_Latn',
        'tg': 'tgk_Cyrl',
        'uz': 'uzb_Latn',
        'ky': 'kir_Cyrl',
        'my': 'mya_Mymr',
        'af': 'afr_Latn',
        'oc': 'oci_Latn',
        'ka': 'kat_Geor',
        'be': 'bel_Cyrl',
        'tt': 'tat_Cyrl',
        'sd': 'snd_Arab',
        'ug': 'uig_Arab',
        'ha': 'hau_Latn',
        'sa': 'san_Deva',
        'gn': 'grn_Latn',
        'gu': 'guj_Gujr',
        'ps': 'pus_Arab',
        'tk': 'tuk_Latn',
        'yi': 'ydd_Hebr',
        'lo': 'lao_Laoo',
        'fo': 'fao_Latn',
        'su': 'sun_Latn',
        'ht': 'hat_Latn',
        'dz': 'dzo_Tibt',
        'bo': 'bod_Tibt',
        'ig': 'ibo_Latn',
        'so': 'som_Latn',
        'as': 'asm_Beng',
        'or': 'ori_Orya',
        'cu': 'chu_Cyrl',
        'ce': 'che_Cyrl',
        'rw': 'kin_Latn',
        'wo': 'wol_Latn',
        'prs': 'prs_Arab',
        'mg': 'mlg_Latn',
        'ckb': 'ckb_Arab',
        'ln': 'lin_Latn',
        'jv': 'jav_Latn'
    }

    if whisper_lang_code not in lang_map:
        sys.exit(1)
        raise ValueError(f"Unsupported Whisper language code: {whisper_lang_code}")

    return lang_map[whisper_lang_code]


if __name__ == '__main__':
    args = parse_arguments()
    input_path = args.input
    timeout = args.timeout
    target_subtitle = args.subtitle
    target_audio = args.audio
    start_time = time.time()

    if check_file_exists(input_path):
        extract_audio_subtitle(input_path, timeout, target_subtitle, target_audio)
        audio_path = os.path.join(os.path.dirname(input_path),
                                  f"{os.path.splitext(os.path.basename(input_path))[0]}_{target_audio}")
        transcribe_audio_to_subtitle(audio_path)
        # 记录结束时间
        end_time = time.time()

        # 计算并打印执行时间
        execution_time = end_time - start_time
        print(f"脚本的总共执行时间是 {execution_time} 秒")

    else:
        print("文件不存在")
