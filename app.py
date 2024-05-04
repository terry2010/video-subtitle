import argparse
from audio_subtitle_extractor import extract_audio_subtitle
from audio_subtitle_transcriber import transcribe_audio_to_subtitle

def parse_arguments():
    parser = argparse.ArgumentParser(description='提取文件中的音轨和字幕,并按语言存储到同级目录')
    parser.add_argument('--input', type=str, required=True, help='输入的文件路径')
    parser.add_argument('--timeout', type=int, default=60, help='每个提取命令的超时时间(秒),默认为60秒')
    parser.add_argument('--subtitle', type=str, help='要提取的字幕名称')
    parser.add_argument('--audio', type=str, help='要提取的音轨名称')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    extract_audio_subtitle(args.input, args.timeout, args.subtitle, args.audio)
    transcribe_audio_to_subtitle(args.input)