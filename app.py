import argparse
import os
import subprocess
import shutil
import json
import time

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

    command_info = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_file]

    try:
        # 运行命令并捕获输出
        info_result = subprocess.run(command_info, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 解析音轨和字幕信息
        info = json.loads(info_result.stdout.decode())
        audio_list = parse_audio_info(info)
        subtitle_list = parse_subtitle_info(info)

        print("开始提取音轨和字幕...")

        # 提取音轨并按语言存储到同级目录
        for audio in audio_list:
            output_audio = os.path.join(input_dir, f"{input_name}_{audio['language']}.{audio['codec']}")
            command_extract_audio = ['ffmpeg', '-i', input_file, '-map', f"0:{audio['index']}", '-c', 'copy', output_audio]
            try:
                subprocess.run(command_extract_audio, check=True, stderr=subprocess.PIPE, timeout=timeout)
                print(f"已提取音轨: {output_audio}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"提取音轨失败: {output_audio}")
                print("错误信息:", str(e))

        # 提取字幕并按语言存储到同级目录
        for subtitle in subtitle_list:
            output_subtitle_srt = os.path.join(input_dir, f"{input_name}_{subtitle['language']}.srt")
            output_subtitle_ass = os.path.join(input_dir, f"{input_name}_{subtitle['language']}.ass")

            # 尝试使用srt格式提取字幕
            command_extract_subtitle_srt = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}", '-c', 'srt', output_subtitle_srt]
            try:
                subprocess.run(command_extract_subtitle_srt, check=True, stderr=subprocess.PIPE, timeout=timeout)
                print(f"已提取字幕: {output_subtitle_srt}")
                continue
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"使用srt格式提取字幕失败: {output_subtitle_srt}")
                print("错误信息:", str(e))

            # 如果srt格式提取失败,尝试使用ass格式提取字幕
            command_extract_subtitle_ass = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}", '-c', 'ass', output_subtitle_ass]
            try:
                subprocess.run(command_extract_subtitle_ass, check=True, stderr=subprocess.PIPE, timeout=timeout)
                print(f"已提取字幕: {output_subtitle_ass}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"使用ass格式提取字幕失败: {output_subtitle_ass}")
                print("错误信息:", str(e))

        print("提取完成")
        print("音轨信息:", audio_list)
        print("字幕信息:", subtitle_list)
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
            subtitle_list.append({'index': index, 'language': language, 'codec': codec})
    return subtitle_list

if __name__ == '__main__':
    args = parse_arguments()
    input_path = args.input
    timeout = args.timeout

    if check_file_exists(input_path):
        extract_audio_subtitle(input_path, timeout)
    else:
        print("文件不存在")