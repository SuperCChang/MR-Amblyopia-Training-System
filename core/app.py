import pygame
from settings import COLORS

# 引入具体场景
from games.main_menu import MainMenu
from games.snake.game import SnakeGame
# from games.eyesight.game import EyesightGame  <--- 【修改1】注释掉这行，暂时不用它

class GameManager:
    def __init__(self):
        self.is_running = True
        
        # 默认难度设为字符串 key
        self.difficulty = 'EASY' 
        
        self.scenes = {} 
        self.current_scene = None

    def load_scenes(self):
        # 重新导入以避免循环依赖
        from games.main_menu import MainMenu
        from games.snake.game import SnakeGame
        # from games.eyesight.game import EyesightGame <--- 【修改2】注释掉这行
        
        self.scenes = {
            # 'eyesight': EyesightGame(self),          <--- 【修改3】注释掉这行，不初始化它
            'menu': MainMenu(self),
            'snake': SnakeGame(self)
        }
        
        # 【修改4】将入口场景强制设为主菜单
        self.current_scene = self.scenes['menu']

    def change_scene(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            # 如果场景有 reset_game 方法，切换时重置一下（比如贪吃蛇）
            if hasattr(self.current_scene, 'reset_game'):
                self.current_scene.reset_game()
        else:
            print(f"Error: Scene '{scene_name}' not found.")

    def handle_input(self, event):
        if self.current_scene:
            self.current_scene.handle_input(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, surface):
        if self.current_scene:
            self.current_scene.draw(surface)