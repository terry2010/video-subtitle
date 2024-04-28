import argparse
import os
import subprocess
import shutil
import json
import time
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(description='提取文件中的音轨和字幕,并按语言存储到同级目录')
    parser.add_argument('--input', type=str, required=True, help='输入的文件路径')
    parser.add_argument('--timeout', type=int, default=60, help='每个提取命令的超时时间(秒),默认为60秒')
    return parser.parse_args()


def check_file_exists(filepath):
    return os.path.exists(filepath)


def extract_audio_subtitle(input_file, timeout):
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
            title = tags.get('title', '')  # 尝试获取字幕标题
            grouped_subtitles[(language, title)].append(subtitle)

        # 打印信息
        print("文件中存在的音轨:")
        for audio in audio_list:
            print(f"- 语言: {audio['language']}, 编解码器: {audio['codec']}")

        print("\n文件中存在的字幕:")
        for (language, title), subtitles in grouped_subtitles.items():
            subtitle_name = f"{language}_{title}" if title else language  # 构造字幕名称
            print(f"- {subtitle_name}")
            for subtitle in subtitles:
                print(f"  - 编解码器: {subtitle['codec']}")

        print("\n开始提取音轨和字幕...")

        # 提取音轨并显示进度
        for audio in audio_list:
            output_audio = os.path.join(input_dir, f"{input_name}_{audio['language']}.{audio['codec']}")
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

        # 提取字幕并显示进度
        subtitle_counts = defaultdict(int)
        for (language, title), subtitles in grouped_subtitles.items():
            subtitle_base_name = f"{language}_{title}" if title else language
            if len(subtitles) > 1:  # 仅在存在多个字幕时才添加数字后缀
                for subtitle in subtitles:
                    subtitle_counts[(language, title)] += 1
                    output_subtitle = os.path.join(input_dir,
                                                   f"{input_name}_{subtitle_base_name}_{subtitle_counts[(language, title)]}.srt")
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
                output_subtitle = os.path.join(input_dir, f"{input_name}_{subtitle_base_name}.srt")
                subtitle = subtitles[0]  # 获取唯一的字幕
                command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}", '-c', 'srt',
                                            '-nostats', '-loglevel', '0', '-y', output_subtitle]
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


if __name__ == '__main__':
    args = parse_arguments()
    input_path = args.input
    timeout = args.timeout
    if check_file_exists(input_path):
        extract_audio_subtitle(input_path, timeout)
    else:
        print("文件不存在")