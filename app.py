import argparse
import os
import subprocess
import shutil  # 导入shutil模块


def parse_arguments():
    parser = argparse.ArgumentParser(description='提取并打印文件中的音轨和字幕数据')
    parser.add_argument('--input', type=str, required=True, help='输入的文件路径')
    return parser.parse_args()


def check_file_exists(filepath):
    return os.path.exists(filepath)


def extract_audio_subtitle(input_file):
    # 检查 ffmpeg 是否存在
    if not shutil.which("ffmpeg"):
        print("请确保ffmpeg已安装")
        return

    # 构建ffmpeg命令来提取音轨和字幕信息
    # 提取音轨信息
    command_audio = ['ffmpeg', '-i', input_file, '-map', '0:a', '-c', 'copy', '-f', 'null', '-']
    # 提取字幕信息
    command_subtitle = ['ffmpeg', '-i', input_file, '-map', '0:s', '-c', 'copy', '-f', 'null', '-']

    try:
        # 运行命令并捕获音轨输出
        audio_result = subprocess.run(command_audio, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # 打印音轨信息的stderr部分
        print("音轨信息:", audio_result.stderr.decode())

        # 运行命令并捕获字幕输出
        subtitle_result = subprocess.run(command_subtitle, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # 打印字幕信息的stderr部分
        print("字幕信息:", subtitle_result.stderr.decode())

        print("提取完成，请检查输出")
    except subprocess.CalledProcessError as e:
        print("错误：", e.output.decode())


if __name__ == '__main__':
    # 解析输入参数
    args = parse_arguments()
    input_path = args.input

    # 检查文件是否存在
    if check_file_exists(input_path):
        # 提取音轨和字幕
        extract_audio_subtitle(input_path)
    else:
        print("文件不存在")