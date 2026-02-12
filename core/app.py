# core/app.py
import pygame
from settings import COLORS, DIFFICULTY_LEVELS

# 稍后导入具体场景
# from games.main_menu import MainMenu
# from games.snake.game import SnakeGame
# from games.eyesight.game import EyesightGame

class GameManager:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # 【核心】全局难度等级 (索引 0-9)
        # 默认为 0，之后由 EyesightGame 修改
        self.difficulty = 0 
        
        # 场景占位，等下具体实现文件写好了再填
        self.scenes = {} 
        self.current_scene = None

    def load_scenes(self):
        """为了解决循环导入问题，建议单独写个方法加载场景"""
        from games.main_menu import MainMenu
        from games.snake.game import SnakeGame
        from games.eyesight.game import EyesightGame
        
        self.scenes = {
            'eyesight': EyesightGame(self),
            'menu': MainMenu(self),
            'snake': SnakeGame(self)
        }
        # 游戏启动默认进入视力测试
        self.current_scene = self.scenes['eyesight']

    def change_scene(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            # 如果进入贪吃蛇，可能需要根据新难度重置一下
            if hasattr(self.current_scene, 'reset_game'):
                self.current_scene.reset_game()

    def handle_input(self, event):
        if self.current_scene:
            self.current_scene.handle_input(event)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, surface):
        if self.current_scene:
            self.current_scene.draw(surface)