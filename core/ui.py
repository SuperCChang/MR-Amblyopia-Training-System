# core/ui.py
import pygame
from settings import COLORS

class Button:
    # ... (Button 类保持之前的描边版本不变，为了节省篇幅我省略了，请保留你现有的 Button 代码) ...
    def __init__(self, x, y, width, height, text, font, text_color=COLORS['white'], bg_color=COLORS['blue'], hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.base_color = bg_color
        self.hover_color = hover_color if hover_color else self._adjust_color(bg_color, 30)
        self.is_hovered = False
        self.is_pressed = False 

    def _adjust_color(self, color, amount):
        r, g, b = color[:3]
        return (max(0, min(255, r + amount)), max(0, min(255, g + amount)), max(0, min(255, b + amount)))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        return False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        offset_y = -2 if not self.is_pressed else 0
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4 
        pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=12)
        draw_rect = self.rect.copy()
        draw_rect.y += offset_y
        pygame.draw.rect(surface, color, draw_rect, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), draw_rect, 2, border_radius=12)

        # 描边
        outline_surf = self.font.render(self.text, True, (0, 0, 0))
        outline_rect = outline_surf.get_rect()
        center_x, center_y = draw_rect.centerx, draw_rect.centery
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dx, dy in offsets:
            outline_rect.center = (center_x + dx, center_y + dy)
            surface.blit(outline_surf, outline_rect)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

# --- 2. 输入框类 (核心修改) ---
class InputBox:
    def __init__(self, x, y, w, h, font, is_password=False, placeholder="", restrict_ascii=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (100, 100, 100)
        self.color_active = COLORS['blue']
        self.color = self.color_inactive
        self.text = ""
        self.font = font
        self.active = False
        self.is_password = is_password
        self.placeholder = placeholder
        # 【新增】是否限制只能输入英文/数字 (用于账号密码)
        self.restrict_ascii = restrict_ascii

    def handle_event(self, event):
        # 1. 鼠标点击激活
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                # 激活时开启输入法支持
                if self.active:
                    pygame.key.start_text_input()
            else:
                self.active = False
                # pygame.key.stop_text_input() # 可选：失去焦点时关闭输入法
            self.color = self.color_active if self.active else self.color_inactive

        # 2. 处理功能键 (回车、退格) - 依然用 KEYDOWN
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return "submit"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

        # 3. 【核心修改】处理文本输入 (支持中文) - 使用 TEXTINPUT
        if event.type == pygame.TEXTINPUT and self.active:
            # 如果开启了 ASCII 限制 (比如账号框)，则过滤掉中文
            if self.restrict_ascii:
                # 只允许 ASCII 字符 (英文、数字、符号)
                if event.text.isascii():
                    self.text += event.text
            else:
                # 允许所有字符 (包括中文)
                self.text += event.text
                
        return None

    def draw(self, surface):
        # 半透明底板
        s = pygame.Surface((self.rect.w, self.rect.h))
        s.set_alpha(128)
        s.fill((0,0,0))
        surface.blit(s, (self.rect.x, self.rect.y))
        
        # 边框
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=5)
        
        # 内容
        display_text = self.text
        if self.is_password:
            display_text = "*" * len(self.text)
        
        if len(self.text) == 0 and not self.active:
            txt_surf = self.font.render(self.placeholder, True, (200, 200, 200))
        else:
            txt_surf = self.font.render(display_text, True, COLORS['white'])
            
        surface.blit(txt_surf, (self.rect.x + 10, self.rect.y + (self.rect.h - txt_surf.get_height())//2))
        
        # 光标
        if self.active:
             cursor_x = self.rect.x + 10 + txt_surf.get_width()
             # 简单的光标闪烁
             if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(surface, COLORS['white'], (cursor_x, self.rect.y + 10), (cursor_x, self.rect.y + self.rect.h - 10), 2)

class Checkbox:
    # ... (保持 Checkbox 不变) ...
    def __init__(self, x, y, size, text, font, text_color=COLORS['white'], checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.checked = checked
        self.bg_color = (50, 50, 50)
        self.check_color = COLORS['green']

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_rect = self.rect.copy()
            click_rect.w += 150 
            if click_rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=4)
        if self.checked:
            inner = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, self.check_color, inner, border_radius=2)

        text_x = self.rect.right + 10
        text_y = self.rect.centery - self.font.get_height() // 2
        
        outline_surf = self.font.render(self.text, True, (0,0,0))
        surface.blit(outline_surf, (text_x - 1, text_y))
        surface.blit(outline_surf, (text_x + 1, text_y))
        surface.blit(outline_surf, (text_x, text_y - 1))
        surface.blit(outline_surf, (text_x, text_y + 1))
        
        txt_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(txt_surf, (text_x, text_y))