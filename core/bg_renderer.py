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
    def draw(surface, mode_index, current_time, grid_size, stripe_width, rotate_ratio):
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
            angle = (current_time / 50) % 360 * rotate_ratio
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
        # 1. 缓存键值 (加入 supersample 标记以防万一，虽然这里隐式包含在width里)
        cache_key = (width, color1, color2, "supersampled")

        # 2. 创建缓存 (如果不存在)
        if cache_key not in BackgroundRenderer._stripe_cache:
            w, h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
            # 计算对角线长度，保证旋转时不会露出黑边
            diagonal = math.ceil(math.sqrt(w**2 + h**2))
            size = diagonal + 20 

            # === 【核心优化：预渲染超采样】 ===
            # 我们创建一个 2 倍大小的画布进行绘制
            # 然后缩小回 1 倍，这样边缘就会自带抗锯齿效果
            scale_ratio = 2
            big_size = size * scale_ratio
            big_width = width * scale_ratio
            
            # 在大画布上绘图
            temp_surf = pygame.Surface((big_size, big_size))
            temp_surf.fill(color1)
            
            # 绘制大条纹
            for x in range(0, big_size, big_width * 2):
                pygame.draw.rect(temp_surf, color2, (x + big_width, 0, big_width, big_size))
            
            # 使用 smoothscale 高质量缩小回目标尺寸 (抗锯齿发生的步骤)
            # 这一步比较慢，但只在游戏加载或切换难度时执行一次，不影响游戏帧率
            final_surf = pygame.transform.smoothscale(temp_surf, (size, size))

            # 转换为显示格式，加速 blit
            if pygame.display.get_surface():
                final_surf = final_surf.convert()

            BackgroundRenderer._stripe_cache[cache_key] = final_surf

        # 3. 取出源图 (此时源图已经是抗锯齿过的了)
        source_surf = BackgroundRenderer._stripe_cache[cache_key]

        # 4. 实时旋转
        # 依然使用最快的 rotate (而非 slow rotozoom)，因为源图已经柔化过
        # 这样旋转产生的锯齿感会大幅降低，且帧率保持 60FPS
        rotated_surf = pygame.transform.rotate(source_surf, angle)
        
        # 5. 居中绘制
        rect = rotated_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        surface.blit(rotated_surf, rect)

    @staticmethod
    def _draw_checkerboard(surface, bg_color, fill_color, size):
        safe_size = max(1, min(size, settings.SCREEN_WIDTH - 1, settings.SCREEN_HEIGHT - 1))
        if safe_size < 5: return 

        surface.fill(bg_color)
        for y in range(0, settings.SCREEN_HEIGHT, safe_size):
            for x in range(0, settings.SCREEN_WIDTH, safe_size):
                if ((y // safe_size) + (x // safe_size)) % 2 == 1:
                    pygame.draw.rect(surface, fill_color, (x, y, safe_size, safe_size))