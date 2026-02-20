# core/bg_renderer.py
import pygame
import math
import settings
from settings import COLORS

class BackgroundRenderer:
    # 缓存：键 -> Surface
    _stripe_cache = {}
    _rotated_cache = {} # 【新增】缓存当前帧角度的抗锯齿图像
    _last_screen_size = (0, 0)

    @staticmethod
    def draw(surface, mode_index, current_time, grid_size, stripe_width, rotate_ratio, difficulty='EASY'):
        # 0. 分辨率变化检测
        current_size = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        if current_size != BackgroundRenderer._last_screen_size:
            BackgroundRenderer._stripe_cache.clear()
            BackgroundRenderer._rotated_cache.clear() # 清除旋转缓存
            BackgroundRenderer._last_screen_size = current_size

        # --- Group 1: 纯色闪烁 (0-2) ---
        if mode_index in [0, 1, 2]:
            # 【需求1】根据难度设定闪烁周期 (毫秒)
            # EASY: 1000ms周期 (亮500, 暗500) -> 1 Hz
            # MEDIUM: 500ms周期 (亮250, 暗250) -> 2 Hz
            # HARD: 250ms周期 (亮125, 暗125) -> 4 Hz
            flash_intervals = {'EASY': 500, 'MEDIUM': 250, 'HARD': 125}
            interval = flash_intervals.get(difficulty, 500)
            
            # 判断当前是"亮"还是"暗"
            is_color = (current_time // interval) % 2 == 0
            
            if is_color:
                if mode_index == 0: surface.fill(COLORS['red'])
                elif mode_index == 1: surface.fill(COLORS['yellow'])
                elif mode_index == 2: surface.fill(COLORS['green'])
            else:
                surface.fill(COLORS['black']) # 黑底交替，形成闪烁

        # --- Group 2: 旋转条栅 (3-5) ---
        elif mode_index in [3, 4, 5]:
            # 【需求2】降低条栅格旋转的"帧率" (注意：不是速度)
            # 我们将连续的时间"阶梯化"，设定背景目标帧率为 10 FPS
            bg_fps = 10
            step_ms = 1000 // bg_fps
            # 这样算出来的时间，在 100ms 内都是同一个固定值
            stepped_time = (current_time // step_ms) * step_ms
            
            # 使用阶梯化后的时间计算角度，角度会一卡一卡地跳跃
            angle = (stepped_time / 50) % 360 * rotate_ratio
            
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
        cache_key = (width, color1, color2, "supersampled")

        # 1. 创建基础超采样缓存
        if cache_key not in BackgroundRenderer._stripe_cache:
            w, h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
            diagonal = math.ceil(math.sqrt(w**2 + h**2))
            size = diagonal + 20 

            scale_ratio = 2
            big_size = size * scale_ratio
            big_width = width * scale_ratio
            
            temp_surf = pygame.Surface((big_size, big_size))
            temp_surf.fill(color1)
            
            for x in range(0, big_size, big_width * 2):
                pygame.draw.rect(temp_surf, color2, (x + big_width, 0, big_width, big_size))
            
            final_surf = pygame.transform.smoothscale(temp_surf, (size, size))
            if pygame.display.get_surface():
                final_surf = final_surf.convert()

            BackgroundRenderer._stripe_cache[cache_key] = final_surf

        source_surf = BackgroundRenderer._stripe_cache[cache_key]

        # 2. === 【核心优化：高质量抗锯齿 + 旋转帧缓存】 ===
        # 获取当前缓存的角度和图像
        cached_angle, cached_surf = BackgroundRenderer._rotated_cache.get(cache_key, (None, None))
        
        # 如果角度发生了变化（例如每100ms跳跃一次），才进行沉重的抗锯齿旋转计算
        if cached_angle != angle:
            # 放弃原本有锯齿的 rotate，改用高质量自带平滑滤波的 rotozoom (scale=1.0)
            cached_surf = pygame.transform.rotozoom(source_surf, angle, 1.0)
            BackgroundRenderer._rotated_cache[cache_key] = (angle, cached_surf)
        
        # 对于不更新角度的那 50 多帧，直接 0 延迟渲染缓存图！
        rotated_surf = cached_surf
        
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