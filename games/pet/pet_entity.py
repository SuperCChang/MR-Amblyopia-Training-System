# games/pet/pet_entity.py
import pygame
import os
import math
import settings
from core.path_utils import resource_path

class PetEntity:
    def __init__(self, pet_id, center_x, center_y, level=1):
        self.pet_id = pet_id
        self.center_x = center_x
        self.center_y = center_y
        self.level = level
        
        self.raw_image = None 
        self.image = None     
        self.rect = None
        
        # 【新增】音效相关属性
        self.sound_voice = None
        self.last_sound_time = 0 # 上次播放时间
        self.sound_cooldown = 300 # 冷却时间 (毫秒)
        
        self._load_resources() # 改名为加载资源(包含图片和声音)
        self.update_size() 
        
        self.is_bouncing = False
        self.bounce_timer = 0
        
    def _load_resources(self):
        """加载图片和音效"""
        # 1. 加载图片 (保持之前的逻辑)
        try:
            img_name = f"pet_{self.pet_id}.png"
            for p in settings.PET_SHOP_LIST:
                if p['id'] == self.pet_id:
                    img_name = p['img']
                    break
            
            img_path = resource_path(os.path.join('assets', 'images', img_name))
            
            if os.path.exists(img_path):
                self.raw_image = pygame.image.load(img_path).convert_alpha()
                self.raw_image = pygame.transform.smoothscale(self.raw_image, (200, 200))
            else:
                raise FileNotFoundError
        except:
            self.raw_image = pygame.Surface((200, 200), pygame.SRCALPHA)
            color = (255, 200, 100) if 'cat' in self.pet_id else (100, 200, 255)
            pygame.draw.circle(self.raw_image, color, (100, 100), 80)

        # 2. 【新增】加载音效
        try:
            # 根据 ID 判断是猫还是狗
            snd_file = 'meow.wav' # 默认为猫
            if 'dog' in self.pet_id:
                snd_file = 'bark.wav'
            
            snd_path = resource_path(os.path.join('assets', 'sounds', snd_file))
            if os.path.exists(snd_path):
                self.sound_voice = pygame.mixer.Sound(snd_path)
                self.sound_voice.set_volume(0.6)
        except Exception as e:
            print(f"Pet Sound Error: {e}")

    def play_voice(self):
        """【新增】播放叫声 (带冷却)"""
        if not self.sound_voice: return
        
        now = pygame.time.get_ticks()
        if now - self.last_sound_time > self.sound_cooldown:
            self.sound_voice.play()
            self.last_sound_time = now

    def set_level(self, level):
        if self.level != level:
            self.level = level
            self.update_size()

    def update_size(self):
        if not self.raw_image: return
        lvl = max(1, min(self.level, settings.PET_CONFIG['max_level']))
        min_scale = 0.6
        max_scale = 1.5
        ratio = (lvl - 1) / (settings.PET_CONFIG['max_level'] - 1)
        current_scale = min_scale + ratio * (max_scale - min_scale)
        
        base_w, base_h = self.raw_image.get_size()
        new_w = int(base_w * current_scale)
        new_h = int(base_h * current_scale)
        
        self.image = pygame.transform.smoothscale(self.raw_image, (new_w, new_h))
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))

    def handle_click(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.is_bouncing = True
            self.bounce_timer = 0
            
            # 【新增】点击时播放叫声
            self.play_voice()
            
            return True
        return False

    def update(self):
        if not self.is_bouncing:
            t = pygame.time.get_ticks() / 500
            offset = math.sin(t) * 5
            self.rect.centery = self.center_y + offset
        else:
            self.bounce_timer += 1
            if self.bounce_timer < 20:
                self.rect.centery = self.center_y - 30 + (self.bounce_timer * 2)
            else:
                self.is_bouncing = False

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)