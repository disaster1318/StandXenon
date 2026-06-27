"""
StandXenon V1.1 — ПОЛНАЯ ВЕРСИЯ
Всё работает: меню, профиль, друзья, инвентарь, магазин, рынок, настройки, бой, Supabase, WebSocket (Railway)
"""

import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
import random
import json
import os
import webbrowser
import asyncio
import websockets

# ==================== КОНФИГ ====================
CONFIG = {
    "SUPABASE_URL": "https://xemjwqonyuthadlcacmu.supabase.co",
    "SUPABASE_KEY": "sb_publishable_aA9v38Ce1Aulc6L--joUDw_KiQsk-_z",
    "SERVER_URL": "wss://standxenon-production.up.railway.app/ws"
}

# ==================== SUPABASE ====================
from supabase import create_client
supabase = create_client(CONFIG["SUPABASE_URL"], CONFIG["SUPABASE_KEY"])

# ==================== WEBSOCKET (RAILWAY) ====================
class OnlineClient:
    def __init__(self):
        self.ws = None
        self.room = None
        self.connected = False
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def connect(self):
        Clock.schedule_once(lambda dt: asyncio.run_coroutine_threadsafe(self._connect(), self.loop), 0)

    async def _connect(self):
        try:
            self.ws = await websockets.connect(CONFIG["SERVER_URL"])
            self.connected = True
            print("[WS] Подключено")
            await self.ws.send(json.dumps({"type": "auth", "player_id": PLAYER_ID}))
            asyncio.create_task(self._listen())
        except Exception as e:
            print(f"[WS] Ошибка: {e}")

    async def _listen(self):
        try:
            async for msg in self.ws:
                data = json.loads(msg)
                print(f"[WS] {data}")
        except:
            self.connected = False

    def send(self, action, data=None):
        if not self.connected or not self.ws:
            return
        payload = {"type": action, "player_id": PLAYER_ID, "room_id": self.room, "data": data or {}}
        asyncio.run_coroutine_threadsafe(self.ws.send(json.dumps(payload)), self.loop)

    def create_room(self):
        self.send("create_room")

    def join_room(self, room_id):
        self.room = room_id
        self.send("join_room", {"room_id": room_id})

online = OnlineClient()

# ==================== ГОСТЕВОЙ ID ====================
GUEST_ID_FILE = "guest_id.json"

def get_guest_id():
    if os.path.exists(GUEST_ID_FILE):
        try:
            with open(GUEST_ID_FILE, 'r') as f:
                return json.load(f)['id']
        except:
            pass
    new_id = str(random.randint(10000000, 99999999))
    with open(GUEST_ID_FILE, 'w') as f:
        json.dump({'id': new_id}, f)
    return new_id

PLAYER_ID = get_guest_id()

# ==================== ЗАГРУЗКА ПРОФИЛЯ ====================
def load_profile():
    try:
        res = supabase.table('players').select('*').eq('id', PLAYER_ID).execute()
        if res.data:
            return res.data[0]
    except:
        pass
    return {
        'nickname': 'Игрок',
        'level': 1,
        'exp': 0,
        'gold': 0,
        'silver': 0,
        'kills': 0,
        'deaths': 0,
        'accuracy': 0.0,
        'playtime': 0.0,
        'avatar': ''
    }

def save_profile(data):
    try:
        supabase.table('players').upsert({'id': PLAYER_ID, **data}).execute()
    except:
        pass

PLAYER_DATA = load_profile()

# ==================== ИНВЕНТАРЬ ====================
def load_inventory():
    try:
        res = supabase.table('inventory').select('*').eq('player_id', PLAYER_ID).execute()
        return res.data if res.data else []
    except:
        return []

INVENTORY = load_inventory()

# ==================== ДРУЗЬЯ ====================
def load_friends():
    try:
        res = supabase.table('friends').select('friend_id').eq('player_id', PLAYER_ID).eq('status', 'accepted').execute()
        return [f['friend_id'] for f in res.data] if res.data else []
    except:
        return []

FRIENDS = load_friends()

# ==================== НАСТРОЙКИ ====================
def load_settings():
    try:
        res = supabase.table('players').select('settings').eq('id', PLAYER_ID).execute()
        if res.data and res.data[0].get('settings'):
            return res.data[0]['settings']
    except:
        pass
    return {
        'sound': 1.0,
        'music': 1.0,
        'sensitivity': 2.61,
        'fov': 1.25,
        'language': 'ru'
    }

SETTINGS = load_settings()

