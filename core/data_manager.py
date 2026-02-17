# core/data_manager.py
import threading
import hashlib
import json
import time
import random
from supabase import create_client, Client
import settings

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

    def register(self, username, password):
        if not self.is_connected: return "网络未连接"
        pwd_hash = self._hash_password(password)
        
        new_user = {
            'username': username, 
            'password': pwd_hash,
            'coins': 0, 
            'pet_data': [] # 新账号初始化为空列表
        }
        try:
            self.client.table('users').insert(new_user).execute()
            return "SUCCESS"
        except Exception as e:
            print(f"Register error: {e}")
            return "用户名已存在"

    def login(self, username, password):
        if not self.is_connected: return "网络未连接"
        try:
            pwd_hash = self._hash_password(password)
            response = self.client.table('users').select("*").eq('username', username).execute()
            
            if len(response.data) == 0: return "用户不存在"
            user = response.data[0]
            if user['password'] != pwd_hash: return "密码错误"
            
            self.user_data = user
            
            # === 【关键】数据迁移逻辑 ===
            # 如果老数据的 pet_data 是字典（旧版），把它包进列表里
            p_data = self.user_data.get('pet_data')
            if isinstance(p_data, dict):
                # 如果字典里有 'type' 且不为 None，说明有旧宠物，保留它
                if p_data.get('type'):
                    # 给旧宠物补一个 name 字段
                    p_data['name'] = '我的宠物'
                    p_data['id'] = p_data['type'] # 简单映射
                    self.user_data['pet_data'] = [p_data]
                else:
                    self.user_data['pet_data'] = []
            elif p_data is None:
                self.user_data['pet_data'] = []
            
            for pet in self.user_data['pet_data']:
                if 'level' not in pet: pet['level'] = 1
                if 'exp' not in pet: pet['exp'] = 0

            # 计算离线衰减
            self._calculate_offline_decay()
            return "SUCCESS"
        except Exception as e:
            print(f"Login error: {e}")
            return "未知错误"

    def _calculate_offline_decay(self):
        """计算所有宠物的离线衰减"""
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
                print(f"宠物 {pet.get('name')} 离线 {cycles} 周期，结算状态...")
                updated = True
                loss_hunger = cycles * cfg.get('hunger_decay', 5)
                loss_mood = cycles * cfg.get('mood_decay', 5)
                
                pet['hunger'] = max(0, pet['hunger'] - loss_hunger)
                pet['mood'] = max(0, pet['mood'] - loss_mood)
                
                if not pet.get('is_sick', False):
                    for _ in range(cycles):
                        if random.random() < cfg.get('sick_chance', 0.1):
                            pet['is_sick'] = True
                            print(f"糟糕！{pet.get('name')} 生病了！")
                            break
                
                if pet.get('is_sick'):
                    loss_health = cycles * 20
                    pet['health'] = max(0, pet['health'] - loss_health)
                
                pet['last_update'] = current_time
        
        if updated:
            self.sync_data()

    def sync_data(self):
        if not self.is_connected or not self.user_data: return
        threading.Thread(target=self._sync_thread, daemon=True).start()

    def _sync_thread(self):
        try:
            # 更新所有宠物的 last_update 为当前时间，避免重复扣除
            for p in self.user_data['pet_data']:
                p['last_update'] = time.time()
                
            self.client.table('users').update({
                'coins': self.user_data['coins'],
                'pet_data': self.user_data['pet_data']
            }).eq('username', self.user_data['username']).execute()
            print("Cloud sync success.")
        except Exception as e:
            print(f"Sync failed: {e}")

    # --- 接口 ---
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
        """购买新宠物 (支持自定义名字)"""
        if len(self.get_pets()) >= settings.MAX_PET_COUNT:
            return False, "宠物已满"
            
        # 如果用户没填名字，就用默认种族名 (如"大橘猫")
        final_name = custom_name if custom_name and custom_name.strip() else pet_config['name']
            
        new_pet = {
            "id": pet_config['id'],
            "name": final_name,     # 使用最终决定的名字
            "hunger": 100,
            "health": 100,
            "mood": 100,
            "is_sick": False,
            "last_update": time.time(),
            "level": 1,
            "exp": 0
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