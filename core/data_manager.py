# core/data_manager.py
import threading
import hashlib
import json
import time, datetime
import random
from supabase import create_client, Client
import settings
from core.security import get_machine_id

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.user_data = None
            cls._instance.is_connected = False
            # 默认宠物是一个空列表
            cls._instance.default_pets = [] 
        return cls._instance

    def connect(self):
        try:
            if not hasattr(settings, 'SUPABASE_URL') or not settings.SUPABASE_URL:
                print("Error: SUPABASE_URL not configured.")
                return
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.is_connected = True
            print("Connected to Supabase!")
        except Exception as e:
            print(f"Connection failed: {e}")
            self.is_connected = False

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # 【注意】register 方法已被移除，注册功能请使用独立的 register_tool.py

    def login(self, username, password):
        if not self.is_connected: return "网络未连接"
        
        # =========================================
        # 【新增】设备白名单安全检查
        # =========================================
        current_hwid = get_machine_id()
        try:
            # 查询 device_whitelist 表，看是否存在当前机器码
            res = self.client.table('device_whitelist').select("hwid").eq('hwid', current_hwid).execute()
            
            # 如果结果为空，说明不在白名单里
            if len(res.data) == 0:
                print(f"拦截未授权设备: {current_hwid}")
                # 返回错误信息包含机器码前8位，方便用户截图发给你授权
                return f"设备未授权！\n机器码: {current_hwid[:8]}..." 
        except Exception as e:
            print(f"白名单检查失败: {e}")
            # 为了安全，如果检查出错（比如表不存在），也应该阻止登录
            return "安全检查失败"

        # =========================================
        #  账号密码验证逻辑
        # =========================================
        try:
            pwd_hash = self._hash_password(password)
            response = self.client.table('users').select("*").eq('username', username).execute()
            
            if len(response.data) == 0: return "用户不存在"
            user = response.data[0]
            if user['password'] != pwd_hash: return "密码错误"
            
            self.user_data = user
            
            # === 数据迁移与完整性检查 ===
            p_data = self.user_data.get('pet_data')
            if isinstance(p_data, dict):
                # 旧版数据兼容：如果 pet_data 是字典，转为列表
                if p_data.get('type'):
                    p_data['name'] = '我的宠物'
                    p_data['id'] = p_data['type']
                    self.user_data['pet_data'] = [p_data]
                else:
                    self.user_data['pet_data'] = []
            elif p_data is None:
                self.user_data['pet_data'] = []
            
            today_str = datetime.date.today().isoformat()
            for pet in self.user_data['pet_data']:
                if 'level' not in pet: pet['level'] = 1
                if 'exp' not in pet: pet['exp'] = 0
                
                # 补全点击限制字段
                if 'daily_click_exp' not in pet: pet['daily_click_exp'] = 0
                if 'last_click_date' not in pet: pet['last_click_date'] = today_str
                
                # 检查跨天重置
                if pet['last_click_date'] != today_str:
                    pet['daily_click_exp'] = 0
                    pet['last_click_date'] = today_str
            
            # 计算离线衰减
            self._calculate_offline_decay()
            return "SUCCESS"
        except Exception as e:
            print(f"Login error: {e}")
            return "未知错误"
    
    def get_max_slots(self):
        """计算最大宠物栏位 = 基础3 + (30级宠物的数量)"""
        base = settings.PET_CONFIG.get('base_pet_slots', 3)
        pets = self.get_pets()
        bonus = 0
        for p in pets:
            if p.get('level', 1) >= settings.PET_CONFIG['max_level']:
                bonus += 1
        return base + bonus

    def _calculate_offline_decay(self):
        pets = self.get_pets()
        if not pets: return

        current_time = time.time()
        interval = getattr(settings, 'PET_CONFIG', {}).get('decay_interval', 3600)
        cfg = getattr(settings, 'PET_CONFIG', {})

        updated = False
        for pet in pets:
            last_time = pet.get('last_update', current_time)
            cycles = int((current_time - last_time) / interval)
            
            if cycles > 0:
                print(f"宠物 {pet.get('name')} 离线 {cycles} 周期...")
                updated = True
                
                # 1. 基础衰减
                loss_hunger = cycles * cfg.get('hunger_decay', 3)
                loss_mood = cycles * cfg.get('mood_decay', 2)
                
                pet['hunger'] = max(0, pet['hunger'] - loss_hunger)
                pet['mood'] = max(0, pet['mood'] - loss_mood)
                
                # 2. 生病判定
                if not pet.get('is_sick', False):
                    fail_prob = 1.0 - cfg.get('sick_chance', 0.15)
                    if random.random() > (fail_prob ** cycles):
                         pet['is_sick'] = True
                         print(f"  - {pet['name']} 生病了！")
                
                # 3. 健康值惩罚 (生病或极度饥饿时才扣)
                if pet.get('is_sick') or pet['hunger'] < 20:
                    loss_health = cycles * cfg.get('health_decay_punish', 2)
                    pet['health'] = max(0, pet['health'] - loss_health)
                    print(f"  - 状态恶化，健康值减少 {loss_health}")

                # 4. 经验倒扣
                exp_loss = 0
                if pet['hunger'] < 10: exp_loss += cycles * cfg.get('exp_decay_starve', 50)
                if pet.get('is_sick'): exp_loss += cycles * cfg.get('exp_decay_sick', 30)
                
                if exp_loss > 0:
                    pet['exp'] = max(0, pet.get('exp', 0) - exp_loss)
                
                pet['last_update'] = current_time
        
        if updated:
            self.sync_data()

    def sync_data(self):
        if not self.is_connected or not self.user_data: return
        threading.Thread(target=self._sync_thread, daemon=True).start()

    def _sync_thread(self):
        try:
            # 更新所有宠物的 last_update 为当前时间
            for p in self.user_data['pet_data']:
                p['last_update'] = time.time()
                
            self.client.table('users').update({
                'coins': self.user_data['coins'],
                'pet_data': self.user_data['pet_data']
            }).eq('username', self.user_data['username']).execute()
            print("Cloud sync success.")
        except Exception as e:
            print(f"Sync failed: {e}")

    # --- 数据接口 ---
    def get_coins(self):
        return self.user_data['coins'] if self.user_data else 0

    def add_coins(self, amount):
        if self.user_data:
            self.user_data['coins'] += amount
            self.sync_data()
            
    def get_pets(self):
        """返回宠物列表"""
        if not self.user_data: return []
        return self.user_data.get('pet_data', [])

    def add_new_pet(self, pet_config, custom_name=None):
        """购买新宠物"""
        max_slots = self.get_max_slots()
        if len(self.get_pets()) >= max_slots:
            return False, f"宠物栏已满 ({len(self.get_pets())}/{max_slots})\n培养满级宠物可增加栏位！"
            
        final_name = custom_name if custom_name and custom_name.strip() else pet_config['name']
        today_str = datetime.date.today().isoformat()  
        
        new_pet = {
            "id": pet_config['id'],
            "name": final_name,
            "hunger": 100,
            "health": 100,
            "mood": 100,
            "is_sick": False,
            "last_update": time.time(),
            "level": 1,
            "exp": 0,
            "daily_click_exp": 0,
            "last_click_date": today_str
        }
        self.user_data['pet_data'].append(new_pet)
        self.sync_data()
        return True, "Success"

    def remove_pet(self, index):
        """弃养宠物"""
        pets = self.get_pets()
        if 0 <= index < len(pets):
            del pets[index]
            self.sync_data()
            return True
        return False
    
    def update_pet_status(self, index, status_dict):
        """更新指定宠物的状态"""
        pets = self.get_pets()
        if 0 <= index < len(pets):
            pets[index].update(status_dict)
            self.sync_data()