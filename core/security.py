# core/security.py
import uuid
import hashlib
import platform

def get_machine_id():
    """
    获取当前机器的唯一指纹 (MAC + 节点名)
    """
    mac = uuid.getnode()
    node = platform.node()
    raw_id = f"{mac}-{node}"
    # 使用 SHA256 生成固定长度的特征码
    return hashlib.sha256(raw_id.encode()).hexdigest()