# games/pet/pet_entity.py
import pygame
import os
import math
import settings
from core.path_utils import resource_path

class PetEntity:
    def __init__(self, pet_id, center_x, center_y):
        self.pet_id = pet_id # 例如 'cat_orange', 'dog_husky'
        self.center_x = center_x
        self.center_y = center_y
        
        self.image = None
        self._load_image()
        
        self.is_bouncing = False
        self.bounce_timer = 0
        
    def _load_image(self):
        """尝试加载 pet_{id}.png"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            # 这里的 filename 对应 settings.PET_SHOP_LIST 里的 img 字段
            # 但为了简化，我们假设文件名格式统一为 "pet_{id}.png"
            # 或者直接去 settings 里找对应的 img 文件名 (这里为了简单直接拼)
            
            # 查找对应的配置
            img_name = f"pet_{self.pet_id}.png"
            for p in settings.PET_SHOP_LIST:
                if p['id'] == self.pet_id:
                    img_name = p['img']
                    break
            
            # img_path = os.path.join(base_path, 'assets', 'images', img_name)
            img_path = resource_path(os.path.join('assets', 'images', img_name))

            if os.path.exists(img_path):
                raw = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(raw, (200, 200))
            else:
                raise FileNotFoundError
        except:
            # 备用色块
            self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
            # 根据 ID 稍微变点颜色
            color = (255, 200, 100) if 'cat' in self.pet_id else (100, 200, 255)
            if 'black' in self.pet_id: color = (50, 50, 50)
            if 'white' in self.pet_id: color = (240, 240, 240)
            pygame.draw.circle(self.image, color, (100, 100), 80)
            
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.is_bouncing = True
            self.bounce_timer = 0
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
        surface.blit(self.image, self.rect)