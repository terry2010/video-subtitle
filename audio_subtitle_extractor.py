import os
import subprocess
import shutil
import json
from collections import defaultdict
from utils import parse_audio_info, parse_subtitle_info, print_audio_subtitle_info


def extract_audio_subtitle(input_file, timeout, target_subtitle=None, target_audio=None, audio_format='wav',
                           audio_sample_rate=16000):
    if not shutil.which("ffmpeg"):
        print("请确保ffmpeg已安装")
        return "",""

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

        # 检查指定的字幕和音轨是否存在
        found_subtitle = False
        found_audio = False
        if target_subtitle:
            for (language, title), subtitles in grouped_subtitles.items():
                subtitle_name = f"{language}_{title}" if title else language
                if subtitle_name == target_subtitle:
                    found_subtitle = True
                    break
        else:
            found_subtitle = True

        if target_audio:
            for audio in audio_list:
                audio_name = audio['language']  # 只使用语言名称，忽略后缀名
                if audio_name == target_audio:
                    found_audio = True
                    break
        else:
            found_audio = True

        if not found_subtitle:
            print("指定的字幕不存在。")
            print_audio_subtitle_info(audio_list, grouped_subtitles)
        if not found_audio:
            print("指定的音轨不存在。")
            print_audio_subtitle_info(audio_list, grouped_subtitles)

        print("开始提取音轨和字幕...")

        # 提取音轨
        if target_audio or found_audio:
            for audio in audio_list:
                audio_name = audio['language']
                audio_codec = audio['codec']
                if not target_audio or audio_name == target_audio:
                    if "auto" != audio_format:
                        output_audio = os.path.join(input_dir, f"{input_name}_{audio_name}.{audio_format}")
                        tmp_acodec = get_audio_codec_by_extension(audio_format)
                        command_extract_audio = ['ffmpeg', '-i', input_file, '-map', f"0:{audio['index']}", '-acodec',
                                                 tmp_acodec, '-ar', str(audio_sample_rate), '-ac', '1', '-vn',
                                                 '-nostats', '-loglevel', '0', '-y', output_audio]
                    else:
                        output_audio = os.path.join(input_dir, f"{input_name}_{audio_name}.{audio_codec}")
                        command_extract_audio = ['ffmpeg', '-i', input_file, '-map', f"0:{audio['index']}", '-acodec',
                                                 'copy', '-vn', '-nostats', '-loglevel', '0', '-y', output_audio]
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
        if target_subtitle or found_subtitle:
            subtitle_counts = defaultdict(int)
            for (language, title), subtitles in grouped_subtitles.items():
                subtitle_name = f"{language}_{title}" if title else language
                if not target_subtitle or subtitle_name == target_subtitle:
                    if len(subtitles) > 1:
                        for subtitle in subtitles:
                            subtitle_counts[(language, title)] += 1
                            output_subtitle = os.path.join(input_dir,
                                                           f"{input_name}_{subtitle_name}_{subtitle_counts[(language, title)]}.srt")
                            command_extract_subtitle = ['ffmpeg', '-i', input_file, '-map', f"0:{subtitle['index']}",
                                                        '-c',
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
        return output_audio, output_subtitle
    except subprocess.CalledProcessError as e:
        print("错误:", e.stderr.decode())
        return output_audio, output_subtitle


def get_audio_codec_by_extension(extension):
    """
    根据音频文件扩展名，返回推荐的FFmpeg编码器名称。
    这个示例包括了一些常见的音频格式，但不是全部。

    :param extension: 音频文件的扩展名，不包括点，如'mp3', 'wav', 'aac'等。
    :return: 对应的音频编码器名称，若未知扩展名，则返回None。
    """
    codec_mapping = {
        'mp3': 'libmp3lame',  # 常用的MP3编码器
        'wav': 'pcm_s16le',  # 适用于需要无损PCM数据的场景
        'aac': 'aac',  # 高效率音频编码
        'flac': 'flac',  # 无损音频压缩
        'alac': 'alac',  # 苹果无损音频编码
        'ogg': 'libvorbis',  # Ogg容器中常用的Vorbis编码
        'opus': 'libopus',  # 高质量且适合网络传输的编码
        'wma': 'wmav2',  # Windows Media Audio，注意FFmpeg支持有限
        'm4a': 'aac',  # M4A通常使用AAC编码
        'aiff': 'pcm_s16le',  # 类似WAV，适用于AIFF文件
        'ac3': 'ac3',  # Dolby Digital编码
        'dts': 'dca',  # DTS音频编码
    }

    return codec_mapping.get(extension.lower(), None)
