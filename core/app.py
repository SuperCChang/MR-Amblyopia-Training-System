# core/app.py
import pygame
import os
from settings import FPS, WINDOW_TITLE, CURSOR_CONFIG
from core.path_utils import resource_path

class GameManager:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.difficulty = 'EASY'
        
        # 场景容器
        self.scenes = {}
        self.current_scene = None
        
        # FPS显示
        self.show_fps = False
        self.font_fps = pygame.font.SysFont("arial", 20, bold=True)
        
        # 【新增】初始化自定义光标
        self._init_custom_cursor()
        
        # 加载所有场景
        self.load_scenes()

    def load_scenes(self):
        from games.login_scene import LoginScene
        from games.main_menu import MainMenu
        from games.snake.game import SnakeGame
        from games.pet.scene import PetScene
        from games.catch.game import CatchGame
        from games.fruit.game import FruitGame
        from games.pigeon.game import PigeonGame

        self.scenes = {
            'login': LoginScene(self),
            'menu': MainMenu(self),
            'snake': SnakeGame(self),
            'pet': PetScene(self),
            'catch': CatchGame(self),
            'fruit': FruitGame(self),
            'pigeon': PigeonGame(self),
        }
        
        self.current_scene = self.scenes['login']

    def change_scene(self, scene_name):
        """切换场景"""
        if scene_name in self.scenes:
            print(f"[系统] 切换场景 -> {scene_name}")
            
            # 【关键修复】切换场景时，清空当前的消息队列
            # 防止你在"登录"按钮上点了一下，鼠标抬起时却误触了新场景里的按钮
            pygame.event.clear()
            
            self.current_scene = self.scenes[scene_name]
            
            # 触发新场景的刷新逻辑
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter()
        else:
            print(f"[Error] 试图切换到不存在的场景: {scene_name}")

    def _init_custom_cursor(self):
        if not CURSOR_CONFIG.get('enabled', False):
            return

        try:
            cursor_surf = None
            hotspot = CURSOR_CONFIG.get('hotspot', (0, 0))
            
            # 1. 尝试加载图片
            img_name = CURSOR_CONFIG.get('image', 'cursor.png')
            img_path = resource_path(os.path.join('assets', 'images', img_name))
            
            if os.path.exists(img_path):
                # 加载并缩放
                raw_cursor = pygame.image.load(img_path).convert_alpha()
                target_size = CURSOR_CONFIG.get('size', (64, 64))
                cursor_surf = pygame.transform.smoothscale(raw_cursor, target_size)
                print(f"Loaded custom cursor from: {img_name}")
            else:
                # 2. 图片不存在，绘制默认的高对比度光标 (代码保底)
                print("Cursor image not found. Using fallback style.")
                radius = CURSOR_CONFIG.get('fallback_radius', 20)
                outline = CURSOR_CONFIG.get('fallback_outline', 3)
                size = radius * 2 + outline * 2
                
                # 创建一个透明图层
                cursor_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # 画黑色描边 (增强对比度)
                pygame.draw.circle(cursor_surf, (0, 0, 0), (size//2, size//2), radius + outline)
                # 画内部颜色 (高亮色)
                color = CURSOR_CONFIG.get('fallback_color', (255, 255, 0))
                pygame.draw.circle(cursor_surf, color, (size//2, size//2), radius)
                
                # 对于圆形光标，热点通常在中心
                hotspot = (size // 2, size // 2)

            # 3. 应用光标 (需要 Pygame 2.0+)
            if cursor_surf:
                cursor = pygame.cursors.Cursor(hotspot, cursor_surf)
                pygame.mouse.set_cursor(cursor)
                
        except Exception as e:
            print(f"Failed to set cursor: {e}")
            # 出错则回退到系统默认
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
        # ... (FPS绘制代码保持不变) ...
        fps = int(self.clock.get_fps())
        if fps >= 55: color = (0, 255, 0)
        elif fps >= 30: color = (255, 255, 0)
        else: color = (255, 0, 0)
        
        fps_text = f"FPS: {fps}"
        text_surf = self.font_fps.render(fps_text, True, color)
        bg_rect = text_surf.get_rect(topright=(surface.get_width() - 10, 10))
        bg_rect.inflate_ip(10, 10)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, border_radius=5)
        surface.blit(text_surf, text_surf.get_rect(center=bg_rect.center))