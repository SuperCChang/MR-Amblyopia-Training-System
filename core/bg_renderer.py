# core/bg_renderer.py
import pygame
import math
import settings
from settings import COLORS

class BackgroundRenderer:
    # 缓存：键 -> Surface
    _stripe_cache = {}
    _last_screen_size = (0, 0)

    @staticmethod
    def draw(surface, mode_index, current_time, grid_size, stripe_width):
        # 0. 分辨率变化检测
        current_size = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        if current_size != BackgroundRenderer._last_screen_size:
            BackgroundRenderer._stripe_cache.clear()
            BackgroundRenderer._last_screen_size = current_size

        # --- Group 1: 纯色 (0-2) ---
        if mode_index == 0: surface.fill(COLORS['red'])
        elif mode_index == 1: surface.fill(COLORS['yellow'])
        elif mode_index == 2: surface.fill(COLORS['green'])
            
        # --- Group 2: 旋转条栅 (3-5) ---
        elif mode_index in [3, 4, 5]:
            angle = (current_time / 50) % 360
            c1, c2 = COLORS['black'], COLORS['white']
            if mode_index == 4: c1, c2 = COLORS['red'], COLORS['yellow']
            if mode_index == 5: c1, c2 = COLORS['blue'], COLORS['yellow']
            
            BackgroundRenderer._draw_rotating_stripes(surface, angle, c1, c2, stripe_width)

        # --- Group 3: 棋盘格 (6-8) ---
        elif mode_index in [6, 7, 8]:
            state = (current_time // 1000) % 2
            color_a, color_b = COLORS['black'], COLORS['white']
            if mode_index == 7: color_a, color_b = COLORS['red'], COLORS['yellow']
            if mode_index == 8: color_a, color_b = COLORS['blue'], COLORS['yellow']

            main_c = color_a if state == 0 else color_b
            alt_c = color_b if state == 0 else color_a
            
            BackgroundRenderer._draw_checkerboard(surface, main_c, alt_c, grid_size)

    @staticmethod
    def _draw_rotating_stripes(surface, angle, color1, color2, width):
        # 1. 缓存键值
        cache_key = (width, color1, color2)

        # 2. 创建缓存 (如果不存在)
        if cache_key not in BackgroundRenderer._stripe_cache:
            w, h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
            diagonal = math.ceil(math.sqrt(w**2 + h**2))
            size = diagonal + 20 

            # 创建大图
            temp_surf = pygame.Surface((size, size))
            temp_surf.fill(color1)
            
            for x in range(0, size, width * 2):
                pygame.draw.rect(temp_surf, color2, (x + width, 0, width, size))
            
            # 【核心优化 1】转换为显示格式！
            # 这能极大提升后续的 blit 和 rotate 速度 (从 20FPS 提升到 60FPS 的关键)
            # 注意：如果 convert() 报错，可能是因为 display 还没 init，但在 draw 调用时肯定已经 init 了
            if pygame.display.get_surface():
                temp_surf = temp_surf.convert()

            BackgroundRenderer._stripe_cache[cache_key] = temp_surf

        # 3. 取出源图
        source_surf = BackgroundRenderer._stripe_cache[cache_key]

        # 4. 【核心优化 2】回退到 rotate (快速旋转)
        # 放弃 rotozoom，因为在 1080p+ 分辨率下实时插值太慢了
        rotated_surf = pygame.transform.rotate(source_surf, angle)
        
        # 5. 居中绘制
        rect = rotated_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        surface.blit(rotated_surf, rect)

    @staticmethod
    def _draw_checkerboard(surface, bg_color, fill_color, size):
        # 保持之前的逻辑...
        safe_size = max(1, min(size, settings.SCREEN_WIDTH - 1, settings.SCREEN_HEIGHT - 1))
        if safe_size < 5: return 

        surface.fill(bg_color)
        for y in range(0, settings.SCREEN_HEIGHT, safe_size):
            for x in range(0, settings.SCREEN_WIDTH, safe_size):
                if ((y // safe_size) + (x // safe_size)) % 2 == 1:
                    pygame.draw.rect(surface, fill_color, (x, y, safe_size, safe_size))