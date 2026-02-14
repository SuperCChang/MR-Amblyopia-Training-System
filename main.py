# main.py (Debug 版本)
import pygame
import sys
import settings
from core.app import GameManager

def main():
    print("--- STEP 1: Pygame Init ---")
    pygame.init()
    pygame.font.init()
    
    print("--- STEP 2: Setting Window Mode ---")
    # 全屏启动
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    print("--- STEP 3: Getting Display Info ---")
    info = pygame.display.Info()
    settings.SCREEN_WIDTH = info.current_w
    settings.SCREEN_HEIGHT = info.current_h
    print(f"Screen Size: {settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT}")
    
    pygame.display.set_caption(settings.WINDOW_TITLE)
    clock = pygame.time.Clock()

    print("--- STEP 4: Initializing GameManager ---")
    game_manager = GameManager()
    
    print("--- STEP 5: Loading Scenes (Possbile Freeze Here) ---")
    # 这里的 load_scenes 会初始化 LoginScene，LoginScene 会初始化 DataManager，
    # DataManager 会尝试连接网络。如果不打印 STEP 6，说明死在网络上了。
    game_manager.load_scenes()
    
    print("--- STEP 6: Scenes Loaded Successfully ---")
    
    # 强制设为登录界面
    if 'login' in game_manager.scenes:
        game_manager.current_scene = game_manager.scenes['login']
    else:
        print("ERROR: Login scene not found!")

    print("--- STEP 7: Starting Main Loop ---")
    while game_manager.is_running:
        dt = clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_manager.is_running = False
            # 传递事件
            game_manager.handle_input(event)

        game_manager.update(dt)
        game_manager.draw(screen)

        pygame.display.flip()

    print("--- Game Exiting ---")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nCRITICAL ERROR CAUGHT: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...") # 让窗口停住，不要闪退