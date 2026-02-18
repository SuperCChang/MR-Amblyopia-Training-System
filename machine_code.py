# get_id.py
import sys
import os
import uuid
import hashlib
import platform
import tkinter as tk

def get_machine_id():
    """
    获取当前机器的唯一指纹 (MAC + 节点名)
    """
    mac = uuid.getnode()
    node = platform.node()
    raw_id = f"{mac}-{node}"
    # 使用 SHA256 生成固定长度的特征码
    return hashlib.sha256(raw_id.encode()).hexdigest()

def show_id():
    # 1. 获取机器码
    hwid = get_machine_id()
    print(f"您的机器码: {hwid}")
    
    # 2. 弹窗显示，方便复制
    root = tk.Tk()
    root.title("获取机器码")
    root.geometry("500x150")
    
    tk.Label(root, text="请将下面的机器码发给管理员：", font=("Arial", 12)).pack(pady=10)
    
    entry = tk.Entry(root, font=("Arial", 10), width=60)
    entry.pack(pady=5, padx=10)
    entry.insert(0, hwid) # 自动填入
    
    # 选中所有文本，方便用户直接 Ctrl+C
    entry.select_range(0, tk.END)
    entry.focus_set()
    
    tk.Button(root, text="复制并退出", command=root.destroy).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    show_id()