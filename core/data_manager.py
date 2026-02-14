import threading
import hashlib
import json
import time
from datetime import datetime
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
            # 默认宠物数据结构
            cls._instance.default_pet = {
                "hunger": 100,      # 饱食度 0-100
                "mood": 100,        # 心情 0-100
                "is_sick": False,   # 是否生病
                "last_update": 0    # 上次存档的时间戳
            }
        return cls._instance

    def connect(self):
        try:
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.is_connected = True
            print("Connected to Supabase!")
        except Exception as e:
            print(f"Connection failed: {e}")
            self.is_connected = False

    def _hash_password(self, password):
        """简单的 SHA256 加密"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        """注册新用户"""
        if not self.is_connected: return "网络未连接"
        
        pwd_hash = self._hash_password(password)
        # 初始化宠物数据，记录当前时间
        pet_init = self.default_pet.copy()
        pet_init['last_update'] = time.time()

        new_user = {
            'username': username, 
            'password': pwd_hash,
            'coins': 0, 
            'pet_data': pet_init
        }
        
        try:
            self.client.table('users').insert(new_user).execute()
            print(f"User {username} registered.")
            return "SUCCESS"
        except Exception as e:
            # 通常是因为用户名已存在
            print(f"Register error: {e}")
            return "用户名已存在"

    def login(self, username, password):
        """登录并计算宠物离线衰减"""
        if not self.is_connected: return "网络未连接"
        
        try:
            pwd_hash = self._hash_password(password)
            response = self.client.table('users').select("*").eq('username', username).execute()
            
            if len(response.data) == 0:
                return "用户不存在"
            
            user = response.data[0]
            if user['password'] != pwd_hash:
                return "密码错误"
            
            # --- 登录成功，处理数据 ---
            self.user_data = user
            
            # 兼容性处理：如果老账号没有 pet_data
            if not self.user_data.get('pet_data'):
                self.user_data['pet_data'] = self.default_pet.copy()
                self.user_data['pet_data']['last_update'] = time.time()
            
            # 【核心逻辑】计算离线衰减
            self._calculate_offline_decay()
            
            return "SUCCESS"
        except Exception as e:
            print(f"Login error: {e}")
            return "未知错误"

    def _calculate_offline_decay(self):
        """根据上次下线时间，扣除饱食度和心情"""
        pet = self.user_data['pet_data']
        last_time = pet.get('last_update', time.time())
        current_time = time.time()
        
        # 计算过去了多少小时
        hours_passed = (current_time - last_time) / 3600
        
        if hours_passed > 0.1: # 只有离线超过几分钟才计算，避免频繁扣除
            # 衰减率：假设每小时扣 5 点
            decay_rate = 5 
            drop_amount = int(hours_passed * decay_rate)
            
            if drop_amount > 0:
                print(f"离线 {hours_passed:.2f} 小时，扣除 {drop_amount} 点状态")
                pet['hunger'] = max(0, pet['hunger'] - drop_amount)
                pet['mood'] = max(0, pet['mood'] - drop_amount)
                
                # 更新时间戳
                pet['last_update'] = current_time
                self.sync_data() # 立即同步回云端

    def sync_data(self):
        """同步金币和宠物数据到云端"""
        if not self.is_connected or not self.user_data: return
        threading.Thread(target=self._sync_thread).start()

    def _sync_thread(self):
        try:
            # 更新时间戳
            self.user_data['pet_data']['last_update'] = time.time()
            
            self.client.table('users').update({
                'coins': self.user_data['coins'],
                'pet_data': self.user_data['pet_data']
            }).eq('username', self.user_data['username']).execute()
            print("Cloud sync success.")
        except Exception as e:
            print(f"Sync failed: {e}")

    # --- 简便的数据操作接口 ---
    def get_coins(self):
        return self.user_data['coins'] if self.user_data else 0

    def add_coins(self, amount):
        if self.user_data:
            self.user_data['coins'] += amount
            self.sync_data()
            
    def get_pet(self):
        return self.user_data.get('pet_data', self.default_pet)