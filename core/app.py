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
        
        self.clock = pygame.time.Clock()
        self.scenes = {} 
        self.current_scene = None

        self.show_fps = True
        self.font_fps = pygame.font.SysFont("arial", 20, bold=True)

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
        if self.show_fps:
            self._draw_fps(surface)
    
    def _draw_fps(self, surface):
        # 获取当前帧率
        fps = int(self.clock.get_fps())
        
        # 根据流畅度变色 (绿 > 黄 > 红)
        if fps >= 55: color = COLORS['green']
        elif fps >= 30: color = COLORS['yellow']
        else: color = COLORS['red']
        
        fps_text = f"FPS: {fps}"
        text_surf = self.font_fps.render(fps_text, True, color)
        
        # 画个黑色背景框，保证看清楚
        bg_rect = text_surf.get_rect(topright=(surface.get_width() - 10, 10))
        # 稍微扩充一点背景框
        bg_rect.inflate_ip(10, 10) 
        
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, border_radius=5)
        surface.blit(text_surf, text_surf.get_rect(center=bg_rect.center))