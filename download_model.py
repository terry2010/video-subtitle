from transformers import AutoModelForSpeechSeq2Seq
import os
import sys

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 获取当前 Python 文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 models 目录的路径
custom_model_dir = os.path.join(current_dir, "models")

# 如果 models 目录不存在,则创建它
os.makedirs(custom_model_dir, exist_ok=True)

model_ids = [
    "openai/whisper-large-v2",
    "openai/whisper-medium",
    "openai/whisper-small",
    "openai/whisper-base"
]

for model_id in model_ids:
    AutoModelForSpeechSeq2Seq.from_pretrained(model_id, cache_dir=custom_model_dir)

sys.exit(1)