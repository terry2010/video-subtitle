# video-subtitle
a video subtitle generator


# 提取视频中的所有字幕和音轨:
``` 
python app.py extract --input test.mov

python app.py extract --input test.mov  --audio eng --audio-format mp3 --audio-sample-rate 16000

```

仅将音频文件转换成字幕（假设你已经从视频中提取了音频或有单独的音频文件）:

``` 
python app.py transcribe --audio-path test.mov

python app.py transcribe --audio-path test_eng.mp3


python app.py transcribe --audio-path test_eng.mp3 --model-size small

```

翻译已有字幕文件（假设你已经有了一个名为'subtitles.srt'的字幕文件需要从日语翻译成中文）:

``` 
python app.py translate --srt-file test_eng.mp3.ai.en.srt --src-lang en --tgt-lang zho_Hans

```

一步完成：从音频文件直接生成翻译后的字幕（假设音频为test_audio.wav，目标是将其内容转为字幕后并翻译成中文，源语言自动检测）:

``` 
python app.py translate_from_audio --audio-path test_eng.aac --model-size large-v1 --device cuda --tgt-lang zho_Hans


python app.py translate_from_audio --audio-path test_eng.mp3 --model-size small --device cuda --tgt-lang zho_Hans

```





全程使用chatgpt4.0, claude3-opus 网页版 生成代码

整体而言， 目前（2024-04-29） chatgpt4网页版 在编程能力方面全面落后于 claude3-opus 。 chatgpt4 仅适合生成代码片段，无法正确无错误的生成完整代码

chatgpt4:

``` 
你是一个顶级python专家，写一个python程序：app.py, 功能为：
1. 启动方式：python app.py --input=test.mkv
2. 启动后获取输入参数 input ， 并检测input的文件是否存在， 若是存在输出“找到文件”，若是不存在输出“文件不存在”
```

``` 
如何给python 项目添加单元测试程序， 目录结构是什么样子的
```

``` 
我按你说的目录结构建立测试目录了， 给app.py 写个单元测试， 告诉我文件名和完整代码
```

``` 
 python -m unittest discover tests
E
======================================================================
ERROR: test_app (unittest.loader._FailedTest.test_app)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_app
Traceback (most recent call last):
  File "C:\ProgramData\anaconda3\Lib\unittest\loader.py", line 419, in _find_test_path
    module = self._get_module_from_name(name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\ProgramData\anaconda3\Lib\unittest\loader.py", line 362, in _get_module_from_name
    __import__(name)
  File "F:\code\video-subtitle\tests\test_app.py", line 3, in <module>
    from app.app import check_file_exists
ModuleNotFoundError: No module named 'app.app'; 'app' is not a package


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)

```

``` 
修改代码， 修改为：获取 input 的值后， 用ffmpeg 将文件中的音轨数据和字幕数据的解析出来， 并打印到屏幕上
```
#### commit：f465b53fe0e5ae9ac0eca4ec6eb2947b5a6debf4

使用chatgpt4.0 尝试多次后始终生成代码错误， 改为使用claude3.0-opus 生成
将app.py 源码发给claude之后：
``` 
在刚才的程序的基础上修改功能：提取音轨和字幕，并按语言将 音轨和字幕 存到test.mkv 同级目录。 并将这些音轨和字幕的信息赋值到 audio_list 和 subtitle_list 这两个变量里。 并将这两个变量的值打印出来

```

#####  commit: d43e995dc0375be40c3e2c4f8dff6ae9ebeadd24

``` 
修改代码，在提取音轨和字幕之前 打印出文件中存在的音轨和字幕， 并能实时显示提取进度

```

#####  commit: c9212337d14d077373614241ac03318aee4de27f

在本地调试后发现， 若字幕文件或音轨文件存在， 则会有交互提示：是否删除文件， 如果不输入y 或 n， 就会一直等在哪里
``` 
运行的时候， 如果字幕文件或者音轨文件存在， 会提示：已提取音轨: F:\code\video-subtitle\test_jpn.eac3\test_jpn.eac3.rwrite? [y/N] Not overwriting - exiting 。 去掉这个提示，让他自动覆盖

```
#####  commit: ba949a1f4f9bde86348b4e3cd2ef74a69c406b01

