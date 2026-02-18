# admin_tool.py
import tkinter as tk
from tkinter import messagebox, ttk
from supabase import create_client
import sys
import hashlib  # 【新增】用于密码加密

# =================配置区域=================
SUPABASE_URL = "https://ztljczelgprcymxwqywp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0bGpjemVsZ3ByY3lteHdxeXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwMDUyOTgsImV4cCI6MjA4NjU4MTI5OH0.3PdvN9-L8w4vKQqKRPNwun3VSN5L0Ef-wUbB21e5ToA"
# =========================================

class AdminTool:
    def __init__(self, root):
        self.root = root
        self.root.title("游戏后台管理工具 (全能版)")
        self.root.geometry("700x550") # 稍微加大一点高度
        
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.status_text = "数据库连接成功"
        except Exception as e:
            self.client = None
            self.status_text = f"连接失败: {e}"

        # 使用 Notebook 实现分页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 页签 1: 用户管理
        self.frame_users = tk.Frame(self.notebook)
        self.notebook.add(self.frame_users, text="用户管理")
        self._init_user_ui()
        
        # 页签 2: 白名单管理
        self.frame_whitelist = tk.Frame(self.notebook)
        self.notebook.add(self.frame_whitelist, text="设备白名单")
        self._init_whitelist_ui()
        
        # 页签 3: 注册新用户 【新增】
        self.frame_register = tk.Frame(self.notebook)
        self.notebook.add(self.frame_register, text="注册新用户")
        self._init_register_ui()

        # 底部状态
        tk.Label(self.root, text=self.status_text, fg="gray").pack(side="bottom", pady=5)
        
        # 初始加载
        self.refresh_user_list()
        self.refresh_whitelist()

    # ================= 1. 用户管理部分 =================
    def _init_user_ui(self):
        frame_top = tk.Frame(self.frame_users)
        frame_top.pack(pady=10, fill="x")
        tk.Button(frame_top, text="刷新列表", command=self.refresh_user_list).pack(side="left", padx=5)
        tk.Button(frame_top, text="删除用户", bg="red", fg="white", command=self.delete_user).pack(side="right", padx=5)

        cols = ("username", "coins")
        self.tree_users = ttk.Treeview(self.frame_users, columns=cols, show="headings")
        self.tree_users.heading("username", text="用户名")
        self.tree_users.heading("coins", text="金币")
        self.tree_users.pack(fill="both", expand=True)

    def refresh_user_list(self):
        for item in self.tree_users.get_children(): self.tree_users.delete(item)
        if not self.client: return
        try:
            res = self.client.table('users').select("*").execute()
            for user in res.data:
                self.tree_users.insert("", "end", values=(user['username'], user['coins']))
        except Exception as e: messagebox.showerror("错误", str(e))

    def delete_user(self):
        sel = self.tree_users.selection()
        if not sel: return
        user = self.tree_users.item(sel[0])['values'][0]
        if messagebox.askyesno("确认", f"删除用户 {user}?"):
            try:
                self.client.table('users').delete().eq('username', user).execute()
                self.refresh_user_list()
                messagebox.showinfo("成功", "用户已删除")
            except Exception as e:
                messagebox.showerror("错误", str(e))

    # ================= 2. 白名单管理部分 =================
    def _init_whitelist_ui(self):
        # 顶部输入栏
        frame_top = tk.Frame(self.frame_whitelist)
        frame_top.pack(pady=10, fill="x")
        
        tk.Label(frame_top, text="机器码:").pack(side="left", padx=5)
        self.entry_hwid = tk.Entry(frame_top, width=30)
        self.entry_hwid.pack(side="left", padx=5)
        
        tk.Label(frame_top, text="备注:").pack(side="left", padx=5)
        self.entry_note = tk.Entry(frame_top, width=15)
        self.entry_note.pack(side="left", padx=5)
        
        tk.Button(frame_top, text="添加设备", bg="#4CAF50", fg="white", command=self.add_whitelist).pack(side="left", padx=10)
        tk.Button(frame_top, text="删除选中", bg="red", fg="white", command=self.del_whitelist).pack(side="right", padx=5)
        tk.Button(frame_top, text="刷新", command=self.refresh_whitelist).pack(side="right", padx=5)

        # 列表
        cols = ("hwid", "note")
        self.tree_wl = ttk.Treeview(self.frame_whitelist, columns=cols, show="headings")
        self.tree_wl.heading("hwid", text="机器码 (HWID)")
        self.tree_wl.heading("note", text="备注")
        self.tree_wl.column("hwid", width=350)
        self.tree_wl.column("note", width=150)
        self.tree_wl.pack(fill="both", expand=True)

    def refresh_whitelist(self):
        for item in self.tree_wl.get_children(): self.tree_wl.delete(item)
        if not self.client: return
        try:
            res = self.client.table('device_whitelist').select("*").execute()
            for row in res.data:
                self.tree_wl.insert("", "end", values=(row['hwid'], row.get('note', '')))
        except Exception as e: messagebox.showerror("错误", str(e))

    def add_whitelist(self):
        hwid = self.entry_hwid.get().strip()
        note = self.entry_note.get().strip()
        if not hwid:
            messagebox.showwarning("提示", "机器码不能为空")
            return
        try:
            self.client.table('device_whitelist').insert({'hwid': hwid, 'note': note}).execute()
            messagebox.showinfo("成功", "设备已加入白名单")
            self.entry_hwid.delete(0, tk.END)
            self.entry_note.delete(0, tk.END)
            self.refresh_whitelist()
        except Exception as e:
            messagebox.showerror("添加失败", f"可能是机器码已存在或格式错误\n{e}")

    def del_whitelist(self):
        sel = self.tree_wl.selection()
        if not sel: return
        hwid = self.tree_wl.item(sel[0])['values'][0]
        if messagebox.askyesno("确认", f"将设备移除白名单?\n{hwid[:10]}..."):
            try:
                self.client.table('device_whitelist').delete().eq('hwid', hwid).execute()
                self.refresh_whitelist()
            except Exception as e:
                messagebox.showerror("错误", str(e))

    # ================= 3. 注册新用户部分 (新增) =================
    def _init_register_ui(self):
        # 使用 Frame 居中显示内容
        frame_center = tk.Frame(self.frame_register)
        frame_center.pack(expand=True)

        tk.Label(frame_center, text="创建新游戏账号", font=("Arial", 16, "bold")).pack(pady=20)

        # 表单区域
        form_frame = tk.Frame(frame_center)
        form_frame.pack(pady=10)

        # 用户名
        tk.Label(form_frame, text="用户名:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.reg_user = tk.Entry(form_frame, font=("Arial", 12))
        self.reg_user.grid(row=0, column=1, padx=10, pady=10)

        # 密码
        tk.Label(form_frame, text="密码:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.reg_pwd = tk.Entry(form_frame, font=("Arial", 12)) # 管理员模式下默认不隐藏密码，方便记录
        self.reg_pwd.grid(row=1, column=1, padx=10, pady=10)

        # 注册按钮
        btn = tk.Button(frame_center, text="立即开户", font=("Arial", 12), bg="#2196F3", fg="white", command=self.do_register)
        btn.pack(pady=20, ipadx=30)
        
        # 提示
        tk.Label(frame_center, text="注：注册成功后，该用户会自动出现在[用户管理]列表中", fg="gray").pack()

    def _hash_password(self, password):
        """与游戏保持一致的 SHA256 加密"""
        return hashlib.sha256(password.encode()).hexdigest()

    def do_register(self):
        username = self.reg_user.get().strip()
        password = self.reg_pwd.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "用户名和密码不能为空")
            return

        if not self.client:
            messagebox.showerror("错误", "无法连接到数据库")
            return

        # 准备数据
        new_user = {
            'username': username, 
            'password': self._hash_password(password),
            'coins': 0, 
            'pet_data': []
        }

        try:
            self.client.table('users').insert(new_user).execute()
            messagebox.showinfo("成功", f"用户 [{username}] 创建成功！")
            
            # 清空输入框
            self.reg_user.delete(0, tk.END)
            self.reg_pwd.delete(0, tk.END)
            
            # 自动刷新第一个分页的列表，方便查看
            self.refresh_user_list()
            
        except Exception as e:
            err_msg = str(e)
            if "duplicate key" in err_msg or "unique constraint" in err_msg:
                messagebox.showerror("失败", "注册失败：该用户名已存在")
            else:
                messagebox.showerror("失败", f"未知错误: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminTool(root)
    root.mainloop()