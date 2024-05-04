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
    segments, info = model.transcribe(audio_path, beam_size=1, no_speech_threshold=0.6, best_of=5, patience=1)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    output_path = audio_path + ".ai." + info.language + ".srt"

    srt_dict = {}

    with open(output_path, "w", encoding="utf-8") as srt:
        for segment in segments:
            print(
                f"{segment.id}\n"
                f"{segment.start} --> {segment.end}\n"
                f"{segment.text.strip()}\n",
                file=srt,
                flush=True,
            )
            srt_dict[segment.id] = {"id":segment.id,"start":segment.start,"end":segment.end,"text":segment.text.strip()}
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    time_taken = time.time() - audio_time_start
    print(f"原生字幕已保存到: {output_path},花费时间：{time_taken}" )

    del model
    torch.cuda.empty_cache()

    return output_path, srt_dict, info.language