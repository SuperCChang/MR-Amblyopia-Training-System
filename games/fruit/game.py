# games/fruit/game.py
import pygame
import random
import math
import os
import settings
from core.base_game import BaseGame
from core.data_manager import DataManager
from core.path_utils import resource_path
from settings import COLORS, DIFFICULTY_LEVELS, FRUIT_CONFIG

# === 1. 粒子系统 ===
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255 

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2 
        self.life -= 10 

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(self.life)
            s.fill(self.color)
            surface.blit(s, (self.x, self.y))

# === 2. 水果实体类 ===
class FruitEntity:
    def __init__(self, x, y, speed_min, speed_max, gravity, size, type_data):
        self.type_data = type_data 
        self.kind = 'NORMAL' 
        
        if type_data['id'] == 'bomb': self.kind = 'BOMB'
        elif type_data['id'] == 'dragon': self.kind = 'DRAGON'

        self.x = x
        self.y = y
        
        # 保存尺寸
        self.size = size
        # 火龙果稍微大一点，炸弹稍微小一点
        if self.kind == 'DRAGON': self.size = int(size * 1.2)
        if self.kind == 'BOMB': self.size = int(size * 0.9)
        
        # 物理属性：抛射
        screen_center = settings.SCREEN_WIDTH / 2
        if x < screen_center - 100:
            self.vx = random.uniform(2, 5)
        elif x > screen_center + 100:
            self.vx = random.uniform(-5, -2)
        else:
            self.vx = random.uniform(-3, 3)
            
        self.vy = -random.uniform(speed_min, speed_max)
        self.gravity = gravity
        
        self.angle = 0
        self.rotate_speed = random.uniform(-5, 5)
        
        self.raw_image = None
        self._load_image()
        self.rect = self.raw_image.get_rect(center=(x, y))
        
        self.is_active = True
        self.sliced = False

    def _load_image(self):
        try:
            name = self.type_data['img']
            path = resource_path(os.path.join('assets', 'images', name))
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                self.raw_image = pygame.transform.smoothscale(raw, (self.size, self.size))
            else:
                raise FileNotFoundError
        except:
            self.raw_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            color = self.type_data.get('color', (200, 200, 200))
            if self.kind == 'BOMB': color = (50, 50, 50)
            if self.kind == 'DRAGON': color = (200, 50, 200)
            pygame.draw.circle(self.raw_image, color, (self.size//2, self.size//2), self.size//2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rotate_speed
        
        self.rect.center = (self.x, self.y)
        
        if self.y > settings.SCREEN_HEIGHT + 100:
            self.is_active = False

    def draw(self, surface):
        if not self.is_active: return
        rotated = pygame.transform.rotate(self.raw_image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, new_rect)

# === 3. 游戏主逻辑 ===
class FruitGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.fruits = []
        self.particles = []
        self.mouse_trail = [] 
        
        self.time = 0
        self.spawn_timer = 0
        
        self.snd_throw = self._load_snd(FRUIT_CONFIG['sound_throw'])
        self.snd_splat = self._load_snd(FRUIT_CONFIG['sound_splat'])
        self.snd_boom = self._load_snd(FRUIT_CONFIG['sound_boom'])
        self.snd_bonus = self._load_snd(FRUIT_CONFIG['sound_bonus'])
        
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("simhei", 60, bold=True)
        
        self.game_over_timer = 0 

    def _load_snd(self, name):
        try:
            path = resource_path(os.path.join('assets', 'sounds', name))
            if os.path.exists(path): return pygame.mixer.Sound(path)
        except: pass
        return None

    def on_enter(self):
        print(f"进入切水果，难度: {self.app.difficulty}")
        diff_cfg = DIFFICULTY_LEVELS[self.app.difficulty]
        self.set_bg_speed(diff_cfg.get('bg_speed', 30))
        
        self.fruits = []
        self.particles = []
        self.mouse_trail = []
        self.time = 0
        self.game_over_timer = 0
        self.spawn_timer = 0

    def update(self, dt):
        super().update(dt) 
        
        if self.game_over_timer > 0:
            self.game_over_timer -= dt
            if self.game_over_timer <= 0:
                self.on_enter() 
            return

        self.time += dt
        self.spawn_timer += dt
        
        diff_cfg = DIFFICULTY_LEVELS[self.app.difficulty]['fruit']
        
        if self.spawn_timer > diff_cfg['spawn_interval']:
            if len(self.fruits) < diff_cfg['max_active']:
                self.spawn_timer = 0
                self._spawn_fruit(diff_cfg)
                
                if self.app.difficulty == 'HARD' and random.random() < 0.3:
                     self._spawn_fruit(diff_cfg)

        for f in self.fruits:
            f.update()
        self.fruits = [f for f in self.fruits if f.is_active]
        
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        if len(self.mouse_trail) > 0:
            self.mouse_trail.pop(0)

    def _spawn_fruit(self, diff_cfg):
        x = random.randint(150, settings.SCREEN_WIDTH - 150)
        y = settings.SCREEN_HEIGHT + 50
        
        roll = random.random()
        if roll < 0.15: # 炸弹
            f_data = {'id': 'bomb', 'img': FRUIT_CONFIG['bomb_img'], 'color': (0,0,0)}
        elif roll < 0.25: # 火龙果
            f_data = {'id': 'dragon', 'img': FRUIT_CONFIG['dragon_img'], 'color': (255,0,255)}
        else:
            f_data = random.choice(FRUIT_CONFIG['fruits'])
            
        new_fruit = FruitEntity(
            x, y, 
            diff_cfg['speed_min'], diff_cfg['speed_max'], 
            diff_cfg['gravity'], 
            diff_cfg['base_size'], 
            f_data
        )
        self.fruits.append(new_fruit)
        
        if self.snd_throw: self.snd_throw.play()

    def handle_input(self, event):
        if self.game_over_timer > 0: return

        super().handle_input(event)
        
        if event.type == pygame.MOUSEMOTION:
            self.mouse_trail.append(event.pos)
            # 【修改 1】让刀光轨迹更长一点 (从 8 改为 15)
            if len(self.mouse_trail) > 15: 
                self.mouse_trail.pop(0)
            
            self._check_slice(event.pos)

    def _check_slice(self, pos):
        for f in self.fruits:
            if not f.sliced and f.rect.collidepoint(pos):
                self._handle_slice(f)
                
                if f.kind == 'NORMAL':
                    f.sliced = True
                    f.is_active = False 
                elif f.kind == 'BOMB':
                    f.sliced = True
                    
    def _handle_slice(self, fruit):
        if fruit.kind == 'NORMAL':
            if self.snd_splat: self.snd_splat.play()
            DataManager().add_coins(0.5)
            self._spawn_particles(fruit.x, fruit.y, fruit.type_data['color'])
            
        elif fruit.kind == 'BOMB':
            if self.snd_boom: self.snd_boom.play()
            print("切到炸弹！")
            self.fruits.clear()
            self.particles.clear()
            self.game_over_timer = 2000 
            
        elif fruit.kind == 'DRAGON':
            if self.snd_bonus: self.snd_bonus.stop(); self.snd_bonus.play()
            DataManager().add_coins(0.2) 
            self._spawn_particles(fruit.x, fruit.y, (255, 0, 255), count=3)
            # fruit.vy -= 2 
            # fruit.vx += random.uniform(-1, 1)

    def _spawn_particles(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def draw_content(self, surface):
        for f in self.fruits:
            f.draw(surface)
            
        for p in self.particles:
            p.draw(surface)
            
        # 【修改 2】绘制更显眼的双层刀光
        if len(self.mouse_trail) > 1:
            # 外层：青色光晕 (更粗)
            pygame.draw.lines(surface, (0, 255, 255), False, self.mouse_trail, 10)
            # 内层：白色核心 (稍细)
            pygame.draw.lines(surface, (255, 255, 255), False, self.mouse_trail, 4)

        # UI
        s = pygame.Surface((settings.SCREEN_WIDTH, 40))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        surface.blit(s, (0,0))
        
        seconds = int(self.time / 1000)
        time_str = f"Time: {seconds//60:02}:{seconds%60:02}"
        current_coins = DataManager().get_coins()
        coin_str = f"Coins: {current_coins:.1f}"
        
        txt_time = self.font.render(time_str, True, COLORS['white'])
        txt_coins = self.font.render(coin_str, True, COLORS['yellow'])
        
        surface.blit(txt_coins, (20, 10))
        surface.blit(txt_time, (settings.SCREEN_WIDTH // 2 - txt_time.get_width() // 2, 10))
        
        # 【修改 3】移除白屏闪烁，仅保留文字提示
        if self.game_over_timer > 0:
            # 这里删除了原本的 overlay 代码，不再有全屏遮罩
            
            # 只显示文字 (红色大字)
            txt = self.font_big.render("BOOM!", True, (255, 0, 0))
            rect = txt.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2))
            surface.blit(txt, rect)