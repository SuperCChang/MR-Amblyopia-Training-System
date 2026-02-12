# core/base_game.py
import pygame
from settings import DIFFICULTY_LEVELS
from core.bg_renderer import BackgroundRenderer

class BaseGame:
    def __init__(self, app):
        self.app = app
        self.bg_mode = 0
        self.bg_timer = 0
        self.SWITCH_INTERVAL = 5000 # 5秒切换

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # 调试用：Tab 手动切
            if event.key == pygame.K_TAB:
                self.bg_mode = (self.bg_mode + 1) % 9
                self.bg_timer = 0
            elif event.key == pygame.K_ESCAPE:
                self.app.change_scene('menu')

    def update(self):
        # 自动切换逻辑
        dt = self.app.clock.get_time()
        self.bg_timer += dt
        
        if self.bg_timer >= self.SWITCH_INTERVAL:
            self.bg_mode = (self.bg_mode + 1) % 9 # 0-8 循环
            self.bg_timer = 0
            # print(f"Background switched to: {self.bg_mode}")

    def draw(self, surface):
        # 获取当前难度参数
        current_diff = self.app.difficulty
        settings = DIFFICULTY_LEVELS[current_diff]
        
        # 提取独立的变量
        g_size = settings['grid_size']      # 用于网格背景
        s_width = settings['stripe_width']  # 用于条栅背景
        
        current_time = pygame.time.get_ticks()
        
        # 渲染背景
        BackgroundRenderer.draw(surface, self.bg_mode, current_time, g_size, s_width)
        
        # 渲染子类内容
        self.draw_content(surface)

    def draw_content(self, surface):
        pass