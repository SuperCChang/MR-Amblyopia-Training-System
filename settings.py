# settings.py
import pygame

# --- 屏幕设置 ---
# 设置为 (0, 0) 配合 FULLSCREEN 可以自适应分辨率
# 但我们需要在 main.py 里动态更新这两个值，供其他模块使用
SCREEN_WIDTH = 0  
SCREEN_HEIGHT = 0
FPS = 60
WINDOW_TITLE = "Python Game Collection"

# --- 游戏参数 ---
# 蛇的大小 = 屏幕宽度 / 这个比例
# 例如屏幕宽 1920，比例 40，那么蛇就是 48px
GAME_GRID_RATIO = 20 

# --- 颜色定义 ---
COLORS = {
    'bg_solid': (30, 30, 30),
    'menu_bg': (40, 44, 52), # 独立的菜单背景色
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'yellow': (255, 255, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'grey': (100, 100, 100)
}

# --- 难度配置表 (只控制背景和速度) ---
DIFFICULTY_LEVELS = {
    'EASY':   {'bg_grid_size': 30, 'stripe_width': 30, 'snake_speed': 250, 'snake_size': 10},
    'MEDIUM': {'bg_grid_size': 20, 'stripe_width': 20,  'snake_speed': 150, 'snake_size': 15},
    'HARD':   {'bg_grid_size': 15,  'stripe_width': 10,  'snake_speed': 80, 'snake_size': 20},
}

TRAINING_DURATION = 10 * 60  # 训练时长 (秒)
SPEED_ACCELERATION = 5       # 每吃一个苹果，蛇移动间隔减少多少毫秒
MIN_MOVE_INTERVAL = 40       # 速度上限

SUPABASE_URL = "https://ztljczelgprcymxwqywp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0bGpjemVsZ3ByY3lteHdxeXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwMDUyOTgsImV4cCI6MjA4NjU4MTI5OH0.3PdvN9-L8w4vKQqKRPNwun3VSN5L0Ef-wUbB21e5ToA"
PLAYER_NAME = "MyPlayer1"