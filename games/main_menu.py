# games/main_menu.py
import pygame, os
from core.base_game import BaseGame
from core.ui import Button
import settings
from settings import COLORS
from core.data_manager import DataManager
from core.path_utils import resource_path

class MainMenu(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        self.font_title = pygame.font.SysFont("simhei", 60, bold=True)
        self.font_btn = pygame.font.SysFont("simhei", 30)
        
        self.menu_state = 'ROOT'
        self.init_buttons()
        
        # 【新增】加载背景图片
        self.bg_image = None
        self._load_bg()
    
    def _load_bg(self):
        try:
            path = resource_path(os.path.join('assets', 'images', 'menu_bg.png'))
            if os.path.exists(path):
                raw = pygame.image.load(path).convert()
                # 缩放到屏幕大小
                self.bg_image = pygame.transform.scale(raw, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
                print("Background image loaded.")
        except Exception as e:
            print(f"BG Load Error: {e}")

    def init_buttons(self):
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        w, h = 240, 60
        gap = 80
        
        self.title_y = cy - 200
        
        # --- 状态 1: 主菜单按钮 ---
        # 包含：贪吃蛇入口、宠物入口、退出
        self.btns_root = [
            Button(cx - w//2, cy - gap, w, h, "贪吃蛇训练", self.font_btn, bg_color=COLORS['blue']),
            Button(cx - w//2, cy + 10, w, h, "宠物乐园", self.font_btn, bg_color=COLORS['yellow']),
            Button(cx - w//2, cy + 120, w, h, "退出系统", self.font_btn, bg_color=COLORS['red'])
        ]
        
        # --- 状态 2: 贪吃蛇难度选择按钮 ---
        # 包含：简单、中等、困难、返回
        self.btns_diff = [
            Button(cx - w//2, cy - gap - 40, w, h, "简单模式", self.font_btn, bg_color=COLORS['green']),
            Button(cx - w//2, cy + 10 - 40, w, h, "中等模式", self.font_btn, bg_color=COLORS['yellow']),
            Button(cx - w//2, cy + 120 - 40, w, h, "困难模式", self.font_btn, bg_color=COLORS['red']),
            Button(cx - w//2, cy + 200, w, h, "返回上一级", self.font_btn, bg_color=COLORS['grey'])
        ]

    def handle_input(self, event):
        # 根据当前状态，决定检查哪组按钮
        current_btns = self.btns_root if self.menu_state == 'ROOT' else self.btns_diff
        
        # 1. 鼠标悬停处理
        if event.type == pygame.MOUSEMOTION:
            for btn in current_btns:
                btn.check_hover(event.pos)
                
        # 2. 鼠标点击处理
        if event.type == pygame.MOUSEBUTTONDOWN:
            # === 主菜单逻辑 ===
            if self.menu_state == 'ROOT':
                if self.btns_root[0].is_clicked(event):   # 贪吃蛇训练
                    print("选择贪吃蛇，进入难度选择")
                    self.menu_state = 'SNAKE_DIFF' # 切换状态
                    # 可以在这里做个防误触，清空一下事件
                    pygame.event.clear()
                    
                elif self.btns_root[1].is_clicked(event): # 宠物乐园
                    self.app.change_scene('pet')
                    
                elif self.btns_root[2].is_clicked(event): # 退出
                    self.app.is_running = False

            # === 难度选择逻辑 ===
            elif self.menu_state == 'SNAKE_DIFF':
                if self.btns_diff[0].is_clicked(event):   # 简单
                    self._start_snake('EASY')
                elif self.btns_diff[1].is_clicked(event): # 中等
                    self._start_snake('MEDIUM')
                elif self.btns_diff[2].is_clicked(event): # 困难
                    self._start_snake('HARD')
                elif self.btns_diff[3].is_clicked(event): # 返回
                    self.menu_state = 'ROOT'

    def _start_snake(self, difficulty):
        """设置难度并开始游戏"""
        self.app.difficulty = difficulty
        print(f"Difficulty set to {difficulty}, starting game...")
        self.app.change_scene('snake')
        # 重置菜单状态，这样下次回来还是主页
        self.menu_state = 'ROOT'

    def update(self, dt):
        super().update(dt) # 动态背景

    def draw(self, surface):
        # 1. 【修改】绘制背景
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            # 如果没有图片，用原来的深色背景
            surface.fill(COLORS['menu_bg'])
            super().draw(surface) # 或者是动态背景

        # 为了让文字在花哨的背景上也能看清，我们可以加一个全屏的半透明黑色遮罩
        # 或者只在按钮区域加面板。这里简单点，加个轻微的暗角。
        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(50) # 透明度
        mask.fill((0,0,0))
        surface.blit(mask, (0,0))

        cx = settings.SCREEN_WIDTH // 2
        
        # 2. 绘制顶部信息栏 (增加一个黑底条，防止看不清)
        top_bar = pygame.Surface((settings.SCREEN_WIDTH, 60))
        top_bar.set_alpha(150)
        top_bar.fill((0,0,0))
        surface.blit(top_bar, (0,0))
        
        coins = DataManager().get_coins()
        coin_surf = self.font_btn.render(f"金币: {coins}", True, COLORS['yellow'])
        surface.blit(coin_surf, (settings.SCREEN_WIDTH - 200, 15))

        # 3. 绘制内容
        if self.menu_state == 'ROOT':
            # 给标题加个阴影
            title_str = "训练项目选择"
            title = self.font_title.render(title_str, True, COLORS['white'])
            shadow = self.font_title.render(title_str, True, (0,0,0))
            
            rect = title.get_rect(center=(cx, self.title_y))
            surface.blit(shadow, (rect.x+2, rect.y+2)) # 阴影偏移
            surface.blit(title, rect)
            
            for btn in self.btns_root:
                btn.draw(surface)
                
        elif self.menu_state == 'SNAKE_DIFF':
            title = self.font_title.render("请选择训练难度", True, COLORS['white'])
            rect = title.get_rect(center=(cx, self.title_y))
            surface.blit(title, rect)
            
            for btn in self.btns_diff:
                btn.draw(surface)