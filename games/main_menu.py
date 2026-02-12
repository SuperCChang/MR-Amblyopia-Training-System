# games/main_menu.py
import pygame
from core.base_game import BaseGame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu(BaseGame):
    def __init__(self, app):
        # 必须调用父类的初始化，这样才有 self.bg_mode
        super().__init__(app)
        self.font = pygame.font.SysFont("arial", 40)
        self.title_text = "GAME COLLECTION"
        self.sub_text = "Press 1 for Snake | Press TAB for BG"

    # 注意：我们这里没有写 handle_input，
    # 但因为继承了 BaseGame，所以按 TAB 依然能切换背景！

    def handle_input(self, event):
        # 1. 别忘了先调用父类，保持菜单也能切背景！
        super().handle_input(event)

        if event.type == pygame.KEYDOWN:
            # 按 '1' 进入贪吃蛇
            if event.key == pygame.K_1:
                self.app.change_scene('snake')

    def update(self, dt):
        super().update(dt)

    def draw_content(self, surface):
        # 只画文字，背景已经在父类 draw() 里画好了
        
        # 1. 画标题
        title = self.font.render(self.title_text, True, COLORS['white'])
        # 居中显示
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(title, rect)

        # 2. 画提示
        sub = pygame.font.SysFont("arial", 20).render(self.sub_text, True, COLORS['text'])
        sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(sub, sub_rect)
    