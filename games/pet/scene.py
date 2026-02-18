# games/pet/scene.py
import pygame, os
import datetime
from core.base_game import BaseGame
from core.ui import Button, InputBox
from core.data_manager import DataManager
from core.path_utils import resource_path
from games.pet.pet_entity import PetEntity
import settings
from settings import COLORS

class PetScene(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.dm = DataManager()
        self.font = pygame.font.SysFont("simhei", 24)
        self.font_title = pygame.font.SysFont("simhei", 40, bold=True)
        
        self.state = 'HOME'
        
        self.pets_data = []
        self.current_index = 0 # 当前选中的是列表里的第几个宠物
        
        # 【修改】现在管理多个实体列表
        self.pet_entities = [] 
        
        self.buttons = []
        self.msg = ""
        self.msg_timer = 0
        
        # 弹窗组件
        self.show_name_modal = False
        self.pending_buy_item = None
        self.show_abandon_modal = False
        
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        self.input_pet_name = InputBox(cx - 100, cy, 200, 50, self.font, placeholder="给它取个名...")
        
        self.btn_confirm_buy = Button(0, 0, 100, 40, "确认带走", self.font, bg_color=COLORS['green'])
        self.btn_cancel_buy = Button(0, 0, 100, 40, "算了", self.font, bg_color=COLORS['red'])
        self.btn_confirm_abandon = Button(0, 0, 100, 40, "确认弃养", self.font, bg_color=COLORS['red'])
        self.btn_cancel_abandon = Button(0, 0, 100, 40, "我再想想", self.font, bg_color=COLORS['green'])

        self.snd_feed = None
        try:
            path = resource_path(os.path.join('assets', 'sounds', 'eat.wav'))
            if os.path.exists(path): self.snd_feed = pygame.mixer.Sound(path)
        except: pass

    def on_enter(self):
        """进入场景刷新"""
        self.pets_data = self.dm.get_pets()
        if self.current_index >= len(self.pets_data):
            self.current_index = 0
            
        # 检查离线降级
        for p in self.pets_data:
            self._check_level_change(p, quiet=True) 
            
        self.state = 'HOME'
        self.show_name_modal = False
        self.show_abandon_modal = False
        
        # 【修改】初始化所有实体
        self._init_all_entities()
        self._init_ui()

    def _init_all_entities(self):
        """一次性生成所有宠物的实体"""
        self.pet_entities = []
        for i, p_data in enumerate(self.pets_data):
            level = p_data.get('level', 1)
            entity = PetEntity(p_data, level) # 传入完整数据引用
            # 如果是当前选中的索引，标记为选中
            if i == self.current_index:
                entity.is_selected = True
            self.pet_entities.append(entity)

    def _select_pet(self, index):
        """切换当前选中的宠物"""
        if 0 <= index < len(self.pet_entities):
            # 取消旧的选中
            if 0 <= self.current_index < len(self.pet_entities):
                self.pet_entities[self.current_index].is_selected = False
            
            # 设置新的选中
            self.current_index = index
            self.pet_entities[index].is_selected = True
            
            # 播放叫声提示
            self.pet_entities[index].play_voice()
            self._init_ui() # 刷新UI状态栏

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
            
            # 底部操作栏
            btn_y = settings.SCREEN_HEIGHT - 80 
            self.btn_feed = Button(50, btn_y, 100, 50, f"喂食(${p_food})", self.font, bg_color=COLORS['green'])
            self.btn_heal = Button(160, btn_y, 100, 50, f"治疗(${p_med})", self.font, bg_color=COLORS['red'])
            self.btn_play = Button(270, btn_y, 100, 50, f"玩耍(${p_toy})", self.font, bg_color=COLORS['yellow'])
            
            self.btn_abandon = Button(settings.SCREEN_WIDTH - 120, 80, 100, 40, "弃养", self.font, bg_color=(100, 0, 0))
            self.buttons.extend([self.btn_feed, self.btn_heal, self.btn_play, self.btn_abandon])
            
            # 【移除】左右切换按钮不再需要，靠点击宠物切换

        # 商店入口
        max_slots = self.dm.get_max_slots()
        if len(self.pets_data) < max_slots:
            slot_txt = f"商店 ({len(self.pets_data)}/{max_slots})"
            txt = slot_txt if self.pets_data else "去领养第一只宠物"
            btn_w = 200 if not self.pets_data else 150
            pos_x = cx - btn_w//2 if not self.pets_data else settings.SCREEN_WIDTH - 200
            pos_y = settings.SCREEN_HEIGHT // 2 if not self.pets_data else settings.SCREEN_HEIGHT - 140 
            
            self.btn_shop = Button(pos_x, pos_y, btn_w, 60, txt, self.font, bg_color=COLORS['blue'])
            self.buttons.append(self.btn_shop)

        self.btn_exit = Button(settings.SCREEN_WIDTH - 150, settings.SCREEN_HEIGHT - 80, 120, 50, "返回菜单", self.font, bg_color=COLORS['grey'])
        self.buttons.append(self.btn_exit)

    def handle_input(self, event):
        if self.show_name_modal:
            self._handle_name_modal_input(event)
            return
        if self.show_abandon_modal:
            self._handle_abandon_modal_input(event)
            return

        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons: btn.check_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1. 检查UI按钮点击
            clicked_ui = False
            for btn in self.buttons:
                if btn.is_clicked(event):
                    if self.state == 'SHOP': self._handle_shop_click(btn)
                    else: self._handle_home_click(btn)
                    clicked_ui = True
                    return # UI 优先级最高
            
            # 2. 检查宠物点击 (仅在 HOME 状态)
            if self.state == 'HOME' and not clicked_ui:
                # 倒序遍历，优先检测前面的（图层遮挡时选最上面的）
                for i in range(len(self.pet_entities) - 1, -1, -1):
                    entity = self.pet_entities[i]
                    if entity.handle_click(event.pos):
                        # 如果点的不是当前选中的，切换选中
                        if i != self.current_index:
                            self._select_pet(i)
                        else:
                            # 如果点的是当前选中的，触发互动增加心情
                            self._action_click_pet()
                        break

    # --- 弹窗逻辑 (保持不变) ---
    def _open_name_modal(self, item_data):
        self.pending_buy_item = item_data
        self.show_name_modal = True
        self.input_pet_name.text = "" 
        self.input_pet_name.active = True 
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        self.btn_confirm_buy.rect.topleft = (cx - 110, cy + 80)
        self.btn_cancel_buy.rect.topleft = (cx + 10, cy + 80)
        self.input_pet_name.rect.topleft = (cx - 100, cy)

    def _handle_name_modal_input(self, event):
        res = self.input_pet_name.handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            self.btn_confirm_buy.check_hover(event.pos)
            self.btn_cancel_buy.check_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN or res == 'submit':
            if self.btn_confirm_buy.is_clicked(event) or res == 'submit': self._confirm_buy()
            elif self.btn_cancel_buy.is_clicked(event): self.show_name_modal = False

    def _confirm_buy(self):
        item = self.pending_buy_item
        custom_name = self.input_pet_name.text
        if self.dm.get_coins() >= item['price']:
            success, msg = self.dm.add_new_pet(item, custom_name)
            if success:
                self.dm.add_coins(-item['price'])
                self._show_msg(f"成功领养 {custom_name if custom_name else item['name']}!")
                self.on_enter()
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
                self.on_enter() # 刷新列表
            elif self.btn_cancel_abandon.is_clicked(event):
                self.show_abandon_modal = False

    # --- 点击与互动 ---
    def _handle_shop_click(self, btn):
        if btn == getattr(self, 'btn_back_home', None):
            self.state = 'HOME'
            self._init_ui()
        elif hasattr(btn, 'item_data'):
            self._open_name_modal(btn.item_data)

    def _handle_home_click(self, btn):
        if btn == getattr(self, 'btn_shop', None):
            self.state = 'SHOP'
            self._init_ui()
        elif btn == getattr(self, 'btn_exit', None):
            self.app.change_scene('menu')
        # 喂食等操作只针对 self.current_index
        elif btn == getattr(self, 'btn_feed', None): self._action_feed()
        elif btn == getattr(self, 'btn_heal', None): self._action_heal()
        elif btn == getattr(self, 'btn_play', None): self._action_play()
        elif btn == getattr(self, 'btn_abandon', None): self._open_abandon_modal()

    def _action_feed(self):
        self._interact('hunger', settings.PET_CONFIG['food_price'], settings.PET_CONFIG['food_effect'], "喂食成功", settings.PET_CONFIG['exp_gain_food'])
        if self.snd_feed and self.dm.get_coins() >= settings.PET_CONFIG['food_price']:
            self.snd_feed.play()
    
    def _action_heal(self):
        cost = settings.PET_CONFIG['med_price']
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            self.pets_data[self.current_index]['is_sick'] = False
            self.pets_data[self.current_index]['health'] = 100
            self._add_exp(settings.PET_CONFIG['exp_gain_med'])
            self.dm.sync_data()
            self._show_msg("治疗成功！")
            if 0 <= self.current_index < len(self.pet_entities):
                self.pet_entities[self.current_index].play_voice()
        else: self._show_msg("金币不足！")
        
    def _action_play(self):
        self._interact('mood', settings.PET_CONFIG['toy_price'], settings.PET_CONFIG['toy_effect'], "玩耍成功", settings.PET_CONFIG['exp_gain_toy'])
        if 0 <= self.current_index < len(self.pet_entities):
            self.pet_entities[self.current_index].play_voice()
    
    def _action_click_pet(self):
        # 这里的 click_pet 只针对当前选中的互动 (比如摸头)
        if not (0 <= self.current_index < len(self.pet_entities)): return
        
        curr_pet = self.pets_data[self.current_index]
        entity = self.pet_entities[self.current_index]
        
        entity.play_voice()
        entity.is_bouncing = True # 弹一下
        
        # 跨天重置
        today_str = datetime.date.today().isoformat()
        if curr_pet.get('last_click_date') != today_str:
            curr_pet['daily_click_exp'] = 0
            curr_pet['last_click_date'] = today_str

        # 增加心情
        gain_mood = settings.PET_CONFIG['click_mood_gain']
        curr_pet['mood'] = min(200, curr_pet['mood'] + gain_mood)
        
        # 增加经验
        max_daily = settings.PET_CONFIG['max_daily_click_exp']
        current_daily = curr_pet.get('daily_click_exp', 0)
        msg = "心情变好了~"
        
        if current_daily < max_daily:
            exp_gain = settings.PET_CONFIG['click_exp_gain']
            self._add_exp(exp_gain)
            curr_pet['daily_click_exp'] = current_daily + exp_gain
        else:
            msg = "抚摸过多，它累了~"

        self.dm.sync_data()
        self._show_msg(msg)

    def _interact(self, attr, cost, effect, success_msg, exp_gain=0):
        if not self.pets_data: return
        if self.dm.get_coins() >= cost:
            self.dm.add_coins(-cost)
            curr_pet = self.pets_data[self.current_index]
            new_val = min(100, curr_pet[attr] + effect)
            self.pets_data[self.current_index][attr] = new_val
            if exp_gain > 0: self._add_exp(exp_gain)
            self.dm.sync_data()
            self._show_msg(success_msg)
            
            # 让对应实体弹跳
            if 0 <= self.current_index < len(self.pet_entities):
                self.pet_entities[self.current_index].is_bouncing = True
        else: self._show_msg("金币不足！")

    def _add_exp(self, amount):
        curr_pet = self.pets_data[self.current_index]
        health = curr_pet.get('health', 100)
        sick_threshold = settings.PET_CONFIG['sick_threshold']
        
        multiplier = 1.0
        if curr_pet.get('is_sick'): multiplier = 0.5 
        if health < sick_threshold:
            multiplier = 0.1 
            self._show_msg("健康太低，无法有效训练！")
            
        final_exp = int(amount * multiplier)
        if final_exp > 0:
            curr_pet['exp'] = curr_pet.get('exp', 0) + final_exp
            self._check_level_change(curr_pet)

    def _check_level_change(self, pet, quiet=False):
        loop_safety = 0
        while loop_safety < 100:
            loop_safety += 1
            level = pet.get('level', 1)
            exp = pet.get('exp', 0)
            if hasattr(settings, 'get_exp_needed'):
                needed = settings.get_exp_needed(level)
            else: needed = 100 * level
            if needed <= 0: needed = 100

            # 升级
            if exp >= needed and level < settings.PET_CONFIG['max_level']:
                pet['level'] = level + 1
                pet['exp'] = exp - needed
                if not quiet:
                    self._show_msg(f"升级！{pet['name']} -> Lv.{pet['level']}")
                    pet['mood'] = 100
                    pet['health'] = 100
                
                # 更新对应实体的等级大小
                # 需要找到对应的实体对象
                for entity in self.pet_entities:
                    if entity.pet_data is pet: # 通过对象引用判断
                        entity.set_level(pet['level'])
                        break
                continue 
            
            # 降级
            elif exp < 0 and level > 1:
                pet['level'] = level - 1
                if hasattr(settings, 'get_exp_needed'):
                    prev_needed = settings.get_exp_needed(pet['level'])
                else: prev_needed = 100 * pet['level']
                pet['exp'] = prev_needed + exp 
                if not quiet: self._show_msg(f"警报！{pet['name']} 降级为 Lv.{pet['level']}!")
                
                for entity in self.pet_entities:
                    if entity.pet_data is pet:
                        entity.set_level(pet['level'])
                        break
                continue
            break

    def _show_msg(self, text):
        self.msg = text
        self.msg_timer = 120

    def update(self, dt):
        super().update(dt)
        # 更新所有实体
        for entity in self.pet_entities:
            entity.update()
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
        
        title_txt = "宠物商店" if self.state == 'SHOP' else "温馨小屋"
        self._draw_text_with_outline(surface, title_txt, self.font_title, (20, 20), COLORS['white'])
        
        if self.state == 'HOME':
            if not self.pets_data:
                center_txt = "你还没有宠物，去商店看看吧！"
                cx = settings.SCREEN_WIDTH//2 - self.font.size(center_txt)[0]//2
                self._draw_text_with_outline(surface, center_txt, self.font, (cx, settings.SCREEN_HEIGHT//2 - 50), COLORS['white'])
            else:
                # 1. 绘制所有实体 (按Y轴排序，实现简单的遮挡关系)
                sorted_entities = sorted(self.pet_entities, key=lambda e: e.rect.bottom)
                for entity in sorted_entities:
                    entity.draw(surface)

                # 2. 绘制选中宠物的状态面板 (只显示当前选中的)
                self._draw_stats(surface)

        for btn in self.buttons: btn.draw(surface)
        if self.msg_timer > 0:
            msg_w = self.font.size(self.msg)[0]
            self._draw_text_with_outline(surface, self.msg, self.font, (settings.SCREEN_WIDTH//2 - msg_w//2, settings.SCREEN_HEIGHT - 170), COLORS['yellow'])

        if self.show_name_modal: self._draw_name_modal(surface)
        if self.show_abandon_modal: self._draw_abandon_modal(surface)

    # ... (_draw_name_modal, _draw_abandon_modal 保持不变) ...
    def _draw_name_modal(self, surface):
        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(180)
        mask.fill((0,0,0))
        surface.blit(mask, (0,0))
        cx, cy = settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2
        panel_rect = pygame.Rect(0, 0, 400, 250)
        panel_rect.center = (cx, cy)
        pygame.draw.rect(surface, (60, 60, 70), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (200, 200, 200), panel_rect, 2, border_radius=15)
        title = "为它取个名字吧"
        tw = self.font.size(title)[0]
        self._draw_text_with_outline(surface, title, self.font, (cx - tw//2, cy - 80), COLORS['white'])
        self.input_pet_name.draw(surface)
        self.btn_confirm_buy.draw(surface)
        self.btn_cancel_buy.draw(surface)

    def _draw_abandon_modal(self, surface):
        mask = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        mask.set_alpha(180)
        mask.fill((0,0,0))
        surface.blit(mask, (0,0))
        cx, cy = settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2
        panel_rect = pygame.Rect(0, 0, 400, 200)
        panel_rect.center = (cx, cy)
        pygame.draw.rect(surface, (80, 20, 20), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (200, 200, 200), panel_rect, 2, border_radius=15)
        line1 = "确定要弃养它吗？"
        line2 = "此操作无法撤销！"
        w1 = self.font.size(line1)[0]
        w2 = self.font.size(line2)[0]
        self._draw_text_with_outline(surface, line1, self.font, (cx - w1//2, cy - 60), COLORS['white'])
        self._draw_text_with_outline(surface, line2, self.font, (cx - w2//2, cy - 30), COLORS['yellow'])
        self.btn_confirm_abandon.draw(surface)
        self.btn_cancel_abandon.draw(surface)

    def _draw_stats(self, surface):
        if not self.pets_data: return
        # 只绘制当前 current_index 的数据
        p = self.pets_data[self.current_index]
        
        # 【修改】将 panel_y 从 80 改为 130 (向下移动 50 像素)
        panel_x, panel_y = 20, 130 
        
        panel_w, panel_h = 320, 150
        if p.get('is_sick'): panel_h += 40
        
        # 背景板
        s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 160), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, (255, 255, 0, 100), s.get_rect(), 2, border_radius=15) # 黄色边框强调当前选中
        surface.blit(s, (panel_x, panel_y))
        
        # 名字 (跟随 panel_y 自动下移)
        name_str = f"Lv.{p.get('level', 1)}  {p['name']}"
        self._draw_text_with_outline(surface, name_str, self.font_title, (panel_x + 15, panel_y - 40), COLORS['yellow'])

        # 属性条
        bar_x = panel_x + 80
        bar_y_start = panel_y + 15
        bar_w, bar_h = 200, 20
        gap = 35

        display_mood = min(100, p.get('mood', 0))
        stats = [("饱食", p.get('hunger', 0), COLORS['green']),
                 ("健康", p.get('health', 0), COLORS['red']),
                 ("心情", display_mood, COLORS['yellow'])]
        
        for i, (label, val, color) in enumerate(stats):
            y = bar_y_start + i * gap
            txt = self.font.render(f"{label}", True, COLORS['white'])
            surface.blit(txt, (panel_x + 15, y))
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, y + 5, bar_w, bar_h), border_radius=5)
            fill_w = int(bar_w * (val / 100))
            if fill_w > 0: pygame.draw.rect(surface, color, (bar_x, y + 5, fill_w, bar_h), border_radius=5)
            val_txt = pygame.font.SysFont("arial", 12).render(f"{int(val)}/100", True, COLORS['black'])
            val_rect = val_txt.get_rect(center=(bar_x + bar_w//2, y + 5 + bar_h//2))
            surface.blit(val_txt, val_rect)

        # 经验条绘制在面板最下方
        exp = p.get('exp', 0)
        level = p.get('level', 1)
        needed = settings.get_exp_needed(level)
        exp_bar_y = panel_y + panel_h + 10
        pygame.draw.rect(surface, (50, 50, 50), (panel_x, exp_bar_y, panel_w, 10), border_radius=5)
        fill_exp = int(panel_w * (exp / needed))
        if fill_exp > 0: pygame.draw.rect(surface, (0, 200, 255), (panel_x, exp_bar_y, fill_exp, 10), border_radius=5)
        
        if p.get('is_sick'):
            self._draw_text_with_outline(surface, "警告: 宠物生病了!", self.font, (panel_x + 20, panel_y + 3 * gap + 15), COLORS['red'])