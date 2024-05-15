from faster_whisper import WhisperModel
from transformers import SeamlessM4TModel, SeamlessM4TConfig, AutoTokenizer, AutoModelForSeq2SeqLM
import  ctranslate2
import os
import sys

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
#windows powershell:
#$env:HF_ENDPOINT = "https://hf-mirror.com"
#linux
# HF_ENDPOINT="https://hf-mirror.com" python download_model.py

# 获取当前 Python 文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 models 目录的路径
custom_model_dir = os.path.join(current_dir, "models")

# 如果 models 目录不存在,则创建它
os.makedirs(custom_model_dir, exist_ok=True)

# model_name = "facebook/hf-seamless-m4t-medium"
# config = SeamlessM4TConfig.from_pretrained(model_name, cache_dir=custom_model_dir)
# model = SeamlessM4TModel.from_pretrained(model_name, cache_dir=custom_model_dir)
#
# # Move the model to the GPU (if available)
# model.to("cuda")


# # 模型名称
# model_name = "facebook/ct2fast-nllb-200-distilled-1.3B"
#
# # 检查模型是否已经在models文件夹中
# model_dir = os.path.join('models', model_name)
# if not os.path.exists(model_dir):
#     os.makedirs(model_dir)
#
# # 加载分词器和模型
# tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_dir)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=model_dir)

model_list = ["facebook/ct2fast-nllb-200-distilled-1.3B","facebook/nllb-200-3.3B"]

for model_name in model_list:
    model_dir = os.path.join('models', model_name)
    model_path = os.path.join(model_dir, model_name)
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    # 加载分词器和模型
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=model_dir)

# windows:
#ct2-transformers-converter --model facebook/nllb-200-3.3B --output_dir ~/tmp-ct2fast-nllb-200-3.3B --force --copy_files tokenizer.json README.md tokenizer_config.json generation_config.json special_tokens_map.json .gitattributes --quantization int8_float16 --trust_remote_code
#ct2-transformers-converter --model F:\ai\models\michaelfeil\ct2fast-nllb-200-3.3B --output_dir models/tmp-ct2fast-nllb-200-3.3B --force --copy_files tokenizer.json README.md tokenizer_config.json generation_config.json special_tokens_map.json .gitattributes --quantization int8_float16 --trust_remote_code

# linux:
# ct2-transformers-converter --model /workspace/model_repository/facebook/nllb-200-3.3B --output_dir models/ctranslate2/ct2fast-nllb-200-3.3B --force --copy_files tokenizer.json README.md tokenizer_config.json generation_config.json special_tokens_map.json .gitattributes --quantization int8_float16 --trust_remote_code
# ct2-transformers-converter --model /workspace/model_repository/facebook/ct2fast-nllb-200-distilled-1.3B  --output_dir models/ctranslate2/ct2fast-ct2fast-nllb-200-distilled-1.3B  --force --copy_files tokenizer.json README.md tokenizer_config.json generation_config.json special_tokens_map.json .gitattributes --quantization int8_float16 --trust_remote_code

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
