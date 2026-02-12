# games/snake/game.py
import pygame
import random
from core.base_game import BaseGame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, DIFFICULTY_LEVELS

class SnakeGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.reset_game()

    def reset_game(self):
        """重置游戏，同时读取最新的难度配置"""
        diff_index = self.app.difficulty
        settings = DIFFICULTY_LEVELS[diff_index]
        
        # --- 核心：从难度配置读取参数 ---
        self.grid_size = settings['grid_size']   # 决定蛇的大小
        self.move_interval = settings['snake_speed'] # 决定蛇的速度
        
        # 初始化蛇的位置 (确保对齐新的网格)
        start_x = (SCREEN_WIDTH // self.grid_size // 2) * self.grid_size
        start_y = (SCREEN_HEIGHT // self.grid_size // 2) * self.grid_size
        
        self.snake = [
            (start_x, start_y),
            (start_x - self.grid_size, start_y),
            (start_x - 2*self.grid_size, start_y)
        ]
        self.direction = (1, 0)
        self.score = 0
        self.food = self._get_random_food()
        
        self.move_timer = pygame.time.get_ticks()

    def _get_random_food(self):
        cols = SCREEN_WIDTH // self.grid_size
        rows = SCREEN_HEIGHT // self.grid_size
        x = random.randint(0, cols - 1) * self.grid_size
        y = random.randint(0, rows - 1) * self.grid_size
        return (x, y)

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

    def update(self):
        super().update() # 别忘了背景计时
        
        current_time = pygame.time.get_ticks()
        if current_time - self.move_timer > self.move_interval:
            self.move_snake()
            self.move_timer = current_time

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        
        # 使用当前的 grid_size 计算
        new_head = (head_x + dx * self.grid_size, head_y + dy * self.grid_size)

        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in self.snake):
            self.reset_game()
            return

        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 1
            self.food = self._get_random_food()
        else:
            self.snake.pop()

    def draw_content(self, surface):
        # 画食物
        pygame.draw.rect(surface, COLORS['red'], (*self.food, self.grid_size, self.grid_size))
        
        # 画蛇
        for segment in self.snake:
            pygame.draw.rect(surface, COLORS['green'], (*segment, self.grid_size, self.grid_size))
            # 蛇身描边
            pygame.draw.rect(surface, COLORS['bg_solid'], (*segment, self.grid_size, self.grid_size), 1)