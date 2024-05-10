import os
import subprocess
import shutil
import json
from collections import defaultdict
from utils import parse_audio_info, parse_subtitle_info, print_audio_subtitle_info


def extract_audio_subtitle(input_file, timeout, target_subtitle=None, target_audio=None, audio_format='wav',
                           audio_sample_rate=16000, print_info=False):
    if not shutil.which("ffmpeg"):
        print("请确保ffmpeg已安装")
        return "", "", [], [], False

    input_dir = os.path.dirname(os.path.abspath(input_file))
    input_name = os.path.splitext(os.path.basename(input_file))[0]

    output_audio = ""
    output_subtitle = ""

    # 获取音轨和字幕信息,并按语言分组
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

        if print_info:
            print_audio_subtitle_info(audio_list, grouped_subtitles)

        print("开始提取...")

        # 提取音轨
        if target_audio:
            found_audio = False
            for audio in audio_list:
                audio_name = audio['language']
                if audio_name == target_audio:
                    found_audio = True
                    output_audio = os.path.join(input_dir,
                                                f"{input_name}_{audio_name}.{audio_format if audio_format != 'auto' else audio['codec']}")
                    command_extract_audio = ['ffmpeg', '-i', input_file, '-map', f"0:{audio['index']}",
                                             '-acodec', get_audio_codec_by_extension(
                            audio_format) if audio_format != 'auto' else 'copy',
                                             '-ar', str(audio_sample_rate), '-ac', '1', '-vn', '-nostats', '-loglevel',
                                             '0', '-y', output_audio]
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
                    if len(subtitles) == 1:
                        subtitle = subtitles[0]
                        output_subtitle = os.path.join(input_dir, f"{input_name}_{subtitle_name}.srt")
                        command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}",
                                                    '-c', 'srt', '-nostats', '-loglevel', '0', '-y', output_subtitle]
                        try:
                            subprocess.run(command_extract_subtitle, check=True, timeout=timeout)
                            print(f"已提取字幕: {output_subtitle}")
                        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                            print(f"提取字幕失败: {output_subtitle}")
                            print("错误信息:", str(e))
                    else:
                        for i, subtitle in enumerate(subtitles):
                            output_subtitle = os.path.join(input_dir, f"{input_name}_{subtitle_name}.srt")
                            command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}",
                                                        '-c', 'srt', '-nostats', '-loglevel', '0', '-y',
                                                        output_subtitle]
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