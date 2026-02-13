# main.py
import pygame
import sys
import settings # 导入 settings 模块
from core.app import GameManager

def main():
    pygame.init()
    pygame.font.init()
    
    # 【核心修改】全屏启动
    # 传入 (0, 0) 和 pygame.FULLSCREEN，Pygame 会使用当前显示器的最佳分辨率
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    # 获取实际的分辨率
    info = pygame.display.Info()
    actual_w = info.current_w
    actual_h = info.current_h
    
    # 【关键】反向更新 settings 中的全局变量
    # 这样 SnakeGame 里引用的 settings.SCREEN_WIDTH 就会变成正确的值
    settings.SCREEN_WIDTH = actual_w
    settings.SCREEN_HEIGHT = actual_h
    
    pygame.display.set_caption(settings.WINDOW_TITLE)
    clock = pygame.time.Clock()

    game_manager = GameManager()
    # 确保在屏幕尺寸更新后再加载场景 (这样主菜单的按钮位置才能算对)
    game_manager.load_scenes()
    
    # 默认难度设为 EASY
    game_manager.difficulty = 'EASY'

    while game_manager.is_running:
        dt = clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_manager.is_running = False
            game_manager.handle_input(event)

        game_manager.update(dt)
        game_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()