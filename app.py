import argparse
from audio_subtitle_extractor import extract_audio_subtitle
from subtitle_translator import translate_subtitle
from audio_transcriber import transcribe_audio
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='音轨与字幕处理工具')
    subparsers = parser.add_subparsers(dest='action', help='操作选择')

    # 提取音频和字幕的子命令
    extract_parser = subparsers.add_parser('extract', help='提取音频和/或字幕')
    extract_parser.add_argument('--audio-path', type=str, required=True, help='输入的视频文件路径')
    extract_parser.add_argument('--timeout', type=int, default=60, help='提取命令超时时间(秒)')
    extract_parser.add_argument('--subtitle', type=str, default=None, help='要提取的字幕名称')
    extract_parser.add_argument('--audio-lang', type=str, default=None, help='要提取的音轨名称')
    extract_parser.add_argument('--audio-format', type=str, default='auto', help='提取音频的输出格式')
    extract_parser.add_argument('--audio-sample-rate', type=int, default=16000, help='提取音频的采样率')
    extract_parser.add_argument('--print-info', action='store_true', help='打印所有字幕列表和音频列表')

    # 音频转字幕的子命令
    transcribe_parser = subparsers.add_parser('transcribe', help='将音频转为字幕')
    transcribe_parser.add_argument('--audio-path', type=str, required=True, help='音频文件路径')
    transcribe_parser.add_argument('--src-lang', type=str, help='源语言代码,默认自动检测')
    transcribe_parser.add_argument('--model-size', type=str, default="large-v1", help='模型大小')
    transcribe_parser.add_argument('--device', type=str, default="cuda", help='运行设备')
    transcribe_parser.add_argument('--compute-type', type=str, default="int8", help='显卡支持的计算类型')

    # 字幕翻译的子命令
    translate_parser = subparsers.add_parser('translate', help='翻译字幕')
    translate_parser.add_argument('--srt-file', type=str, required=True, help='待翻译的字幕文件路径')
    translate_parser.add_argument('--src-lang', type=str, help='源语言代码')
    translate_parser.add_argument('--tgt-lang', type=str, required=True, help='目标语言代码')
    translate_parser.add_argument('--translate-model', type=str, required=False, help='翻译模型名字')
    translate_parser.add_argument('--device', type=str, default="cuda", help='运行设备')
    translate_parser.add_argument('--compute-type', type=str, default="int8", help='显卡支持的计算类型')

    # 一步完成从音频到字幕翻译的子命令
    translate_from_audio_parser = subparsers.add_parser('translate_from_audio', help='直接从音频文件生成翻译后的字幕')
    translate_from_audio_parser.add_argument('--audio-path', type=str, required=True, help='音频文件路径')
    translate_from_audio_parser.add_argument('--timeout', type=int, default=60, help='提取命令超时时间(秒)')
    translate_from_audio_parser.add_argument('--subtitle', type=str, help='要提取的字幕名称')
    translate_from_audio_parser.add_argument('--audio-lang', type=str, help='要提取的音轨名称')
    translate_from_audio_parser.add_argument('--audio-format', type=str, default='auto', help='提取音频的输出格式')
    translate_from_audio_parser.add_argument('--audio-sample-rate', type=int, default=16000, help='提取音频的采样率')
    translate_from_audio_parser.add_argument('--model-size', type=str, default="large-v2", help='模型大小')
    translate_from_audio_parser.add_argument('--device', type=str, default="cuda", help='运行设备')
    translate_from_audio_parser.add_argument('--compute-type', type=str, default="int8", help='显卡支持的计算类型')
    translate_from_audio_parser.add_argument('--src-lang', type=str, help='源语言代码,默认自动检测')
    translate_from_audio_parser.add_argument('--tgt-lang', type=str, required=True, help='目标语言代码')
    translate_from_audio_parser.add_argument('--translate-model', type=str, required=False, help='翻译模型名字')
    translate_from_audio_parser.add_argument('--print-info', action='store_true', help='打印所有字幕列表和音频列表')

    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_arguments()

        if args.action == 'extract':
            output_audio, output_subtitle, all_subtitles, all_audios, success = extract_audio_subtitle(
                args.audio_path,
                args.timeout,
                args.subtitle,
                args.audio_lang,
                args.audio_format,
                args.audio_sample_rate,
                args.print_info
            )
            if success:
                print(f"所有字幕列表: {all_subtitles}")
                print(f"所有音频列表: {all_audios}")
        elif args.action == 'transcribe':
            src_path, srt_dict, detected_lang = transcribe_audio(args.audio_path,
                                                                 args.src_lang,
                                                                 args.model_size,
                                                                 args.device,
                                                                 args.compute_type)
            print(f"src_path:{src_path},detected_lang:{detected_lang}")
        elif args.action == 'translate':
            translate_subtitle(args.srt_file,
                               args.src_lang,
                               args.tgt_lang,
                               args.translate_model,
                               args.device,
                               args.compute_type)
        elif args.action == 'translate_from_audio':
            output_audio, output_subtitle, all_subtitles, all_audios, success = extract_audio_subtitle(
                args.audio_path,
                args.timeout,
                args.subtitle,
                args.audio_lang,
                args.audio_format,
                args.audio_sample_rate,
                args.print_info
            )
            if success:
                if output_subtitle:
                    srt_file_path = output_subtitle
                    detected_language = args.src_lang
                else:
                    # 如果没有提取到字幕,则使用音频生成字幕
                    srt_file_path, srt_dict, detected_language = transcribe_audio(
                        output_audio if output_audio else args.audio_path,
                        args.src_lang,
                        args.model_size,
                        args.device,
                        args.compute_type)

                # 翻译生成的字幕文件
                translate_subtitle(srt_file_path,
                                   detected_language,
                                   args.tgt_lang,
                                   args.translate_model,
                                   args.device,
                                   args.compute_type)

                print(f"所有字幕列表: {all_subtitles}")
                print(f"所有音频列表: {all_audios}")
            else:
                print("未选择有效的操作,请使用 --help 查看可用操作。")

    except Exception as e:
        print(f"未处理的异常: {str(e)}")
