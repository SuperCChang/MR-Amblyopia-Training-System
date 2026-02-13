import pygame
import random
import os
import settings
from core.base_game import BaseGame
from settings import COLORS, DIFFICULTY_LEVELS, GAME_GRID_RATIO

class SnakeGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        
        # --- 1. 加载图片资源 ---
        self.images_loaded = False
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            img_dir = os.path.join(base_path, 'assets', 'images')
            
            # 加载并处理透明度
            # 假设你的图片是白底，使用 set_colorkey 去除白色背景 (255, 255, 255)
            # 如果是透明PNG，convert_alpha() 就足够了，不需要 set_colorkey
            
            self.raw_head = pygame.image.load(os.path.join(img_dir, 'snake_head.png')).convert_alpha()
            self.raw_body = pygame.image.load(os.path.join(img_dir, 'snake_body.png')).convert_alpha()
            self.raw_corner = pygame.image.load(os.path.join(img_dir, 'snake_corner.png')).convert_alpha()
            self.raw_tail = pygame.image.load(os.path.join(img_dir, 'snake_tail.png')).convert_alpha() # 新增蛇尾
            self.raw_food = pygame.image.load(os.path.join(img_dir, 'apple.png')).convert_alpha()
            
            self.images_loaded = True
            print("Snake images loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load images. Using fallback rectangles. Error: {e}")
            self.images_loaded = False

        self.reset_game()

    def reset_game(self):
        # 1. 获取选定的难度配置
        # self.app.difficulty 现在是字符串 'EASY', 'MEDIUM' 等
        diff_key = self.app.difficulty 
        diff_settings = DIFFICULTY_LEVELS[diff_key]
        
        # 2. 设置移动速度 (由难度决定)
        self.move_interval = diff_settings['snake_speed']
        
        # 3. 【核心修改】计算游戏网格大小 (由屏幕大小决定)
        # 这样无论分辨率是多少，蛇相对于屏幕的比例是固定的
        self.grid_size = settings.SCREEN_WIDTH // GAME_GRID_RATIO
        
        # 确保 grid_size 至少是 20，防止过小
        self.grid_size = max(20, self.grid_size)

        print(f"Game Grid Size: {self.grid_size}px (Screen: {settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT})")

        # --- 图片缩放 (代码逻辑不变，但使用的是新计算的 self.grid_size) ---
        if self.images_loaded:
            self.img_head = pygame.transform.scale(self.raw_head, (self.grid_size, self.grid_size))
            self.img_body = pygame.transform.scale(self.raw_body, (self.grid_size, self.grid_size))
            if hasattr(self, 'raw_tail'):
                self.img_tail = pygame.transform.scale(self.raw_tail, (self.grid_size, self.grid_size))
            if hasattr(self, 'raw_corner'):
                self.img_corner = pygame.transform.scale(self.raw_corner, (self.grid_size, self.grid_size))
            self.img_food = pygame.transform.scale(self.raw_food, (self.grid_size, self.grid_size))

        # --- 初始位置 (使用 settings.SCREEN_WIDTH) ---
        start_x = (settings.SCREEN_WIDTH // self.grid_size // 2) * self.grid_size
        start_y = (settings.SCREEN_HEIGHT // self.grid_size // 2) * self.grid_size
        
        self.snake = [
            (start_x, start_y),
            (start_x - self.grid_size, start_y),
            (start_x - 2 * self.grid_size, start_y)
        ]
        self.direction = (1, 0)
        self.score = 0
        self.move_timer = 0
        
        self.foods = []
        for _ in range(3):
            self._add_new_food()

    def _add_new_food(self):
        cols = settings.SCREEN_WIDTH // self.grid_size
        rows = settings.SCREEN_HEIGHT // self.grid_size
        while True:
            x = random.randint(0, cols - 1) * self.game_grid_size
            y = random.randint(0, rows - 1) * self.game_grid_size
            pos = (x, y)
            if pos not in self.snake and pos not in self.foods:
                self.foods.append(pos)
                break
    
    def handle_input(self, event):
        # 1. 必须调用父类，否则 TAB 和 ESC 会失效
        super().handle_input(event)

        # 2. 监听方向键
        if event.type == pygame.KEYDOWN:
            # 防止 180 度掉头逻辑：
            # 如果当前向右 (1, 0)，就不能按左 (-1, 0)
            # 如果当前向下 (0, 1)，就不能按上 (0, -1)
            
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

        if new_head in self.snake:
            self.reset_game()
            return

        self.snake.insert(0, new_head)
        
        if new_head in self.foods:
            self.score += 1
            self.foods.remove(new_head)
            self._add_new_food()
        else:
            self.snake.pop()
    
    def _get_neighbor_direction(self, current, target):
        """
        计算 target 相对于 current 的方向。
        返回 (dx, dy)，值只可能是 -1, 0, 1
        处理了穿墙的情况。
        """
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        
        # 处理 X 轴穿墙
        # 如果距离超过半个屏幕，说明发生了穿墙，实际方向是反的
        if dx > SCREEN_WIDTH / 2: dx = -self.game_grid_size
        elif dx < -SCREEN_WIDTH / 2: dx = self.game_grid_size
        
        # 处理 Y 轴穿墙
        if dy > SCREEN_HEIGHT / 2: dy = -self.game_grid_size
        elif dy < -SCREEN_HEIGHT / 2: dy = self.game_grid_size

        # 归一化为 (1, 0, -1)
        if dx != 0: dx = dx // abs(dx)
        if dy != 0: dy = dy // abs(dy)
        
        return (dx, dy)
    
    def _get_rotation(self, current_pos, prev_pos):
        """
        计算图片的旋转角度。
        Pygame 旋转是逆时针的。
        假设图片默认是朝右的 (Right)。
        """
        dx = current_pos[0] - prev_pos[0]
        dy = current_pos[1] - prev_pos[1]
        
        # 处理穿墙情况 (例如从左边穿到右边，dx 会很大)
        if dx > self.game_grid_size: dx = -self.game_grid_size # 实际是向左走
        elif dx < -self.game_grid_size: dx = self.game_grid_size # 实际是向右走
        if dy > self.game_grid_size: dy = -self.game_grid_size
        elif dy < -self.game_grid_size: dy = self.game_grid_size

        if dx > 0: return 0      # Right
        if dx < 0: return 180    # Left
        if dy > 0: return 270    # Down
        if dy < 0: return 90     # Up
        return 0

    def draw_content(self, surface):
        # 1. 画苹果
        for food_pos in self.foods:
            if self.images_loaded:
                surface.blit(self.img_food, food_pos)
            else:
                pygame.draw.rect(surface, COLORS['red'], (*food_pos, self.game_grid_size, self.game_grid_size))

        # 2. 画蛇
        for i, segment in enumerate(self.snake):
            rect_pos = (segment[0], segment[1])
            
            if not self.images_loaded:
                # 备用方块绘制
                color = (0, 255, 0)
                if i == 0: color = (0, 200, 0)
                pygame.draw.rect(surface, color, (*segment, self.game_grid_size, self.game_grid_size))
                continue

            # --- 图片绘制逻辑 ---
            img_to_draw = None  # 初始化为空
            angle = 0
            
            # A. 蛇头 (Head)
            if i == 0:
                img_to_draw = self.img_head
                # 计算头部的朝向
                if len(self.snake) > 1:
                    neck = self.snake[1]
                    dx, dy = self._get_neighbor_direction(neck, segment)
                else:
                    dx, dy = self.direction
                
                if dx == 1: angle = 0
                elif dx == -1: angle = 180
                elif dy == 1: angle = 270
                elif dy == -1: angle = 90

            # B. 蛇尾 (Tail)
            elif i == len(self.snake) - 1:
                img_to_draw = self.img_tail
                prev = self.snake[i - 1]
                dx, dy = self._get_neighbor_direction(segment, prev)
                if dx == 1: angle = 0
                elif dx == -1: angle = 180
                elif dy == 1: angle = 270
                elif dy == -1: angle = 90

            # C. 蛇身 (Body)
            else:
                # 【修复】先给一个默认值，防止后面逻辑漏掉赋值
                img_to_draw = self.img_body 
                
                prev = self.snake[i - 1]
                next_seg = self.snake[i + 1]
                
                p_dir = self._get_neighbor_direction(segment, prev)
                n_dir = self._get_neighbor_direction(segment, next_seg)

                # 判断是否是直身
                if p_dir[0] == n_dir[0] or p_dir[1] == n_dir[1]:
                    img_to_draw = self.img_body
                    if p_dir[0] != 0: angle = 0
                    else: angle = 90
                else:
                    # 拐弯逻辑
                    # 检查是否加载了 corner 图片，如果没有，就回退到 body
                    if hasattr(self, 'img_corner'):
                        img_to_draw = self.img_corner
                        
                        # 计算拐弯角度
                        dirs = {p_dir, n_dir}
                        # 连接 左(-1,0) 和 上(0,-1) -> 默认角度0 (假设素材是左上的拐角)
                        if (-1, 0) in dirs and (0, -1) in dirs: angle = 0
                        elif (0, -1) in dirs and (1, 0) in dirs: angle = 270
                        elif (1, 0) in dirs and (0, 1) in dirs: angle = 180
                        elif (0, 1) in dirs and (-1, 0) in dirs: angle = 90
                    else:
                        # 如果还没做 corner 图片，就用 body 凑合
                        img_to_draw = self.img_body

            # 【修复】安全检查：只有当图片不为空时才旋转和绘制
            if img_to_draw is not None:
                rotated_img = pygame.transform.rotate(img_to_draw, angle)
                surface.blit(rotated_img, rect_pos)