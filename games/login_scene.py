import pygame
import sys
import threading
from core.base_game import BaseGame
from core.ui import Button, InputBox
from core.data_manager import DataManager
import settings
from settings import COLORS

class LoginScene(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        self.dm = DataManager()
        
        # 【防卡死】启动后台线程连接数据库
        # 这样启动游戏时窗口会瞬间显示，不会因为连不上网而白屏
        print("LoginScene: 正在后台连接数据库...")
        threading.Thread(target=self._async_connect, daemon=True).start()
            
        self.font = pygame.font.SysFont("simhei", 30)
        self.font_big = pygame.font.SysFont("simhei", 70, bold=True)
        
        # --- 布局参数 ---
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        
        input_w, input_h = 360, 60
        btn_w, btn_h = 160, 60
        gap = 80 
        
        self.title_y = cy - 250
        
        # --- 初始化控件 ---
        self.input_user = InputBox(cx - input_w//2, cy - 100, input_w, input_h, self.font, placeholder="用户名")
        self.input_pass = InputBox(cx - input_w//2, cy - 100 + gap, input_w, input_h, self.font, is_password=True, placeholder="密码")
        
        btn_y = cy - 100 + gap * 2 + 10
        self.btn_login = Button(cx - btn_w - 20, btn_y, btn_w, btn_h, "登录", self.font, bg_color=COLORS['green'])
        self.btn_reg = Button(cx + 20, btn_y, btn_w, btn_h, "注册", self.font, bg_color=COLORS['blue'])
        self.btn_exit = Button(cx - btn_w//2, btn_y + gap, btn_w, btn_h, "退出", self.font, bg_color=COLORS['red'])
        
        self.status_msg = "请登录或注册账号"
        self.msg_color = COLORS['white']

    def _async_connect(self):
        """后台连接任务"""
        try:
            if not self.dm.is_connected:
                self.dm.connect()
                if self.dm.is_connected:
                    print("LoginScene: 后台连接成功!")
                    self.status_msg = "云端连接成功"
        except Exception as e:
            print(f"LoginScene: 连接错误 {e}")

    def handle_input(self, event):
        # 1. 处理鼠标悬停 (让按钮变色)
        if event.type == pygame.MOUSEMOTION:
            self.btn_login.check_hover(event.pos)
            self.btn_reg.check_hover(event.pos)
            self.btn_exit.check_hover(event.pos)

        # 2. 处理输入框事件
        res1 = self.input_user.handle_event(event)
        res2 = self.input_pass.handle_event(event)
        
        # 密码框回车 -> 触发登录
        if res2 == "submit":
            print("LoginScene: 检测到回车键，触发登录")
            self.do_login()

        # 3. 处理鼠标点击 (最稳健的写法)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            print(f"LoginScene: 点击坐标 {mouse_pos}") # 【调试】打印点击位置
            
            # 使用最底层的矩形碰撞检测，不依赖 UI 库的状态
            if self.btn_login.rect.collidepoint(mouse_pos):
                print(">>> 点击了【登录】按钮")
                self.do_login()
                
            elif self.btn_reg.rect.collidepoint(mouse_pos):
                print(">>> 点击了【注册】按钮")
                self.do_register()
                
            elif self.btn_exit.rect.collidepoint(mouse_pos):
                print(">>> 点击了【退出】按钮")
                self.app.is_running = False

    def do_login(self):
        user = self.input_user.text
        pwd = self.input_pass.text
        
        if not user or not pwd:
            self.status_msg = "输入不能为空！"
            self.msg_color = COLORS['red']
            return

        self.status_msg = "正在验证..."
        self._force_draw() # 强制刷新界面显示状态
        
        # 此时应该已经连上了，如果还没连上会尝试重连
        if not self.dm.is_connected:
            self.status_msg = "正在连接云端，请稍候..."
            self._force_draw()
            self.dm.connect()

        res = self.dm.login(user, pwd)
        
        if res == "SUCCESS":
            print("LoginScene: 登录成功，跳转菜单")
            self.app.change_scene('menu')
        else:
            print(f"LoginScene: 登录失败 - {res}")
            self.status_msg = f"登录失败: {res}"
            self.msg_color = COLORS['red']

    def do_register(self):
        user = self.input_user.text
        pwd = self.input_pass.text
        
        if len(user) < 3:
            self.status_msg = "用户名至少3个字符"
            self.msg_color = COLORS['red']
            return
            
        self.status_msg = "正在注册..."
        self._force_draw()

        if not self.dm.is_connected:
            self.dm.connect()

        res = self.dm.register(user, pwd)
        
        if res == "SUCCESS":
            self.status_msg = "注册成功！请点击登录"
            self.msg_color = COLORS['green']
        else:
            self.status_msg = f"注册失败: {res}"
            self.msg_color = COLORS['red']

    def _force_draw(self):
        """强制刷新一帧，让用户看到'正在连接'的字样"""
        try:
            surface = pygame.display.get_surface()
            self.draw(surface)
            pygame.display.flip()
        except:
            pass

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(COLORS['menu_bg'])
        
        # 绘制面板背景
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        panel_rect = pygame.Rect(0, 0, 500, 600)
        panel_rect.center = (cx, cy)
        
        # 阴影
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(surface, (20, 20, 20), shadow_rect, border_radius=20)
        
        # 本体
        pygame.draw.rect(surface, (50, 55, 65), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (100, 100, 100), panel_rect, 2, border_radius=20)
        
        # 标题
        title = self.font_big.render("MR 弱视训练系统", True, COLORS['white'])
        title_rect = title.get_rect(center=(cx, self.title_y))
        surface.blit(title, title_rect)
        
        # 控件
        self.input_user.draw(surface)
        self.input_pass.draw(surface)
        self.btn_login.draw(surface)
        self.btn_reg.draw(surface)
        self.btn_exit.draw(surface)
        
        # 状态文字
        msg_surf = self.font.render(self.status_msg, True, self.msg_color)
        msg_rect = msg_surf.get_rect(center=(cx, cy + 220))
        surface.blit(msg_surf, msg_rect)