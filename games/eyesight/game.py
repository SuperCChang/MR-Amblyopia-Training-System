# games/eyesight/game.py
import pygame
import random
from core.base_game import BaseGame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, DIFFICULTY_LEVELS

class EyesightGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        self.current_level = 0 # 当前正在测试的难度等级 (0-9)
        self.mistakes_in_row = 0 # 当前等级连续错误次数
        self.max_mistakes = 3    # 容错阈值
        
        self.reset_round()

    def reset_round(self):
        """生成新的 E"""
        self.current_dir = random.choice(self.directions)
        
        # 根据当前等级获取字体大小
        size = DIFFICULTY_LEVELS[self.current_level]['font_size']
        self.font = pygame.font.SysFont("arial", size, bold=True)

    def handle_input(self, event):
        # 不调用 super().handle_input，屏蔽背景切换和ESC
        if event.type == pygame.KEYDOWN:
            input_dir = None
            if event.key == pygame.K_UP: input_dir = 'UP'
            elif event.key == pygame.K_DOWN: input_dir = 'DOWN'
            elif event.key == pygame.K_LEFT: input_dir = 'LEFT'
            elif event.key == pygame.K_RIGHT: input_dir = 'RIGHT'
            
            if input_dir:
                self.check_answer(input_dir)

    def check_answer(self, input_dir):
        if input_dir == self.current_dir:
            # --- 答对了 ---
            self.mistakes_in_row = 0 # 清空连续错误
            
            # 如果不是最后一级，则升级
            if self.current_level < len(DIFFICULTY_LEVELS) - 1:
                self.current_level += 1
                self.reset_round()
            else:
                # 通关了 (达到最高级)
                self.finish_test(final_level=self.current_level)
        else:
            # --- 答错了 ---
            self.mistakes_in_row += 1
            print(f"Wrong! Mistakes in a row: {self.mistakes_in_row}")
            
            if self.mistakes_in_row >= self.max_mistakes:
                # 连续错3次，游戏结束
                # 难度定级为：当前等级 - 1 (因为当前等级没过)
                # 如果第0级就挂了，那就只能是0级
                final = max(0, self.current_level - 1)
                self.finish_test(final_level=final)
            else:
                # 还有机会，刷新一个方向重试当前等级
                self.reset_round()

    def finish_test(self, final_level):
        print(f"Test Finished. Difficulty set to Level: {final_level}")
        self.app.difficulty = final_level
        self.app.change_scene('menu')

    def draw(self, surface):
        # 强制纯白背景
        surface.fill(COLORS['white'])
        
        # 绘制中心 E
        text_surf = self.font.render("E", True, COLORS['black'])
        
        # 旋转
        angle = 0
        if self.current_dir == 'UP': angle = 90
        elif self.current_dir == 'LEFT': angle = 180
        elif self.current_dir == 'DOWN': angle = 270
        
        rotated_surf = pygame.transform.rotate(text_surf, angle)
        rect = rotated_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(rotated_surf, rect)

        # 绘制UI提示
        info_font = pygame.font.SysFont("arial", 20)
        status = f"Level: {self.current_level} | Mistakes: {self.mistakes_in_row}/{self.max_mistakes}"
        surface.blit(info_font.render(status, True, COLORS['black']), (10, 10))