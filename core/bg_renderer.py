import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS

class BackgroundRenderer:
    @staticmethod
    def draw(surface, mode_index, current_time, bg_grid_size, stripe_width):
        """
        mode_index (0-8):
        0-2: 纯色
        3-5: 旋转条栅
        6-8: 闪烁棋盘格 (Checkerboard)
        """
        
        # --- Group 1: 纯色背景 (0-2) ---
        if mode_index == 0:
            surface.fill(COLORS['red'])
        elif mode_index == 1:
            surface.fill(COLORS['yellow'])
        elif mode_index == 2:
            surface.fill(COLORS['green'])
            
        # --- Group 2: 旋转条栅 (3-5) ---
        elif mode_index in [3, 4, 5]:
            angle = (current_time / 20) % 360
            c1, c2 = COLORS['black'], COLORS['white']
            if mode_index == 4: c1, c2 = COLORS['red'], COLORS['yellow']
            if mode_index == 5: c1, c2 = COLORS['blue'], COLORS['yellow']
            
            BackgroundRenderer._draw_rotating_stripes(surface, angle, c1, c2, stripe_width)

        # --- Group 3: 闪烁棋盘格 (6-8) ---
        elif mode_index in [6, 7, 8]:
            # 每 1000ms (1秒) 切换状态 (0 或 1)
            state = (current_time // 1000) % 2
            
            # 确定颜色组合
            color_a, color_b = COLORS['black'], COLORS['white']
            if mode_index == 7: color_a, color_b = COLORS['red'], COLORS['yellow']
            if mode_index == 8: color_a, color_b = COLORS['blue'], COLORS['yellow']

            # 根据状态交换颜色，实现闪烁
            main_color = color_a if state == 0 else color_b
            alt_color = color_b if state == 0 else color_a
            
            # 【核心修改】调用棋盘格绘制
            BackgroundRenderer._draw_checkerboard(surface, main_color, alt_color, bg_grid_size)

    # --- 辅助绘制方法 ---

    @staticmethod
    def _draw_rotating_stripes(surface, angle, color1, color2, width):
        # (保持原样，无需修改)
        size = 1500
        temp_surf = pygame.Surface((size, size))
        temp_surf.fill(color1)
        for x in range(0, size, width * 2):
            pygame.draw.rect(temp_surf, color2, (x + width, 0, width, size))
        rotated_surf = pygame.transform.rotate(temp_surf, angle)
        rect = rotated_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(rotated_surf, rect)

    @staticmethod
    def _draw_checkerboard(surface, bg_color, fill_color, size):
        """
        绘制国际象棋样式的交替棋盘格
        :param bg_color: 底色 (例如白色)
        :param fill_color: 填充色 (例如黑色)
        :param size: 格子大小
        """
        # 1. 性能优化：先把全屏填满底色 (比如全白)
        surface.fill(bg_color)
        
        # 2. 只画另一种颜色的格子 (比如黑)，减少一半的绘制工作量
        # 遍历屏幕上的网格点
        for y in range(0, SCREEN_HEIGHT, size):
            for x in range(0, SCREEN_WIDTH, size):
                
                # 计算当前是第几行、第几列
                row = y // size
                col = x // size
                
                # 棋盘格算法：如果 (行号 + 列号) 是奇数，就画色块
                # 0,0(偶) -> 不画(底色)
                # 0,1(奇) -> 画黑
                # 0,2(偶) -> 不画(底色)
                # 1,0(奇) -> 画黑
                if (row + col) % 2 == 1:
                    pygame.draw.rect(surface, fill_color, (x, y, size, size))