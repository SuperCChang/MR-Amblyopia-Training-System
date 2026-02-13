# core/ui.py
import pygame
from settings import COLORS

class Button:
    def __init__(self, x, y, width, height, text, font, text_color=COLORS['white'], bg_color=COLORS['blue'], hover_color=COLORS['red']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        # 1. 根据是否悬停决定颜色
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # 2. 画按钮背景
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['white'], self.rect, 2, border_radius=10) # 边框

        # 3. 画文字（居中）
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """检查鼠标是否悬停"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """检查是否被点击"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False