import unittest
import sys
from unittest.mock import patch

# 添加主目录到sys.path中，以确保可以导入app.py
sys.path.append('../')

from app import check_file_exists  # 现在这样导入check_file_exists函数

class TestCheckFileExists(unittest.TestCase):

    @patch('app.os.path')  # 注意更正mock的路径为'app.os.path'
    def test_file_exists(self, mock_os_path):
        # 模拟os.path.exists的返回值为True，表示文件存在
        mock_os_path.exists.return_value = True
        self.assertTrue(check_file_exists("/fake/file/path"))

    @patch('app.os.path')  # 注意更正mock的路径为'app.os.path'
    def test_file_does_not_exist(self, mock_os_path):
        # 模拟os.path.exists的返回值为False，表示文件不存在
        mock_os_path.exists.return_value = False
        self.assertFalse(check_file_exists("/fake/file/not/found"))

if __name__ == '__main__':
    unittest.main()