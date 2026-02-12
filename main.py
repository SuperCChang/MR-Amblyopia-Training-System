# main.py
import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from core.app import GameManager

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    game_manager = GameManager()
    game_manager.load_scenes()

    while game_manager.is_running:
        # 1. 计算时间增量 (dt: delta time, 单位: 毫秒)
        # clock.tick(FPS) 会限制帧率，并返回两次调用之间的时间间隔
        dt = clock.tick(FPS) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_manager.is_running = False
            game_manager.handle_input(event)

        # 2. 【关键修改】把 dt 传给管理器
        game_manager.update(dt)
        
        game_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()