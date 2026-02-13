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

    def update(self, dt):
        self.bg_timer += dt
        
        if self.bg_timer >= self.SWITCH_INTERVAL:
            self.bg_mode = (self.bg_mode + 1) % 9 # 0-8 循环
            self.bg_timer = 0
            # print(f"Background switched to: {self.bg_mode}")

    def draw(self, surface):
        # 获取难度 key
        diff_key = self.app.difficulty
        # 从字典中取配置
        settings_data = DIFFICULTY_LEVELS[diff_key]
        
        bg_g_size = settings_data['bg_grid_size']
        s_width = settings_data['stripe_width']
        
        current_time = pygame.time.get_ticks()
        BackgroundRenderer.draw(surface, self.bg_mode, current_time, bg_g_size, s_width)
        
        self.draw_content(surface)

    def draw_content(self, surface):
        pass