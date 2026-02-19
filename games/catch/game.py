# games/catch/game.py
import pygame
import random
import math
import os
import settings
from core.base_game import BaseGame
from core.data_manager import DataManager
from core.path_utils import resource_path
from settings import COLORS, DIFFICULTY_LEVELS, CATCH_CONFIG

class Thief:
    def __init__(self, game_app, difficulty_settings):
        self.app = game_app
        self.settings = difficulty_settings
        
        self.max_hp = self.settings['hp']
        self.current_hp = self.max_hp
        self.base_size = self.settings['base_size']
        self.min_size = self.settings['min_size']
        self.speed = self.settings['speed']
        
        self.raw_image = None
        self._load_random_image()
        
        self.x = random.randint(100, settings.SCREEN_WIDTH - 100)
        self.y = random.randint(100, settings.SCREEN_HEIGHT - 100)
        self.target_x = self.x
        self.target_y = self.y
        self.move_timer = 0
        
        self.alpha = 255
        self.alpha_direction = -1
        self.blink_speed = CATCH_CONFIG['blink_speed']
        
        self.rect = pygame.Rect(0, 0, self.base_size, self.base_size)
        self.is_dead = False
        self._update_rect_size()

    def _load_random_image(self):
        img_name = random.choice(CATCH_CONFIG['images'])
        try:
            path = resource_path(os.path.join('assets', 'images', img_name))
            if os.path.exists(path):
                self.raw_image = pygame.image.load(path).convert_alpha()
            else:
                raise FileNotFoundError
        except:
            self.raw_image = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(self.raw_image, (255, 0, 0), (100, 100), 100)
            pygame.draw.rect(self.raw_image, (0,0,0), (50, 60, 100, 30))

    def _update_rect_size(self):
        ratio = self.current_hp / self.max_hp
        size = self.min_size + ratio * (self.base_size - self.min_size)
        size = int(size)
        
        center = (self.x, self.y)
        self.rect.size = (size, size)
        self.rect.center = center
        
        self.display_image = pygame.transform.smoothscale(self.raw_image, (size, size))

    def update(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < 10:
            self.target_x = random.randint(50, settings.SCREEN_WIDTH - 50)
            self.target_y = random.randint(100, settings.SCREEN_HEIGHT - 100)
        else:
            move_dist = self.speed * (dt / 1000.0)
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist
            
        self.alpha += self.blink_speed * self.alpha_direction
        if self.alpha >= 255:
            self.alpha = 255
            self.alpha_direction = -1
        elif self.alpha <= 50:
            self.alpha = 50
            self.alpha_direction = 1
            
        self._update_rect_size()

    def draw(self, surface):
        self.display_image.set_alpha(self.alpha)
        surface.blit(self.display_image, self.rect)

    def on_click(self, pos):
        if self.rect.collidepoint(pos):
            self.current_hp -= 1
            coin = self.settings['coin_per_hit']
            
            is_dead = False
            if self.current_hp <= 0:
                is_dead = True
                self.is_dead = True
            
            return True, coin, is_dead
        return False, 0, False


class CatchGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.current_thief = None
        
        # 【修改】初始化计时器
        self.time = 0
        # self.score = 0  <-- 移除这个
        
        # 加载音效
        self.snd_hit = None
        self.snd_die = None
        try:
            p_hit = resource_path(os.path.join('assets', 'sounds', CATCH_CONFIG['sound_hit']))
            if os.path.exists(p_hit): self.snd_hit = pygame.mixer.Sound(p_hit)
            
            p_die = resource_path(os.path.join('assets', 'sounds', CATCH_CONFIG['sound_die']))
            if os.path.exists(p_die): self.snd_die = pygame.mixer.Sound(p_die)
        except Exception as e:
            print(f"Catch sound error: {e}")

        # 字体
        self.font = pygame.font.SysFont("simhei", 24, bold=True)

    def on_enter(self):
        """进入场景重置"""
        print(f"进入抓小偷，难度: {self.app.difficulty}")
        
        diff_cfg = DIFFICULTY_LEVELS[self.app.difficulty]
        self.set_bg_speed(diff_cfg.get('bg_speed', 50))
        
        # 【修改】重置计时器
        self.time = 0
        self._spawn_thief()

    def _spawn_thief(self):
        diff_cfg = DIFFICULTY_LEVELS[self.app.difficulty]['catch']
        self.current_thief = Thief(self.app, diff_cfg)

    def handle_input(self, event):
        super().handle_input(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.current_thief:
                hit, coins, died = self.current_thief.on_click(event.pos)
                
                if hit:
                    # 加金币 (不再维护 self.score)
                    DataManager().add_coins(coins)
                    
                    # 播放音效
                    if died:
                        if self.snd_die: self.snd_die.play()
                        self._spawn_thief()
                    else:
                        if self.snd_hit: self.snd_hit.play()

    def update(self, dt):
        super().update(dt)
        
        # 【修改】更新计时器
        self.time += dt
        
        if self.current_thief:
            self.current_thief.update(dt)

    def draw_content(self, surface):
        # 1. 绘制小偷
        if self.current_thief:
            self.current_thief.draw(surface)
            
        # 2. 绘制 UI (显示计时和金币)
        # 绘制半透明黑底
        s = pygame.Surface((settings.SCREEN_WIDTH, 40))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        surface.blit(s, (0,0))
        
        # 计算时间字符串
        seconds = int(self.time / 1000)
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"时间: {minutes:02}:{secs:02}"
        
        # 获取当前金币 (保留1位小数)
        current_coins = DataManager().get_coins()
        coin_str = f"金币: {current_coins:.1f}"
        
        # 渲染文字
        txt_time = self.font.render(time_str, True, COLORS['white'])
        txt_coins = self.font.render(coin_str, True, COLORS['yellow'])
        
        # 布局
        surface.blit(txt_coins, (20, 10))
        surface.blit(txt_time, (settings.SCREEN_WIDTH // 2 - txt_time.get_width() // 2, 10))