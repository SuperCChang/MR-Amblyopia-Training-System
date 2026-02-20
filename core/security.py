import sys
import subprocess
import hashlib
import uuid
import re

def get_machine_id():
    """
    获取稳定的机器码 (跨平台增强版)
    优先级:
    1. Windows PowerShell (CIM/WMI) - 主板 UUID
    2. Windows 注册表 (MachineGuid) - 系统唯一 ID
    3. Windows WMIC (旧版兼容)
    4. Mac/Linux 硬件 ID
    5. Fallback: MAC 地址 (最不推荐)
    """
    machine_uuid = None
    
    try:
        if sys.platform == 'win32':
            # --- 方案 A: PowerShell (推荐，适用于 Win10/11) ---
            try:
                cmd = 'powershell -Command "Get-CimInstance -Class Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
                # creationflags=0x08000000 用于隐藏弹出的控制台窗口 (CREATE_NO_WINDOW)
                output = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode().strip()
                if output and len(output) > 10:
                    print("[Security] Got UUID via PowerShell")
                    machine_uuid = output
            except Exception:
                pass

            # --- 方案 B: 注册表 MachineGuid (极其稳定，无视硬件驱动) ---
            if not machine_uuid:
                try:
                    cmd = 'reg query HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid'
                    output = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode().strip()
                    # 输出格式通常包含: MachineGuid    REG_SZ    xxxxxxxx-xxxx...
                    # 使用正则提取 UUID 格式
                    match = re.search(r'[a-fA-F0-9-]{8,}', output)
                    if match:
                        print("[Security] Got MachineGuid via Registry")
                        machine_uuid = match.group(0)
                except Exception:
                    pass

            # --- 方案 C: WMIC (老系统兼容) ---
            if not machine_uuid:
                try:
                    cmd = "wmic csproduct get uuid"
                    output = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode().strip()
                    lines = output.split('\n')
                    if len(lines) >= 2:
                        print("[Security] Got UUID via WMIC")
                        machine_uuid = lines[1].strip()
                except Exception:
                    pass
        
        elif sys.platform == 'darwin':
            # --- Mac ---
            cmd = "system_profiler SPHardwareDataType | grep 'Hardware UUID'"
            output = subprocess.check_output(cmd, shell=True).decode()
            machine_uuid = output.split(':')[1].strip()
            
        elif sys.platform.startswith('linux'):
            # --- Linux ---
            try:
                with open('/etc/machine-id', 'r') as f:
                    machine_uuid = f.read().strip()
            except:
                cmd = "cat /var/lib/dbus/machine-id"
                machine_uuid = subprocess.check_output(cmd, shell=True).decode().strip()

    except Exception as e:
        print(f"[Security] Error getting hardware ID: {e}")
        machine_uuid = None

    # === 生成最终 ID ===
    if machine_uuid:
        # 成功获取硬件/系统级 ID
        return hashlib.md5(machine_uuid.encode()).hexdigest()
    else:
        # === 保底方案 (Fallback) ===
        print("[Security] Warning: Using MAC address fallback (Unstable).")
        mac_addr = uuid.getnode()
        return hashlib.md5(str(mac_addr).encode()).hexdigest()

if __name__ == "__main__":
    print(f"My Stable Machine ID: {get_machine_id()}")