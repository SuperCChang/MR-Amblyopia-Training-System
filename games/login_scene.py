# games/login_scene.py
import pygame
import sys
import threading
import os
from core.base_game import BaseGame
from core.ui import Button, InputBox, Checkbox # 导入 Checkbox
from core.data_manager import DataManager
import settings
from settings import COLORS
from core.path_utils import resource_path

class LoginScene(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        self.dm = DataManager()
        
        print("LoginScene: 正在后台连接数据库...")
        threading.Thread(target=self._async_connect, daemon=True).start()
            
        self.font = pygame.font.SysFont("simhei", 30)
        self.font_big = pygame.font.SysFont("simhei", 70, bold=True)
        
        # 加载背景 (如果有)
        self.bg_image = None
        self._load_bg()

        # --- 布局 ---
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        
        input_w, input_h = 360, 60
        btn_w, btn_h = 160, 60
        gap = 80 
        
        self.title_y = cy - 250
        
        self.input_user = InputBox(cx - input_w//2, cy - 100, input_w, input_h, self.font, placeholder="用户名")
        self.input_pass = InputBox(cx - input_w//2, cy - 100 + gap, input_w, input_h, self.font, is_password=True, placeholder="密码")
        
        # 【新增】显示密码复选框 (放在密码框下面)
        self.chk_show_pass = Checkbox(cx - input_w//2, cy - 100 + gap + input_h + 10, 24, "显示密码", self.font, checked=False)

        btn_y = cy - 100 + gap * 2 + 30
        self.btn_login = Button(cx - btn_w//2, btn_y, btn_w, btn_h, "登录", self.font, bg_color=COLORS['green'])
        # self.btn_reg = Button(cx + 20, btn_y, btn_w, btn_h, "注册", self.font, bg_color=COLORS['blue'])
        self.btn_exit = Button(cx - btn_w//2, btn_y + gap, btn_w, btn_h, "退出", self.font, bg_color=COLORS['red'])
        
        self.status_msg = "请登录账号"
        self.msg_color = COLORS['white']

    def _load_bg(self):
        try:
            path = resource_path(os.path.join('assets', 'images', 'menu_bg.png'))
            if os.path.exists(path):
                raw = pygame.image.load(path).convert()
                self.bg_image = pygame.transform.scale(raw, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except: pass

    def _async_connect(self):
        try:
            if not self.dm.is_connected:
                self.dm.connect()
                if self.dm.is_connected:
                    self.status_msg = "云端连接成功"
        except: pass

    def handle_input(self, event):
        # 1. 鼠标悬停
        if event.type == pygame.MOUSEMOTION:
            self.btn_login.check_hover(event.pos)
            # self.btn_reg.check_hover(event.pos)
            self.btn_exit.check_hover(event.pos)

        # 2. 复选框逻辑
        if self.chk_show_pass.handle_event(event):
            # 如果点击了复选框，切换密码框显示模式
            # checked = True -> is_password = False (显示明文)
            self.input_pass.is_password = not self.chk_show_pass.checked

        # 3. 输入框
        self.input_user.handle_event(event)
        res2 = self.input_pass.handle_event(event)
        if res2 == "submit": self.do_login()

        # 4. 按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_login.rect.collidepoint(event.pos): self.do_login()
            # elif self.btn_reg.rect.collidepoint(event.pos): self.do_register()
            elif self.btn_exit.rect.collidepoint(event.pos): self.app.is_running = False

    def do_login(self):
        user = self.input_user.text
        pwd = self.input_pass.text
        if not user or not pwd:
            self.status_msg = "输入不能为空！"
            self.msg_color = COLORS['red']
            return
        
        self.status_msg = "正在验证..."
        self._force_draw()
        if not self.dm.is_connected: self.dm.connect()
        res = self.dm.login(user, pwd)
        
        if res == "SUCCESS":
            print("LoginScene: 登录成功，跳转菜单")
            self.app.change_scene('menu')
        else:
            self.status_msg = f"登录失败: {res}"
            self.msg_color = COLORS['red']

    def do_register(self):
        user = self.input_user.text
        pwd = self.input_pass.text
        if len(user) < 3:
            self.status_msg = "用户名太短"
            self.msg_color = COLORS['red']
            return
        self.status_msg = "正在注册..."
        self._force_draw()
        if not self.dm.is_connected: self.dm.connect()
        res = self.dm.register(user, pwd)
        if res == "SUCCESS":
            self.status_msg = "注册成功！请登录"
            self.msg_color = COLORS['green']
        else:
            self.status_msg = f"注册失败: {res}"
            self.msg_color = COLORS['red']

    def _force_draw(self):
        self.draw(pygame.display.get_surface())
        pygame.display.flip()

    def _draw_text_with_outline(self, surface, text, font, center_pos, color, outline_color=(0,0,0)):
        """【辅助函数】绘制带描边的居中文字"""
        # 1. 绘制描边 (8个方向偏移)
        outline_surf = font.render(text, True, outline_color)
        outline_rect = outline_surf.get_rect()
        cx, cy = center_pos
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        
        for dx, dy in offsets:
            outline_rect.center = (cx + dx, cy + dy)
            surface.blit(outline_surf, outline_rect)
            
        # 2. 绘制本体
        txt_surf = font.render(text, True, color)
        txt_rect = txt_surf.get_rect(center=center_pos)
        surface.blit(txt_surf, txt_rect)

    def update(self, dt): pass

    def draw(self, surface):
        # 背景
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(COLORS['menu_bg'])

        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        
        # 标题 (使用描边函数)
        self._draw_text_with_outline(surface, "弱视训练系统", self.font_big, (cx, self.title_y), COLORS['white'])
        
        # 控件
        self.input_user.draw(surface)
        self.input_pass.draw(surface)
        self.chk_show_pass.draw(surface) # 绘制复选框
        self.btn_login.draw(surface)
        # self.btn_reg.draw(surface)
        self.btn_exit.draw(surface)
        
        # 状态文字 (使用描边函数)
        self._draw_text_with_outline(surface, self.status_msg, self.font, (cx, cy + 300), self.msg_color)