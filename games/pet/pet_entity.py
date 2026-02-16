import pygame
import os
import math
import settings

class PetEntity:
    def __init__(self, pet_type, center_x, center_y):
        self.type = pet_type
        self.center_x = center_x
        self.center_y = center_y
        
        # 加载图片
        self.image = None
        self._load_image()
        
        # 动画状态
        self.is_bouncing = False
        self.bounce_timer = 0
        self.scale = 1.0 # 缩放比例
        
    def _load_image(self):
        """根据类型加载图片，失败则用色块"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            img_path = os.path.join(base_path, 'assets', 'images', f'pet_{self.type}.png')
            raw = pygame.image.load(img_path).convert_alpha()
            # 假设宠物图片统一缩放到 200x200
            self.image = pygame.transform.scale(raw, (200, 200))
        except:
            # 备用：生成一个带颜色的方块
            self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
            color = (255, 200, 100) if self.type == 'cat' else (100, 200, 255)
            pygame.draw.circle(self.image, color, (100, 100), 80)
            
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))

    def handle_click(self, pos):
        """处理点击交互"""
        if self.rect.collidepoint(pos):
            self.is_bouncing = True
            self.bounce_timer = 0
            return True # 返回 True 表示点中了
        return False

    def update(self):
        """处理动画 (呼吸效果 + 点击跳跃)"""
        # 简单的呼吸效果 (Breathing)
        if not self.is_bouncing:
            t = pygame.time.get_ticks() / 500
            offset = math.sin(t) * 5 # 上下浮动 5 像素
            self.rect.centery = self.center_y + offset
        else:
            # 点击后的弹跳动画 (Bouncing)
            self.bounce_timer += 1
            # 模拟一个简单的抛物线跳跃
            if self.bounce_timer < 20:
                self.rect.centery = self.center_y - 30 + (self.bounce_timer * 2)
            else:
                self.is_bouncing = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
