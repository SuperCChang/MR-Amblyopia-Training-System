import pygame
import sys
from core.base_game import BaseGame
from core.ui import Button, InputBox
from core.data_manager import DataManager
import settings
from settings import COLORS

class LoginScene(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        # 1. 确保云端连接
        self.dm = DataManager()
        if not self.dm.is_connected:
            self.dm.connect()
            
        # 2. 字体设置
        # 标题字号大一点，输入框和按钮适中
        self.font = pygame.font.SysFont("simhei", 30)
        self.font_big = pygame.font.SysFont("simhei", 70, bold=True)
        
        # 3. 布局计算 (核心修改：拉大间距)
        # 获取屏幕中心点
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        
        # 定义组件尺寸
        input_w, input_h = 360, 60  # 输入框宽一点，高一点
        btn_w, btn_h = 160, 60      # 按钮尺寸
        
        # 定义垂直间距 (Gap)
        gap = 80 
        
        # --- 组件位置 ---
        # 标题在最上面 (中心点向上偏 250像素)
        self.title_y = cy - 250
        
        # 用户名输入框 (中心点向上偏 80像素)
        self.input_user = InputBox(cx - input_w//2, cy - 100, input_w, input_h, self.font, placeholder="用户名")
        
        # 密码输入框 (中心点，稍微向下一点)
        self.input_pass = InputBox(cx - input_w//2, cy - 100 + gap, input_w, input_h, self.font, is_password=True, placeholder="密码")
        
        # 登录和注册按钮 (在密码框下面)
        btn_y = cy - 100 + gap * 2 + 10
        self.btn_login = Button(cx - btn_w - 20, btn_y, btn_w, btn_h, "登录", self.font, bg_color=COLORS['green'])
        self.btn_reg = Button(cx + 20, btn_y, btn_w, btn_h, "注册", self.font, bg_color=COLORS['blue'])
        
        # 【新增】退出按钮 (在最下方)
        self.btn_exit = Button(cx - btn_w//2, btn_y + gap, btn_w, btn_h, "退出", self.font, bg_color=COLORS['red'])
        
        self.status_msg = "请登录或注册账号"
        self.msg_color = COLORS['white']

    def handle_input(self, event):
        # 1. 处理输入框事件
        res1 = self.input_user.handle_event(event)
        res2 = self.input_pass.handle_event(event)
        
        # 密码框回车 -> 登录
        if res2 == "submit":
            self.do_login()

        # 2. 处理按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_login.is_clicked(event):
                self.do_login()
            elif self.btn_reg.is_clicked(event):
                self.do_register()
            elif self.btn_exit.is_clicked(event): # 【新增】退出逻辑
                self.app.is_running = False

    def do_login(self):
        user = self.input_user.text
        pwd = self.input_pass.text
        
        if not user or not pwd:
            self.status_msg = "输入不能为空！"
            self.msg_color = COLORS['red']
            return

        self.status_msg = "正在连接云端..."
        # 强制刷新一帧以显示状态 (简易做法)
        pygame.display.get_surface().fill(COLORS['menu_bg']) # 临时刷个背景防止残影
        self.draw(pygame.display.get_surface())
        pygame.display.flip()
        
        # 调用数据管理器
        res = self.dm.login(user, pwd)
        
        if res == "SUCCESS":
            # 登录成功，切到主菜单
            self.app.change_scene('menu')
        else:
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
        pygame.display.get_surface().fill(COLORS['menu_bg'])
        self.draw(pygame.display.get_surface())
        pygame.display.flip()

        res = self.dm.register(user, pwd)
        
        if res == "SUCCESS":
            self.status_msg = "注册成功！请点击登录"
            self.msg_color = COLORS['green']
        else:
            self.status_msg = f"注册失败: {res}"
            self.msg_color = COLORS['red']

    def update(self, dt):
        pass

    def draw(self, surface):
        # 【修改】使用与主菜单一致的纯色背景
        surface.fill(COLORS['menu_bg'])
        
        # 1. 绘制半透明装饰框 (可选，增加层次感)
        # 在中心画一个稍微亮一点的深色矩形作为"面板"
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        panel_rect = pygame.Rect(0, 0, 500, 600)
        panel_rect.center = (cx, cy)
        pygame.draw.rect(surface, (50, 55, 65), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (100, 100, 100), panel_rect, 2, border_radius=20) # 描边
        
        # 2. 绘制标题
        title = self.font_big.render("MR 弱视训练系统", True, COLORS['white'])
        title_rect = title.get_rect(center=(cx, self.title_y))
        surface.blit(title, title_rect)
        
        # 3. 绘制组件
        self.input_user.draw(surface)
        self.input_pass.draw(surface)
        self.btn_login.draw(surface)
        self.btn_reg.draw(surface)
        self.btn_exit.draw(surface) # 【新增】
        
        # 4. 绘制状态信息 (在面板最下方)
        msg_surf = self.font.render(self.status_msg, True, self.msg_color)
        msg_rect = msg_surf.get_rect(center=(cx, cy + 220))
        surface.blit(msg_surf, msg_rect)