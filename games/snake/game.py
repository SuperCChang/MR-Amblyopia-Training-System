import pygame
import random
import os
import math
from core.base_game import BaseGame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, DIFFICULTY_LEVELS

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
            self.raw_tail = pygame.image.load(os.path.join(img_dir, 'snake_tail.png')).convert_alpha() # 新增蛇尾
            self.raw_food = pygame.image.load(os.path.join(img_dir, 'apple.png')).convert_alpha()
            
            self.images_loaded = True
            print("Snake images loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load images. Using fallback rectangles. Error: {e}")
            self.images_loaded = False

        self.reset_game()

    def reset_game(self):
        diff_index = self.app.difficulty
        settings = DIFFICULTY_LEVELS[diff_index]
        
        self.grid_size = settings['grid_size']
        self.move_interval = settings['snake_speed']
        
        # --- 图片缩放 ---
        if self.images_loaded:
            self.img_head = pygame.transform.scale(self.raw_head, (self.grid_size, self.grid_size))
            self.img_body = pygame.transform.scale(self.raw_body, (self.grid_size, self.grid_size))
            self.img_tail = pygame.transform.scale(self.raw_tail, (self.grid_size, self.grid_size))
            self.img_food = pygame.transform.scale(self.raw_food, (self.grid_size, self.grid_size))

        # 初始化蛇
        start_x = (SCREEN_WIDTH // self.grid_size // 2) * self.grid_size
        start_y = (SCREEN_HEIGHT // self.grid_size // 2) * self.grid_size
        
        # 初始长度至少为3，才能明显看到头、身、尾
        self.snake = [
            (start_x, start_y),
            (start_x - self.grid_size, start_y),
            (start_x - 2 * self.grid_size, start_y)
        ]
        self.direction = (1, 0)
        self.score = 0
        self.move_timer = 0
        
        # 3 个苹果
        self.foods = []
        for _ in range(3):
            self._add_new_food()

    def _add_new_food(self):
        cols = SCREEN_WIDTH // self.grid_size
        rows = SCREEN_HEIGHT // self.grid_size
        while True:
            x = random.randint(0, cols - 1) * self.grid_size
            y = random.randint(0, rows - 1) * self.grid_size
            pos = (x, y)
            if pos not in self.snake and pos not in self.foods:
                self.foods.append(pos)
                break

    def update(self, dt):
        super().update(dt)
        self.move_timer += dt
        if self.move_timer > self.move_interval:
            self.move_snake()
            self.move_timer = 0

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        
        new_x = (head_x + dx * self.grid_size) % SCREEN_WIDTH
        new_y = (head_y + dy * self.grid_size) % SCREEN_HEIGHT
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

    def _get_rotation(self, current_pos, prev_pos):
        """
        计算图片的旋转角度。
        Pygame 旋转是逆时针的。
        假设图片默认是朝右的 (Right)。
        """
        dx = current_pos[0] - prev_pos[0]
        dy = current_pos[1] - prev_pos[1]
        
        # 处理穿墙情况 (例如从左边穿到右边，dx 会很大)
        if dx > self.grid_size: dx = -self.grid_size # 实际是向左走
        elif dx < -self.grid_size: dx = self.grid_size # 实际是向右走
        if dy > self.grid_size: dy = -self.grid_size
        elif dy < -self.grid_size: dy = self.grid_size

        if dx > 0: return 0      # Right
        if dx < 0: return 180    # Left
        if dy > 0: return 270    # Down
        if dy < 0: return 90     # Up
        return 0

    def draw_content(self, surface):
        # --- 画苹果 ---
        for food_pos in self.foods:
            if self.images_loaded:
                surface.blit(self.img_food, food_pos)
            else:
                pygame.draw.rect(surface, COLORS['red'], (*food_pos, self.grid_size, self.grid_size))

        # --- 画蛇 ---
        for i, segment in enumerate(self.snake):
            if self.images_loaded:
                img_to_draw = self.img_body
                angle = 0
                
                # 1. 蛇头
                if i == 0:
                    img_to_draw = self.img_head
                    # 计算头的角度：根据现在的移动方向 (self.direction)
                    dx, dy = self.direction
                    if dx == 1: angle = 0
                    elif dx == -1: angle = 180
                    elif dy == 1: angle = 270
                    elif dy == -1: angle = 90
                
                # 2. 蛇尾
                elif i == len(self.snake) - 1:
                    img_to_draw = self.img_tail
                    # 计算尾巴的角度：看倒数第二节在哪里
                    prev_segment = self.snake[i - 1]
                    # 尾巴应该指向倒数第二节
                    angle = self._get_rotation(prev_segment, segment)
                
                # 3. 蛇身 (为了简单，蛇身暂时不旋转，或者你可以画圆形的蛇身)
                else:
                    img_to_draw = self.img_body
                
                # 旋转并绘制
                # 注意：transform.rotate 可能会稍微改变 rect 大小，最好重新获取 rect
                rotated_img = pygame.transform.rotate(img_to_draw, angle)
                # 简单的 blit 可能会有位置偏移，这里我们直接 blit 到左上角，
                # 因为我们的图片是正方形且旋转90度倍数，大小不会变。
                surface.blit(rotated_img, segment)
                
            else:
                # 备用方块绘制
                color = (0, 255, 0)
                if i == 0: color = (0, 200, 0)
                elif i == len(self.snake) - 1: color = (0, 150, 0)
                
                pygame.draw.rect(surface, color, (*segment, self.grid_size, self.grid_size))
                pygame.draw.rect(surface, COLORS['bg_solid'], (*segment, self.grid_size, self.grid_size), 1)