# games/pet/scene.py (调试防闪退版)
import pygame
from core.base_game import BaseGame
from core.ui import Button
from core.data_manager import DataManager
from games.pet.pet_entity import PetEntity
import settings
from settings import COLORS

class PetScene(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.dm = DataManager()
        self.font = pygame.font.SysFont("simhei", 24)
        self.font_title = pygame.font.SysFont("simhei", 40, bold=True)
        
        # 初始为空，等待 on_enter 填充
        self.pet_data = None 
        self.pet_type = None
        
        self.pet_entity = None
        self.buttons = []
        
        self.msg = ""
        self.msg_timer = 0
        print("PetScene: 初始化完成")

    def on_enter(self):
        """进入场景时刷新数据"""
        print("PetScene: 进入场景 (on_enter)")
        try:
            # 1. 获取数据
            self.pet_data = self.dm.get_pet()
            self.pet_type = self.pet_data.get('type')
            print(f"PetScene: 获取到宠物数据 type={self.pet_type}")
            
            # 2. 初始化 UI
            self._init_ui()
            print("PetScene: UI 初始化成功")
            
        except Exception as e:
            print(f"CRITICAL ERROR in PetScene.on_enter: {e}")
            import traceback
            traceback.print_exc()

    def _init_ui(self):
        print("PetScene: 开始构建 UI...")
        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2
        
        self.buttons = []
        
        # 检查配置是否存在 (防止闪退)
        if not hasattr(settings, 'PET_CONFIG'):
            print("ERROR: settings.py 缺少 PET_CONFIG！请检查代码！")
            return

        # --- A. 未领养 ---
        if not self.pet_type:
            self.btn_adopt_cat = Button(cx - 160, cy, 140, 60, "领养猫咪", self.font, bg_color=COLORS['yellow'])
            self.btn_adopt_dog = Button(cx + 20, cy, 140, 60, "领养狗狗", self.font, bg_color=COLORS['blue'])
            self.buttons = [self.btn_adopt_cat, self.btn_adopt_dog]
            
        # --- B. 已领养 ---
        else:
            # 1. 创建实体
            if not self.pet_entity:
                print(f"PetScene: 创建宠物实体 {self.pet_type}")
                self.pet_entity = PetEntity(self.pet_type, cx, cy)
            
            # 2. 创建按钮
            # 使用 settings.PET_CONFIG
            try:
                p_food = settings.PET_CONFIG['food_price']
                p_med = settings.PET_CONFIG['med_price']
                p_toy = settings.PET_CONFIG['toy_price']
                
                self.btn_feed = Button(50, settings.SCREEN_HEIGHT - 100, 120, 60, f"喂食(${p_food})", self.font, bg_color=COLORS['green'])
                self.btn_heal = Button(190, settings.SCREEN_HEIGHT - 100, 120, 60, f"治疗(${p_med})", self.font, bg_color=COLORS['red'])
                self.btn_play = Button(330, settings.SCREEN_HEIGHT - 100, 120, 60, f"玩耍(${p_toy})", self.font, bg_color=COLORS['yellow'])
                self.btn_back = Button(settings.SCREEN_WIDTH - 150, settings.SCREEN_HEIGHT - 100, 120, 60, "返回菜单", self.font, bg_color=COLORS['grey'])
                
                self.buttons = [self.btn_feed, self.btn_heal, self.btn_play, self.btn_back]
            except KeyError as e:
                print(f"ERROR: settings.PET_CONFIG 缺少键值 {e}")

    def handle_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons: btn.check_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.buttons:
                if btn.is_clicked(event):
                    self._on_button_click(btn)
                    return
            
            if self.pet_entity and self.pet_entity.handle_click(event.pos):
                self._show_msg("宠物看起来很开心！")

    def _on_button_click(self, btn):
        if not self.pet_type:
            if btn == self.btn_adopt_cat: self._adopt('cat')
            elif btn == self.btn_adopt_dog: self._adopt('dog')
        else:
            if btn == self.btn_feed: self._action_feed()
            elif btn == self.btn_heal: self._action_heal()
            elif btn == self.btn_play: self._action_play()
            elif btn == self.btn_back: self.app.change_scene('menu')

    def _adopt(self, p_type):
        print(f"PetScene: 领养 {p_type}")
        self.dm.update_pet_data({'type': p_type, 'last_update': 0})
        self.on_enter() # 重新刷新
        self._show_msg(f"恭喜你领养了 {p_type}!")

    def _action_feed(self):
        cost = settings.PET_CONFIG['food_price']
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            new_val = min(100, self.pet_data['hunger'] + settings.PET_CONFIG['food_effect'])
            self.dm.update_pet_data({'hunger': new_val})
            self._show_msg("喂食成功！饱食度上升。")
        else:
            self._show_msg("金币不足！去贪吃蛇赚点钱吧。")

    def _action_heal(self):
        cost = settings.PET_CONFIG['med_price']
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            self.dm.update_pet_data({'is_sick': False, 'health': 100})
            self._show_msg("治疗成功！宠物恢复健康了。")
        else:
            self._show_msg("金币不足！")

    def _action_play(self):
        cost = settings.PET_CONFIG['toy_price']
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            new_val = min(100, self.pet_data['mood'] + settings.PET_CONFIG['toy_effect'])
            self.dm.update_pet_data({'mood': new_val})
            self._show_msg("宠物玩得很开心！心情上升。")
            if self.pet_entity: self.pet_entity.is_bouncing = True
        else:
            self._show_msg("金币不足！")

    def _show_msg(self, text):
        self.msg = text
        self.msg_timer = 120

    def update(self, dt):
        super().update(dt)
        if self.pet_entity:
            self.pet_entity.update()
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self, surface):
        super().draw(surface)
        
        title = self.font_title.render("宠物家园", True, COLORS['white'])
        surface.blit(title, (20, 20))
        
        # 错误提示：如果没有加载成功
        if not self.pet_data:
            err = self.font.render("数据加载错误...", True, COLORS['red'])
            surface.blit(err, (settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2))
            return

        if not self.pet_type:
            hint = self.font.render("请选择你的初始宠物：", True, COLORS['white'])
            surface.blit(hint, (settings.SCREEN_WIDTH//2 - 100, settings.SCREEN_HEIGHT//2 - 100))
        else:
            if self.pet_entity:
                self.pet_entity.draw(surface)
            self._draw_stats(surface)
            
        for btn in self.buttons:
            btn.draw(surface)
            
        if self.msg_timer > 0:
            # 简单的消息框
            msg_surf = self.font.render(self.msg, True, COLORS['yellow'])
            pygame.draw.rect(surface, (0,0,0), (settings.SCREEN_WIDTH//2 - 150, settings.SCREEN_HEIGHT - 180, 300, 40))
            surface.blit(msg_surf, (settings.SCREEN_WIDTH//2 - msg_surf.get_width()//2, settings.SCREEN_HEIGHT - 170))

    def _draw_stats(self, surface):
        panel_x, panel_y = 20, 80
        bar_w, bar_h = 200, 20
        gap = 30
        
        p = self.pet_data
        if not p: return

        stats = [
            ("饱食", p.get('hunger', 0), COLORS['green']),
            ("健康", p.get('health', 0), COLORS['red']),
            ("心情", p.get('mood', 0), COLORS['yellow'])
        ]
        
        for i, (label, val, color) in enumerate(stats):
            y = panel_y + i * gap
            txt = self.font.render(f"{label}: {int(val)}/100", True, COLORS['white'])
            surface.blit(txt, (panel_x, y))
            
            pygame.draw.rect(surface, (50,50,50), (panel_x + 80, y + 5, bar_w, bar_h))
            fill_w = int(bar_w * (val / 100))
            if fill_w > 0:
                pygame.draw.rect(surface, color, (panel_x + 80, y + 5, fill_w, bar_h))
        
        if p.get('is_sick'):
            sick_txt = self.font.render("状态: 生病 (请尽快治疗!)", True, COLORS['red'])
            surface.blit(sick_txt, (panel_x, panel_y + 3 * gap))