# ==================== ВСЕ СКИНЫ ИЗ СТАНДОФФ 2 ====================
ALL_SKINS = {
    "Пистолеты": [
        "G22", "USP", "P350", "Desert Eagle", "TEC-9", "F/S", "Berettas"
    ],
    "Пистолеты-пулемёты": [
        "MP7", "P90", "UMP45", "MP5", "MAC10", "Akimbo Uzi"
    ],
    "Винтовки": [
        "M4", "M4A1", "AKR", "VAL", "M16", "FN FAL", "FAMAS"
    ],
    "Снайперские": [
        "AWM", "M44A1", "Mallard"
    ],
    "Дробовики": [
        "SPAS", "SM1014"
    ],
    "Ножи": [
        "M9 Bayonet", "Karambit", "Kommando", "Butterfly", "Flip", "Stiletto", "Mantis", "Sting"
    ],
    "Перчатки": [
        "Gloves Artificer", "Gloves Dragon", "Gloves Mimicry", "Gloves Stream",
        "Gloves Nightmare", "Gloves Lincoln", "Gloves Impulse"
    ],
    "Агенты CT": [
        "Agent CT Warden", "Agent CT Hammer"
    ],
    "Агенты T": [
        "Agent T Reis", "Agent T Adam", "Agent T Marco"
    ]
}

CASE_SKINS = {
    "Division Case": [
        "UMP45", "FAMAS Protocol", "M4 Catalyst", "SPAS Hammer",
        "G22 Adam", "USP Warden", "SM1014 Signal", "Berettas Marco",
        "MP5 Phantom", "M4A1 Renegade", "AKR Twilight", "AWM Venom",
        "Agent T Adam", "Agent T Marco", "Agent CT Warden", "Agent CT Hammer"
    ],
    "Valor Case": [
        "F/S Flashing Flame", "VAL Vertex", "MP7 Magma Trail", "P90 Horizon",
        "M4 Retro Film", "M16 Accuracy", "Akimbo Uzi Zenith", "P350 Emberbird",
        "AKR Sketch", "Mallard Snake", "M44A1 Tresillo", "M9 Bayonet Sketch",
        "M9 Bayonet Citrine", "M9 Bayonet Poison", "M9 Bayonet Twilight"
    ],
    "Dynasty Case": [
        "M16 Mayhem", "Akimbo Uzi Skull", "FN FAL PRO", "SM1014 Wasp",
        "AWM Sylvan", "P350 Ooze", "G22 Brian", "P90 Noir", "M4A1 Overdrive",
        "Desert Eagle Eclipse", "Akimbo Uzi Overdrive", "AKR Genesis",
        "Mantis Eclipse", "Mantis Citrine", "Mantis Nest", "Mantis Genesis"
    ],
    "Chameleon Case": [
        "Desert Eagle Violet", "M4A1 Stainless", "VAL Joker", "G22 Flock",
        "M4 Flock", "USP Ghosts", "M4O Disguise", "TEC-9 Disguise",
        "MP7 Fight", "AKR12 Mimicry", "VAL Gilded Gaols", "AWM Hohei Taisho",
        "Gloves Artificer", "Gloves Dragon", "Gloves Mimicry", "Gloves Stream"
    ]
}

RARITIES = {
    "Common": 0.45,
    "Uncommon": 0.30,
    "Rare": 0.15,
    "Epic": 0.08,
    "Arcana": 0.02
}

# ==================== КАРТЫ И РЕЖИМЫ ====================
MAPS = [
    'Rust', 'Dune', 'Breeze', 'Province', 'Sandstone', 'Perimeter',
    'Prison', 'Hanami', 'Calypso', 'Favelas', 'Arena', 'Sand Yards',
    'Training Ditches', 'Villano', 'Block', 'Pipeline', 'Bridge',
    'Pool', 'Temple', 'Cableway', 'Dust 2x2', 'Mirage'
]

MODES = [
    {'name': 'Командный бой', 'unlock': 0},
    {'name': 'Соревновательный', 'unlock': 20},
    {'name': 'Союзники', 'unlock': 15},
    {'name': 'Дуэль', 'unlock': 10}
]

SELECTED_MODE = None
SELECTED_MAP = None

