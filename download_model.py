from faster_whisper import WhisperModel
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
    WhisperModel(model_size,
                 device="cuda",
                 compute_type="int8",
                 download_root=os.path.join("models", "Whisper", "faster-whisper"),
                 )

sys.exit(1)