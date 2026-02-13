# games/main_menu.py
import pygame
import settings # 注意：这里我们要直接导入模块，以便访问动态更新后的宽高
from core.base_game import BaseGame
from core.ui import Button
from settings import COLORS, DIFFICULTY_LEVELS

class MainMenu(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.font_title = pygame.font.SysFont("arial", 80, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 40)
        
        # 菜单状态: "SELECT_GAME" 或 "SELECT_DIFFICULTY"
        self.state = "SELECT_GAME" 
        self.selected_game = None # 暂存用户选了哪个游戏
        
        # 初始化按钮 (位置稍后在 update_layout 里设置)
        self.buttons = {}
        self.update_layout()

    def update_layout(self):
        """根据屏幕大小重新计算按钮位置"""
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        w, h = 300, 80
        gap = 100

        # --- 游戏选择界面的按钮 ---
        self.btns_game = [
            Button(cx - w//2, cy - gap, w, h, "Play Snake", self.font_btn, bg_color=COLORS['green']),
            Button(cx - w//2, cy + 20, w, h, "Exit", self.font_btn, bg_color=COLORS['red'])
        ]

        # --- 难度选择界面的按钮 ---
        self.btns_diff = [
            Button(cx - w//2, cy - gap, w, h, "EASY", self.font_btn, bg_color=COLORS['green']),
            Button(cx - w//2, cy, w, h, "MEDIUM", self.font_btn, bg_color=COLORS['yellow']),
            Button(cx - w//2, cy + gap, w, h, "HARD", self.font_btn, bg_color=COLORS['red']),
        ]

    def handle_input(self, event):
        # 菜单里不需要通用的 Tab 切背景逻辑，所以不调 super
        
        if event.type == pygame.MOUSEMOTION:
            btns = self.btns_game if self.state == "SELECT_GAME" else self.btns_diff
            for btn in btns:
                btn.check_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "SELECT_GAME":
                if self.btns_game[0].is_clicked(event): # Snake
                    self.selected_game = 'snake'
                    self.state = "SELECT_DIFFICULTY"
                elif self.btns_game[1].is_clicked(event): # Exit
                    self.app.is_running = False
            
            elif self.state == "SELECT_DIFFICULTY":
                # 点击难度后，设置 app.difficulty，并启动游戏
                if self.btns_diff[0].is_clicked(event): self.start_game('EASY')
                elif self.btns_diff[1].is_clicked(event): self.start_game('MEDIUM')
                elif self.btns_diff[2].is_clicked(event): self.start_game('HARD')
        
        # 允许按 ESC 返回上一级
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state == "SELECT_DIFFICULTY":
                self.state = "SELECT_GAME"

    def start_game(self, diff_key):
        """设置难度并跳转"""
        self.app.difficulty = diff_key # 这里存的是字符串 'EASY', 'MEDIUM' 等
        self.app.change_scene(self.selected_game)
        self.state = "SELECT_GAME" # 重置状态以便下次回来

    def update(self, dt):
        # 菜单不需要更新逻辑，但如果按钮位置不对(比如刚启动)，可以刷新一下
        # 这里为了简单，每次绘制前确保 layout 是对的
        pass

    def draw(self, surface):
        """【覆盖父类】完全独立的绘制逻辑"""
        # 1. 绘制独立背景
        surface.fill(COLORS['menu_bg'])
        
        # 2. 绘制标题
        title_text = "GAME STATION" if self.state == "SELECT_GAME" else "SELECT DIFFICULTY"
        title_surf = self.font_title.render(title_text, True, COLORS['white'])
        title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 100))
        surface.blit(title_surf, title_rect)

        # 3. 绘制当前状态的按钮
        btns = self.btns_game if self.state == "SELECT_GAME" else self.btns_diff
        for btn in btns:
            btn.draw(surface)