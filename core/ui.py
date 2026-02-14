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

class InputBox:
    def __init__(self, x, y, w, h, font, is_password=False, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = COLORS['grey']
        self.color_active = COLORS['blue']
        self.color = self.color_inactive
        self.text = ""
        self.font = font
        self.active = False
        self.is_password = is_password
        self.placeholder = placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果点击了框内，激活；否则取消激活
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return "submit"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # 过滤非法字符
                    if event.unicode.isprintable():
                        self.text += event.unicode
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=5)
        
        display_text = self.text
        if self.is_password:
            display_text = "*" * len(self.text)
        
        if len(self.text) == 0 and not self.active:
            # 绘制占位符
            txt_surf = self.font.render(self.placeholder, True, (150, 150, 150))
        else:
            txt_surf = self.font.render(display_text, True, COLORS['white'])
            
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + (self.rect.h - txt_surf.get_height())//2))
        
        if self.active:
             cursor_x = self.rect.x + 5 + txt_surf.get_width()
             pygame.draw.line(surface, COLORS['white'], (cursor_x, self.rect.y + 5), (cursor_x, self.rect.y + self.rect.h - 5), 2)