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
    # Run on GPU with FP16
    # model = WhisperModel(model_size, device="cuda", compute_type="int8")

    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    # model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # model = WhisperModel("F:\\ai\\models\\Systran\\faster-whisper-large-v3", device=device, compute_type=compute_type)
    segments, info = model.transcribe(audio_path, beam_size=1, no_speech_threshold=0.6, best_of=5, patience=1)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai.srt"

    # 指定本地模型路径
    model_path = "F:/ai/models/facebook/nllb-200-distilled-1.3B"
    # model_path = "F:/ai/models/facebook/nllb-200-1.3B"

    # 初始化模型和 tokenizer
    translate_model, translate_tokenizer, translate_device = translate_init(model_path)

    # 设置源语言和目标语言 (根据您的模型支持的语言进行调整)
    src_lang = "jpn_Jpan"
    tgt_lang = "zho_Hans"

    # 输入文本
    # article = "中国電力などが山口県上関町で計画する、原発の使用済み核燃料を一時保管する中間貯蔵施設の建設を巡り、中国電が23日、予定地で建設が可能かを判断するためのボーリング調査を開始した。調査は半年程度を予定し、既に進めている文献調査の結果と合わせて分析する。建設が可能と判断されれば、町に改めて建設の申し入れをし、町が建設の是非を判断する見通しだ。"

    # 翻译文本
    # translation, elapsed_time = translate_text(translate_model, translate_tokenizer, translate_device, article, src_lang, tgt_lang)

    # 打印原文、翻译结果和运行时间
    # print(f"原文: {article}")
    # print(f"翻译: {translation}")
    # print(f"运行时间: {elapsed_time:.2f} 秒")



    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:
            translation, elapsed_time = translate_text(translate_model,
                                                       translate_tokenizer,
                                                       translate_device,
                                                       segment.text.strip(),
                                                       src_lang, tgt_lang)
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


def translate_init(model_path):
    # 加载本地模型和 tokenizer
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)

    # 使用 GPU (如果有)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 将模型移动到 GPU
    model.to(device)

    return model, tokenizer, device

def translate_text(model, tokenizer, device, article, src_lang, tgt_lang):
    # 开始计时
    start_time = time.time()

    # 准备输入并移动到 GPU
    inputs = tokenizer(article, return_tensors="pt", max_length=1024, truncation=False).to(device)

    # 生成翻译 (在 GPU 上运行)
    with torch.no_grad():
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang],
            max_length=1024,
            num_beams=5,
        )

    # 结束计时
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 解码并返回翻译结果和运行时间
    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    return translation, elapsed_time


if __name__ == '__main__':
    args = parse_arguments()
    input_path = args.input
    timeout = args.timeout
    target_subtitle = args.subtitle
    target_audio = args.audio

    if check_file_exists(input_path):
        extract_audio_subtitle(input_path, timeout, target_subtitle, target_audio)
        audio_path = os.path.join(os.path.dirname(input_path),
                                  f"{os.path.splitext(os.path.basename(input_path))[0]}_{target_audio}")
        transcribe_audio_to_subtitle(audio_path)
    else:
        print("文件不存在")
