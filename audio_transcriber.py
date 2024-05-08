import os
import time
import torch
from faster_whisper import WhisperModel


def transcribe_audio(audio_path, model_size="large-v1", device="cuda", compute_type="int8"):
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
                                      vad_parameters=dict(min_silence_duration_ms=500),
                                      )
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai." + info.language + ".srt"

    srt_dict = {}

    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:
            # 将秒数转换为小时:分钟:秒,毫秒的格式
            hours, remainder = divmod(int(segment.start), 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((segment.start - int(segment.start)) * 1000)

            formatted_start = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

            hours, remainder = divmod(int(segment.end), 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((segment.end - int(segment.end)) * 1000)

            formatted_end = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

            print(
                f"{segment.id}\n"
                f"{formatted_start} --> {formatted_end}\n"
                f"{segment.text.strip()}\n",
                file=srt,
                flush=True,
            )
            srt_dict[segment.id] = {"id": segment.id, "start": segment.start, "end": segment.end,
                                    "text": segment.text.strip()}
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    time_taken = time.time() - audio_time_start
    print(f"原生字幕已保存到: {output_path},花费时间：{time_taken}")

    del model
    torch.cuda.empty_cache()

    return output_path, srt_dict, info.language
