# video-subtitle
a video subtitle generator

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