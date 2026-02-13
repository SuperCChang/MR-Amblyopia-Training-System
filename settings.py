# settings.py
import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "明润弱视训练系统"

# 颜色定义
COLORS = {
    'bg_solid': (30, 30, 30),
    'line': (70, 70, 70),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'yellow': (255, 255, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'text': (200, 200, 200)
}

# --- 难度配置表 (0-9级，共10级) ---
# 这是一个列表，索引就是难度等级。
# 我们可以任意调整数值，确保 bg_grid_size 是 SCREEN_WIDTH(800) 的约数，防止画出半个格子。
# 800 的约数: 200, 160, 100, 80, 50, 40, 25, 20
DIFFICULTY_LEVELS = [
    # Level 0 (最简单): 超大字，网格巨大，蛇很慢，线条很细
    {'font_size': 300, 'bg_grid_size': 50, 'stripe_width': 40, 'snake_speed': 300, 'game_grid_size': 80},
    # Level 1
    {'font_size': 260, 'bg_bg_grid_size': 40,  'stripe_width': 35, 'snake_speed': 250, 'game_grid_size': 80},
    # Level 2
    {'font_size': 220, 'bg_grid_size': 30,  'stripe_width': 30, 'snake_speed': 200, 'game_grid_size': 80},
    """# Level 3
    {'font_size': 180, 'bg_grid_size': 50,  'stripe_width': 15, 'snake_speed': 160},
    # Level 4
    {'font_size': 140, 'bg_grid_size': 50,  'stripe_width': 10, 'snake_speed': 130},
    # Level 5
    {'font_size': 100, 'bg_grid_size': 40,  'stripe_width': 8, 'snake_speed': 100},
    # Level 6
    {'font_size': 80,  'bg_grid_size': 40,  'stripe_width': 6, 'snake_speed': 80},
    # Level 7
    {'font_size': 60,  'bg_grid_size': 25,  'stripe_width': 5,'snake_speed': 60},
    # Level 8
    {'font_size': 40,  'bg_grid_size': 25,  'stripe_width': 3,'snake_speed': 50},
    # Level 9 (地狱): 字超小，网格超密，蛇极快，背景线条巨粗(干扰视线)
    {'font_size': 20,  'bg_grid_size': 20,  'stripe_width': 2,'snake_speed': 40},"""
]