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
    game_manager.load_scenes() # 【关键】加载场景

    while game_manager.is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_manager.is_running = False
            game_manager.handle_input(event)

        game_manager.update()
        game_manager.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()