# ==================== ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ ====================
class StandXenonApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainMenu(name='main'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        self.sm.add_widget(FriendsScreen(name='friends'))
        self.sm.add_widget(InventoryScreen(name='inventory'))
        self.sm.add_widget(ShopScreen(name='shop'))
        self.sm.add_widget(MarketScreen(name='market'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(ModeSelectScreen(name='modes'))
        self.sm.add_widget(LoadScreen(name='load'))
        self.sm.add_widget(BattleScreen(name='battle'))
        self.sm.add_widget(MapSelectScreen(name='map_select'))
        self.sm.add_widget(AvatarScreen(name='avatar'))
        self.sm.add_widget(EditNickScreen(name='edit_nick'))
        return self.sm

# ==================== ЭКРАН ГЛАВНОГО МЕНЮ ====================
class MainMenu(Screen):
    def on_enter(self):
        self.update_ui()
    
    def update_ui(self):
        data = PLAYER_DATA
        self.ids.nick_label.text = data.get('nickname', 'Игрок')
        self.ids.level_label.text = f"LVL {data.get('level', 1)}"
        exp = data.get('exp', 0)
        lvl = data.get('level', 1)
        need = lvl * 500
        self.ids.exp_label.text = f"{exp} / {need} XP"
        self.ids.gold_label.text = f"G {data.get('gold', 0)}"
        self.ids.silver_label.text = f"S {data.get('silver', 0)}"

class ProfileScreen(Screen):
    def on_enter(self):
        data = PLAYER_DATA
        k = data.get('kills', 0)
        d = data.get('deaths', 1)
        self.ids.kd_label.text = f"К/Д: {k / d:.2f}"
        self.ids.kills_label.text = f"Убийств: {k}"
        self.ids.deaths_label.text = f"Смертей: {d}"
        self.ids.accuracy_label.text = f"Точность: {data.get('accuracy', 0):.1f}%"
        self.ids.time_label.text = f"Время: {data.get('playtime', 0):.1f} ч"
    
    def go_back(self):
        self.manager.current = 'main'

class FriendsScreen(Screen):
    def on_enter(self):
        self.update_list()
    
    def update_list(self):
        self.ids.friends_list.clear_widgets()
        if not FRIENDS:
            self.ids.friends_list.add_widget(Label(text="Нет друзей"))
        for fid in FRIENDS:
            btn = Button(text=f"ID: {fid}", size_hint_y=None, height=40)
            self.ids.friends_list.add_widget(btn)
    
    def find_friend(self):
        uid = self.ids.search_input.text.strip()
        if not uid:
            self.ids.result_label.text = "Введите ID"
            return
        try:
            res = supabase.table('players').select('nickname').eq('id', uid).execute()
            if res.data:
                self.ids.result_label.text = f"Найден: {res.data[0]['nickname']}"
            else:
                self.ids.result_label.text = "Не найден"
        except:
            self.ids.result_label.text = "Ошибка"
    
    def go_back(self):
        self.manager.current = 'main'

class InventoryScreen(Screen):
    def on_enter(self):
        self.update_grid()
    
    def update_grid(self):
        self.ids.inventory_grid.clear_widgets()
        if not INVENTORY:
            self.ids.inventory_grid.add_widget(Label(text="Инвентарь пуст"))
        for item in INVENTORY:
            btn = Button(text=item.get('item_name', 'Неизвестно'), size_hint_y=None, height=50)
            self.ids.inventory_grid.add_widget(btn)
    
    def go_back(self):
        self.manager.current = 'main'

class ShopScreen(Screen):
    def on_enter(self):
        self.update_shop()
    
    def update_shop(self):
        self.ids.shop_grid.clear_widgets()
        for name, skins in CASE_SKINS.items():
            price = 300 if "Chameleon" not in name else 100
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            layout.add_widget(Label(text=f"{name} - G {price}"))
            btn = Button(text="Купить", size_hint_x=0.2)
            btn.bind(on_press=lambda x, n=name, p=price: self.buy_case(n, p))
            btn2 = Button(text="👁", size_hint_x=0.1)
            btn2.bind(on_press=lambda x, s=skins: self.preview_case(s))
            layout.add_widget(btn)
            layout.add_widget(btn2)
            self.ids.shop_grid.add_widget(layout)
    
    def buy_case(self, name, price):
        global PLAYER_DATA, INVENTORY
        if PLAYER_DATA.get('gold', 0) >= price:
            PLAYER_DATA['gold'] -= price
            save_profile(PLAYER_DATA)
            skins = CASE_SKINS.get(name, [])
            if skins:
                roll = random.random()
                rarity = "Common"
                for r, chance in RARITIES.items():
                    if roll < chance:
                        rarity = r
                        break
                item = random.choice(skins)
                INVENTORY.append({'player_id': PLAYER_ID, 'item_name': item, 'rarity': rarity})
                self.ids.status_label.text = f"Выпало: {item} [{rarity}]"
            self.update_shop()
        else:
            self.ids.status_label.text = "Не хватает G!"
    
    def preview_case(self, skins):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Содержимое:"))
        for s in skins[:10]:
            content.add_widget(Label(text=f"• {s}"))
        btn = Button(text="Закрыть", size_hint_y=0.1)
        popup = Popup(title="Осмотр", content=content, size_hint=(0.8, 0.6))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.current = 'main'

class MarketScreen(Screen):
    def on_enter(self):
        self.update_market()
    
    def update_market(self):
        self.ids.market_list.clear_widgets()
        try:
            res = supabase.table('market').select('*').eq('status', 'active').execute()
            lots = res.data if res.data else []
            if not lots:
                self.ids.market_list.add_widget(Label(text="Нет лотов"))
            for lot in lots:
                layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                layout.add_widget(Label(text=f"{lot['item_name']} - G {lot['price']}"))
                btn = Button(text="Купить", size_hint_x=0.2)
                btn.bind(on_press=lambda x, l=lot: self.buy_lot(l))
                layout.add_widget(btn)
                self.ids.market_list.add_widget(layout)
        except:
            self.ids.market_list.add_widget(Label(text="Ошибка"))
    
    def buy_lot(self, lot):
        global PLAYER_DATA, INVENTORY
        if PLAYER_DATA.get('gold', 0) >= lot['price']:
            PLAYER_DATA['gold'] -= lot['price']
            save_profile(PLAYER_DATA)
            INVENTORY.append({'player_id': PLAYER_ID, 'item_name': lot['item_name'], 'rarity': 'Rare'})
            supabase.table('market').update({'status': 'sold'}).eq('id', lot['id']).execute()
            self.ids.status_label.text = f"Куплен {lot['item_name']}"
            self.update_market()
        else:
            self.ids.status_label.text = "Не хватает G!"
    
    def go_back(self):
        self.manager.current = 'main'

class SettingsScreen(Screen):
    def on_enter(self):
        self.load_ui()
    
    def load_ui(self):
        s = SETTINGS
        self.ids.sound_slider.value = s.get('sound', 1.0)
        self.ids.music_slider.value = s.get('music', 1.0)
        self.ids.sens_slider.value = s.get('sensitivity', 2.61)
        self.ids.fov_slider.value = s.get('fov', 1.25)
    
    def save_settings(self):
        SETTINGS['sound'] = self.ids.sound_slider.value
        SETTINGS['music'] = self.ids.music_slider.value
        SETTINGS['sensitivity'] = self.ids.sens_slider.value
        SETTINGS['fov'] = self.ids.fov_slider.value
        try:
            supabase.table('players').update({'settings': SETTINGS}).eq('id', PLAYER_ID).execute()
        except:
            pass
        self.ids.status_label.text = "Сохранено!"
    
    def report_bug(self):
        webbrowser.open('https://t.me/StandXenon')
    
    def go_back(self):
        self.manager.current = 'main'

class ModeSelectScreen(Screen):
    def on_enter(self):
        self.update_modes()
    
    def update_modes(self):
        self.ids.modes_grid.clear_widgets()
        lvl = PLAYER_DATA.get('level', 1)
        for mode in MODES:
            btn = Button(
                text=f"{mode['name']}\n{'Требуется ' + str(mode['unlock']) + ' лвл' if mode['unlock'] > 0 else 'Доступен'}",
                size_hint_y=None, height=80
            )
            if mode['unlock'] <= lvl:
                btn.disabled = False
                btn.bind(on_press=lambda x, m=mode['name']: self.select_mode(m))
            else:
                btn.disabled = True
            self.ids.modes_grid.add_widget(btn)
    
    def select_mode(self, mode_name):
        global SELECTED_MODE
        SELECTED_MODE = mode_name
        self.manager.current = 'map_select'
    
    def create_online_room(self):
        online.create_room()
        self.ids.status_label.text = "Создание комнаты..."
        self.manager.current = 'battle'
    
    def go_back(self):
        self.manager.current = 'main'

class MapSelectScreen(Screen):
    def on_enter(self):
        self.update_maps()
    
    def update_maps(self):
        self.ids.maps_grid.clear_widgets()
        for map_name in MAPS:
            btn = Button(text=map_name, size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, m=map_name: self.select_map(m))
            self.ids.maps_grid.add_widget(btn)
    
    def select_map(self, map_name):
        global SELECTED_MAP
        SELECTED_MAP = map_name
        self.manager.current = 'load'
    
    def go_back(self):
        self.manager.current = 'modes'

class LoadScreen(Screen):
    def on_enter(self):
        tips = [
            "Не забывай броню!", "Целься в голову!", "Слушай шаги!",
            "Используй дым!", "Меняй позицию!", "Экономь деньги!"
        ]
        self.ids.tip_label.text = random.choice(tips)
        self.ids.mode_label.text = f"Режим: {SELECTED_MODE or 'Командный бой'}"
        self.ids.map_label.text = f"Карта: {SELECTED_MAP or 'Dust 2x2'}"
        Clock.schedule_once(self.start_battle, 4)
    
    def start_battle(self, dt):
        self.manager.current = 'battle'
    
    def go_back(self):
        self.manager.current = 'modes'

class BattleScreen(Screen):
    def on_enter(self):
        self.team = None
        self.round = 1
        self.gold = 800
        self.kills = 0
        self.deaths = 0
        self.ids.team_label.text = "Выберите команду"
        self.ids.round_label.text = "Раунд 1"
        self.ids.gold_label.text = "G 800"
        self.ids.status_label.text = ""
    
    def select_ct(self):
        self.team = 'CT'
        self.ids.team_label.text = "Оборона (CT)"
        self.start_round()
    
    def select_t(self):
        self.team = 'T'
        self.ids.team_label.text = "Атака (T)"
        self.start_round()
    
    def start_round(self):
        self.ids.round_label.text = f"Раунд {self.round}"
        self.ids.status_label.text = "Бой!"
        self.gold = 800 + (self.round - 1) * 100
        self.ids.gold_label.text = f"G {self.gold}"
        Clock.schedule_once(self.end_round, 10)
    
    def end_round(self, dt):
        global PLAYER_DATA
        victory = random.choice([True, False])
        if victory:
            reward_gold = 10
            reward_silver = random.randint(10, 50)
            self.ids.status_label.text = f"Победа! +{reward_gold} G, +{reward_silver} S"
            PLAYER_DATA['gold'] = PLAYER_DATA.get('gold', 0) + reward_gold
            PLAYER_DATA['silver'] = PLAYER_DATA.get('silver', 0) + reward_silver
            PLAYER_DATA['exp'] = PLAYER_DATA.get('exp', 0) + 150
            PLAYER_DATA['kills'] = PLAYER_DATA.get('kills', 0) + random.randint(1, 5)
            while PLAYER_DATA['exp'] >= PLAYER_DATA['level'] * 500:
                PLAYER_DATA['exp'] -= PLAYER_DATA['level'] * 500
                PLAYER_DATA['level'] += 1
        else:
            reward_silver = random.randint(0, 10)
            self.ids.status_label.text = f"Поражение... +{reward_silver} S"
            PLAYER_DATA['silver'] = PLAYER_DATA.get('silver', 0) + reward_silver
            PLAYER_DATA['exp'] = PLAYER_DATA.get('exp', 0) + 50
            PLAYER_DATA['deaths'] = PLAYER_DATA.get('deaths', 0) + random.randint(1, 3)
        save_profile(PLAYER_DATA)
        self.ids.gold_label.text = f"G {PLAYER_DATA.get('gold', 0)}"
        self.round += 1
        self.ids.team_label.text = "Выберите команду"
    
    def go_back(self):
        self.manager.current = 'main'

class AvatarScreen(Screen):
    def go_back(self):
        self.manager.current = 'main'

class EditNickScreen(Screen):
    def on_enter(self):
        self.ids.nick_input.text = PLAYER_DATA.get('nickname', '')
        self.ids.status_label.text = ""
    
    def save_nick(self):
        new_nick = self.ids.nick_input.text.strip()
        if not new_nick:
            self.ids.status_label.text = "Ник не может быть пустым!"
            return
        if len(new_nick) > 16:
            self.ids.status_label.text = "Максимум 16 символов!"
            return
        try:
            supabase.table('players').update({'nickname': new_nick}).eq('id', PLAYER_ID).execute()
            PLAYER_DATA['nickname'] = new_nick
            self.ids.status_label.text = "Сохранено!"
            self.manager.current = 'main'
        except:
            self.ids.status_label.text = "Ошибка или ник занят!"
    
    def go_back(self):
        self.manager.current = 'main'

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    Clock.schedule_once(lambda dt: online.connect(), 1)
    StandXenonApp().run()
