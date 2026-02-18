# games/pet/pet_entity.py
import pygame
import os
import math
import random
import settings
from core.path_utils import resource_path

class PetEntity:
    def __init__(self, pet_data, level=1):
        self.pet_data = pet_data
        self.pet_id = pet_data['id']
        self.level = level
        
        # 初始位置
        self.center_x = random.randint(100, settings.SCREEN_WIDTH - 100)
        self.center_y = random.randint(300, settings.SCREEN_HEIGHT - 100)
        
        self.raw_image = None 
        self.image = None     
        self.rect = None
        
        # 移动相关
        self.target_x = self.center_x
        self.target_y = self.center_y
        self.speed = random.uniform(0.5, 1.0) # 稍微降低一点速度，更悠闲
        self.state = 'IDLE' 
        self.state_timer = 0
        self.flip = False

        # 【修复】动画相位偏移量 (固定值)
        # 每个宠物有一个固定的随机偏移，这样它们呼吸不同步，但移动时不会抖动
        self.anim_offset = random.uniform(0, 100)

        # 选中状态
        self.is_selected = False
        
        # 音效
        self.sound_voice = None
        self.last_sound_time = 0
        self.sound_cooldown = 300 
        
        self._load_resources()
        self.update_size() 
        
        # 互动弹跳
        self.is_bouncing = False
        self.bounce_timer = 0
        
    def _load_resources(self):
        """加载图片和音效"""
        # 1. 图片
        try:
            img_name = f"pet_{self.pet_id}.png"
            for p in settings.PET_SHOP_LIST:
                if p['id'] == self.pet_id:
                    img_name = p['img']
                    break
            
            img_path = resource_path(os.path.join('assets', 'images', img_name))
            
            if os.path.exists(img_path):
                self.raw_image = pygame.image.load(img_path).convert_alpha()
                # 预先缩放到合适大小，避免太大
                self.raw_image = pygame.transform.smoothscale(self.raw_image, (200, 200))
            else:
                raise FileNotFoundError
        except:
            self.raw_image = pygame.Surface((200, 200), pygame.SRCALPHA)
            color = (255, 200, 100) if 'cat' in self.pet_id else (100, 200, 255)
            pygame.draw.circle(self.raw_image, color, (100, 100), 80)

        # 2. 音效
        try:
            snd_file = 'meow.wav'
            if 'dog' in self.pet_id: snd_file = 'bark.wav'
            
            snd_path = resource_path(os.path.join('assets', 'sounds', snd_file))
            if os.path.exists(snd_path):
                self.sound_voice = pygame.mixer.Sound(snd_path)
                self.sound_voice.set_volume(0.6)
        except: pass

    def play_voice(self):
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
        # 根据等级缩放
        lvl = max(1, min(self.level, settings.PET_CONFIG['max_level']))
        min_scale = 0.4 # 稍微调小一点，方便多只宠物共存
        max_scale = 2.0
        ratio = (lvl - 1) / (settings.PET_CONFIG['max_level'] - 1)
        current_scale = min_scale + ratio * (max_scale - min_scale)
        
        base_w, base_h = self.raw_image.get_size()
        new_w = int(base_w * current_scale)
        new_h = int(base_h * current_scale)
        
        scaled_img = pygame.transform.smoothscale(self.raw_image, (new_w, new_h))
        
        # 处理朝向翻转
        if self.flip:
            self.image = pygame.transform.flip(scaled_img, True, False)
        else:
            self.image = scaled_img
            
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))

    def handle_click(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.is_bouncing = True
            self.bounce_timer = 0
            self.play_voice()
            return True
        return False

    def update(self):
        # === 1. AI 行为状态机 ===
        self.state_timer -= 1
        
        if self.state_timer <= 0:
            # 切换状态
            if self.state == 'IDLE':
                # 发呆结束，开始移动
                self.state = 'MOVE'
                self.state_timer = random.randint(60, 200) # 移动 1-3秒
                # 随机找个新目标点 (限制在屏幕区域内)
                padding = 100
                self.target_x = random.randint(padding, settings.SCREEN_WIDTH - padding)
                self.target_y = random.randint(200, settings.SCREEN_HEIGHT - 150) # 不跑太高也不跑太低
                
                # 决定朝向
                if self.target_x < self.center_x: self.flip = True
                else: self.flip = False
                self.update_size() # 刷新翻转
                
            elif self.state == 'MOVE':
                # 移动结束，开始发呆
                self.state = 'IDLE'
                self.state_timer = random.randint(60, 180) # 发呆 1-3秒

        # === 2. 执行移动 ===
        if self.state == 'MOVE':
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < 5: # 到达目标
                self.state = 'IDLE'
                self.state_timer = random.randint(60, 180)
            else:
                move_dist = self.speed
                self.center_x += (dx / dist) * move_dist
                self.center_y += (dy / dist) * move_dist

        # === 3. 更新 Rect 和 弹跳动画 ===
        self.rect.centerx = self.center_x
        
        if not self.is_bouncing:
            # 【修复】动画只依赖 时间 + 固定偏移，不再加上 center_x
            # 这样移动时，正弦波的频率不会改变
            t = pygame.time.get_ticks() / 300
            offset = math.sin(t + self.anim_offset) * 4 
            self.rect.centery = self.center_y + offset
        else:
            # 弹跳
            self.bounce_timer += 1
            if self.bounce_timer < 15:
                self.rect.centery = self.center_y - 20 + (self.bounce_timer * 2)
            else:
                self.is_bouncing = False

    def draw(self, surface):
        if self.image:
            # 绘制阴影 (椭圆)
            shadow_rect = pygame.Rect(0, 0, self.rect.width * 0.8, 10)
            shadow_rect.centerx = self.rect.centerx
            shadow_rect.centery = self.rect.bottom - 5
            shadow_surf = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
            surface.blit(shadow_surf, shadow_rect)
            
            # 如果被选中，画一个光圈或箭头
            if self.is_selected:
                # 画个黄色光圈
                pygame.draw.ellipse(surface, (255, 255, 0), shadow_rect.inflate(20, 10), 3)
                # 或者头顶画个倒三角
                tri_points = [
                    (self.rect.centerx, self.rect.top - 15),
                    (self.rect.centerx - 10, self.rect.top - 30),
                    (self.rect.centerx + 10, self.rect.top - 30)
                ]
                pygame.draw.polygon(surface, (255, 255, 0), tri_points)

            # 绘制本体
            surface.blit(self.image, self.rect)