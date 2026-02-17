# games/pet/scene.py
import pygame
from core.base_game import BaseGame
from core.ui import Button, InputBox  # 需要 InputBox
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
        
        self.state = 'HOME' # 'HOME' 或 'SHOP'
        
        self.pets_data = []
        self.current_index = 0
        self.current_entity = None
        
        self.buttons = []
        self.msg = ""
        self.msg_timer = 0
        
        # --- 弹窗状态管理 ---
        self.show_name_modal = False      # 是否显示取名弹窗
        self.pending_buy_item = None      # 待购买的宠物配置
        self.input_pet_name = None        # 取名输入框
        
        self.show_abandon_modal = False   # 是否显示弃养确认
        
        # 初始化输入框 (位置稍后在 update_ui 里定，这里先实例化)
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        self.input_pet_name = InputBox(cx - 100, cy, 200, 50, self.font, placeholder="给它取个名...")
        
        # 弹窗按钮
        self.btn_confirm_buy = Button(0, 0, 100, 40, "确认带走", self.font, bg_color=COLORS['green'])
        self.btn_cancel_buy = Button(0, 0, 100, 40, "算了", self.font, bg_color=COLORS['red'])
        
        self.btn_confirm_abandon = Button(0, 0, 100, 40, "确认弃养", self.font, bg_color=COLORS['red'])
        self.btn_cancel_abandon = Button(0, 0, 100, 40, "我再想想", self.font, bg_color=COLORS['green'])

    def on_enter(self):
        """进入场景刷新"""
        self.pets_data = self.dm.get_pets()
        if self.current_index >= len(self.pets_data):
            self.current_index = 0
        self.state = 'HOME'
        self.show_name_modal = False
        self.show_abandon_modal = False
        self._refresh_entity()
        self._init_ui()

    def _refresh_entity(self):
        if self.pets_data and 0 <= self.current_index < len(self.pets_data):
            p_data = self.pets_data[self.current_index]
            cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
            self.current_entity = PetEntity(p_data['id'], cx, cy)
        else:
            self.current_entity = None

    def _init_ui(self):
        self.buttons = []
        cx = settings.SCREEN_WIDTH // 2
        
        # === 状态 1: 商店界面 ===
        if self.state == 'SHOP':
            y = 100
            for i, item in enumerate(settings.PET_SHOP_LIST):
                btn_txt = f"{item['name']} - ${item['price']}"
                btn = Button(cx - 150, y, 300, 50, btn_txt, self.font, bg_color=COLORS['blue'])
                btn.item_data = item 
                self.buttons.append(btn)
                y += 70
            
            self.btn_back_home = Button(cx - 100, settings.SCREEN_HEIGHT - 80, 200, 50, "返回我的家", self.font, bg_color=COLORS['grey'])
            self.buttons.append(self.btn_back_home)
            return

        # === 状态 2: 我的家 ===
        if self.pets_data:
            p_food = settings.PET_CONFIG['food_price']
            p_med = settings.PET_CONFIG['med_price']
            p_toy = settings.PET_CONFIG['toy_price']
            
            self.btn_feed = Button(50, settings.SCREEN_HEIGHT - 100, 100, 50, f"喂食(${p_food})", self.font, bg_color=COLORS['green'])
            self.btn_heal = Button(160, settings.SCREEN_HEIGHT - 100, 100, 50, f"治疗(${p_med})", self.font, bg_color=COLORS['red'])
            self.btn_play = Button(270, settings.SCREEN_HEIGHT - 100, 100, 50, f"玩耍(${p_toy})", self.font, bg_color=COLORS['yellow'])
            
            # 弃养按钮
            self.btn_abandon = Button(settings.SCREEN_WIDTH - 120, 80, 100, 40, "弃养", self.font, bg_color=(100, 0, 0))
            
            self.buttons.extend([self.btn_feed, self.btn_heal, self.btn_play, self.btn_abandon])

            if len(self.pets_data) > 1:
                cy = settings.SCREEN_HEIGHT // 2
                self.btn_prev = Button(cx - 200, cy, 50, 50, "<", self.font_title, bg_color=COLORS['grey'])
                self.btn_next = Button(cx + 150, cy, 50, 50, ">", self.font_title, bg_color=COLORS['grey'])
                self.buttons.extend([self.btn_prev, self.btn_next])

        if len(self.pets_data) < settings.MAX_PET_COUNT:
            txt = "去商店买宠" if self.pets_data else "去领养第一只宠物"
            btn_w = 200 if not self.pets_data else 150
            pos_x = cx - btn_w//2 if not self.pets_data else settings.SCREEN_WIDTH - 200
            pos_y = settings.SCREEN_HEIGHT // 2 if not self.pets_data else settings.SCREEN_HEIGHT - 160
            
            self.btn_shop = Button(pos_x, pos_y, btn_w, 60, txt, self.font, bg_color=COLORS['blue'])
            self.buttons.append(self.btn_shop)

        self.btn_exit = Button(settings.SCREEN_WIDTH - 150, settings.SCREEN_HEIGHT - 100, 120, 50, "返回菜单", self.font, bg_color=COLORS['grey'])
        self.buttons.append(self.btn_exit)

    def handle_input(self, event):
        # === 优先级 1: 弹窗处理 (拦截所有背景操作) ===
        if self.show_name_modal:
            self._handle_name_modal_input(event)
            return
        if self.show_abandon_modal:
            self._handle_abandon_modal_input(event)
            return

        # === 优先级 2: 正常界面 ===
        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons: btn.check_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.buttons:
                if btn.is_clicked(event):
                    if self.state == 'SHOP': self._handle_shop_click(btn)
                    else: self._handle_home_click(btn)
                    return
            
            if self.state == 'HOME' and self.current_entity:
                if self.current_entity.handle_click(event.pos):
                    self._show_msg("它蹭了蹭你！")

    # --- 弹窗逻辑 ---
    def _open_name_modal(self, item_data):
        self.pending_buy_item = item_data
        self.show_name_modal = True
        self.input_pet_name.text = "" # 清空上次输入
        self.input_pet_name.active = True # 自动聚焦
        # 重新定位弹窗按钮
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        self.btn_confirm_buy.rect.topleft = (cx - 110, cy + 80)
        self.btn_cancel_buy.rect.topleft = (cx + 10, cy + 80)
        # 重新定位输入框
        self.input_pet_name.rect.topleft = (cx - 100, cy)

    def _handle_name_modal_input(self, event):
        # 处理输入框
        res = self.input_pet_name.handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            self.btn_confirm_buy.check_hover(event.pos)
            self.btn_cancel_buy.check_hover(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN or res == 'submit':
            # 点击确认或回车
            if self.btn_confirm_buy.is_clicked(event) or res == 'submit':
                self._confirm_buy()
            # 点击取消
            elif self.btn_cancel_buy.is_clicked(event):
                self.show_name_modal = False
                self.pending_buy_item = None

    def _confirm_buy(self):
        item = self.pending_buy_item
        custom_name = self.input_pet_name.text
        
        if self.dm.get_coins() >= item['price']:
            # 传入自定义名字
            success, msg = self.dm.add_new_pet(item, custom_name)
            if success:
                self.dm.add_coins(-item['price'])
                self._show_msg(f"成功领养 {custom_name if custom_name else item['name']}!")
                self.on_enter() # 刷新回首页
            else:
                self._show_msg(msg)
                self.show_name_modal = False
        else:
            self._show_msg("金币不足！")
            self.show_name_modal = False

    def _open_abandon_modal(self):
        self.show_abandon_modal = True
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        self.btn_confirm_abandon.rect.topleft = (cx - 110, cy + 50)
        self.btn_cancel_abandon.rect.topleft = (cx + 10, cy + 50)

    def _handle_abandon_modal_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.btn_confirm_abandon.check_hover(event.pos)
            self.btn_cancel_abandon.check_hover(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_confirm_abandon.is_clicked(event):
                self.dm.remove_pet(self.current_index)
                self._show_msg("宠物已送走...")
                self.on_enter()
            elif self.btn_cancel_abandon.is_clicked(event):
                self.show_abandon_modal = False

    # --- 点击逻辑 ---
    def _handle_shop_click(self, btn):
        if btn == getattr(self, 'btn_back_home', None):
            self.state = 'HOME'
            self._init_ui()
        elif hasattr(btn, 'item_data'):
            # 点击商品，不是直接买，而是打开取名弹窗
            self._open_name_modal(btn.item_data)

    def _handle_home_click(self, btn):
        if btn == getattr(self, 'btn_shop', None):
            self.state = 'SHOP'
            self._init_ui()
        elif btn == getattr(self, 'btn_exit', None):
            self.app.change_scene('menu')
        elif btn == getattr(self, 'btn_prev', None):
            self.current_index = (self.current_index - 1) % len(self.pets_data)
            self._refresh_entity()
        elif btn == getattr(self, 'btn_next', None):
            self.current_index = (self.current_index + 1) % len(self.pets_data)
            self._refresh_entity()
            
        elif btn == getattr(self, 'btn_feed', None): self._action_feed()
        elif btn == getattr(self, 'btn_heal', None): self._action_heal()
        elif btn == getattr(self, 'btn_play', None): self._action_play()
        
        elif btn == getattr(self, 'btn_abandon', None):
            # 点击弃养，打开确认弹窗
            self._open_abandon_modal()

    # --- 互动动作 (代码不变，保持之前的经验值逻辑) ---
    def _action_feed(self):
        self._interact('hunger', settings.PET_CONFIG['food_price'], settings.PET_CONFIG['food_effect'], "喂食成功", settings.PET_CONFIG['exp_gain_food'])
    
    def _action_heal(self):
        cost = settings.PET_CONFIG['med_price']
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            self.pets_data[self.current_index]['is_sick'] = False
            self.pets_data[self.current_index]['health'] = 100
            self._add_exp(settings.PET_CONFIG['exp_gain_med'])
            self.dm.sync_data()
            self._show_msg("治疗成功！")
        else: self._show_msg("金币不足！")

    def _action_play(self):
        self._interact('mood', settings.PET_CONFIG['toy_price'], settings.PET_CONFIG['toy_effect'], "玩耍成功", settings.PET_CONFIG['exp_gain_toy'])

    def _interact(self, attr, cost, effect, success_msg, exp_gain=0):
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            curr_pet = self.pets_data[self.current_index]
            new_val = min(100, curr_pet[attr] + effect)
            self.pets_data[self.current_index][attr] = new_val
            if exp_gain > 0: self._add_exp(exp_gain)
            self.dm.sync_data()
            self._show_msg(success_msg)
            if self.current_entity and attr == 'mood': self.current_entity.is_bouncing = True
        else: self._show_msg("金币不足！")

    def _add_exp(self, amount):
        curr_pet = self.pets_data[self.current_index]
        curr_pet['exp'] = curr_pet.get('exp', 0) + amount
        level = curr_pet.get('level', 1)
        needed = level * settings.PET_CONFIG['exp_base']
        if curr_pet['exp'] >= needed:
            curr_pet['level'] = level + 1
            curr_pet['exp'] -= needed
            self._show_msg(f"升级啦！{curr_pet['name']} 升到了 Lv.{curr_pet['level']}!")
            curr_pet['mood'] = 100 
            curr_pet['health'] = 100

    def _show_msg(self, text):
        self.msg = text
        self.msg_timer = 120

    def update(self, dt):
        super().update(dt)
        if self.current_entity: self.current_entity.update()
        if self.msg_timer > 0: self.msg_timer -= 1

    def _draw_text_with_outline(self, surface, text, font, pos, color, outline_color=(0,0,0)):
        outline_surf = font.render(text, True, outline_color)
        x, y = pos
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in offsets:
            surface.blit(outline_surf, (x + dx, y + dy))
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, pos)

    def draw(self, surface):
        super().draw(surface)
        
        # 1. 绘制底层界面
        title_txt = "宠物商店" if self.state == 'SHOP' else "温馨小屋"
        self._draw_text_with_outline(surface, title_txt, self.font_title, (20, 20), COLORS['white'])
        
        if self.state == 'HOME':
            if not self.pets_data:
                center_txt = "你还没有宠物，去商店看看吧！"
                cx = settings.SCREEN_WIDTH//2 - self.font.size(center_txt)[0]//2
                self._draw_text_with_outline(surface, center_txt, self.font, (cx, settings.SCREEN_HEIGHT//2 - 50), COLORS['white'])
            else:
                if self.current_entity:
                    self.current_entity.draw(surface)
                    curr_pet = self.pets_data[self.current_index]
                    # 显示自定义名字
                    name_str = f"Lv.{curr_pet.get('level', 1)}  {curr_pet['name']}"
                    name_w = self.font_title.size(name_str)[0]
                    name_pos = (settings.SCREEN_WIDTH//2 - name_w//2, settings.SCREEN_HEIGHT//2 - 140)
                    self._draw_text_with_outline(surface, name_str, self.font_title, name_pos, COLORS['yellow'])
                    
                    # 经验条
                    exp = curr_pet.get('exp', 0)
                    level = curr_pet.get('level', 1)
                    max_exp = level * settings.PET_CONFIG['exp_base']
                    bar_w, bar_h = 200, 8
                    bar_x = settings.SCREEN_WIDTH//2 - bar_w//2
                    bar_y = name_pos[1] + 45
                    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
                    fill_w = int(bar_w * (exp / max_exp))
                    if fill_w > 0: pygame.draw.rect(surface, (0, 200, 255), (bar_x, bar_y, fill_w, bar_h), border_radius=4)
                    
                    page_str = f"{self.current_index + 1} / {len(self.pets_data)}"
                    self._draw_text_with_outline(surface, page_str, self.font, (settings.SCREEN_WIDTH//2 - 20, settings.SCREEN_HEIGHT//2 + 110), COLORS['white'])

                self._draw_stats(surface)

        for btn in self.buttons: btn.draw(surface)

        if self.msg_timer > 0:
            msg_w = self.font.size(self.msg)[0]
            self._draw_text_with_outline(surface, self.msg, self.font, (settings.SCREEN_WIDTH//2 - msg_w//2, settings.SCREEN_HEIGHT - 170), COLORS['yellow'])

        # === 2. 绘制弹窗 (覆盖在最上层) ===
        if self.show_name_modal: self._draw_name_modal(surface)
        if self.show_abandon_modal: self._draw_abandon_modal(surface)

    def _draw_name_modal(self, surface):
        # 半透明黑色遮罩
        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(180)
        mask.fill((0,0,0))
        surface.blit(mask, (0,0))
        
        # 弹窗框
        cx, cy = settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2
        panel_rect = pygame.Rect(0, 0, 400, 250)
        panel_rect.center = (cx, cy)
        pygame.draw.rect(surface, (60, 60, 70), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (200, 200, 200), panel_rect, 2, border_radius=15)
        
        # 标题
        title = "为它取个名字吧"
        tw = self.font.size(title)[0]
        self._draw_text_with_outline(surface, title, self.font, (cx - tw//2, cy - 80), COLORS['white'])
        
        # 输入框
        self.input_pet_name.draw(surface)
        
        # 按钮
        self.btn_confirm_buy.draw(surface)
        self.btn_cancel_buy.draw(surface)

    def _draw_abandon_modal(self, surface):
        # 遮罩
        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(180)
        mask.fill((0,0,0))
        surface.blit(mask, (0,0))
        
        # 弹窗
        cx, cy = settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2
        panel_rect = pygame.Rect(0, 0, 400, 200)
        panel_rect.center = (cx, cy)
        pygame.draw.rect(surface, (80, 20, 20), panel_rect, border_radius=15) # 红色警示背景
        pygame.draw.rect(surface, (200, 200, 200), panel_rect, 2, border_radius=15)
        
        # 警示语
        line1 = "确定要弃养它吗？"
        line2 = "此操作无法撤销！"
        w1 = self.font.size(line1)[0]
        w2 = self.font.size(line2)[0]
        self._draw_text_with_outline(surface, line1, self.font, (cx - w1//2, cy - 60), COLORS['white'])
        self._draw_text_with_outline(surface, line2, self.font, (cx - w2//2, cy - 30), COLORS['yellow'])
        
        # 按钮
        self.btn_confirm_abandon.draw(surface)
        self.btn_cancel_abandon.draw(surface)

    def _draw_stats(self, surface):
        if not self.pets_data: return
        p = self.pets_data[self.current_index]
        
        panel_x, panel_y = 20, 80
        panel_w, panel_h = 320, 150
        if p.get('is_sick'): panel_h += 40
        
        s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 160), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, (255, 255, 255, 50), s.get_rect(), 2, border_radius=15)
        surface.blit(s, (panel_x, panel_y))
        
        bar_x = panel_x + 80
        bar_y_start = panel_y + 15
        bar_w, bar_h = 200, 20
        gap = 35
        
        stats = [("饱食", p.get('hunger', 0), COLORS['green']),
                 ("健康", p.get('health', 0), COLORS['red']),
                 ("心情", p.get('mood', 0), COLORS['yellow'])]
        
        for i, (label, val, color) in enumerate(stats):
            y = bar_y_start + i * gap
            txt = self.font.render(f"{label}", True, COLORS['white'])
            surface.blit(txt, (panel_x + 15, y))
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, y + 5, bar_w, bar_h), border_radius=5)
            fill_w = int(bar_w * (val / 100))
            if fill_w > 0: pygame.draw.rect(surface, color, (bar_x, y + 5, fill_w, bar_h), border_radius=5)
            val_txt = pygame.font.SysFont("arial", 12).render(f"{int(val)}/100", True, (255,255,255))
            val_rect = val_txt.get_rect(center=(bar_x + bar_w//2, y + 5 + bar_h//2))
            surface.blit(val_txt, val_rect)
            
        if p.get('is_sick'):
            self._draw_text_with_outline(surface, "警告: 宠物生病了!", self.font, (panel_x + 20, panel_y + 3 * gap + 15), COLORS['red'])