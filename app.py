import argparse
from audio_subtitle_extractor import extract_audio_subtitle
from audio_subtitle_transcriber import transcribe_audio_to_subtitle
from subtitle_translator import translate_subtitle


def parse_arguments():
    parser = argparse.ArgumentParser(description='音轨与字幕处理工具')
    subparsers = parser.add_subparsers(dest='action', help='操作选择')

    # 提取音频和字幕的子命令
    extract_parser = subparsers.add_parser('extract', help='提取音频和/或字幕')
    extract_parser.add_argument('--input', type=str, required=True, help='输入的视频文件路径')
    extract_parser.add_argument('--timeout', type=int, default=60, help='提取命令超时时间(秒)')
    extract_parser.add_argument('--subtitle', type=str, help='要提取的字幕名称')
    extract_parser.add_argument('--audio', type=str, help='要提取的音轨名称')

    # 音频转字幕的子命令
    transcribe_parser = subparsers.add_parser('transcribe', help='将音频转为字幕')
    transcribe_parser.add_argument('--audio-path', type=str, required=True, help='音频文件路径')
    transcribe_parser.add_argument('--model-size', type=str, default="large-v1", help='模型大小')
    transcribe_parser.add_argument('--device', type=str, default="cuda", help='运行设备')

    # 字幕翻译的子命令
    translate_parser = subparsers.add_parser('translate', help='翻译字幕')
    translate_parser.add_argument('--srt-file', type=str, required=True, help='待翻译的字幕文件路径')
    translate_parser.add_argument('--src-lang', type=str, help='源语言代码')
    translate_parser.add_argument('--tgt-lang', type=str, help='目标语言代码')

    # 新增一步完成的子命令
    translate_from_audio_parser = subparsers.add_parser('translate_from_audio', help='直接从音频文件生成翻译后的字幕')
    translate_from_audio_parser.add_argument('--audio-path', type=str, required=True, help='音频文件路径')
    translate_from_audio_parser.add_argument('--model-size', type=str, default="large-v2", help='模型大小')
    translate_from_audio_parser.add_argument('--device', type=str, default="cuda", help='运行设备')
    translate_from_audio_parser.add_argument('--src-lang', type=str, help='源语言代码，默认自动检测')
    translate_from_audio_parser.add_argument('--tgt-lang', type=str, required=True, help='目标语言代码')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.action == 'extract':
        extract_audio_subtitle(args.input, args.timeout, args.subtitle, args.audio)
    elif args.action == 'transcribe':
        transcribe_audio_to_subtitle(args.audio_path, args.model_size, args.device)
    elif args.action == 'translate':
        translate_subtitle(args.srt_file, args.src_lang, args.tgt_lang)
    elif args.action == 'translate_from_audio':
        # 先转录音频为字幕
        srt_file = transcribe_audio_to_subtitle(args.audio_path, args.model_size, args.device)

        # 假设转录后的字幕文件名格式为 'audio_path_language.srt'
        # 这里需要根据实际输出的文件名规则调整
        base_name = os.path.splitext(os.path.basename(args.audio_path))[0]
        language_detected = args.src_lang or "auto"  # 如果没有指定源语言，则自动检测
        srt_file_with_lang = f"{base_name}_{language_detected}.srt"

        # 进行翻译
        translate_subtitle(srt_file_with_lang, language_detected, args.tgt_lang)
    else:
        print("未选择有效的操作，请使用 --help 查看可用操作。")