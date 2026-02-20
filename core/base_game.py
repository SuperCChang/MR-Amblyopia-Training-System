# core/base_game.py
import pygame
import settings # 确保导入 settings 模块
from settings import DIFFICULTY_LEVELS
from core.bg_renderer import BackgroundRenderer

class BaseGame:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        
        self.bg_mode = 0
        self.bg_timer = 0
        
        # 初始切换间隔 (会被 update 里的逻辑覆盖)
        self.SWITCH_INTERVAL = 5000 
        
        # 【关键修复】新增这个属性，防止报错
        # 用于手动覆盖旋转速度 (例如主菜单强制慢速)
        self.override_speed = None 

    # ==========================================
    # 【关键修复】新增这个方法，解决 AttributeError
    # ==========================================
    def set_bg_speed(self, speed):
        """设置背景滚动的速度 (存储到 override_speed)"""
        self.override_speed = speed
        # print(f"Background speed override set to: {speed}")

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_scene('menu')

    def update(self, dt):
        self.bg_timer += dt
        
        # 【修复】实时获取当前难度的切换间隔
        # 这样如果你在 settings 里给不同难度设置了不同的切换时间，也能生效
        current_settings = DIFFICULTY_LEVELS.get(self.app.difficulty, {})
        self.SWITCH_INTERVAL = current_settings.get('switch_interval', 5000)
        
        if self.bg_timer >= self.SWITCH_INTERVAL:
            # 向前切换背景
            self.bg_mode += 1
            
            # --- 【新增】判断逻辑 ---
            # 模式9是红黄绿，一直开启。
            # 模式10是黑圆，仅在勾选时开启。如果当前是10且没勾选，直接跳过。
            if self.bg_mode == 10 and not getattr(settings, 'ENABLE_CIRCLE_BG', False):
                self.bg_mode = 11
                
            # 如果超过了最大模式索引(当前最大为10)，则回到0
            if self.bg_mode > 10:
                self.bg_mode = 0
                
            self.bg_timer = 0

    def draw(self, surface):
        # 1. 获取当前难度的配置
        current_settings = DIFFICULTY_LEVELS.get(self.app.difficulty, {})
        
        bg_g_size = current_settings.get('bg_grid_size', 30)
        s_width = current_settings.get('stripe_width', 30)
        
        # 2. 【核心逻辑】决定旋转速度 (rotate_ratio)
        # 逻辑：如果设置了 override_speed (比如在主菜单)，就通过计算覆盖掉默认的 rotate_ratio
        if self.override_speed is not None:
            # 将速度值 (如 20, 200) 转换为旋转倍率
            # 假设速度 20 对应倍率 1.0 (基准)
            rotate_ratio = self.override_speed / 20.0
        else:
            rotate_ratio = current_settings.get('bg_speed', 30) / 20.0

        # 3. 绘制背景
        # 注意这里不仅传入了时间，还传入了 self.app.difficulty，用于给模式9/10控制闪烁频率
        BackgroundRenderer.draw(
            surface, 
            self.bg_mode, 
            pygame.time.get_ticks(), 
            bg_g_size, 
            s_width, 
            rotate_ratio,
            self.app.difficulty
        )