# main.py (Debug 版本)
import pygame, sys, os
import settings
from core.app import GameManager
from core.path_utils import resource_path

def main():
    print("--- STEP 0: Audio Init ---")
    # 【新增】显式初始化音频模块
    # frequency=44100: 标准采样率
    # size=-16: 16位有符号音频
    # channels=2: 双声道
    # buffer=512: 缓冲区大小，越小延迟越低，但太小可能没声音。如果还不行，尝试改为 2048 或 4096
    try:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        print("Audio mixer initialized successfully.")
    except Exception as e:
        print(f"Audio init failed: {e}")
    
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
    
    print("--- STEP 3.5: Loading BGM ---")
    try:
        # 1. 寻找 bgm.wav
        bgm_path = resource_path(os.path.join('assets', 'sounds', 'bgm.wav'))
        
        if os.path.exists(bgm_path):
            # 2. 加载音乐 (Music 模式，专门用于长音频)
            pygame.mixer.music.load(bgm_path)
            
            # 3. 设置音量 (0.0 ~ 1.0)，背景音乐不要太吵，建议 0.2
            pygame.mixer.music.set_volume(0.2)
            
            # 4. 播放 (-1 表示无限循环)
            pygame.mixer.music.play(-1)
            print("Global BGM started.")
        else:
            print("Warning: bgm.wav not found.")
    except Exception as e:
        print(f"BGM Error: {e}")

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