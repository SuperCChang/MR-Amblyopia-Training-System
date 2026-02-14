import pygame
import random
import os
import settings
from core.base_game import BaseGame
from core.data_manager import DataManager
from settings import COLORS, DIFFICULTY_LEVELS, GAME_GRID_RATIO

class SnakeGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        # --- 1. 倒计时系统 ---
        self.total_time = settings.TRAINING_DURATION * 1000 
        self.time_left = self.total_time
        self.is_time_up = False
        
        # --- 2. 分数系统 (内存版) ---
        self.high_score = 0  # 【修改】初始化为0，不读取文件
        self.current_score = 0
        
        # 字体
        try:
            # 尝试加载中文字体，如果没有则回退
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            font_path = os.path.join(base_path, 'assets', 'fonts', 'simhei.ttf') # 如果你有放字体文件
            # self.font_ui = pygame.font.Font(font_path, 24) 
            self.font_ui = pygame.font.SysFont("simhei", 24)
            self.font_msg = pygame.font.SysFont("simhei", 60, bold=True)
        except:
            self.font_ui = pygame.font.SysFont("arial", 24)
            self.font_msg = pygame.font.SysFont("arial", 60, bold=True)
        
        # --- 3. 资源加载 ---
        self.images_loaded = False
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            img_dir = os.path.join(base_path, 'assets', 'images')
            
            self.raw_head = pygame.image.load(os.path.join(img_dir, 'snake_head.png')).convert_alpha()
            self.raw_body = pygame.image.load(os.path.join(img_dir, 'snake_body.png')).convert_alpha()
            
            # 尝试加载尾巴和转角 (如果文件存在)
            p_tail = os.path.join(img_dir, 'snake_tail.png')
            if os.path.exists(p_tail):
                self.raw_tail = pygame.image.load(p_tail).convert_alpha()
            
            p_corner = os.path.join(img_dir, 'snake_corner.png')
            if os.path.exists(p_corner):
                self.raw_corner = pygame.image.load(p_corner).convert_alpha()
                
            self.raw_food = pygame.image.load(os.path.join(img_dir, 'apple.png')).convert_alpha()
            
            self.images_loaded = True
            print("Snake images loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load images. Using fallback rectangles. Error: {e}")
            self.images_loaded = False

        self.reset_game()

    # 【删除】 _load_high_score 和 _save_high_score 方法都被移除了

    def reset_game(self):
        """蛇死亡或重新开始时调用"""
        if self.current_score > 0:
            coins_earned = self.current_score // 10 # 整除10
            if coins_earned > 0:
                print(f"Game Over! You earned {coins_earned} coins.")
                # 调用单例增加金币
                DataManager().add_coins(coins_earned)
        
        # 【修改】最高分更新逻辑：
        # 如果死掉的时候分数比最高分高，更新一下（双重保险）
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            
        # 重置当前分
        self.current_score = 0
        
        # 读取配置
        diff_key = self.app.difficulty 
        diff_settings = DIFFICULTY_LEVELS[diff_key]
        
        # 速度设置
        self.base_speed = diff_settings['snake_speed']
        self.move_interval = self.base_speed
        
        # 尺寸设置
        self.grid_size = settings.SCREEN_WIDTH // diff_settings['snake_size']
        self.grid_size = max(20, self.grid_size)

        # 图片缩放
        if self.images_loaded:
            self.img_head = pygame.transform.scale(self.raw_head, (self.grid_size, self.grid_size))
            self.img_body = pygame.transform.scale(self.raw_body, (self.grid_size, self.grid_size))
            if hasattr(self, 'raw_tail'):
                self.img_tail = pygame.transform.scale(self.raw_tail, (self.grid_size, self.grid_size))
            if hasattr(self, 'raw_corner'):
                self.img_corner = pygame.transform.scale(self.raw_corner, (self.grid_size, self.grid_size))
            self.img_food = pygame.transform.scale(self.raw_food, (self.grid_size, self.grid_size))

        # 蛇的位置
        start_x = (settings.SCREEN_WIDTH // self.grid_size // 2) * self.grid_size
        start_y = (settings.SCREEN_HEIGHT // self.grid_size // 2) * self.grid_size
        
        self.snake = [
            (start_x, start_y),
            (start_x - self.grid_size, start_y),
            (start_x - 2 * self.grid_size, start_y)
        ]
        self.direction = (1, 0)
        self.move_timer = 0
        
        self.foods = []
        for _ in range(3):
            self._add_new_food()

    def _add_new_food(self):
        cols = settings.SCREEN_WIDTH // self.grid_size
        rows = settings.SCREEN_HEIGHT // self.grid_size
        while True:
            x = random.randint(0, cols - 1) * self.grid_size
            y = random.randint(0, rows - 1) * self.grid_size
            pos = (x, y)
            if pos not in self.snake and pos not in self.foods:
                self.foods.append(pos)
                break

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.direction = (1, 0)

    def update(self, dt):
        super().update(dt) 
        
        # 1. 倒计时
        if self.time_left > 0:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.is_time_up = True

        # 2. 动态速度
        # 基础速度减去 (当前分 * 加速系数)
        dynamic_speed = self.base_speed - (self.current_score * settings.SPEED_ACCELERATION)
        self.move_interval = max(settings.MIN_MOVE_INTERVAL, dynamic_speed)

        # 3. 移动
        self.move_timer += dt
        if self.move_timer > self.move_interval:
            self.move_snake()
            self.move_timer = 0

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        
        new_x = (head_x + dx * self.grid_size) % settings.SCREEN_WIDTH
        new_y = (head_y + dy * self.grid_size) % settings.SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # 撞到自己
        if new_head in self.snake:
            self.reset_game() 
            return

        self.snake.insert(0, new_head)
        
        # 吃到食物
        if new_head in self.foods:
            self.current_score += 1 
            
            # 【修改】实时更新最高分 (打破纪录时立即显示)
            if self.current_score > self.high_score:
                self.high_score = self.current_score
                
            self.foods.remove(new_head)
            self._add_new_food()
        else:
            self.snake.pop()

    def _get_neighbor_direction(self, current, target):
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        
        if dx > settings.SCREEN_WIDTH / 2: dx = -self.grid_size
        elif dx < -settings.SCREEN_WIDTH / 2: dx = self.grid_size
        if dy > settings.SCREEN_HEIGHT / 2: dy = -self.grid_size
        elif dy < -settings.SCREEN_HEIGHT / 2: dy = self.grid_size

        if dx != 0: dx = dx // abs(dx)
        if dy != 0: dy = dy // abs(dy)
        return (dx, dy)

    def draw_content(self, surface):
        # 1. 绘制苹果
        for food_pos in self.foods:
            if self.images_loaded: surface.blit(self.img_food, food_pos)
            else: pygame.draw.rect(surface, COLORS['red'], (*food_pos, self.grid_size, self.grid_size))

        # 2. 绘制蛇 (请把之前那个包含 Corner/Tail 完整逻辑的代码块贴在这里)
        # 这里为了演示方便，我放一个简化版，实际请务必使用你之前修复好的那个完整版本
        for i, segment in enumerate(self.snake):
            rect_pos = (segment[0], segment[1])
            
            if not self.images_loaded:
                pygame.draw.rect(surface, (0, 255, 0), (*segment, self.grid_size, self.grid_size))
                continue

            img_to_draw = None
            angle = 0
            
            # A. 头
            if i == 0:
                img_to_draw = self.img_head
                if len(self.snake) > 1:
                    neck = self.snake[1]
                    dx, dy = self._get_neighbor_direction(neck, segment)
                else:
                    dx, dy = self.direction
                
                if dx == 1: angle = 0
                elif dx == -1: angle = 180
                elif dy == 1: angle = 270
                elif dy == -1: angle = 90
            
            # B. 尾
            elif i == len(self.snake) - 1:
                # 如果有尾巴图片就用，没有就用身体
                img_to_draw = getattr(self, 'img_tail', self.img_body)
                prev = self.snake[i - 1]
                dx, dy = self._get_neighbor_direction(segment, prev)
                if dx == 1: angle = 0
                elif dx == -1: angle = 180
                elif dy == 1: angle = 270
                elif dy == -1: angle = 90

            # C. 身
            else:
                img_to_draw = self.img_body
                prev = self.snake[i - 1]
                next_seg = self.snake[i + 1]
                
                p_dir = self._get_neighbor_direction(segment, prev)
                n_dir = self._get_neighbor_direction(segment, next_seg)

                if p_dir[0] == n_dir[0] or p_dir[1] == n_dir[1]:
                    # 直身
                    if p_dir[0] != 0: angle = 0
                    else: angle = 90
                else:
                    # 拐弯 (如果有图片)
                    if hasattr(self, 'img_corner'):
                        img_to_draw = self.img_corner
                        dirs = {p_dir, n_dir}
                        if (-1, 0) in dirs and (0, -1) in dirs: angle = 0
                        elif (0, -1) in dirs and (1, 0) in dirs: angle = 270
                        elif (1, 0) in dirs and (0, 1) in dirs: angle = 180
                        elif (0, 1) in dirs and (-1, 0) in dirs: angle = 90
            
            if img_to_draw:
                rotated_img = pygame.transform.rotate(img_to_draw, angle)
                surface.blit(rotated_img, rect_pos)

        # 3. 绘制 UI
        self._draw_ui(surface)

    def _draw_ui(self, surface):
        seconds = int(self.time_left / 1000)
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"倒计时: {minutes:02}:{secs:02}"
        
        score_str = f"得分: {self.current_score}"
        # 最高分是本次会话的最高分
        high_str = f"最高: {self.high_score}"
        
        # 背景条
        s = pygame.Surface((settings.SCREEN_WIDTH, 40))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        surface.blit(s, (0,0))

        txt_time = self.font_ui.render(time_str, True, COLORS['white'])
        txt_score = self.font_ui.render(score_str, True, COLORS['white'])
        txt_high = self.font_ui.render(high_str, True, COLORS['yellow'])

        # 布局
        surface.blit(txt_score, (20, 10))
        surface.blit(txt_time, (settings.SCREEN_WIDTH // 2 - txt_time.get_width() // 2, 10))
        surface.blit(txt_high, (settings.SCREEN_WIDTH - 20 - txt_high.get_width(), 10))

        if self.is_time_up:
            msg = "训练完成！"
            msg_surf = self.font_msg.render(msg, True, COLORS['red'])
            msg_bg = self.font_msg.render(msg, True, COLORS['white'])
            
            cx = settings.SCREEN_WIDTH // 2
            cy = settings.SCREEN_HEIGHT // 2
            
            surface.blit(msg_bg, (cx - msg_surf.get_width()//2 + 2, cy - msg_surf.get_height()//2 + 2))
            surface.blit(msg_surf, (cx - msg_surf.get_width()//2, cy - msg_surf.get_height()//2))