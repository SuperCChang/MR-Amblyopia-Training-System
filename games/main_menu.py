# games/main_menu.py
import pygame, os
from core.base_game import BaseGame
from core.ui import Button
import settings
from settings import COLORS
from core.data_manager import DataManager
from core.path_utils import resource_path

class MainMenu(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.font_title = pygame.font.SysFont("simhei", 60, bold=True)
        self.font_btn = pygame.font.SysFont("simhei", 30)

        # 放置在右下角
        self.checkbox_rect = pygame.Rect(settings.SCREEN_WIDTH - 280, settings.SCREEN_HEIGHT - 60, 30, 30)
        # 初始化全局变量（如果还没设置过的话）
        if not hasattr(settings, 'ENABLE_CIRCLE_BG'):
            settings.ENABLE_CIRCLE_BG = False
        
        # 状态机：ROOT, SNAKE_DIFF, CATCH_DIFF, FRUIT_DIFF, PIGEON_DIFF
        self.menu_state = 'ROOT' 
        self.init_buttons()
        self.bg_image = None
        self._load_bg()
    
    def on_enter(self):
        default_speed = getattr(settings, 'MENU_BG_SPEED', 20)
        self.set_bg_speed(default_speed)
        self.menu_state = 'ROOT'

    def _load_bg(self):
        try:
            path = resource_path(os.path.join('assets', 'images', 'menu_bg.png'))
            if os.path.exists(path):
                raw = pygame.image.load(path).convert()
                self.bg_image = pygame.transform.scale(raw, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except: pass

    def init_buttons(self):
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        w, h = 260, 60
        gap = 75 # 稍微紧凑一点，因为按钮变多了
        
        self.title_y = cy - 240
        start_y = cy - 120
        
        # --- 1. 主菜单 (ROOT) ---
        self.btns_root = [
            Button(cx - w//2, start_y, w, h, "贪吃蛇", self.font_btn, bg_color=COLORS['blue']),
            Button(cx - w//2, start_y + gap, w, h, "抓小偷", self.font_btn, bg_color=COLORS['red']),
            Button(cx - w//2, start_y + gap*2, w, h, "切水果", self.font_btn, bg_color=(255, 140, 0)),
            Button(cx - w//2, start_y + gap*3, w, h, "疯狂鸽子", self.font_btn, bg_color=COLORS['yellow']),
            Button(cx - w//2, start_y + gap*4, w, h, "宠物乐园", self.font_btn, bg_color=COLORS['green']),
            Button(cx - w//2, start_y + gap*5, w, h, "退出系统", self.font_btn, bg_color=COLORS['grey'])
        ]
        
        # --- 难度选择按钮生成器 ---
        def create_diff_btns(y_start):
            return [
                Button(cx - w//2, y_start, w, h, "新手", self.font_btn, bg_color=COLORS['green']),
                Button(cx - w//2, y_start + gap, w, h, "熟手", self.font_btn, bg_color=COLORS['yellow']),
                Button(cx - w//2, y_start + gap*2, w, h, "高手", self.font_btn, bg_color=COLORS['red']),
                Button(cx - w//2, y_start + gap*3, w, h, "返回上一级", self.font_btn, bg_color=COLORS['grey'])
            ]

        self.btns_snake_diff = create_diff_btns(cy - 60)
        self.btns_catch_diff = create_diff_btns(cy - 60)
        self.btns_fruit_diff = create_diff_btns(cy - 60)
        self.btns_pigeon_diff = create_diff_btns(cy - 60)

    def handle_input(self, event):
        # 1. 确定当前按钮组
        current_btns = []
        if self.menu_state == 'ROOT': current_btns = self.btns_root
        elif self.menu_state == 'SNAKE_DIFF': current_btns = self.btns_snake_diff
        elif self.menu_state == 'CATCH_DIFF': current_btns = self.btns_catch_diff
        elif self.menu_state == 'FRUIT_DIFF': current_btns = self.btns_fruit_diff
        elif self.menu_state == 'PIGEON_DIFF': current_btns = self.btns_pigeon_diff
        
        # 2. 悬停
        if event.type == pygame.MOUSEMOTION:
            for btn in current_btns: btn.check_hover(event.pos)
                
        # 3. 点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_state == 'ROOT':
                if self.btns_root[0].is_clicked(event): self.menu_state = 'SNAKE_DIFF'; pygame.event.clear()
                elif self.btns_root[1].is_clicked(event): self.menu_state = 'CATCH_DIFF'; pygame.event.clear()
                elif self.btns_root[2].is_clicked(event): self.menu_state = 'FRUIT_DIFF'; pygame.event.clear()
                elif self.btns_root[3].is_clicked(event): self.menu_state = 'PIGEON_DIFF'; pygame.event.clear()
                elif self.btns_root[4].is_clicked(event): self.app.change_scene('pet')
                elif self.btns_root[5].is_clicked(event): self.app.is_running = False
                elif self.checkbox_rect.collidepoint(event.pos):
                    # 翻转勾选状态
                    settings.ENABLE_CIRCLE_BG = not getattr(settings, 'ENABLE_CIRCLE_BG', False)

            elif self.menu_state == 'SNAKE_DIFF': self._handle_diff(event, self.btns_snake_diff, 'snake')
            elif self.menu_state == 'CATCH_DIFF': self._handle_diff(event, self.btns_catch_diff, 'catch')
            elif self.menu_state == 'FRUIT_DIFF': self._handle_diff(event, self.btns_fruit_diff, 'fruit')
            # 【修复 BUG】这里之前误传了 self.btns_fruit_diff，已修正为 self.btns_pigeon_diff
            elif self.menu_state == 'PIGEON_DIFF': self._handle_diff(event, self.btns_pigeon_diff, 'pigeon')

    def _handle_diff(self, event, btns, scene_name):
        if btns[0].is_clicked(event): self._start_game(scene_name, 'EASY')
        elif btns[1].is_clicked(event): self._start_game(scene_name, 'MEDIUM')
        elif btns[2].is_clicked(event): self._start_game(scene_name, 'HARD')
        elif btns[3].is_clicked(event): self.menu_state = 'ROOT'

    def _start_game(self, scene_name, difficulty):
        self.app.difficulty = difficulty
        self.app.change_scene(scene_name)

    def draw(self, surface):
        if self.bg_image: surface.blit(self.bg_image, (0, 0))
        else: surface.fill(COLORS['menu_bg']); super().draw(surface)

        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(50); mask.fill((0,0,0)); surface.blit(mask, (0,0))

        # 顶部栏
        top_bar = pygame.Surface((settings.SCREEN_WIDTH, 60))
        top_bar.set_alpha(150); top_bar.fill((0,0,0)); surface.blit(top_bar, (0,0))
        
        coins = DataManager().get_coins()
        coin_surf = self.font_btn.render(f"金币: {coins:.1f}", True, COLORS['yellow']) # 保留1位小数
        surface.blit(coin_surf, (settings.SCREEN_WIDTH - 200, 15))

        # 标题与按钮
        current_title = ""
        current_btns = []
        if self.menu_state == 'ROOT': current_title = "综合视觉训练系统"; current_btns = self.btns_root
        elif self.menu_state == 'SNAKE_DIFF': current_title = "贪吃蛇 - 选择难度"; current_btns = self.btns_snake_diff
        elif self.menu_state == 'CATCH_DIFF': current_title = "抓小偷 - 选择难度"; current_btns = self.btns_catch_diff
        elif self.menu_state == 'FRUIT_DIFF': current_title = "切水果 - 选择难度"; current_btns = self.btns_fruit_diff
        elif self.menu_state == 'PIGEON_DIFF': current_title = "疯狂鸽子 - 选择难度"; current_btns = self.btns_pigeon_diff

        cx = settings.SCREEN_WIDTH // 2
        title_img = self.font_title.render(current_title, True, COLORS['white'])
        shadow_img = self.font_title.render(current_title, True, (0,0,0))
        title_rect = title_img.get_rect(center=(cx, self.title_y))
        surface.blit(shadow_img, (title_rect.x+2, title_rect.y+2))
        surface.blit(title_img, title_rect)
        
        for btn in current_btns: btn.draw(surface)

        # --- 【新增】在 ROOT 状态下绘制复选框 ---
        if self.menu_state == 'ROOT':
            # 画外框
            pygame.draw.rect(surface, COLORS['white'], self.checkbox_rect, 2)
            # 如果勾选了，画内部的绿色实心块
            if getattr(settings, 'ENABLE_CIRCLE_BG', False):
                inner_rect = self.checkbox_rect.inflate(-10, -10)
                pygame.draw.rect(surface, COLORS['green'], inner_rect)
            
            # 绘制文字标签
            lbl_surf = self.font_btn.render("黑圆闪烁", True, COLORS['white'])
            surface.blit(lbl_surf, (self.checkbox_rect.right + 10, self.checkbox_rect.centery - lbl_surf.get_height() // 2))