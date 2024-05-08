from faster_whisper import WhisperModel
from transformers import SeamlessM4TModel, SeamlessM4TConfig

import os
import sys

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 获取当前 Python 文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 models 目录的路径
custom_model_dir = os.path.join(current_dir, "models")

# 如果 models 目录不存在,则创建它
os.makedirs(custom_model_dir, exist_ok=True)



model_name = "facebook/hf-seamless-m4t-medium"
config = SeamlessM4TConfig.from_pretrained(model_name, cache_dir=custom_model_dir)
model = SeamlessM4TModel.from_pretrained(model_name, cache_dir=custom_model_dir)

# Move the model to the GPU (if available)
model.to("cuda")




# 设置环境变量 WHISPER_MODELS_DIR 为自定义目录
os.environ["WHISPER_MODELS_DIR"] = custom_model_dir

model_sizes = [
    "large-v3",
    "large-v2",
    "large-v1",
    "large",
    "medium",
    "small",
    "base"]

for model_size in model_sizes:
    print(f"downloading model {model_size}...")
    WhisperModel(model_size,
                 device="cuda",
                 compute_type="int8",
                 download_root=os.path.join("models", "Whisper", "faster-whisper"),
                 )

sys.exit(1)

# ct2-transformers-converter --model  "F:\\ai\\models\\Whisper\\faster-whisper\\models--Systran--faster-whisper-large-v3\\" --output_dir models/ctranslate2/Whisper/faster-whisper/large-v3