在本地调试后发现， 若字幕文件出现多种相同语言的文件， 会相互覆盖， 最终只剩一个语言的字幕文件
``` 
使用potplayer 查看测试的mkv文件， 发现字幕有chinese simpfied 和 chinese tranditional 两个中文字幕。还有3个英文字幕， 但是导出之后发现只有一个英文字幕和一个中文字幕。 修改代码，修复这个问题。
执行程序后的信息： python.exe .\app.py --input=test.mkv --timeout=3
文件中存在的音轨:
- 语言: jpn, 编解码器: eac3
- 语言: eng, 编解码器: eac3

文件中存在的字幕:
- 语言: eng, 编解码器: subrip
- 语言: eng, 编解码器: subrip
- 语言: eng, 编解码器: subrip
- 语言: jpn, 编解码器: subrip
- 语言: ara, 编解码器: subrip
- 语言: cze, 编解码器: subrip
- 语言: dan, 编解码器: subrip
- 语言: ger, 编解码器: subrip
- 语言: gre, 编解码器: subrip
- 语言: spa, 编解码器: subrip
- 语言: spa, 编解码器: subrip
- 语言: spa, 编解码器: subrip
- 语言: fin, 编解码器: subrip
- 语言: fil, 编解码器: subrip
- 语言: fre, 编解码器: subrip
- 语言: fre, 编解码器: subrip
- 语言: heb, 编解码器: subrip
- 语言: hin, 编解码器: subrip
- 语言: hrv, 编解码器: subrip
- 语言: hun, 编解码器: subrip
- 语言: ind, 编解码器: subrip
- 语言: ind, 编解码器: subrip
- 语言: ita, 编解码器: subrip
- 语言: ita, 编解码器: subrip
- 语言: kor, 编解码器: subrip
- 语言: may, 编解码器: subrip
- 语言: nob, 编解码器: subrip
- 语言: dut, 编解码器: subrip
- 语言: pol, 编解码器: subrip
- 语言: por, 编解码器: subrip
- 语言: por, 编解码器: subrip
- 语言: rum, 编解码器: subrip
- 语言: swe, 编解码器: subrip
- 语言: tha, 编解码器: subrip
- 语言: tur, 编解码器: subrip
- 语言: ukr, 编解码器: subrip
- 语言: vie, 编解码器: subrip
- 语言: chi, 编解码器: subrip
- 语言: chi, 编解码器: subrip

```

``` 
能不用数字， 使用类似 eng   eng_sdh   eng_double  之类和potplay播放器上显示的字幕名类似的名字么
```

#####  commit:c257dbf05ff735c8cb15785fa479a6218915ea5b

``` 
给刚才的文件增加功能：
启动的时候增加参数 : 
 --subtitle={字幕名字} --audio={音轨名字} ， 若是字幕/音轨名字写错了则列出 音轨列表和字幕列表后退出程序。 若正确输入了两个参数则提取出对应参数，  若是缺少这两个参数则提取出所有音轨和字幕文件
```

#####  commit:6b10ce575f721b462382536b63f6b3623cd588dd


调用fast-whisper  的逻辑没有ai能正确写出代码，故相关代码我手写了

开启新会话后提问：

``` 
我用whisper 将一段语言转换为文字， 并且whisper 判定了这个文字的语言， 我如何把whisper 判定的语言id 正确的传给nllb， 帮我写出我完整代码
```


将pytorch调用nllb 的逻辑换成利用ctranslator2 调用nllb 的代码AI写不出来， 故相关代码我看着官方文档手写了

##### commit:33be1fa476b556561a6690eafe298f5e0a5a4bb9

启动命令：python .\app.py --input=test.mkv --subtitle=jpn_SDH --audio=jpn.eac3         


``` 
整理代码，将单个文件按功能拆分，方便二次开发
```
##### commit:25dc0f38ad139995cd73e3c51dbbcc0d1899f436
``` 
将audio_subtitle_transcriber.py 按功能拆成两个文件
```

##### commit:378034e928b4e89e14acf2673ac757b12362f4d5


``` 
 ct2-transformers-converter --model  "F:\\ai\\models\\Systran\\faster-distil-whisper-large-v3" --output_dir models/ctranslate2/Whisper/faster-whisper/distil-large-v3

```


使用 Qwen1.5-110B 进行推理：
设置 system 的提示词为
``` 
You are a helpful coder assistant.allways  say chinese
```
将整个文件夹的代码全部传到qwen模型后输入提示词
``` 
 帮我修改代码， 实现以下功能：

   1. 可以仅做从音频转字幕
   2. 可以仅做字幕翻译

```
多次测试，将报错信息反馈给模型，修改代码完毕


使用claude3
``` 
修改这个python文件，引入pysubs2， 让translate_subtitle能够输入不同参数， 分别生成双语的srt文件和ass文件。 生成ass文件的时候上面一行字幕默认大小，下面一行字幕是三分之一默认大小。让 load_srt_to_dict 可以解析srt文件和ass文件
以下是源码：
#粘贴subtitle_translator.py的源码
```
