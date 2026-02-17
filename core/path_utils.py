# core/path_utils.py
import sys
import os

def resource_path(relative_path):
    """获取资源的绝对路径，适配 PyInstaller 打包后的路径"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包环境，就使用当前工作目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)