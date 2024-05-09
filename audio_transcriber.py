import os
import time
import torch
import json
from faster_whisper import WhisperModel


def transcribe_audio(audio_path, language=None, model_size="large-v1", device="cuda", compute_type="int8"):
    audio_time_start = time.time()

    model = WhisperModel(model_size,
                         device=device,
                         compute_type=compute_type,
                         download_root=os.path.join("models", "Whisper", "faster-whisper"))
    segments, info = model.transcribe(audio_path,
                                      beam_size=1,
                                      no_speech_threshold=0.6,
                                      best_of=5,
                                      patience=1,
                                      vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=700),
                                      word_timestamps=False,
                                      language=language
                                      )
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai." + info.language + ".srt"

    srt_dict = {}

    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:

            formatted_start = format_seconds(segment.start)
            formatted_end = format_seconds(segment.end)

            print(
                f"{segment.id}\n"
                f"{formatted_start} --> {formatted_end}\n"
                f"{segment.text.strip()}\n",
                file=srt,
                flush=True,
            )
            srt_dict[segment.id] = {"id": segment.id, "start": segment.start, "end": segment.end,
                                    "text": segment.text.strip()}
            # print("[%s -> %s] %s" % (formatted_start, formatted_end, segment.text))
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    time_taken = time.time() - audio_time_start
    print(f"原生字幕已保存到: {output_path},花费时间：{time_taken}")

    del model
    torch.cuda.empty_cache()

    return output_path, srt_dict, info.language


def format_seconds(seconds):
    """将秒数转换为 00:02:03,456 格式的字符串"""
    if seconds < 0:
        return "00:00:00,000"  # 负数秒返回一个默认值

    # 将秒拆分为小时、分钟、秒和毫秒
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 此时 seconds 包含了整秒数和小数部分的秒数
    # 将整数秒和小数秒分开来处理
    int_seconds = int(seconds)  # 整数部分的秒
    fractional_seconds = seconds - int_seconds  # 小数部分的秒
    milliseconds = int(fractional_seconds * 1000)  # 转换小数秒到毫秒

    # 按照 00:02:03,456 的格式格式化字符串
    return f"{int(hours):02d}:{int(minutes):02d}:{int_seconds:02d},{milliseconds:03d}"
