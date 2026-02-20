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
# GAME_GRID_RATIO = 20 

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

CURSOR_CONFIG = {
    'enabled': True,       # 是否开启自定义光标
    'image': 'cursor.png', # 请将你的光标图片命名为 cursor.png 放入 assets/images/
    'size': (64, 64),      # 这里设置大小！(64, 64) 是现在的两倍大
    'hotspot': (0, 0),     # 热点位置：(0,0)是左上角。如果是瞄准镜，设为 (32,32) 居中
    
    # 如果找不到图片，系统会画一个默认的：
    'fallback_radius': 25,          # 默认光标半径
    'fallback_color': (255, 255, 0),# 默认颜色 (黄色)
    'fallback_outline': 3           # 黑色描边宽度
}

# --- 难度配置表 (只控制背景和速度) ---
DIFFICULTY_LEVELS = {
    'EASY':   {'bg_grid_size': 30, 'stripe_width': 30, 'snake_speed': 250, 'snake_size': 20, 'apple_amount': 3,
               'switch_interval': 5000, 'rotate_ratio': 1,'coin_rate': 2,
               'catch': {
                   'base_size': 400,
                    'min_size': 300,
                    'speed': 40,
                    'hp': 5,
                    'coin_per_hit': 0.3
                },
               'fruit': {
                    'spawn_interval': 1500, 
                    'speed_min': 18, 'speed_max': 22, 
                    'gravity': 0.25, 
                    'base_size': 200, 
                    'max_active': 3,
                    'coin_per_slice': 0.6
                }
               },
    'MEDIUM': {'bg_grid_size': 20, 'stripe_width': 10,  'snake_speed': 200, 'snake_size': 30, 'apple_amount': 4,
               'switch_interval': 5000, 'rotate_ratio': 1.5, 'coin_rate': 2,
               'catch': {
                   'base_size': 250,
                   'min_size': 150,
                   'speed': 80,
                   'hp': 8,
                   'coin_per_hit': 0.32
                },
               'fruit': {
                    'spawn_interval': 800, 
                    'speed_min': 20, 'speed_max': 25, 
                    'gravity': 0.3, 
                    'base_size': 150, 
                    'max_active': 5,
                    'coin_per_slice': 0.4
                }
               },
    'HARD':   {'bg_grid_size': 15,  'stripe_width': 5,  'snake_speed': 150, 'snake_size': 40, 'apple_amount': 6,
               'switch_interval': 5000, 'rotate_ratio': 2, 'coin_rate': 2,
               'catch': {
                   'base_size': 150,
                   'min_size': 100,
                   'speed': 100,
                   'hp': 10,
                   'coin_per_hit': 0.35
                },
               'fruit': {
                    'spawn_interval': 500, 
                    'speed_min': 20, 'speed_max': 25, 
                    'gravity': 0.35, 
                    'base_size': 100, 
                    'max_active': 8,
                    'coin_per_slice': 0.2
                }
               },
}

TRAINING_DURATION = 10 * 60  # 训练时长 (秒)
SPEED_ACCELERATION = 5       # 每吃一个苹果，蛇移动间隔减少多少毫秒
MIN_MOVE_INTERVAL = 40       # 速度上限

SUPABASE_URL = "https://ztljczelgprcymxwqywp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0bGpjemVsZ3ByY3lteHdxeXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwMDUyOTgsImV4cCI6MjA4NjU4MTI5OH0.3PdvN9-L8w4vKQqKRPNwun3VSN5L0Ef-wUbB21e5ToA"
PLAYER_NAME = "MyPlayer1"

PET_CONFIG = {
    # --- 时间流逝 ---
    'decay_interval': 3600,    # 结算周期：1小时
    
    # --- 核心衰减逻辑 ---
    'hunger_decay': 2.2,         # 饥饿：快 (24h = -72)
    'mood_decay': 5,           # 心情：中 (24h = -48)
    'health_decay_natural': 0.6,
    'health_decay_punish': 5,  # 健康：仅在生病/饥饿时扣除 (48h不理 = -96)
    
    'sick_chance': 0.05,       # 生病概率 (稍微提高，增加风险)
    'sick_threshold': 30,      # 健康低于50时，严重影响经验
    
    # --- 商店与物品 ---
    # 策略：饭是刚需(稍贵)，药是惩罚(极贵)，玩具是享受(便宜)
    'food_price': 50, 'food_effect': 25,
    'med_price': 200, 'med_effect': 25,   # 生病一次等于白玩一天贪吃蛇
    'toy_price': 20,  'toy_effect': 20,   # 便宜，靠频率刷
    
    # --- 互动点击 ---
    'click_mood_gain': 5,      # 每次点击增加的心情
    'click_exp_gain': 1,       # 点击也有微量经验
    'max_daily_click_exp': 50,
    
    # --- 经验获取 (受健康值修正) ---
    'exp_gain_food': 25,
    'exp_gain_med': 100,
    'exp_gain_toy': 10,
    
    # --- 升级系统 ---
    'max_level': 30,
    'base_pet_slots': 3,
    
    # --- 惩罚 ---
    'exp_decay_starve': 50,    # 饿肚子扣经验巨快
    'exp_decay_sick': 30,      # 生病扣经验
}

PET_SHOP_LIST = [
    {'id': 'cat_orange', 'name': '大橘猫', 'price': 0, 'img': 'pet_cat_orange.png'}, # 免费初始宠
    {'id': 'dog_husky',  'name': '哈士奇', 'price': 0, 'img': 'pet_dog_husky.png'},  # 免费初始宠
    {'id': 'cat_white',  'name': '波斯猫', 'price': 1000, 'img': 'pet_cat_white.png'},
    {'id': 'dog_shiba',  'name': '柴犬',   'price': 2500, 'img': 'pet_dog_shiba.png'},
    {'id': 'cat_black',  'name': '黑猫',   'price': 5000, 'img': 'pet_cat_black.png'},
]

def get_exp_needed(level):
    # 稍微平滑一点的曲线
    if level < 10: return 100
    elif level < 20: return 300
    else: return 800


CATCH_CONFIG = {
    'images': ['thief_1.png', 'thief_2.png', 'thief_3.png'],
    'sound_hit': 'hit.wav',   # 点击音效
    'sound_die': 'die.wav',   # 死亡音效 (可复用蛇的)
    'blink_speed': 5,         # 透明闪烁速度
}

FRUIT_CONFIG = {
    # 水果列表：ID, 图片名, 颜色(用于粒子特效)
    'fruits': [
        {'id': 'apple',      'img': 'fruit_apple.png',      'color': (200, 50, 50)},
        {'id': 'banana',     'img': 'fruit_banana.png',     'color': (255, 255, 0)},
        {'id': 'watermelon', 'img': 'fruit_watermelon.png', 'color': (50, 200, 50)},
        {'id': 'orange',     'img': 'fruit_orange.png',     'color': (255, 165, 0)},
    ],
    'bomb_img': 'fruit_bomb.png',
    'dragon_img': 'fruit_dragon.png',
    
    'sound_throw': 'throw.wav',  # 抛出声音
    'sound_splat': 'splat.wav',  # 切开声音
    'sound_boom': 'boom.wav',    # 炸弹声音
    'sound_bonus': 'bonus.wav',  # 火龙果连击声音
}