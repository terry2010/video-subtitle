#!/bin/bash

# 检查所需的命令是否存在
for cmd in ffprobe ffmpeg jq inotifywait; do
  if ! command -v $cmd &> /dev/null; then
    echo "错误: $cmd 命令未找到。请确保已安装 $cmd。"
    exit 1
  fi
done

# 检查是否提供了 watch 或 extract 参数
if [ $# -lt 2 ]; then
  echo "请提供 watch 或 extract 参数,以及并发进程数量。"
  echo "用法: $0 [--watch <folder>|--extract <folder>] [--processes <num>]"
  exit 1
fi

# 默认并发进程数量为1
processes=1

# 解析参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    --watch)
      if [ -n "$extract" ]; then
        echo "错误: watch 和 extract 参数不能同时传入。"
        exit 1
      fi
      watch="$2"
      shift 2
      ;;
    --extract)
      if [ -n "$watch" ]; then
        echo "错误: watch 和 extract 参数不能同时传入。"
        exit 1
      fi
      extract="$2"
      shift 2
      ;;
    --processes)
      processes="$2"
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
  echo "文件夹 '$watch' 不存在。"
  exit 1
fi

if [ -n "$extract" ] && [ ! -d "$extract" ]; then
  echo "文件夹 '$extract' 不存在。"
  exit 1
fi

# 等待文件复制或下载完成的函数
wait_for_file_completion() {
  local file="$1"
  local stable_time=3600      # 文件没有被修改的时间(秒),默认为 1 小时
  local check_interval=60     # 检查文件修改时间的时间间隔(秒)

  echo "等待文件复制或下载完成: $file"

  local last_modified=$(stat -c %Y "$file")

  while true; do
    sleep $check_interval
    local current_time=$(date +%s)
    local current_modified=$(stat -c %Y "$file")

    if [ $current_modified -eq $last_modified ]; then
      local elapsed_time=$((current_time - last_modified))
      if [ $elapsed_time -ge $stable_time ]; then
        echo "文件在指定时间内没有被修改,认为文件复制或下载已完成: $file"
        break
      fi
    else
      last_modified=$current_modified
    fi
  done
}

# 提取字幕的函数
extract_subtitles() {
  local file="$1"

  echo "Processing file: $file"

  # 检查是否已经提取过字幕
  if [ -f "${file%.*}.extracted" ]; then
    echo "Subtitles already extracted for $file. Skipping extraction."
    return
  fi

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

    # 创建提取完成的标记文件
    touch "${file%.*}.extracted"
  else
    echo "Not a valid media file: $file"
  fi

  echo "------------------------"
}

# 处理文件的函数
process_files() {
  local folder="$1"
  local processes="$2"

  # 创建一个命名管道用于进程同步
  local fifo="/tmp/subtitle_extractor_fifo"
  mkfifo "$fifo"

  # 初始化并发进程数量
  local current_processes=0

  while true; do
    # 查找未处理的文件
    local file=$(find "$folder" -type f ! -name "*.extracted" -print -quit)

    if [ -n "$file" ]; then
      if [ $current_processes -lt $processes ]; then
        # 增加并发进程数量
        current_processes=$((current_processes + 1))

        # 在后台启动提取字幕的进程
        (
          wait_for_file_completion "$file"
          extract_subtitles "$file"
          echo >&"$fifo"
        ) &
      else
        # 等待某个进程完成
        read -u "$fifo"
        current_processes=$((current_processes - 1))
      fi
    else
      # 没有未处理的文件,等待所有进程完成
      while [ $current_processes -gt 0 ]; do
        read -u "$fifo"
        current_processes=$((current_processes - 1))
      done
      break
    fi
  done

  # 删除命名管道
  rm "$fifo"
}

# 如果提供了 watch 参数,则执行监视任务
if [ -n "$watch" ]; then
  echo "监视文件夹: $watch"
  echo "并发进程数量: $processes"

  inotifywait -m -r -e create --format '%w%f' "$watch" | while read -r file; do
    (
      wait_for_file_completion "$file"
      process_files "$(dirname "$file")" "$processes"
    ) &
  done
fi

# 如果提供了 extract 参数,则直接提取字幕
if [ -n "$extract" ]; then
  echo "提取字幕的文件夹: $extract"
  echo "并发进程数量: $processes"
  process_files "$extract" "$processes"
fi