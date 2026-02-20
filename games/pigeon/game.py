# games/pigeon/game.py
import pygame
import math
import random
import os
import settings
from core.base_game import BaseGame
from core.data_manager import DataManager
from core.path_utils import resource_path
from settings import COLORS, DIFFICULTY_LEVELS, PIGEON_CONFIG

class PigeonGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        # 加载音效
        self.snd_peck = self._load_snd(PIGEON_CONFIG['sound_peck'])
        self.snd_eat = self._load_snd(PIGEON_CONFIG['sound_eat'])
        self.snd_bad = self._load_snd(PIGEON_CONFIG['sound_bad'])

        # 加载图片
        self.img_food = self._load_img(PIGEON_CONFIG['food_img'], (50, 50))
        self.img_bomb = self._load_img(PIGEON_CONFIG.get('bomb_img', 'pigeon_bomb.png'), (50, 50))
        self.img_head = self._load_img(PIGEON_CONFIG.get('head_img', 'pigeon_head.png'), (200, 160))
        self.img_body = self._load_img(PIGEON_CONFIG.get('bird_img', 'pigeon_bird.png'), (200, 200))

        # 字体
        self.font = pygame.font.SysFont("simhei", 24, bold=True)
        self.font_big = pygame.font.SysFont("simhei", 60, bold=True)
        
        # 圆盘与鸟的属性
        self.wheel_center = (settings.SCREEN_WIDTH // 2, 300)
        self.wheel_radius = PIGEON_CONFIG['wheel_radius']
        self.bird_x = settings.SCREEN_WIDTH // 2
        self.bird_base_y = settings.SCREEN_HEIGHT - 50
        self.head_base_y = self.bird_base_y - 240
        
        self.items = [] # 圆盘上的物品列表
        self.wheel_angle = 0
        
        # 鸟的状态: IDLE(闲置), EXTENDING(伸出), RETRACTING(缩回), STUNNED(晕眩)
        self.bird_state = 'IDLE'
        self.head_y = self.head_base_y
        self.target_y = self.wheel_center[1] + self.wheel_radius
        self.peck_speed = 2000 # 脖子伸缩像素/秒
        
        self.time = 0
        self.stun_timer = 0
        
    def _load_snd(self, name):
        try:
            path = resource_path(os.path.join('assets', 'sounds', name))
            if os.path.exists(path): return pygame.mixer.Sound(path)
        except: pass
        return None
    
    def _load_img(self, name, size):
        try:
            path = resource_path(os.path.join('assets', 'images', name))
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(raw, size)
        except Exception as e:
            print(f"[Pigeon] 无法加载图片 {name}: {e}")
        return None

    def on_enter(self):
        print(f"进入疯狂鸽子，难度: {self.app.difficulty}")
        diff_cfg = DIFFICULTY_LEVELS[self.app.difficulty]
        self.set_bg_speed(diff_cfg.get('bg_speed', 30))
        
        self.bird_state = 'IDLE'
        self.head_y = self.head_base_y
        self.stun_timer = 0
        self.time = 0
        self._generate_wheel()

    def _generate_wheel(self):
        """生成一轮新的食物和炸弹"""
        self.items.clear()
        cfg = DIFFICULTY_LEVELS[self.app.difficulty]['pigeon']
        slots = cfg['slots']
        
        for i in range(slots):
            angle = i * (360 / slots)
            # 决定是食物还是炸弹
            kind = 'BOMB' if random.random() < cfg['bomb_chance'] else 'FOOD'
            self.items.append({'angle': angle, 'kind': kind, 'active': True})

    def update(self, dt):
        super().update(dt)
        self.time += dt
        
        cfg = DIFFICULTY_LEVELS[self.app.difficulty]['pigeon']
        
        # 1. 圆盘旋转
        self.wheel_angle = (self.wheel_angle + cfg['speed'] * (dt / 1000.0)) % 360
        
        # 2. 处理晕眩状态
        if self.stun_timer > 0:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.bird_state = 'IDLE'
            return

        # 3. 处理脖子伸缩动画
        if self.bird_state == 'EXTENDING':
            self.head_y -= self.peck_speed * (dt / 1000.0)
            if self.head_y <= self.target_y:
                self.head_y = self.target_y
                self._check_hit() # 达到最高点，判定是否吃到东西
                self.bird_state = 'RETRACTING'
                
        elif self.bird_state == 'RETRACTING':
            self.head_y += self.peck_speed * (dt / 1000.0)
            if self.head_y >= self.head_base_y:
                self.head_y = self.head_base_y
                self.bird_state = 'IDLE'
                
        # 4. 检查是否过关 (当前圆盘食物被吃光)
        active_food = sum(1 for item in self.items if item['active'] and item['kind'] == 'FOOD')
        if active_food == 0:
            self._generate_wheel()

    def handle_input(self, event):
        super().handle_input(event)
        
        # 点击鼠标或空格键触发啄食
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if self.bird_state == 'IDLE' and self.stun_timer <= 0:
                self.bird_state = 'EXTENDING'
                if self.snd_peck: self.snd_peck.play()

    def _check_hit(self):
        """判定最高点是否碰到了物品"""
        cfg = DIFFICULTY_LEVELS[self.app.difficulty]['pigeon']
        hit_tolerance = cfg['hit_angle'] # 判定角度范围
        
        # 最正下方的绝对角度是 90 度 (假设 0 度在右侧，顺时针旋转)
        bottom_angle = 90
        
        for item in self.items:
            if not item['active']: continue
            
            # 计算物品当前的全局角度
            current_item_angle = (item['angle'] + self.wheel_angle) % 360
            
            # 计算角度差 (考虑 0 和 360 度的衔接)
            diff = min((current_item_angle - bottom_angle) % 360, (bottom_angle - current_item_angle) % 360)
            
            if diff <= hit_tolerance:
                item['active'] = False
                if item['kind'] == 'FOOD':
                    if self.snd_eat: self.snd_eat.play()
                    DataManager().add_coins(cfg['coin'])
                elif item['kind'] == 'BOMB':
                    if self.snd_bad: self.snd_bad.play()
                    DataManager().add_coins(-cfg['coin'] * 5) # 炸弹惩罚
                    self.bird_state = 'STUNNED'
                    self.stun_timer = 1500 # 晕眩 1.5 秒
                    self.head_y = self.head_base_y # 强制缩回
                break # 每次最多吃一个

    def draw_content(self, surface):
        # 1. 绘制轮盘主轴
        pygame.draw.circle(surface, COLORS['white'], self.wheel_center, self.wheel_radius, 4)
        pygame.draw.circle(surface, COLORS['yellow'], self.wheel_center, 20)
        
        # 2. 绘制圆盘上的物品
        for item in self.items:
            if not item['active']: continue
            
            current_angle_rad = math.radians(item['angle'] + self.wheel_angle)
            item_x = self.wheel_center[0] + self.wheel_radius * math.cos(current_angle_rad)
            item_y = self.wheel_center[1] + self.wheel_radius * math.sin(current_angle_rad)
            
            if item['kind'] == 'FOOD':
                if self.img_food:
                    # 如果有图片，绘制食物图片
                    rect = self.img_food.get_rect(center=(int(item_x), int(item_y)))
                    surface.blit(self.img_food, rect)
                else:
                    # 保底：绿色圆
                    pygame.draw.circle(surface, COLORS['green'], (int(item_x), int(item_y)), 25)
                    pygame.draw.circle(surface, COLORS['white'], (int(item_x), int(item_y)), 25, 2)
            else: # BOMB
                if self.img_bomb:
                    # 如果有图片，绘制炸弹图片
                    rect = self.img_bomb.get_rect(center=(int(item_x), int(item_y)))
                    surface.blit(self.img_bomb, rect)
                else:
                    # 保底：黑色方块
                    rect = pygame.Rect(0, 0, 40, 40)
                    rect.center = (int(item_x), int(item_y))
                    pygame.draw.rect(surface, (50, 50, 50), rect)
                    pygame.draw.rect(surface, COLORS['red'], rect, 2)

        # 3. 绘制鸟的脖子 (无论有没有图片，脖子都用伸缩的矩形画，效果最好)
        # neck_width = 20 if self.img_head else 30
        # neck_rect = pygame.Rect(0, 0, neck_width, self.bird_base_y - self.head_y + 20)
        # neck_rect.midbottom = (self.bird_x, self.bird_base_y)
        # pygame.draw.rect(surface, (200, 200, 200), neck_rect)

        # 4. 绘制鸟头
        if self.img_head:
            head_rect = self.img_head.get_rect(center=(self.bird_x, int(self.head_y)))
            surface.blit(self.img_head, head_rect)
            # 如果晕眩，在头上叠一个红色半透明遮罩警示
            if self.stun_timer > 0:
                stun_mask = pygame.Surface(self.img_head.get_size(), pygame.SRCALPHA)
                stun_mask.fill((255, 0, 0, 100)) # 半透明红
                surface.blit(stun_mask, head_rect.topleft)
        else:
            # 保底：圆头和尖嘴
            head_radius = 40
            pygame.draw.circle(surface, (250, 250, 250), (self.bird_x, int(self.head_y)), head_radius)
            pygame.draw.polygon(surface, COLORS['yellow'], [
                (self.bird_x - 10, self.head_y - head_radius),
                (self.bird_x + 10, self.head_y - head_radius),
                (self.bird_x, self.head_y - head_radius - 30)
            ])
            eye_color = COLORS['red'] if self.stun_timer > 0 else COLORS['black']
            pygame.draw.circle(surface, eye_color, (self.bird_x, int(self.head_y) - 10), 8)

        # 5. 绘制鸟的身体 (固定在底部)
        if self.img_body:
            body_rect = self.img_body.get_rect(midbottom=(self.bird_x, self.bird_base_y + 40))
            surface.blit(self.img_body, body_rect)
        else:
            # 保底：半个椭圆作为身体
            body_rect = pygame.Rect(0, 0, 100, 80)
            body_rect.midtop = (self.bird_x, self.bird_base_y - 20)
            pygame.draw.ellipse(surface, (220, 220, 220), body_rect)

        # 6. UI 信息
        s = pygame.Surface((settings.SCREEN_WIDTH, 40))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        surface.blit(s, (0,0))
        
        seconds = int(self.time / 1000)
        time_str = f"时间: {seconds//60:02}:{seconds%60:02}"
        coin_str = f"金币: {DataManager().get_coins():.1f}"
        
        txt_time = self.font.render(time_str, True, COLORS['white'])
        txt_coins = self.font.render(coin_str, True, COLORS['yellow'])
        surface.blit(txt_coins, (20, 10))
        surface.blit(txt_time, (settings.SCREEN_WIDTH // 2 - txt_time.get_width() // 2, 10))
        
        if self.stun_timer > 0:
            txt_stun = self.font_big.render("晕眩中!", True, COLORS['red'])
            surface.blit(txt_stun, txt_stun.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2)))