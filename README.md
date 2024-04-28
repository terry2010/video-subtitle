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




#####  commit: 