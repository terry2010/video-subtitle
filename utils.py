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