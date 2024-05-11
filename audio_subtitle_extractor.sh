#!/bin/bash

# 检查所需的命令是否存在
for cmd in ffprobe ffmpeg jq inotifywait; do
  if ! command -v $cmd &> /dev/null; then
    echo "错误: $cmd 命令未找到。请确保已安装 $cmd。"
    exit 1
  fi
done

# 检查是否提供了 watch 或 extract 参数
if [ $# -eq 0 ]; then
  echo "请提供 watch 或 extract 参数."
  exit 1
fi

# 解析参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    --watch)
      if [ -n "$extract" ]; then
        echo "错误: watch 和 extract 参数不能同时传入."
        exit 1
      fi
      watch="$2"
      shift 2
      ;;
    --extract)
      if [ -n "$watch" ]; then
        echo "错误: watch 和 extract 参数不能同时传入."
        exit 1
      fi
      extract="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 检查文件夹是否存在
if [ -n "$watch" ] && [ ! -d "$watch" ]; then
  echo "文件夹 '$watch' 不存在."
  exit 1
fi

if [ -n "$extract" ] && [ ! -d "$extract" ]; then
  echo "文件夹 '$extract' 不存在."
  exit 1
fi

# 提取字幕的函数
extract_subtitles() {
  local folder_path="$1"

  # 遍历文件夹下的所有文件
  find "$folder_path" -type f -print0 | while IFS= read -r -d '' file; do
    echo "Processing file: $file"


    # 使用 ffprobe 解析文件信息
    if ffprobe -v quiet -print_format json -show_format -show_streams "$file" >/dev/null 2>&1; then
      echo "Valid media file found: $file"

      # 获取音频流和字幕流的数量
      audio_count=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq '.streams | map(select(.codec_type == "audio")) | length')
      subtitle_count=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq '.streams | map(select(.codec_type == "subtitle")) | length')

      echo "Number of audio streams: $audio_count"
      echo "Number of subtitle streams: $subtitle_count"

      # 如果存在音频流,提取所有音频
      if [ "$audio_count" -gt 0 ]; then
        for ((i=0; i<$audio_count; i++)); do
          # 获取音频的语言
          audio_language=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq -r ".streams | map(select(.codec_type == \"audio\")) | .[$i].tags.language")
          if [ -z "$audio_language" ]; then
            audio_language="unknown"
          fi

          # 获取音频的编码格式
          audio_codec=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq -r ".streams | map(select(.codec_type == \"audio\")) | .[$i].codec_name")

          output_file="${file%.*}_audio_${audio_language}.${audio_codec}"

          # 检查音频文件是否已经存在
          if [ ! -f "$output_file" ]; then
            echo "Extracting audio stream $i ($audio_language) to $output_file"
            ffmpeg -y -i "$file" -map 0:a:$i -c:a copy "$output_file"
          else
            echo "Audio file $output_file already exists. Skipping extraction."
          fi
        done
      fi

      # 如果存在字幕流,提取所有字幕
      if [ "$subtitle_count" -gt 0 ]; then
        for ((i=0; i<$subtitle_count; i++)); do
          # 获取字幕的语言
          subtitle_language=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq -r ".streams | map(select(.codec_type == \"subtitle\")) | .[$i].tags.language")
          if [ -z "$subtitle_language" ]; then
            subtitle_language="unknown"
          fi

          # 获取字幕的编码格式
          subtitle_codec=$(ffprobe -v quiet -print_format json -show_streams "$file" | jq -r ".streams | map(select(.codec_type == \"subtitle\")) | .[$i].codec_name")

          case "$subtitle_codec" in
            subrip)
              subtitle_ext="srt"
              ;;
            webvtt)
              subtitle_ext="vtt"
              ;;
            ass)
              subtitle_ext="ass"
              ;;
            ssa)
              subtitle_ext="ssa"
              ;;
            *)
              subtitle_ext="sub"
              ;;
          esac

          output_file="${file%.*}_subtitle_${subtitle_language}.$subtitle_ext"

          # 检查字幕文件是否已经存在
          if [ ! -f "$output_file" ]; then
            echo "Extracting subtitle stream $i ($subtitle_language) to $output_file"
            ffmpeg -y -i "$file" -map 0:s:$i "$output_file"
          else
            echo "Subtitle file $output_file already exists. Skipping extraction."
          fi
        done
      fi

    else
      echo "Not a valid media file: $file"
    fi

    echo "------------------------"
  done
}

locker_name="extract_subtitle_finished.lock"

# 如果提供了 watch 参数,则执行监视任务
if [ -n "$watch" ]; then
  echo "监视文件夹: $watch"

  inotifywait -m -r -e create --format '%w%f' "$watch" | while read -r file; do
    folder=$(dirname "$file")

    # 如果文件夹中没有 extract_subtitle_finished.lock 文件
    if [ ! -f "$folder/$locker_name" ]; then
      # 调用提取字幕的函数
      extract_subtitles "$folder"

      # 在文件夹中创建 extract_subtitle_finished.lock 文件
      touch "$folder/$locker_name"
    fi
  done
fi

# 如果提供了 extract 参数,则直接提取字幕
if [ -n "$extract" ]; then
  echo "提取字幕的文件夹: $extract"

  # 检查是否已经提取过字幕
  if [ ! -f "$extract/$locker_name" ]; then
    extract_subtitles "$extract"

    # 在文件夹中创建 extract_subtitle_finished.lock 文件
    touch "$extract/$locker_name"
  else
    echo "字幕已经提取过,跳过提取."
  fi
fi