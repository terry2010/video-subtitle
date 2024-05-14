import os
import subprocess
import shutil
import json
from collections import defaultdict
from utils import parse_audio_info, parse_subtitle_info, print_audio_subtitle_info


def extract_audio_subtitle(audit_path, timeout, target_subtitle=None, target_audio_lang=None, audio_format=None,
                           audio_sample_rate=16000, print_info=False):
    if not shutil.which("ffmpeg"):
        print("请确保ffmpeg已安装")
        return "", "", [], [], False

    input_dir = os.path.dirname(os.path.abspath(audit_path))
    input_name = os.path.splitext(os.path.basename(audit_path))[0]

    output_audio = ""
    output_subtitle = ""

    # 获取音轨和字幕信息,并按语言分组
    command_info = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', audit_path]
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

        if print_info:
            print_audio_subtitle_info(audio_list, grouped_subtitles)

        print("开始提取...")

        # 提取音轨
        if target_audio_lang:
            found_audio = False
            for audio in audio_list:
                audio_name = audio['language']
                if audio_name == target_audio_lang:
                    found_audio = True
                    if is_audio_file(audit_path):
                        if not audio_format or audio_format == audio['codec_name']:
                            output_audio = audit_path  # 直接返回传入的音频文件名
                            print(f"使用原始音轨: {output_audio}")
                        else:
                            output_audio = os.path.join(input_dir, f"{input_name}_{audio_name}.{audio_format}")
                            audio_codec = get_audio_codec_by_extension(audio_format)
                            command_extract_audio = ['ffmpeg', '-i', audit_path, '-map', f"0:{audio['index']}",
                                                     '-acodec', audio_codec, '-ar', str(audio_sample_rate),
                                                     '-nostats', '-loglevel', '0', '-y', output_audio]
                            try:
                                subprocess.run(command_extract_audio, check=True, timeout=timeout)
                                print(f"已提取音轨并转码: {output_audio}")
                            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                                print(f"提取音轨失败: {output_audio}")
                                print("错误信息:", str(e))
                    else:
                        output_audio = os.path.join(input_dir, f"{input_name}_{audio_name}.{audio['codec_name']}")
                        command_extract_audio = ['ffmpeg', '-i', audit_path, '-map', f"0:{audio['index']}",
                                                 '-acodec', 'copy', '-nostats', '-loglevel', '0', '-y', output_audio]
                        try:
                            subprocess.run(command_extract_audio, check=True, timeout=timeout)
                            print(f"已提取音轨: {output_audio}")
                        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                            print(f"提取音轨失败: {output_audio}")
                            print("错误信息:", str(e))
            if not found_audio:
                print("指定的音轨不存在。")

        # 提取字幕
        if target_subtitle:
            found_subtitle = False
            for (language, title), subtitles in grouped_subtitles.items():
                subtitle_name = f"{language}_{title}" if title else language
                if subtitle_name == target_subtitle:
                    found_subtitle = True
                    # 提取所有匹配的字幕
                    for i, subtitle in enumerate(subtitles):
                        output_subtitle = os.path.join(input_dir, f"{input_name}_{subtitle_name}_{i+1}.srt")
                        command_extract_subtitle = ['ffmpeg', '-i', audit_path, '-map', f"0:{subtitle['index']}",
                                                    '-c', 'srt', '-nostats', '-loglevel', '0', '-y', output_subtitle]
                        try:
                            subprocess.run(command_extract_subtitle, check=True, timeout=timeout)
                            print(f"已提取字幕: {output_subtitle}")
                        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                            print(f"提取字幕失败: {output_subtitle}")
                            print("错误信息:", str(e))

            if not found_subtitle:
                print("指定的字幕不存在。")

        print("提取完成")
        all_subtitles = [f"{lang}_{title}" if title else lang for (lang, title), subs in grouped_subtitles.items() for sub in subs]
        all_audios = [audio['language'] for audio in audio_list]
        success = True
        return output_audio, output_subtitle, all_subtitles, all_audios, success

    except subprocess.CalledProcessError as e:
        print("错误:", e.stderr.decode())
        return output_audio, output_subtitle, [], [], False



def is_audio_file(file_path):
    command_check = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
    try:
        check_result = subprocess.run(command_check, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = json.loads(check_result.stdout.decode())
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'audio':
                return True
    except subprocess.CalledProcessError:
        pass
    return False



def get_audio_codec_by_extension(extension):
    codec_mapping = {
        'mp3': 'libmp3lame',
        'wav': 'pcm_s16le',
        'aac': 'aac',
        'flac': 'flac',
        'alac': 'alac',
        'ogg': 'libvorbis',
        'opus': 'libopus',
        'wma': 'wmav2',
        'm4a': 'aac',
        'aiff': 'pcm_s16le',
        'ac3': 'ac3',
        'dts': 'dca'
    }
    return codec_mapping.get(extension.lower(), 'copy')  # Default to 'copy' if not found