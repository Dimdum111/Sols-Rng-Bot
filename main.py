# Bot version: 1.1.0
from Config import auras, limbo_auras, BIOMES, GLOBAL_THRESHOLD, aura_gif_map, event_gif_map, start_msg, user_help_text, admin_help_text, changelogs_text
from dotenv import load_dotenv
import telebot
from telebot import types
import random
import json
import os
import threading
import time
import math
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

LOG_BOT_TOKEN = os.environ["LOG_BOT_TOKEN"]  # Токен бота Логера.
TOKEN = os.environ["TOKEN"] # Основной бот
TESTERS_BOT_TOKEN = os.environ["TESTERS_BOT_TOKEN"]

bot = telebot.TeleBot(TOKEN)
MaintanceActive = False

USER_DATA_FILE = "users_data_lines.json"
SAVE_FILE = "global_settings.json"
EVENT_FILE = "event_data.json"
BIOME_FILE = "biome_data.json"
PAGE_SIZE = 20

admin_ids = ["5298923430", "1876839608"]

# Словарь для хранения ожидающих подтверждения команд
# {uid: {"cmd": original_text, "action": callable}}
pending_confirmations = {}

def resolve_uid(uid_str, sender_uid):
    # Заменяет 'me' на uid отправителя.
    return sender_uid if uid_str.lower() == "me" else uid_str

user_locks = {}

def log_admin_action(admin_msg, action_text): # Логирует действие в файл и отправляет уведомление через второго бота
    # 1. Запись в файл UsedAdminCmds.txt
    now = datetime.now().strftime("%Y, %d.%m, %H:%M:%S")
    username = f"@{admin_msg.from_user.username}" if admin_msg.from_user.username else admin_msg.from_user.first_name
    log_entry = f"[{now}] [{username}] Used {action_text}, Userid: [{admin_msg.from_user.id}]\n\n"
    TestBot = ""
    with open("UsedAdminCmds.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
        if TOKEN == TESTERS_BOT_TOKEN: TestBot = "╚ ⚠️ THIS COMMAND WAS USED IN THE TEST BOT ╗"
        else: TestBot = ""
        notification_text = (
            "⚠️ Admin command notification\n"
            f"👤 Admin: {username}\n"
            f"🛠 Used: {action_text}\n"
            f"🆔 ID: {admin_msg.from_user.id}\n\n"
            f"{TestBot}"
        )
        def send_to_all():
            with data_lock:
                uids = list(data.get("auras", {}).keys())
            for user_id in uids:
                try:
                    url = f"https://api.telegram.org/bot{LOG_BOT_TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": user_id, "text": notification_text})
                except Exception as e:
                    print(f"Ошибка отправки через лог-бота пользователю {user_id}: {e}")
        threading.Thread(target=send_to_all, daemon=True).start()

# Загрузка данных события

def load_event_data():

    if os.path.exists(EVENT_FILE):
        try:
            with open(EVENT_FILE, "r", encoding="utf-8") as f:
                event_data = json.load(f)
                # Преобразуем строку времени обратно в datetime
                if "event_end_time" in event_data and event_data["event_end_time"]:
                    event_data["event_end_time"] = datetime.fromisoformat(event_data["event_end_time"])
                return event_data
        except:
            return {"event_active": False, "event_end_time": None, "event_multiplier": 2.0, "event_duration": 18000}
    return {"event_active": False, "event_end_time": None, "event_multiplier": 2.0, "event_duration": 18000}

def save_event_data():

    event_data_to_save = {
        "event_active": EVENT_DATA["event_active"],
        "event_end_time": EVENT_DATA["event_end_time"].isoformat() if EVENT_DATA["event_end_time"] else None,
        "event_multiplier": EVENT_DATA["event_multiplier"]
    }
    with open(EVENT_FILE, "w", encoding="utf-8") as f:
        json.dump(event_data_to_save, f, ensure_ascii=False)

# Загрузка данных биома

def load_biome_data():

    if os.path.exists(BIOME_FILE):
        try:
            with open(BIOME_FILE, "r", encoding="utf-8") as f:
                biome_data = json.load(f)
                # Преобразуем строку времени обратно в datetime
                if "biome_end_time" in biome_data and biome_data["biome_end_time"]:
                    biome_data["biome_end_time"] = datetime.fromisoformat(biome_data["biome_end_time"])
                return biome_data
        except:
            return {"current_biome": "Normal", "biome_end_time": None}
    return {"current_biome": "Normal", "biome_end_time": None}

def save_biome_data():

    biome_data_to_save = {
        "current_biome": BIOME_DATA["current_biome"],
        "biome_end_time": BIOME_DATA["biome_end_time"].isoformat() if BIOME_DATA["biome_end_time"] else None
    }
    with open(BIOME_FILE, "w", encoding="utf-8") as f:
        json.dump(biome_data_to_save, f, ensure_ascii=False)

# Инициализация данных события и биома

EVENT_DATA = load_event_data()

BIOME_DATA = load_biome_data()

# При запуске бота событие выключено по умолчанию

if not EVENT_DATA.get("event_multiplier"):

    EVENT_DATA = {
        "event_active": False,
        "event_end_time": None,
        "event_multiplier": 2.0,
        "event_duration": 18000  # 5 часов по умолчанию
    }
    save_event_data()

# Глобальные переменные для предметов и зелий

lucky_potion_active = False

# load data (глобальные настройки, которые не являются данными пользователя)

data = {}  # Инициализируем data как пустой словарь

# --- ЗАГРУЗКА ГЛОБАЛЬНЫХ ДАННЫХ (остается в формате JSON) ---

GLOBAL_DATA_FILE = SAVE_FILE

if os.path.exists(GLOBAL_DATA_FILE):

    print(f"[💾] Loading global data from {GLOBAL_DATA_FILE}...")
    try:
        with open(GLOBAL_DATA_FILE, "r", encoding="utf-8") as f:
            file_content = f.read()
            if file_content:
                data = json.loads(file_content)
            else:
                print(f"WARNING: Global data file {GLOBAL_DATA_FILE} is empty.")

    except json.JSONDecodeError as e:
        print(f"CRITICAL WARNING: Global data file {GLOBAL_DATA_FILE} corrupted. Error: {e}")
        print("Using empty structure for global data.")
        # При повреждении глобальных данных не падаем, но сбрасываем их

    except Exception as e:
        print(f"CRITICAL WARNING: Error loading global data: {e}")

# Убеждаемся, что ключ 'auras' (для данных пользователей) инициализирован пустым.

if "auras" not in data:

    data["auras"] = {}

# --- ЗАГРУЗКА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ---

if os.path.exists(USER_DATA_FILE):

    print(f"[💾] Loading users data from {USER_DATA_FILE}...")
    try:
        loaded_users_count = 0
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue

                try:
                    user_data = json.loads(line)
                    user_id = user_data.get("user_id")

                    if user_id:
                        # ВАЖНО: убедиться, что uid - строка, т.к. ключи словарей - строки
                        data["auras"][str(user_id)] = user_data
                        loaded_users_count += 1
                    else:
                        print(f"WARNING: Line {line_number + 1} in {USER_DATA_FILE} missing 'user_id'. Skipping.")

                except json.JSONDecodeError as e:
                    # Если одна строка повреждена, мы пропускаем ее, но продолжаем
                    print(f"WARNING: Corrupt JSON line {line_number + 1} in {USER_DATA_FILE}. Skipping this user.")
                    print(f"Error: {e}")

        print(f"[✓] Successfully loaded {loaded_users_count} users.")

    except Exception as e:
        # Если не смогли даже открыть файл (например, проблемы с правами)
        print(f"[⚠️] CRITICAL ERROR: Failed to open or read {USER_DATA_FILE}. All user data might be missing!!")
        print(f"[⚠️] Error: {e}")

else:

    print(f"User data file {USER_DATA_FILE} not found. Starting with empty user data.")
    data = {"auras": {}}

data_lock = threading.RLock()

save_file_lock = threading.Lock()

def save_data():

    """
    Высокопроизводительная и потокобезопасная функция сохранения.
    1. Быстро (под data_lock) копирует данные из памяти.
    2. Медленно (под save_file_lock) записывает копию на диск.
    """

    global_data_to_save = {}
    users_to_save = {}

    # === ЭТАП 1: Быстрое копирование данных ===
    # Блокируем data_lock только на время копирования словарей.
    # Это очень быстро и не будет тормозить auto-roll.
    try:
        with data_lock:
            global_data_to_save = {k: v for k, v in data.items() if k != "auras"}
            # .copy() здесь критически важен!
            users_to_save = data.get("auras", {}).copy()
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to copy data for saving: {e}")
        return  # Если не смогли скопировать, сохранять нечего

    # === ЭТАП 2: Медленная запись на диск ===
    # Блокируем save_file_lock, чтобы только один поток (autosave или админ)
    # мог писать в файл одновременно.
    with save_file_lock:

        # --- 1. СОХРАНЕНИЕ ГЛОБАЛЬНЫХ ДАННЫХ (из копии) ---
        GLOBAL_DATA_FILE = SAVE_FILE
        try:
            with open(GLOBAL_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(global_data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERROR saving global data to {GLOBAL_DATA_FILE}: {e}")

        # --- 2. СОХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ (из копии) ---
        TEMP_FILE = USER_DATA_FILE + ".tmp"
        try:
            with open(TEMP_FILE, "w", encoding="utf-8") as f:
                # Итерируемся по КОПИИ (users_to_save), а не по data
                for uid, user_data in users_to_save.items():
                    # Добавляем user_id в сам объект
                    user_data["user_id"] = str(uid)

                    json_line = json.dumps(user_data, ensure_ascii=False)
                    f.write(json_line + '\n')

            os.replace(TEMP_FILE, USER_DATA_FILE)

        except Exception as e:
            print(f"ERROR saving user data to {USER_DATA_FILE}: {e}")
            if os.path.exists(TEMP_FILE):
                try:
                    os.remove(TEMP_FILE)
                except Exception as e_rm:
                    print(f"ERROR removing temp file {TEMP_FILE}: {e_rm}")

AUTOSAVE_INTERVAL = 600  # Сохранять каждые 10 мин

def autosave_loop():

    # Периодически сохраняет все данные.
    print("[📂] Autosave thread started.")
    while True:
        time.sleep(AUTOSAVE_INTERVAL)
        try:
            # Просто вызываем нашу новую безопасную функцию
            save_data()
        except Exception as e:
            print(f"[Autosave] CRITICAL ERROR during autosave: {e}")

def get_user_data(user_id, user_name="User"):

    user_id = str(user_id)
    with data_lock:
        if "auras" not in data:
            data["auras"] = {}
        if user_id not in data["auras"]:
            data["auras"][user_id] = {
                "name": user_name,
                "user_luck": 1.0,
                "rolls": 0,
                "rarest": None,
                "auras": {},
                "inventory": [],
                "equipped": []
            }
        u = data["auras"].setdefault(user_id, {})
        u.setdefault("user_id", user_id)
        u.setdefault("name", user_name)
        u.setdefault("user_luck", 1.0)  # Это базовая удача
        u.setdefault("rolls", 0)
        u.setdefault("rarest", None)
        u.setdefault("auras", {})
        u.setdefault("inventory", [])
        u.setdefault("equipped", [])
        u.setdefault("notify_day_night", True)
        u.setdefault("notify_global", True)
        u.setdefault("potion_end_time", None)
        u.setdefault("potion_luck_bonus", 0.0)
        u.setdefault("godlike_potion_active", 0)
        u.setdefault("heavenly_potion_active", 0)
        u.setdefault("bound_potion_active", 0)
        u.setdefault("auto_roll_enabled", False)
        u.setdefault("pending_potion_amount", None)
        u.setdefault("auto_pin_rarity", None)
        u.setdefault("last_active", None)
        u.setdefault("forced_aura", None)
        u.setdefault("gif_rarity_threshold", 1000000)
        u.setdefault("DidIntro", False)
        #u.setdefault("codes", []) 
        # лимбо
        u.setdefault("limbo_unlocked", False)
        u.setdefault("in_limbo", False)
        u.setdefault("unknown_potion_end", None)
        u.setdefault("limbo_msg_sent", False)
        # другое

        return u

def get_calculated_luck(user):

    # Рассчитывает ОБЩУЮ удачу. В Лимбо зелья не работают.
    base_luck = user.get("user_luck", 1.0)
    item_bonus = 0.0

    # Перчатки работают везде
    equipped_item = next((item for item in user.get("equipped", []) if item in gear_items), None)
    if equipped_item:
        base_bonus = luck_bonuses.get(equipped_item, 0.0)
        item_bonus = base_bonus

        current_biome = BIOME_DATA["current_biome"]
        # Биомный бонус из WORKSHOP_ITEMS
        biome_info = WORKSHOP_ITEMS.get(equipped_item, {}).get("biome_bonus")
        if biome_info:
            biomes = biome_info["biome"].split("/")
            if current_biome in biomes:
                item_bonus = biome_info["bonus"]

    # Логика зелий
    potion_bonus = 0.0
    # Зелья работают ТОЛЬКО если мы НЕ в Лимбо
    if not user.get("in_limbo", False):
        potion_end_time_str = user.get("potion_end_time")
        if potion_end_time_str:
            try:
                potion_end_time = datetime.fromisoformat(potion_end_time_str)
                if potion_end_time > datetime.now():
                    potion_bonus = user.get("potion_luck_bonus", 0.0)
            except:
                pass

    total_luck = base_luck + item_bonus + potion_bonus # total_luck = ((base_luck + item_bonus + potion_bonus) * 2) * 1.2
    return max(1.0, total_luck)  # Удача не может быть меньше 1

def get_effective_luck(calculated_luck):

    # Возвращает удачу с учетом активного события
    if EVENT_DATA["event_active"] and EVENT_DATA["event_end_time"] and datetime.now() < EVENT_DATA["event_end_time"]:
        return calculated_luck * EVENT_DATA["event_multiplier"]
    return calculated_luck

def get_biome_multiplier(aura_name):

    # Возвращает множитель биома для конкретной ауры
    current_biome = BIOME_DATA["current_biome"]

    # Glitched ауры доступны ТОЛЬКО в Glitched биоме
    if aura_name in ["Oppression", "Glitch", "Fault"] and current_biome != "Glitched":
        return math.inf  # Сделать невозможным выпадение

    # Dreamspace ауры доступны только в Glitched и Dreamspace биомах
    if aura_name in ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"] and current_biome not in ["Glitched", "Dreamspace"]:
        return math.inf  # Сделать невозможным выпадение
    
    if aura_name == "Monarch" and current_biome not in ["Corruption", "Glitched"]:
        return math.inf
    
    if aura_name == "Leviathan" and current_biome not in ["Rainy", "Glitched"]:
        return math.inf
    
    if aura_name == "Borealis" and current_biome != "Dreamspace":
        return math.inf
    
    if aura_name == "Breakthrough" and current_biome == "Null":
        return math.inf

    biome_info = BIOMES[current_biome]

    # Glitched биом включает все множители
    if current_biome == "Glitched":
        for biome_name, info in BIOMES.items():
            if biome_name != "Normal" and aura_name in info["auras"]:
                return info["multiplier"]
        return 1

    # Dreamspace не дает множителя
    if current_biome == "Dreamspace":
        return 1

    # Для других биомов проверяем, относится ли аура к текущему биому
    if aura_name in biome_info["auras"]:
        return biome_info["multiplier"]

    return 1

def roll_aura(effective_luck, user):

    # Определяем, в каком мы мире
    in_limbo = user.get("in_limbo", False)

    if in_limbo:
        # === ЛОГИКА ЛИМБО: Rarity Threshold System ===
        # 1. Сортируем ауры от Редких (High) к Частым (Low), исключая Nothing
        sorted_limbo = sorted(
            [(k, v) for k, v in limbo_auras.items() if k != "Nothing"],
            key=lambda x: x[1],
            reverse=True
        )

        current_biome = BIOME_DATA["current_biome"]

        for aura, base_chance in sorted_limbo:
            # Пропуск аур, не подходящих под биом (для Glitched и Dreamspace)
            if aura in ["Oppression", "Glitch", "Fault"] and current_biome != "Glitched": continue
            if aura in ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"] and current_biome not in ["Glitched", "Dreamspace"]: continue
            if aura == "Monarch" and current_biome not in ["Corruption", "Glitched"]: continue
            if aura == "Leviathan" and current_biome not in ["Rainy", "Glitched"]: continue
            if aura == "Borealis" and current_biome != "Dreamspace": continue
            if aura == "Breakthrough" and current_biome == "Null": continue
            # Если снаружи Null биом, в Лимбо он не должен давать множитель x1000
            if current_biome == "Null":
                biome_multiplier = 1
            else:
                biome_multiplier = get_biome_multiplier(aura)

            adjusted_chance = base_chance / biome_multiplier

            # 1. ГАРАНТ
            if effective_luck >= adjusted_chance:
                return aura, adjusted_chance

            # 2. ПОПЫТКА РОЛЛА
            if random.uniform(0, adjusted_chance) <= effective_luck:
                return aura, adjusted_chance

        # 3. ЕСЛИ НИЧЕГО НЕ ВЫПАЛО В ЛИМБО
        return "Nothing", 1

    # === Luck logic (fixed) ===
    current_biome = BIOME_DATA["current_biome"]

    pool = []
    for aura, base_chance in auras.items():
        if aura in ["Oppression", "Glitch", "Fault"] and current_biome != "Glitched": continue
        if aura in ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"] and current_biome not in ["Glitched", "Dreamspace"]: continue
        if aura == "Monarch" and current_biome not in ["Corruption", "Glitched"]: continue
        if aura == "Leviathan" and current_biome not in ["Rainy", "Glitched"]: continue
        if aura == "Borealis" and current_biome != "Dreamspace": continue
        if aura == "Breakthrough" and current_biome == "Null": continue

        biome_multiplier = get_biome_multiplier(aura)
        adjusted_rarity = base_chance / biome_multiplier
        pool.append((aura, adjusted_rarity))

    # Sort rarest -> most common (highest rarity number first), matching original algorithm
    pool.sort(key=lambda x: x[1], reverse=True)

    for i, (aura, adjusted_rarity) in enumerate(pool):
        if i == len(pool) - 1:
            # Last (most common) aura is the guaranteed catch-all if everything above missed
            return aura, adjusted_rarity

        new_rarity = max(1, math.floor(adjusted_rarity / effective_luck + 0.5))
        if random.randint(1, new_rarity) == 1:
            return aura, adjusted_rarity

    # Should be unreachable, but just in case the pool was empty
    best = min(auras.items(), key=lambda x: x[1])
    return best[0], best[1]


def get_time_remaining():

    # Возвращает оставшееся время события в формате HH:MM:SS
    if not EVENT_DATA["event_active"] or not EVENT_DATA["event_end_time"]:
        return "00:00:00"

    remaining = EVENT_DATA["event_end_time"] - datetime.now()
    if remaining.total_seconds() <= 0:
        # Событие закончилось
        EVENT_DATA["event_active"] = False
        save_event_data()
        return "00:00:00"

    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    seconds = int(remaining.total_seconds() % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_biome_time_remaining():

    # Возвращает оставшееся время биома в формате MM:SS
    if not BIOME_DATA["biome_end_time"]:
        return "∞"

    remaining = BIOME_DATA["biome_end_time"] - datetime.now()
    if remaining.total_seconds() <= 0:
        # Биом закончился
        BIOME_DATA["current_biome"] = "Normal"
        BIOME_DATA["biome_end_time"] = None
        save_biome_data()
        return "00:00"

    minutes = int(remaining.total_seconds() // 60)
    seconds = int(remaining.total_seconds() % 60)
    return f"{minutes:02d}:{seconds:02d}"

def is_event_active():

    # Проверяет, активно ли событие
    if EVENT_DATA["event_active"] and EVENT_DATA["event_end_time"]:
        if datetime.now() < EVENT_DATA["event_end_time"]:
            return True
        else:
            # Событие закончилось
            EVENT_DATA["event_active"] = False
            save_event_data()
    return False

def check_biome_change():

    # Проверяет и меняет биом если нужно
    current_biome = BIOME_DATA["current_biome"]

    # Если текущий биом еще активен, ничего не делаем
    if BIOME_DATA["biome_end_time"] and datetime.now() < BIOME_DATA["biome_end_time"]:
        return

    # Если биом Normal, проверяем шанс на смену
    if current_biome == "Normal":
        for biome_name, biome_info in BIOMES.items():
            if biome_name == "Normal":
                continue

            # Glitched имеет особый шанс (только при смене биома)
            if biome_name == "Glitched":
                if random.random() < biome_info["chance"]:
                    set_biome(biome_name)
                    return
            else:
                # Обычные биомы проверяются каждую секунду
                if random.random() < biome_info["chance"]:
                    set_biome(biome_name)
                    return
    else:
        # Текущий биом закончился, возвращаемся к Normal
        set_biome("Normal")

def set_biome(biome_name):

    # Устанавливает новый биом
    old_biome = BIOME_DATA["current_biome"]
    BIOME_DATA["current_biome"] = biome_name
    if biome_name == "Normal":
        BIOME_DATA["biome_end_time"] = None
    else:
        duration = BIOMES[biome_name]["duration"]
        BIOME_DATA["biome_end_time"] = datetime.now() + timedelta(seconds=duration)

    save_biome_data()

    # Уведомляем всех пользователей о смене биома
    if biome_name != "Normal":
        biome_messages = {
            "Windy": "A refreshing and cool wind passes through the world..",
            "Snowy": "White snow and cold begin to cover the surroundings..",
            "Rainy": "Strong winds and showers sweep through the world..",
            "Sand Storm": "A harsh Sand Storm blocks your path...",
            "Hell": "A strong and violent energy of chaos overtakes the world..",
            "Heaven": "A hand of angel leads you into divine place...",
            "Starfall": "Beautiful and dreamy starlight pours into the world..",
            "Corruption": "Poisonous pollution spreads throughout the world..",
            "Null": "It's too dark here..",
            "Dreamspace": "You begin to feel sleepy...",
            "Glitched": "Unexpected error occurred. [Code 404]"
        }

        message = f"[{biome_name}]: {biome_messages.get(biome_name, '')}"
        threading.Thread(target=lambda: notify_all_users(message, message_type="biome"), daemon=True).start()

    # Уведомление о конце биома
    elif old_biome != "Normal":
        message = ""
        if old_biome == "Dreamspace":
            message = "[Dreamspace]: Waking up..."
        elif old_biome == "Glitched":
            message = "[Manager]: [Code 404] has resolved."

        if message:
            threading.Thread(target=lambda: notify_all_users(message, message_type="biome"), daemon=True).start()

def biome_loop():

    # Цикл смены биомов
    while True:
        check_biome_change()
        time.sleep(1)

def potion_spawn_loop():

    # Цикл спавна зелий
    global lucky_potion_active
    while True:
        time.sleep(60)  # Каждую минуту
        if not lucky_potion_active:
            if random.randint(1, 2) == 1:  # Шанс 1 к 2
                lucky_potion_active = True

def apply_potion_effect(user, amount):

    # Применяет эффект зелья к пользователю
    duration_seconds = amount * 60
    bonus_luck = 1  # +100% = +1.0

    current_end_time_str = user.get("potion_end_time")
    now = datetime.now()

    if current_end_time_str:
        try:
            current_end_time = datetime.fromisoformat(current_end_time_str)
            if current_end_time > now:
                # Зелье уже активно, добавляем время и удачу
                new_end_time = current_end_time + timedelta(seconds=duration_seconds)
                user["potion_end_time"] = new_end_time.isoformat()
                return
        except:
            pass  # Если ошибка формата, просто установим новое

    # Зелье неактивно или истекло
    user["potion_end_time"] = (now + timedelta(seconds=duration_seconds)).isoformat()
    user["potion_luck_bonus"] = bonus_luck

def auto_roll_thread(user_id, chat_id):

    while True:
        # Определяем клавиатуру ОДИН РАЗ
        disable_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        disable_markup.row(types.KeyboardButton("Disable Auto Roll"))

        # 1. Проверяем, должен ли поток все еще работать
        with data_lock:
            user = get_user_data(user_id)
            if not user.get("auto_roll_enabled", False):
                break

        # Переменные для хранения данных, чтобы использовать их ПОСЛЕ закрытия замка
        msg_text = ""
        gif_id_to_send = None
        should_pin = False
        global_msg_to_send = None

        try:
            # === НАЧАЛО БЛОКИРОВКИ ДАННЫХ ===
            with data_lock:
                user = get_user_data(user_id)

                # Проверка на случай если выключили пока ждали лок
                if not user.get("auto_roll_enabled", False):
                    break

                calculated_luck = get_calculated_luck(user)

                # Обработка зелий (ИЗМЕНЕНО: В Лимбо бонусы = 0)
                heavenly_bonus = 0
                bound_bonus = 0
                godlike_bonus = 0
                potion_msg = ""

                if not user.get("in_limbo", False):
                    if user.get("heavenly_potion_active", 0) > 0:
                        heavenly_bonus = 150000
                        user["heavenly_potion_active"] -= 1
                        potion_msg += f"\nHeavenly Potion left: {user['heavenly_potion_active']}"

                    if user.get("bound_potion_active", 0) > 0:
                        bound_bonus = 50000
                        user["bound_potion_active"] -= 1
                        potion_msg += f"\nPotion of Bound left: {user['bound_potion_active']}"

                    if user.get("godlike_potion_active", 0) > 0:
                        godlike_bonus = 400000
                        user["godlike_potion_active"] -= 1
                        potion_msg += f"\nGodlike Potion left: {user['godlike_potion_active']}"

                total_special_bonus = heavenly_bonus + bound_bonus + godlike_bonus
                calculated_luck += total_special_bonus
                effective_luck = get_effective_luck(calculated_luck)

                # Ролл
                forced_aura = user.get("forced_aura")
                forced_reason = user.get("forced_aura_reason")  # <--- Получаем причину

                if forced_aura:
                    aura = forced_aura
                    chance = auras.get(aura, limbo_auras.get(aura, 1000000))
                    user["forced_aura"] = None
                    user["forced_aura_reason"] = None  # <--- Очищаем причину
                else:
                    aura, chance = roll_aura(effective_luck, user)

                # Обновление статистики
                user["rolls"] += 1
                user["auras"][aura] = user["auras"].get(aura, 0) + 1

                current_val = auras.get(aura, limbo_auras.get(aura, 0))
                rarest_val = 0
                if user["rarest"]:
                    rarest_val = auras.get(user["rarest"], limbo_auras.get(user["rarest"], 0))
                if current_val > rarest_val:
                    user["rarest"] = aura

                # Подготовка данных для GIF (но не отправка!)
                gif_threshold = user.get("gif_rarity_threshold", 1000000)
                if aura in aura_gif_map and chance >= gif_threshold:
                    val = aura_gif_map[aura]
                    if val != "YOUR_ID_HERE":
                        gif_id_to_send = val

                # Подготовка данных для сообщения
                display_luck = int(effective_luck) if effective_luck == int(effective_luck) else round(effective_luck, 2)

                from_biome = ""
                current_biome = BIOME_DATA["current_biome"]
                glitched_auras = ["Oppression", "Glitch", "Fault"]
                dreamspace_auras = ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric", "Borealis"]
                base_chance = auras.get(aura, limbo_auras.get(aura, 1))

                if current_biome == "Dreamspace" and aura in dreamspace_auras:
                    from_biome = " [From Dreamspace!]"
                elif current_biome == "Glitched":
                    if aura in glitched_auras or aura in dreamspace_auras:
                        from_biome = " [From Glitched!]"
                    else:
                        biome_multiplier = get_biome_multiplier(aura)
                        if biome_multiplier > 1:
                            adjusted_chance = base_chance / biome_multiplier
                            if adjusted_chance < base_chance:
                                from_biome = " [From Glitched!]"
                elif current_biome != "Normal" and current_biome != "Dreamspace":
                    biome_multiplier = get_biome_multiplier(aura)
                    if biome_multiplier > 1:
                        adjusted_chance = base_chance / biome_multiplier
                        if adjusted_chance < base_chance:
                            from_biome = f" [From {current_biome}!]"

                # Генерация текста сообщения
                if aura == "Nothing":
                    msg_text = f"You rolled Nothing 1 in 1 🍀x{display_luck}\n\n « ⚪ Basic ⚪ »"
                elif aura == "NYCTOPHOBIA":
                    msg_text = f"👁️ You have experienced the literal nightmare. 👁️ 🍀x{display_luck}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
                elif aura == "Pixelation":
                    msg_text = f"🎮👾 You have become PIXELATED!! 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
                elif aura == "Luminosity":
                    msg_text = f"💫 You have been devoured by the blinding light. 💫 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
                elif aura == "Equinox":
                    msg_text = f"⚫ You have found [???????] between POSITIVE and NEGATIVE. ⚪ 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
                elif aura == "Monarch":
                    msg_text = f"👑 All hail, Your Majesty. 👑 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED+ ⚪⚫⚪ »"
                elif aura == "Breakthrough":
                    msg_text = f"you have found ???, chance of 1 in 1,999,999,999 [BREAKTHROUGH!] 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
                elif aura == "⭐":
                    msg_text = f"You rolled ⭐ 1 in 100 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "⭐⭐":
                    msg_text = f"You rolled ⭐⭐ 1 in 1000! 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "⭐⭐⭐":
                    msg_text = f"You rolled ⭐⭐⭐ 1 in 10000!! 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "Glitch":
                    msg_text = f"NO WAY! YOU ROLLED Glitch 1 IN 12210110 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "Oppression":
                    msg_text = f"YOU HAVE DISCOVERED Oppression WITH CHANCE OF 1 IN 220000000 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "Dreammetric":
                    msg_text = f"YOU HAVE DISCOVERED Dreammetric WITH CHANCE OF 1 IN 520000000 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                elif aura == "Leviathan":
                    msg_text = f"You have tamed the Ruler of Beneath. 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
                else:
                    chance_display = int(chance) if chance == int(chance) else chance
                    if chance > 99_999_998:
                        msg_text = f"YOU HAVE DISCOVERED {aura} WITH CHANCE OF 1 IN {chance_display} 🍀x{display_luck}{from_biome}\n\n« 🔴🔴 GLORIOUS 🔴🔴 »"
                    elif chance > 9_999_999:
                        msg_text = f"NO WAY! YOU ROLLED {aura} 1 IN {chance_display}!!!! 🍀x{display_luck}{from_biome}\n\n« 🔵 EXALTED 🔵 »"
                    elif chance > 999_999:
                        msg_text = f"OMG! You rolled {aura} 1 in {chance_display}!!! 🍀x{display_luck}{from_biome}\n\n« 🟠 MYTHIC 🟠 »"
                    elif chance > 99_998:
                        msg_text = f"Wow! You rolled {aura} 1 in {chance_display}!!! 🍀x{display_luck}{from_biome}\n\n« 🟢 Legendary 🟢 »"
                    elif chance > 10_000:
                        msg_text = f"You rolled {aura} 1 in {chance_display}!! 🍀x{display_luck}{from_biome}\n\n« 🟡 Unique 🟡 »"
                    elif chance > 1_000:
                        msg_text = f"You rolled {aura} 1 in {chance_display}! 🍀x{display_luck}{from_biome}\n\n« 🟣 Epic 🟣 »"
                    else:
                        msg_text = f"You rolled {aura} 1 in {chance_display} 🍀x{display_luck}{from_biome}\n\n« ⚪ Basic ⚪ »"
                msg_text += potion_msg

                # Проверка на закрепление (Auto Pin)
                pin_rarity = user.get("auto_pin_rarity")
                if pin_rarity and chance > pin_rarity:
                    should_pin = True

                # --- Добавляем причину админа в личное сообщение ---
                if forced_reason:
                    msg_text += f"\n\n(Was given by admin: {forced_reason})"

                # Подготовка Глобального сообщения
                if chance > GLOBAL_THRESHOLD or aura == "Glitch":
                    from_biome_global = ""
                    # Повторяем логику биома для глобалки (или используем уже готовую логику выше)
                    if current_biome == "Dreamspace" and aura in dreamspace_auras:
                        from_biome_global = " [From Dreamspace!]"
                    elif current_biome == "Glitched":
                        if aura in glitched_auras or aura in dreamspace_auras:
                            from_biome_global = " [From Glitched!]"
                        else:
                            if get_biome_multiplier(aura) > 1:  # Упрощенная проверка, так как уже считали выше
                                from_biome_global = " [From Glitched!]"
                    elif current_biome != "Normal" and current_biome != "Dreamspace":
                        if get_biome_multiplier(aura) > 1:
                            from_biome_global = f" [From {current_biome}!]"

                    chance_display = int(chance) if chance == int(chance) else chance
                    user_name = user.get("name", "User")
                    user_rolls = user.get("rolls", 0)

                    if aura == "Pixelation":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} Has Become PIXELATED!!\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "NYCTOPHOBIA":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} has experienced the literal nightmare.\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Luminosity":
                        global_msg_to_send = f"💫GLOBAL💫\nThe blinding light has devoured {user_name}.\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Leviathan":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} has tamed the Ruler of Beneath.\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Equinox":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} Has Found [???????] Between POSITIVE and NEGATIVE.\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Monarch":
                        global_msg_to_send = f"💫GLOBAL💫\nAll hail, The {user_name}.\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Breakthrough":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} has found ???, chance of 1 in {chance_display} [BREAKTHROUGH!]{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    elif aura == "Glitch":
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} HAS ROLLED {aura}\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"
                    else:
                        global_msg_to_send = f"💫GLOBAL💫\n{user_name} Has rolled {aura}\n1 in {chance_display}{from_biome_global}\nRolled at: {user_rolls}\nWith luck of: x{display_luck}"

            # === КОНЕЦ БЛОКИРОВКИ ДАННЫХ ===
            # (Мы вышли из with data_lock, теперь другие юзеры могут пользоваться ботом, пока этот спит)

            # 1. Отправка GIF (и сон)
            if gif_id_to_send:
                try:
                    bot.send_animation(chat_id, gif_id_to_send, reply_markup=disable_markup)
                    time.sleep(10)
                except Exception as e:
                    print(f"Error sending GIF: {e}")

            # 2. Отправка сообщения о ролле
            try:
                sent_msg = bot.send_message(chat_id, msg_text, reply_markup=disable_markup)
                # 3. Закрепление
                if should_pin:
                    try:
                        bot.pin_chat_message(chat_id, sent_msg.message_id, disable_notification=True)
                    except:
                        pass
            except Exception as e:
                # Если не удалось отправить сообщение, возможно юзер заблочил бота, выключаем авторолл
                print(f"Error sending msg to {user_id}: {e}")
                if "429" in str(e):
                    time.sleep(30)
                    continue
                # --- Добавляем причину админа в глобальное сообщение ---
                if forced_reason and global_msg_to_send:
                    global_msg_to_send += f"\n(Was given by admin: {forced_reason})"
                with data_lock:
                    u = get_user_data(user_id)
                    u["auto_roll_enabled"] = False
                    save_data()
                break

            # 4. Отправка глобального сообщения
            if global_msg_to_send:
                threading.Thread(target=lambda: notify_all_users(global_msg_to_send, message_type="global"),
                                 daemon=True).start()
        
        except Exception as e:
            print(f"CRITICAL Error in auto-roll thread for {user_id}: {e}, Continuing anyways.")
            if "429" in str(e):
                time.sleep(30) # If error is 429 We wait some time instead of disabling auto-roll.
                continue
            try:
                with data_lock:
                    u = get_user_data(user_id)
                    u["auto_roll_enabled"] = False
                    save_data() # added this to ensure we don't lose progress if something goes wrong.
            except:
                pass
            break
        time.sleep(1.25)

def restart_auto_rollers():

    print("[🎲] Checking for active auto-rollers...")
    with data_lock:
        # Копируем данные, чтобы не держать лок во время запуска потоков
        users_data = data.get("auras", {}).copy()

    for uid, user_data in users_data.items():
        if user_data.get("auto_roll_enabled", False):
            print(f"Restarting auto-roll for user {uid}")
            # ID пользователя в Telegram - это и есть ID чата для личных сообщений
            chat_id = uid
            threading.Thread(target=auto_roll_thread, args=(uid, chat_id), daemon=True).start()

def main_menu(user_id=None):  # Добавь user_id, если его нет, или получай внутри

    # (Чтобы это работало красиво, лучше передавать user_id в main_menu везде, где оно вызывается)
    # Но для упрощения, можно получать данные внутри, если user_id известен

    # --- НОВАЯ ЛОГИКА ---
    in_limbo = False
    limbo_unlocked = False  # По умолчанию
    if user_id:
        u = get_user_data(str(user_id))
        in_limbo = u.get("in_limbo", False)
        limbo_unlocked = u.get("limbo_unlocked", False)  # Получаем статус разблокировки
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🎲 Roll"))

    markup.row(types.KeyboardButton("💫 Auras"), types.KeyboardButton("📊 Stats"))
    markup.row(types.KeyboardButton("🏆 Leaderboard"), types.KeyboardButton("📝 Change Logs"))
    markup.row(types.KeyboardButton("🛠️ Workshop"), types.KeyboardButton("🎒 Inventory"))
    markup.row(types.KeyboardButton("🧪 Potions"))
    markup.row(types.KeyboardButton("⚙️ Settings"), types.KeyboardButton("📜 Credits"))

    # --- ИЗМЕНЕННАЯ ЛОГИКА КНОПОК ---
    if user_id:  # Проверяем, что user_id вообще есть
        if in_limbo:
            # Если ВНУТРИ Лимбо, показываем кнопку ВЫХОДА
            markup.row(types.KeyboardButton("🌌 Exit The Limbo"))
        elif limbo_unlocked:
            # Если НЕ внутри, но Лимбо РАЗБЛОКИРОВАН, показываем кнопку ВХОДА
            markup.row(types.KeyboardButton("🌌 Enter The Limbo"))
    # --- КОНЕЦ ИЗМЕНЕННОЙ ЛОГИКИ ---

    if lucky_potion_active and not in_limbo:  # <-- Зелья не спавнятся в Лимбо
        markup.row(types.KeyboardButton("🍀 Lucky Potion spawned!"))

    return markup

def back_menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("⬅️ Back"))
    return markup

user_pages = {}

user_last_command = {}
user_current_menu = {}

def paginate_list(items, page):

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = items[start:end]
    has_next = len(items) > end
    has_prev = page > 0
    return page_items, has_prev, has_next

def send_paginated_list(chat_id, uid, items):

    page = user_pages.get(uid, 0)
    page_items, has_prev, has_next = paginate_list(items, page)
    text = "\n".join(page_items) or "Nothing to show."
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    nav_buttons = []
    if has_prev: nav_buttons.append(types.KeyboardButton("⬅️ Previous page"))
    if has_next: nav_buttons.append(types.KeyboardButton("➡️ Next page"))
    if nav_buttons: markup.row(*nav_buttons)
    markup.row(types.KeyboardButton("⬅️ Back"))
    bot.send_message(chat_id, text, reply_markup=markup)

def redo_last_list(uid, chat_id):

    cmd = user_last_command.get(uid)
    if not cmd:
        return
    if cmd == "Auras":
        user = get_user_data(uid)
        aura_list = [
            f"{a} ✨ x{user['auras'].get(a, 0)}" if a in user.get("auras", {}) else f"🔒 LOCKED"
            for a in auras]
        send_paginated_list(chat_id, uid, aura_list)
    elif cmd == "LeaderboardRoll":
        leaderboard = [(u.get("name", "User"), u.get("rolls", 0)) for u in data["auras"].values()]
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        strings = [f"{i + 1}. {name} — {rolls} rolls" for i, (name, rolls) in enumerate(leaderboard)]
        send_paginated_list(chat_id, uid, strings)
    elif cmd == "LeaderboardRNG":
        leaderboard = []
        for u in data["auras"].values():
            rarest_aura = u.get("rarest")
            if rarest_aura and rarest_aura in auras:
                leaderboard.append((u.get("name", "User"), rarest_aura, auras[rarest_aura]))
        leaderboard.sort(key=lambda x: x[2], reverse=True)
        strings = [f"{i + 1}. {name} — {aura}" for i, (name, aura, _) in enumerate(leaderboard)]
        send_paginated_list(chat_id, uid, strings)

# --- Start ---

@bot.message_handler(commands=["start"])

def start(msg):
    uid = str(msg.from_user.id)
    name = msg.from_user.first_name or "User"
    user = get_user_data(uid, name)
    
    if user['DidIntro'] == False:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_continue = types.InlineKeyboardButton("continue", callback_data="btn_continue", style="success")
        markup.add(btn_continue)
        bot.send_message(msg.chat.id, start_msg, parse_mode="HTML", reply_markup=markup)
        user['DidIntro'] = True
        save_data()
        return
    
    save_data()
    user_handle = name
    if msg.from_user.username:
        user_handle = f"@{msg.from_user.username}"

    # Добавляем информацию о событии и биоме в приветственное сообщение
    event_info = ""
    MaintanceText = ""
    if is_event_active():
        event_info = f"\n\n🎉 X{EVENT_DATA['event_multiplier']} LUCK EVENT ACTIVE! 🎉\nTime left: {get_time_remaining()}"
        
    if MaintanceActive:
        MaintanceText = f"\n\n⚠️ Sol's rng bot is Going down for Scheduled Maintenance soon."

    biome_info = f"\nBIOME: {BIOME_DATA['current_biome']}"
    if BIOME_DATA['current_biome'] != "Normal":
        biome_info += f" (ends in: {get_biome_time_remaining()})"

    bot.send_message(msg.chat.id,
                     f"Welcome to Sol's RNG 🎰\nTime: {'DAYTIME ☀️' if is_day else 'NIGHTTIME 🌙'}{biome_info}{event_info}{MaintanceText}",
                     reply_markup=main_menu(uid))

# --- Day/Night Cycle ---

is_day = True

auras_default = auras.copy()

def apply_day_chances():

    # Сбрасывает ауры к дневным шансам.
    global auras
    auras = auras_default.copy()
    # День - Solar активнее, Lunar слабее
    if "Solar" in auras:
        auras["Solar"] = 5000
    if "Solar : Solstice" in auras:
        auras["Solar : Solstice"] = 500000
    # Остальные возвращаем в дневные значения
    if "Lunar" in auras:
        auras["Lunar"] = 50000
    if "Lunar : Full Moon" in auras:
        auras["Lunar : Full Moon"] = 5000000
    if "Twilight" in auras:
        auras["Twilight"] = 6000000
    if "Melodic : Serenade" in auras:
        auras["Melodic : Serenade"] = 77000000
    if "Dreamer" in auras:
        auras["Dreamer"] = 315000000
    if "Twilight : Iridescent Memory" in auras:
        auras["Twilight : Iridescent Memory"] = 60000000
    if "Twilight : Withering Grace" in auras:
        auras["Twilight : Withering Grace"] = 180000000
    if "Dream Catcher" in auras:
        auras["Dream Catcher"] = 999999999999999999

def apply_night_chances():

    # Устанавливает ночные шансы.
    global auras
    auras = auras_default.copy()
    # Ночь - Lunar/Twilight активнее, Solar слабее
    if "Lunar" in auras:
        auras["Lunar"] = 5000
    if "Lunar : Full Moon" in auras:
        auras["Lunar : Full Moon"] = 500000
    if "Twilight" in auras:
        auras["Twilight"] = 600000
    if "Melodic : Serenade" in auras:
        auras["Melodic : Serenade"] = 7700000
    if "Dreamer" in auras:
        auras["Dreamer"] = 31500000
    if "Twilight : Iridescent Memory" in auras:
        auras["Twilight : Iridescent Memory"] = 6000000
    if "Twilight : Withering Grace" in auras:
        auras["Twilight : Withering Grace"] = 18000000
    # Solar теряет силу ночью
    if "Solar" in auras:
        auras["Solar"] = 50000
    if "Solar : Solstice" in auras:
        auras["Solar : Solstice"] = 5000000
    if "Dream Catcher" in auras:
        auras["Dream Catcher"] = 2222222222

def day_night_cycle():

    global is_day
    while True:
        if is_day:
            # Сейчас день → станет ночь
            time.sleep(150)
            is_day = False
            apply_night_chances()
            threading.Thread(target=lambda: notify_all_users("🌙 NIGHTTIME", message_type="day_night"),
                             daemon=True).start()
        else:
            # Сейчас ночь → станет день
            time.sleep(150)
            is_day = True
            apply_day_chances()
            threading.Thread(target=lambda: notify_all_users("☀ DAYTIME", message_type="day_night"),
                             daemon=True).start()

threading.Thread(target=day_night_cycle, daemon=True).start()

threading.Thread(target=biome_loop, daemon=True).start()

threading.Thread(target=potion_spawn_loop, daemon=True).start()

threading.Thread(target=autosave_loop, daemon=True).start()

user_pages = {}

user_last_command = {}

"""
    Отправляет сообщение всем пользователям с учетом их настроек.
    message_type: 'default', 'global', 'day_night', 'biome'
    pin: Если True, сообщение будет закреплено
"""
def notify_all_users(message, message_type="default", pin=False):
    with data_lock:
        users_data = data.get("auras", {}).copy()

    def send_one(uid, user_data):
        try:
            if message_type == "day_night" and not user_data.get("notify_day_night", True):
                return
            if message_type == "global" and not user_data.get("notify_global", True):
                return
            sent_msg = bot.send_message(uid, message, parse_mode="HTML")
            if pin:
                try:
                    bot.pin_chat_message(uid, sent_msg.message_id, disable_notification=False)
                except:
                    pass
        except:
            pass

    with ThreadPoolExecutor(max_workers=30) as executor:
        for uid, user_data in users_data.items():
            executor.submit(send_one, uid, user_data)


def notify_all_users_gif(gif, pin=False):
    with data_lock:
        users_data = data.get("auras", {}).copy()

    def send_one_gif(uid):
        try:
            sent_msg = bot.send_animation(uid, gif)
            if pin:
                try:    
                    bot.pin_chat_message(uid, sent_msg.message_id, disable_notification=False)
                except:
                    pass
        except:
            pass

    with ThreadPoolExecutor(max_workers=30) as executor:
        for uid in users_data.items():
            executor.submit(send_one_gif, uid)
            


threading.Thread(target=lambda: notify_all_users("🟢 Bot online", message_type="default"), daemon=True).start()

@bot.message_handler(commands=["activeplayers"])
def active_players(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ You don't have permission to use this command.")
        return

    now = datetime.now()
    windows = {"Last 30 seconds": 30/86400, "Last 1 minute": 1/1440, "Last 5 minutes": 5/1440, "Last 1 hour": 1/24, "Last 24 hours": 1, "Last 7 days": 7, "Last 30 days": 30}
    counts = {label: 0 for label in windows}
    total_users = 0
    never_active = 0

    for user_info in data["auras"].values():
        total_users += 1
        last_active_str = user_info.get("last_active")
        if not last_active_str:
            never_active += 1
            continue
        try:
            last_active = datetime.fromisoformat(last_active_str)
        except Exception:
            continue
        days_ago = (now - last_active).total_seconds() / 86400
        for label, days in windows.items():
            if days_ago <= days:
                counts[label] += 1

    report = f"📊 Active Players\n\nTotal registered: {total_users}\nNever recorded (pre-tracking): {never_active}\n\n"
    for label in windows:
        report += f"{label}: {counts[label]}\n"
    bot.send_message(msg.chat.id, report)


"""Scheduled Maintenance
Starts a Scheduled Maintenance in a threading, and sets MaintanceActive to True
so in main menu there will be a notification about Maintenance.
at the end of a countdown it saves users_data and stops polling."""
def ScheduledMaintanceMsgs():
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 1 hour!", message_type="default", pin=True)
    time.sleep(1800) #1800
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 30 minutes!", message_type="default", pin=True)
    time.sleep(1200) #1200
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 10 minutes!", message_type="default", pin=True)
    time.sleep(300) #300
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 5 minutes!", message_type="default", pin=True)
    time.sleep(60) #60
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 4 minutes!", message_type="default", pin=True)
    time.sleep(60) #60
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 3 minutes!", message_type="default", pin=True)
    time.sleep(60) #60
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 2 minutes!", message_type="default", pin=True)
    time.sleep(60) #60
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance In 1 minute!", message_type="default", pin=True)
    time.sleep(60) #60
    notify_all_users("⏱️ | Scheduled Maintenance\nSol's rng bot is going down for Scheduled Maintenance Right now.", message_type="default", pin=True)
    notify_all_users(f"━━━━━━━━━━━━━━━\n🔴 BOT OFFLINE\n💬 Reason: Scheduled Maintenance\n━━━━━━━━━━━━━━━", message_type="default", pin=True)
    save_data()
    bot.stop_polling()
@bot.message_handler(commands=['ScheduledMaintenance'])

def ScheduledMaintance(msg):
    global MaintanceActive
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    bot.send_message(msg.chat.id, "⏱️ Starting Scheduled Maintance")
    threading.Thread(target=ScheduledMaintanceMsgs, daemon=True).start()
    MaintanceActive = True
    return MaintanceActive

"""Profile command.
Accepts an user id or 'me'
and shows a profile. ('me' shows yourself)"""
@bot.message_handler(commands=["profile"])
def profile(msg):
    parts = msg.text.split()
    if len(parts) != 2:
        bot.send_message(msg.chat.id, f"💫 Usage: /profile <User_id|me>")
        return
    if parts[1] == "me":
        parts[1] = str(msg.from_user.id)
    user_info = data["auras"].get(parts[1])
    if not user_info:
        bot.send_message(msg.chat.id, f"💫 User id is not found in our database!")
        return
    # showing the info
    bot.send_message(msg.chat.id,
                     f"┍👤 Profile\n"
                     f"┃⭐ Username: {user_info.get('name')}\n"
                     f"┃🆔 Id: {user_info.get('user_id')}\n"
                     f"┃🎲 Rolls: {user_info.get('rolls')}\n"
                     f"┃🔄 Auto Roll Enabled: {user_info.get('auto_roll_enabled')}\n"
                     f"┃💎 Rarest: {user_info.get('rarest')}\n"
                     f"┕🍀 Luck: x{user_info.get('user_luck')}")
"""
CITADEL OF ORDER event!
CitadelOfOrderMessages Contains all messages that should be send after the command to all users.
It uses notify_all_users function that notifies all users in Users_data_lines.json.
It called after using /CitadelOfOrder command from CitadelOfOrderEvent function.
"""
def CitadelOfOrderMessages():
    cutscene_link = event_gif_map.get("citadel", "https://t.me/solsrngbotcutscenes/228")
    notify_all_users_gif(cutscene_link)
    notify_all_users("Every life commit sins.", message_type="default")
    time.sleep(2.5)
    notify_all_users("Wouldn't you agree?", message_type="default")
    time.sleep(2.5)
    notify_all_users("Prepare.", message_type="default")
    time.sleep(2.5)
    notify_all_users("MUST\n<b>OBEY</b>\nORDER", message_type="default")   
    time.sleep(2)
    notify_all_users("The judgement.", message_type="default")
    time.sleep(2)
    notify_all_users("JUSTICE\n<b>RULES\nTHE</b>\nWORLD", message_type="default")
    time.sleep(1)
    notify_all_users("💫", message_type="default")
    time.sleep(5)
    notify_all_users("EDICT\n~ Judge of Equilibrium ~", message_type="default")
    _do_luck_event_start() # Start luck event

"""
CitadelOfOrderEvent - Handles the event, called after using /CitadelOfOrder command!
It checks if user is in admin list if not says "❌ No permission."
If user IS admin it calls CitadelOfOrderMessages function.
"""
@bot.message_handler(commands=["CitadelOfOrder"])
def CitadelOfOrderEvent(msg):
    chatid = str(msg.chat.id)
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(chatid, "❌ No permission.")
        return
    bot.send_message(chatid, "✨ Starting...")
    log_admin_action(msg, msg.text)
    # Set luck, Set event duration, disable it, and reset End time
    EVENT_DATA["event_multiplier"] = 1.2
    EVENT_DATA["event_duration"] = 3600
    EVENT_DATA["event_active"] = False
    EVENT_DATA["event_end_time"] = None
    threading.Thread(target=CitadelOfOrderMessages, daemon=True).start()

@bot.message_handler(commands=["setluck"])

def setluck(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) != 3:
        bot.send_message(msg.chat.id, "Usage: /setluck <user_id|me> <value>")
        return
    target = resolve_uid(parts[1], uid)
    try:
        val = float(parts[2])
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Value must be a number.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_setluck(target, val)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: set luck for {target_name} ({target}) to x{val}?", reply_markup=markup)

def _do_setluck(target, val):
    u = get_user_data(target)
    u["user_luck"] = val
    save_data()
    return f"✅ Base luck for {target} set to x{val}"

# setAura command
@bot.message_handler(commands=["setAura"])
def set_aura_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) < 5:
        bot.send_message(msg.chat.id, "Usage: /setAura <user_id|me> <aura_name> <+/-/=> <amount>")
        return
    target = resolve_uid(parts[1], uid)
    operation = parts[-2]
    try:
        amount = int(parts[-1])
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Amount must be a number.")
        return
    aura_name = " ".join(parts[2:-2])
    if not aura_name or (aura_name not in auras and aura_name not in limbo_auras):
        bot.send_message(msg.chat.id, "❌ Invalid aura name.")
        return
    if operation not in ("+", "-", "="):
        bot.send_message(msg.chat.id, "❌ Invalid operation. Use +, -, or =.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_set_aura(target, aura_name, operation, amount)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: {operation}{amount} {aura_name} for {target_name} ({target})?", reply_markup=markup)

def _do_set_aura(target_uid, aura_name, operation, amount):
    user = get_user_data(target_uid)
    current = user.get("auras", {}).get(aura_name, 0)
    if operation == "=":
        new_count = max(0, amount)
    elif operation == "+":
        new_count = current + amount
    else:
        new_count = max(0, current - amount)
    user.setdefault("auras", {})[aura_name] = new_count
    save_data()
    target_name = user.get("name", target_uid)
    return f"✅ {aura_name} for {target_name}: {operation}{amount} → now {new_count}"

@bot.message_handler(commands=["giveMeAllAuras"])

def give_me_all_auras_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) != 2:
        bot.send_message(msg.chat.id, "Usage: /giveMeAllAuras <amount>")
        return
    try:
        amount = int(parts[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Amount must be a positive number.")
        return
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_give_me_all_auras(uid, amount)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: give yourself ALL auras x{amount}? This may break game balance!", reply_markup=markup)

def _do_give_me_all_auras(uid, amount):
    user = get_user_data(uid)
    all_aura_names = list(auras.keys()) + list(limbo_auras.keys())
    with data_lock:
        user_auras = user.setdefault("auras", {})
        for aura_name in all_aura_names:
            user_auras[aura_name] = user_auras.get(aura_name, 0) + amount
    save_data()
    return f"✅ Added {amount} of all auras to your inventory."

# --- ADMIN COMMAND: /giveItem ---

@bot.message_handler(commands=["giveItem"])

def give_item(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) < 3:
        bot.send_message(msg.chat.id, "Usage: /giveItem <user_id|me> <Item Name> [amount]")
        return
    target = resolve_uid(parts[1], uid)
    try:
        amount = int(parts[-1])
        item_name = " ".join(parts[2:-1]) if len(parts) >= 4 else parts[2]
        if len(parts) < 4:
            amount = 1
    except ValueError:
        item_name = " ".join(parts[2:])
        amount = 1
    if amount <= 0 or not item_name:
        bot.send_message(msg.chat.id, "❌ Invalid item or amount.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_give_item(target, item_name, amount)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: give {amount}x {item_name} to {target_name} ({target})?", reply_markup=markup)

def _do_give_item(target_uid, item_name, amount):
    user = get_user_data(target_uid)
    inv = user.setdefault("inventory", [])
    for _ in range(amount):
        inv.append(item_name)
    save_data()
    return f"✅ Added {amount}x {item_name} to {user.get('name', target_uid)}"

@bot.message_handler(commands=["setRolls"])

def set_rolls_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) != 4:
        bot.send_message(msg.chat.id, "Usage: /setRolls <user_id|me> <+/-/=> <amount>")
        return
    target = resolve_uid(parts[1], uid)
    operation = parts[2]
    try:
        amount = int(parts[3])
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Amount must be a number.")
        return
    if operation not in ("+", "-", "="):
        bot.send_message(msg.chat.id, "❌ Invalid operation. Use +, -, or =.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_set_rolls(target, operation, amount)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: set rolls for {target_name} ({target}): {operation}{amount}?", reply_markup=markup)

def _do_set_rolls(target_uid, operation, amount):
    user = get_user_data(target_uid)
    current = user.get("rolls", 0)
    if operation == "=":
        new_rolls = max(0, amount)
    elif operation == "+":
        new_rolls = current + amount
    else:
        new_rolls = max(0, current - amount)
    user["rolls"] = new_rolls
    save_data()
    return f"✅ Rolls for {user.get('name', target_uid)}: now {new_rolls}"

@bot.message_handler(commands=["addAuraQueue"])

def add_aura_queue(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(msg.chat.id, "Usage: /addAuraQueue <user_id|me> <aura_name>")
        return
    target = resolve_uid(parts[1], uid)
    aura_name = parts[2]
    if aura_name not in auras:
        bot.send_message(msg.chat.id, f"❌ Aura '{aura_name}' not found.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_add_aura_queue(target, aura_name)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: {target_name} ({target}) will roll {aura_name} on next roll?", reply_markup=markup)

def _do_add_aura_queue(target_uid, aura_name):
    user = get_user_data(target_uid)
    user["forced_aura"] = aura_name
    save_data()
    return f"✅ {user.get('name', target_uid)} will roll {aura_name} on their next roll."

@bot.message_handler(commands=["setmyluck"])

def set_my_luck(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) != 2:
        bot.send_message(msg.chat.id, "Usage: /setmyluck <value>")
        return
    try:
        val = float(parts[1])
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Value must be a number.")
        return
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_setluck(uid, val)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: set your luck to x{val}?", reply_markup=markup)

@bot.message_handler(commands=["sayPin"])

def say_pin_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    if len(msg.text.split()) < 2:
        bot.send_message(msg.chat.id, "Usage: /sayPin <message>")
        return
    message = msg.text.split(" ", 1)[1]
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_say(message, msg, pin=True)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: send and PIN to ALL users:\n\n{message}", reply_markup=markup)

@bot.message_handler(commands=["addAuraQueueReason"])

def add_aura_queue_reason(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(msg.chat.id, "Usage: /addAuraQueueReason <user_id|me> <aura_name> <reason>")
        return
    target = resolve_uid(parts[1], uid)
    rest_text = parts[2]
    found_aura = None
    reason_text = ""
    for aura in sorted(auras.keys(), key=len, reverse=True):
        if rest_text.startswith(aura):
            found_aura = aura
            possible_reason = rest_text[len(aura):].strip().strip('"')
            reason_text = possible_reason
            break
    if not found_aura:
        bot.send_message(msg.chat.id, f"❌ Could not identify aura in: '{rest_text}'.")
        return
    if not reason_text:
        bot.send_message(msg.chat.id, "❌ You must provide a reason.")
        return
    target_name = get_user_data(target).get("name", target)
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_add_aura_queue_reason(target, found_aura, reason_text)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: {target_name} ({target}) will roll {found_aura}\nReason: {reason_text}", reply_markup=markup)

def _do_add_aura_queue_reason(target_uid, aura_name, reason_text):
    user = get_user_data(target_uid)
    user["forced_aura"] = aura_name
    user["forced_aura_reason"] = reason_text
    save_data()
    return f"✅ {user.get('name', target_uid)} will roll {aura_name} (Reason: {reason_text})"

@bot.message_handler(commands=["say"])

def say_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    if len(msg.text.split()) < 2:
        bot.send_message(msg.chat.id, "Usage: /say <message>")
        return
    message = msg.text.split(" ", 1)[1]
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_say(message, msg, pin=False)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: send to ALL users:\n\n{message}", reply_markup=markup)

def _do_say(message, msg, pin=False):
    threading.Thread(target=lambda: notify_all_users(f"{message} \n\n   ✧ {msg.from_user.username} ╝", message_type="global", pin=pin), daemon=True).start()
    return "✅ Sent to all users." + (" Pinned." if pin else "")


# Новые админские команды для управления событием

@bot.message_handler(commands=["luckEventStop"])

def luck_event_stop(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_luck_event_stop()
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, "⚠️ Confirm: stop luck event?", reply_markup=markup)

def _do_luck_event_stop():
    EVENT_DATA["event_active"] = False
    save_event_data()
    threading.Thread(
        target=lambda: notify_all_users("🔴 LUCK EVENT STOPPED!\nYour luck is now back to normal.", message_type="default"),
        daemon=True
    ).start()
    return "✅ Luck event stopped!"

@bot.message_handler(commands=["luckEventStart"])

def luck_event_start(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    if not EVENT_DATA.get("event_duration"):
        bot.send_message(msg.chat.id, "❌ No event settings. Use /luckEventChange first.")
        return
    mult = EVENT_DATA["event_multiplier"]
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_luck_event_start()
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: start x{mult} luck event?", reply_markup=markup)

def _do_luck_event_start():
    EVENT_DATA["event_active"] = True
    EVENT_DATA["event_end_time"] = datetime.now() + timedelta(seconds=EVENT_DATA["event_duration"])
    save_event_data()
    threading.Thread(
        target=lambda:     notify_all_users(
        f"🎉 X{EVENT_DATA['event_multiplier']} LUCK EVENT STARTED! 🎉\nTime left: {get_time_remaining()}\nYour luck is now multiplied by {EVENT_DATA['event_multiplier']}!",
        message_type="default"),
        daemon=True
    ).start()
    return f"✅ x{EVENT_DATA['event_multiplier']} luck event started! Duration: {get_time_remaining()}"

@bot.message_handler(commands=["luckEventChange"])

def luck_event_change(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) != 3:
        bot.send_message(msg.chat.id, "Usage: /luckEventChange <multiplier> <HH:MM:SS>")
        return
    try:
        multiplier = float(parts[1])
        h, m, s = parts[2].split(":")
        total_seconds = int(h) * 3600 + int(m) * 60 + int(s)
    except:
        bot.send_message(msg.chat.id, "❌ Invalid params. Use: /luckEventChange <multiplier> <HH:MM:SS>")
        return
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_luck_event_change(multiplier, total_seconds, parts[2])
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: set event to x{multiplier} for {parts[2]}?", reply_markup=markup)

def _do_luck_event_change(multiplier, total_seconds, time_str):
    EVENT_DATA["event_multiplier"] = multiplier
    EVENT_DATA["event_duration"] = total_seconds
    EVENT_DATA["event_active"] = False
    EVENT_DATA["event_end_time"] = None
    save_event_data()
    return f"✅ Event configured: x{multiplier} for {time_str}. Use /luckEventStart to activate."

# Админские команды для управления биомами

@bot.message_handler(commands=["setbiome"])

def set_biome_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        available = ", ".join(BIOMES.keys())
        bot.send_message(msg.chat.id, f"Usage: /setbiome <biome_name>\nAvailable: {available}")
        return
    biome_name = " ".join(parts[1:])
    if biome_name not in BIOMES:
        available = ", ".join(BIOMES.keys())
        bot.send_message(msg.chat.id, f"❌ Unknown biome.\nAvailable: {available}")
        return
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_set_biome(biome_name)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: set biome to {biome_name}?", reply_markup=markup)

def _do_set_biome(biome_name):
    set_biome(biome_name)
    return f"✅ Biome set to {biome_name}"

@bot.message_handler(commands=["itemReq"])

def item_req_cmd(msg):

    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    log_admin_action(msg, msg.text)

    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.send_message(msg.chat.id, "Usage: /itemReq <item_name>")
        return

    item_name = parts[1]
    user = get_user_data(uid, msg.from_user.first_name or "Admin")

    # Список ВСЕХ предметов, которые могут быть ингредиентами (чтобы отличать их от аур)
    ingredient_items = [
        "[T1] Solar Device", "[T3] Exo Gauntlet", "[T3] Windstorm Device",
        "[T5] Galactic Device", "[T6] Hologrammer", "[T9] Neurolyzer",
        "Lucky Potion", "Hades Godly Potion", "Zeus Godly Potion", "Unknown Potion"
    ]

    # Определяем требования для каждого предмета
    requirements = {
        "[T1] 🧤 Luck Glove": {"Common": 50, "Uncommon": 35, "Rare": 10, "Crystallised": 3, "Sapphire": 1},
        "[T1] 🔥 Desire Glove": {"Rage": 20, "Ruby": 10, "Diaboli": 4, "Bleeding": 2},
        "[T1] ☀️ Solar Device": {"Solar": 1, "Rare": 100, "Divinus": 50, "Uncommon": 300},
        "[T2] ⭐ Shining Star": {"Starlight": 2, "Star Rider": 2, "Wind": 50},
        "[T3] 💠 Exo Gauntlet": {"Gilded": 20, "Precious": 10, "Magnetic": 7, "Sidereum": 3, "Undead": 1, "Exotic": 1},
        "[T3] 🌪️ Windstorm Device": {"Wind": 90, "Stormal": 2, "Aquatic": 2, "Sidereum": 14, "Precious": 28},
        "[T4] ❄️ Subzero Device": {"Permafrost": 3, "Aquatic": 1, "Glacier": 20},
        "[T5] 🌌 Galactic Device": {"Galaxy": 1, "Sapphire": 320, "Solar": 30, "Magnetic": 100, "Comet": 4,
                                   "Diaboli": 150, "[T1] Solar Device": 2},
        "[T5] 🌋 Volcanic Device": {"Hades": 1, "Rage : Heated": 30, "Diaboli": 200, "Rage": 3000, "Bleeding": 133,
                                   "[T1] Solar Device": 3, "[T3] Windstorm Device": 1},
        "[T6] 🔮 Exoflex Device": {"Arcane": 5, "Jade": 15, "Exotic": 80, "Undead": 67, "Sidereum": 500,
                                  "Starlight": 140, "Aquamarine": 2000, "Rare": 70000, "[T3] Exo Gauntlet": 1},
        "[T6] 🌈 Hologrammer": {"Virtual": 5, "Magnetic : Reverse Polarity": 5, "Twilight": 6, "Kyawthuite": 5,
                               "Comet": 60, "Starlight": 100, "Rage : Heated": 250, "Player": 1000, "Magnetic": 1350,
                               "Diaboli": 5000, "Forbidden": 8000},
        "[T7] ⚡ Ragnaröker": {"Zeus": 7, "Hades": 7, "Poseidon": 7, "Star Rider": 175, "Solar": 300, "Lunar": 300,
                              "Rage : Heated": 400, "Lost Soul": 600, "Sidereum": 1000, "Ash": 4000, "Diaboli": 7000,
                              "Rage": 50000},
        "[T8] ✨ Starshaper": {"[T5] Galactic Device": 2, "[T1] Solar Device": 30, "Starscourge": 4, "Hyper-Volt": 6,
                              "Galaxy": 6, "Comet": 270, "Star Rider": 600, "Solar": 3000, "Lunar": 3000,
                              "Sidereum": 5000, "Magnetic": 10000},
        "[T9] 🔬 Neurolyzer": {"[T6] Hologrammer": 1, "Chromatic": 5, "Origin": 12, "Virtual": 30, "Twilight": 18,
                              "Bounded : Unbound": 50, "Exotic": 800, "Starlight": 1200, "Flushed": 5000,
                              "Lost Soul": 7500},
        "[T10] 🌀 Genesis Drive": {"[T9] Neurolyzer": 1, "Chromatic : Genesis": 2, "Matrix": 5, "Chromatic": 10,
                                  "Hyper-Volt": 30, "Origin": 30, "Virtual": 100, "Bounded": 600, "Aether": 600,
                                  "Exotic": 1000, "WATT": 7500, "Powered": 10000},

        # Рецепты зелий
        "Heavenly Potion": {"Celestial": 3, "Lucky Potion": 70, "Divinus : Angel": 2, "Powered": 5, "Quartz": 15},
        "Potion of Bound": {"Bounded": 2, "Permafrost": 5, "Lucky Potion": 35, "Lost Soul": 15},
        "Fortune Potion I": {"Lucky Potion": 10},
        "Fortune Potion II": {"Lucky Potion": 20},
        "Fortune Potion III": {"Lucky Potion": 30},
        "Jewellery Potion": {"Lucky Potion": 23, "Aquamarine": 3, "Sapphire": 3, "Gilded": 3, "Emerald": 3, "Ruby": 3,
                             "Topaz": 3},
        "Zombie Potion": {"Lucky Potion": 17, "Undead": 3, "Bleeding": 3},
        "Hades Godly Potion": {"Lucky Potion": 50, "Hades": 1, "Diaboli": 15, "Bleeding": 12},
        "Zeus Godly Potion": {"Lucky Potion": 40, "Zeus": 1, "Stormal": 4, "Wind": 30},
        "Godlike Potion": {"Zeus Godly Potion": 2, "Hades Godly Potion": 1, "Lucky Potion": 250},
        "Unknown Potion": {"Undefined": 20, "Shift lock": 15, "Nihility": 10}
    }

    if item_name not in requirements:
        bot.send_message(msg.chat.id, f"❌ Item '{item_name}' not found.")
        return

    # Выдаем все ингредиенты
    reqs = requirements[item_name]
    for ingredient_name, amount in reqs.items():
        # Проверяем, ПРЕДМЕТ ли это (сравнивая со списком ingredient_items)
        if ingredient_name in ingredient_items:
            # Добавляем предмет в инвентарь
            if "inventory" not in user:
                user["inventory"] = []

            # Добавляем недостающее кол-во
            current_count = sum(1 for item in user["inventory"] if item == ingredient_name)
            needed = amount - current_count
            if needed > 0:
                for _ in range(needed):
                    user["inventory"].append(ingredient_name)
        else:
            # Это аура, добавляем ее
            user["auras"][ingredient_name] = user["auras"].get(ingredient_name, 0) + amount

    save_data()
    bot.send_message(msg.chat.id, f"✅ All ingredients for {item_name} have been added to your inventory and auras!")

def apply_timed_potion(user, new_bonus, new_duration_seconds):

    """
    Применяет эффект временного зелья.
    Логика:
    1. Если активно зелье с БОЛЬШЕЙ удачей, просто добавляем время к СТАРОМУ зелью.
    2. Если активно зелье с МЕНЬШЕЙ или РАВНОЙ удачей, перезаписываем удачу и УСТАНАВЛИВАЕМ новое время.
    3. Если зелье неактивно, просто устанавливаем.
    """
    current_end_time_str = user.get("potion_end_time")
    now = datetime.now()

    if current_end_time_str:
        try:
            current_end_time = datetime.fromisoformat(current_end_time_str)
            if current_end_time > now:
                # Зелье уже активно
                current_bonus = user.get("potion_luck_bonus", 0.0)

                if new_bonus > current_bonus:
                    # Новое зелье ЛУЧШЕ - перезаписываем
                    user["potion_luck_bonus"] = new_bonus
                    user["potion_end_time"] = (now + timedelta(seconds=new_duration_seconds)).isoformat()
                    return f"New potion is stronger! Applied +{new_bonus} luck for {new_duration_seconds // 60} min."
                else:
                    # Новое зелье ХУЖЕ или такое же - просто добавляем время к СУЩЕСТВУЮЩЕМУ
                    new_end_time = current_end_time + timedelta(seconds=new_duration_seconds)
                    user["potion_end_time"] = new_end_time.isoformat()
                    return f"Potion time extended. Active bonus remains: +{current_bonus} luck."

        except:
            pass  # Ошибка формата, просто установим новое

    # Зелье неактивно или истекло
    user["potion_end_time"] = (now + timedelta(seconds=new_duration_seconds)).isoformat()
    user["potion_luck_bonus"] = new_bonus
    return f"Potion applied! +{new_bonus} luck for {new_duration_seconds // 60} min."

def process_manual_roll(msg):

    """
    Обрабатывает ОДИН ручной ролл в отдельном потоке.
    Логика разделена: вычисления под замком, отправка (и сон) без замка.
    """
    uid = str(msg.from_user.id)
    name = msg.from_user.first_name or "User"

    # Переменные для использования вне замка
    msg_text = ""
    gif_id_to_send = None
    should_pin = False
    global_msg_to_send = None

    # === НАЧАЛО БЛОКИРОВКИ ===
    with data_lock:
        user = get_user_data(uid, name)

        # Логика зелий (ИЗМЕНЕНО: В Лимбо бонусы = 0)
        heavenly_bonus = 0
        bound_bonus = 0
        godlike_bonus = 0
        potion_msg = ""

        # Проверяем, НЕ в лимбо ли мы. Если в Лимбо — бонусы не применяются.
        if not user.get("in_limbo", False):
            if user.get("heavenly_potion_active", 0) > 0:
                heavenly_bonus = 150000
                user["heavenly_potion_active"] -= 1
                potion_msg += f"\nHeavenly Potion left: {user['heavenly_potion_active']}"

            if user.get("bound_potion_active", 0) > 0:
                bound_bonus = 50000
                user["bound_potion_active"] -= 1
                potion_msg += f"\nPotion of Bound left: {user['bound_potion_active']}"

            if user.get("godlike_potion_active", 0) > 0:
                godlike_bonus = 400000
                user["godlike_potion_active"] -= 1
                potion_msg += f"\nGodlike Potion left: {user['godlike_potion_active']}"
        else:
            # Если мы в Лимбо, но зелья активны, можно (опционально) писать, что они отключены
            # Но по ТЗ просто не применяем их.
            pass

        total_special_bonus = heavenly_bonus + bound_bonus + godlike_bonus
        calculated_luck = get_calculated_luck(user) + total_special_bonus
        effective_luck = get_effective_luck(calculated_luck)

        # Ролл
        forced_aura = user.get("forced_aura")
        if forced_aura:
            aura = forced_aura
            chance = auras.get(aura, limbo_auras.get(aura, 1000000))
            user["forced_aura"] = None
        else:
            aura, chance = roll_aura(effective_luck, user)

            # Обновление данных
        user["rolls"] += 1

        # Лимбо сообщение (просто помечаем флагом, отправим позже если надо,
        # но здесь проще оставить проверку статуса)
        limbo_unlock_msg = False
        if user["rolls"] > 99999 and not user.get("limbo_msg_sent", False):
            user["limbo_msg_sent"] = True
            limbo_unlock_msg = True

        user["auras"][aura] = user["auras"].get(aura, 0) + 1
        current_val = auras.get(aura, limbo_auras.get(aura, 0))
        rarest_val = 0
        if user["rarest"]:
            rarest_val = auras.get(user["rarest"], limbo_auras.get(user["rarest"], 0))
        if current_val > rarest_val:
            user["rarest"] = aura

        save_data()  # Быстрое сохранение копии

        # Подготовка GIF
        gif_threshold = user.get("gif_rarity_threshold", 1000000)
        if aura in aura_gif_map and chance >= gif_threshold:
            val = aura_gif_map[aura]
            if val != "YOUR_ID_HERE":
                gif_id_to_send = val

        display_luck = int(effective_luck) if effective_luck == int(effective_luck) else round(effective_luck, 2)

        # From Biome
        from_biome = ""
        current_biome = BIOME_DATA["current_biome"]
        glitched_auras = ["Oppression", "Glitch", "Fault"]
        dreamspace_auras = ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric", "Borealis"]
        base_chance = auras.get(aura, limbo_auras.get(aura, 1))

        if current_biome == "Dreamspace" and aura in dreamspace_auras:
            from_biome = " [From Dreamspace!]"
        elif current_biome == "Glitched":
            if aura in glitched_auras or aura in dreamspace_auras:
                from_biome = " [From Glitched!]"
            else:
                biome_multiplier = get_biome_multiplier(aura)
                if biome_multiplier > 1:
                    adjusted_chance = base_chance / biome_multiplier
                    if adjusted_chance < base_chance:
                        from_biome = " [From Glitched!]"
        elif current_biome != "Normal" and current_biome != "Dreamspace":
            if get_biome_multiplier(aura) > 1:
                from_biome = f" [From {current_biome}!]"

        # Текст сообщения
        if aura == "Nothing":
            msg_text = f"You rolled Nothing 1 in 1 🍀x{display_luck}\n\n « ⚪ Basic ⚪ »"
        elif aura == "NYCTOPHOBIA":
            msg_text = f"👁️ You have experienced the literal nightmare. 👁️ 🍀x{display_luck}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
        elif aura == "Pixelation":
            msg_text = f"🎮👾 You have become PIXELATED!! 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
        elif aura == "Luminosity":
            msg_text = f"💫You have been devoured by the blinding light.💫 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
        elif aura == "Equinox":
            msg_text = f"⚫You have found [???????] between POSITIVE and NEGATIVE.⚪ 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
        elif aura == "Monarch":
            msg_text = f"👑 All hail, Your Majesty. 👑 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED+ ⚪⚫⚪ »"
        elif aura == "Breakthrough":
            msg_text = f"you have found ???, chance of 1 in 1,999,999,999 [BREAKTHROUGH!] 🍀x{display_luck}{from_biome}\n\n« 🟢🔵 TRANSCENDENT 🔵🟢 »"
        elif aura == "Glitch":
            msg_text = f"NO WAY! YOU ROLLED Glitch 1 IN 12210110 🍀x{display_luck}{from_biome}\n\n« ⚪⚫ CHALLENGED ⚪⚫ »"
        elif aura == "Oppression":
            msg_text = f"YOU HAVE DISCOVERED Oppression WITH CHANCE OF 1 IN 220000000 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED+ ⚪⚫⚪ »"
        elif aura == "Dreammetric":
            msg_text = f"YOU HAVE DISCOVERED Dreammetric WITH CHANCE OF 1 IN 520000000 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED+ ⚪⚫⚪ »"
        elif aura == "Leviathan":
            msg_text = f"You have tamed the Ruler of Beneath. 🍀x{display_luck}{from_biome}\n\n« ⚫⚪⚫ CHALLENGED ⚪⚫⚪ »"
        else:
            chance_display = int(chance) if chance == int(chance) else chance
            if chance > 99_999_998:
                msg_text = f"YOU HAVE DISCOVERED {aura} WITH CHANCE OF 1 IN {chance_display} 🍀x{display_luck}{from_biome}\n\n« 🔴🔴 GLORIOUS 🔴🔴 »"
            elif chance > 9_999_999:
                msg_text = f"NO WAY! YOU ROLLED {aura} 1IN {chance_display}!!!! 🍀x{display_luck}{from_biome}\n\n« 🔵 EXALTED 🔵 »"
            elif chance > 999_999:
                msg_text = f"OMG! You rolled {aura} 1 in {chance_display}!!! 🍀x{display_luck}{from_biome}\n\n« 🟠 MYTHIC 🟠 »"
            elif chance > 99_998:
                msg_text = f"Wow! You rolled {aura} 1 in {chance_display}!!! 🍀x{display_luck}{from_biome}\n\n« 🟢 Legendary 🟢 »"
            elif chance > 10_000:
                msg_text = f"You rolled {aura} 1 in {chance_display}!! 🍀x{display_luck}{from_biome}\n\n« 🟡 Unique 🟡 »"
            elif chance > 1_000:
                msg_text = f"You rolled {aura} 1 in {chance_display}! 🍀x{display_luck}{from_biome}\n\n« 🟣 Epic 🟣 »"
            else:
                msg_text = f"You rolled {aura} 1 in {chance_display} 🍀x{display_luck}{from_biome}\n\n« ⚪ Basic ⚪ »"
        msg_text += potion_msg

        # Pin
        pin_rarity = user.get("auto_pin_rarity")
        if pin_rarity and chance > pin_rarity:
            should_pin = True

        # Global
        if chance > GLOBAL_THRESHOLD or aura == "Glitch":
            from_biome_global = ""
            # Упрощаем логику для глобалки, берем то что уже посчитали
            if "Dreamspace" in from_biome:
                from_biome_global = " [From Dreamspace!]"
            elif "Glitched" in from_biome:
                from_biome_global = " [From Glitched!]"
            elif from_biome:
                from_biome_global = from_biome

            chance_display = int(chance) if chance == int(chance) else chance

            if aura == "Pixelation":
                global_msg_to_send = f"💫GLOBAL💫\n{name} Has Become PIXELATED!!\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "NYCTOPHOBIA":
                global_msg_to_send = f"💫GLOBAL💫\n{name} has experienced the literal nightmare.\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "Luminosity":
                global_msg_to_send = f"💫GLOBAL💫\nThe blinding light has devoured {name}.\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "Leviathan":
                global_msg_to_send = f"💫GLOBAL💫\n{name} has tamed the Ruler of Beneath.\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "Equinox":
                global_msg_to_send = f"💫GLOBAL💫\n{name} Has Found [???????] Between POSITIVE and NEGATIVE.\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "Monarch":
                global_msg_to_send = f"💫GLOBAL💫\nAll hail, The {name}.\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            elif aura == "Breakthrough":
                global_msg_to_send = f"💫GLOBAL💫\n{name} has found ???, chance of 1 in {chance_display} [BREAKTHROUGH!]{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"              
            elif aura == "Glitch":
                global_msg_to_send = f"💫GLOBAL💫\n{name} HAS ROLLED {aura}\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"
            else:
                global_msg_to_send = f"💫GLOBAL💫\n{name} Has rolled {aura}\n1 in {chance_display}{from_biome_global}\nRolled at: {user['rolls']}\nWith luck of: x{display_luck}"

    # === КОНЕЦ БЛОКИРОВКИ ===

    # Теперь можно безопасно спать и отправлять

    # GIF
    if gif_id_to_send:
        try:
            bot.send_animation(msg.chat.id, gif_id_to_send)
            time.sleep(12)
        except Exception as e:
            print(f"[⚠️] Failed to send GIF for {aura}: {e}")

    # Сообщение Лимбо анлок
    if limbo_unlock_msg:
        try:
            unlock_msg = bot.send_message(msg.chat.id,
                                          "👁️ ...\nYou have unlocked mysterious potion in your potion list...")
            bot.pin_chat_message(msg.chat.id, unlock_msg.message_id)
        except:
            pass

    # Главное сообщение
    try:
        roll_message = bot.send_message(msg.chat.id, msg_text, reply_markup=main_menu(uid))
        if should_pin:
            try:
                bot.pin_chat_message(msg.chat.id, roll_message.message_id, disable_notification=True)
            except Exception as e:
                print(f"[❌] Failed to pin message for {uid}: {e}")
    except Exception as e:
        pass

    # Global
    if global_msg_to_send:
        threading.Thread(target=lambda: notify_all_users(global_msg_to_send, message_type="global"),
                         daemon=True).start()
    return

@bot.message_handler(func=lambda message: str(message.from_user.id) in admin_ids and

                                          get_user_data(str(message.from_user.id)).get("pending_dangerous_cmd"))

def handle_dangerous_cmd_confirm(msg):

    global auras, limbo_auras, items_data
    uid = str(msg.from_user.id)
    user = get_user_data(uid)
    cmd_data = user.get("pending_dangerous_cmd", {})

    text = msg.text.strip().upper()

    del user["pending_dangerous_cmd"]  # Удаляем pending-состояние сразу
    save_data()

    if text == "Y":
        log_admin_action(msg, msg.text)
        cmd_type = cmd_data.get("type")
        amount = cmd_data.get("amount", 1)

        bot.send_message(msg.chat.id, f"✅ Executing command: {cmd_type.replace('_', ' ').title()}...")
        #

        if cmd_type == "all_auras":
            # Итерируемся по всем аурам (auras и limbo_auras)
            with data_lock:
                user_auras = user.setdefault("auras", {})
                all_aura_names = list(auras.keys()) + list(limbo_auras.keys())
                for aura_name in all_aura_names:
                    user_auras[aura_name] = user_auras.get(aura_name, 0) + amount

            bot.send_message(msg.chat.id, f"✨ You have received {amount} of all available auras!")

        save_data()
        bot.send_message(msg.chat.id, "Done.", reply_markup=main_menu())

    else:  # N или любой другой ответ
        bot.send_message(msg.chat.id, "❌ Command cancelled.", reply_markup=main_menu())

# ============================================================
# ДАННЫЕ ЗЕЛИЙ — добавить новое зелье: одна запись сюда
# type: "roll" = даёт стак на N роллов, "timed" = даёт бафф на время
# ============================================================
POTION_DATA = {
    "use_heavenly_potion": {
        "name": "Heavenly Potion",
        "desc": "Heavenly Potion\n+15000000% (+150000) luck for 1 roll",
        "type": "roll",
        "user_key": "heavenly_potion_active",
        "luck": 150000,
    },
    "use_bound_potion": {
        "name": "Potion of Bound",
        "desc": "Potion of Bound\n+5000000% (+50000) luck for 1 roll",
        "type": "roll",
        "user_key": "bound_potion_active",
        "luck": 50000,
    },
    "use_fortune_potion_1": {
        "name": "Fortune Potion I",
        "desc": "Fortune Potion I\n+50% (+0.5) luck for 5 minutes",
        "type": "timed",
        "luck": 0.5,
        "duration": 300,
    },
    "use_fortune_potion_2": {
        "name": "Fortune Potion II",
        "desc": "Fortune Potion II\n+75% (+0.75) luck for 5 minutes",
        "type": "timed",
        "luck": 0.75,
        "duration": 300,
    },
    "use_fortune_potion_3": {
        "name": "Fortune Potion III",
        "desc": "Fortune Potion III\n+100% (+1) luck for 5 minutes",
        "type": "timed",
        "luck": 1.0,
        "duration": 300,
    },
    "use_jewellery_potion": {
        "name": "Jewellery Potion",
        "desc": "Jewellery Potion\n+120% (+1.2) luck for 10 minutes",
        "type": "timed",
        "luck": 1.2,
        "duration": 600,
    },
    "use_zombie_potion": {
        "name": "Zombie Potion",
        "desc": "Zombie Potion\n+150% (+1.5) luck for 10 minutes",
        "type": "timed",
        "luck": 1.5,
        "duration": 600,
    },
    "use_hades_godly_potion": {
        "name": "Hades Godly Potion",
        "desc": "Hades Godly Potion\n+300% (+3) luck for 4 hours",
        "type": "timed",
        "luck": 3.0,
        "duration": 14400,
    },
    "use_zeus_godly_potion": {
        "name": "Zeus Godly Potion",
        "desc": "Zeus Godly Potion\n+200% (+2) luck for 4 hours",
        "type": "timed",
        "luck": 2.0,
        "duration": 14400,
    },
    "use_godlike_potion": {
        "name": "Godlike Potion",
        "desc": "Godlike Potion\n+40000000% (+400000) luck for 1 roll",
        "type": "roll",
        "user_key": "godlike_potion_active",
        "luck": 400000,
    },
}  

# Имя зелья -> ключ в POTION_DATA (для показа меню при нажатии на зелье из инвентаря)
POTION_NAME_TO_KEY = {v["name"]: k for k, v in POTION_DATA.items()}

def handle_potion_select(msg, uid, potion_name):
    # Показывает меню использования зелья из инвентаря.
    user = get_user_data(uid)
    data_key = POTION_NAME_TO_KEY.get(potion_name)
    if not data_key:
        return False
    potion = POTION_DATA[data_key]
    potion_count = user.get("inventory", []).count(potion_name)
    if potion_count == 0:
        bot.send_message(msg.chat.id, f"You don't have any {potion_name}.", reply_markup=back_menu())
        return True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("Use"))
    if potion_count > 1:
        markup.row(types.KeyboardButton("Use All"))
        markup.row(types.KeyboardButton("Use amount"))
    markup.row(types.KeyboardButton("⬅️ Back"))
    bot.send_message(msg.chat.id, potion["desc"], reply_markup=markup)
    user_last_command[uid] = data_key
    return True

def handle_potion_use(msg, uid, name, use_key, amount=1):
    # Использует 1 или N зелий. Возвращает True если обработал.
    potion = POTION_DATA.get(use_key)
    if not potion:
        return False
    user = get_user_data(uid, name)
    potion_name = potion["name"]
    inv = user.get("inventory", [])
    available = inv.count(potion_name)
    if available < amount:
        bot.send_message(msg.chat.id, "You don\'t have any potions.", reply_markup=back_menu())
        return True
    # Убираем зелья из инвентаря
    removed = 0
    new_inv = []
    for item in inv:
        if item == potion_name and removed < amount:
            removed += 1
        else:
            new_inv.append(item)
    user["inventory"] = new_inv
    # Применяем эффект
    if potion["type"] == "roll":
        key = potion["user_key"]
        user[key] = user.get(key, 0) + amount
        luck = potion["luck"]
        if amount == 1:
            response = f"You used 1 {potion_name}. +{luck} luck for 1 roll."
        else:
            response = f"You used {amount} {potion_name}. +{luck} luck for {amount} rolls."
    else:
        response_msg = apply_timed_potion(user, potion["luck"], potion["duration"] * amount)
        if amount == 1:
            response = response_msg
        else:
            response = f"Used {amount} {potion_name}. {response_msg}"
    save_data()
    bot.send_message(msg.chat.id, response, reply_markup=back_menu())
    user_last_command[uid] = None
    return True

# ============================================================
# УНИВЕРСАЛЬНАЯ ФУНКЦИЯ КРАФТА
# Добавить новый предмет: просто добавь запись в CRAFT_RECIPES
# ============================================================
CRAFT_RECIPES = {
    # --- ЗЕЛЬЯ ---
    "craft_heavenly_potion": {
        "aura_reqs": {"Celestial": 3, "Divinus : Angel": 2, "Powered": 5, "Quartz": 15},
        "item_reqs": {"Lucky Potion": 70},
        "result": "Heavenly Potion", "result_display": "Heavenly Potion",
    },
    "craft_potion_of_bound": {
        "aura_reqs": {"Bounded": 2, "Permafrost": 5, "Lost Soul": 15},
        "item_reqs": {"Lucky Potion": 35},
        "result": "Potion of Bound", "result_display": "Potion of Bound",
    },
    "craft_fortune_potion_1": {
        "aura_reqs": {}, "item_reqs": {"Lucky Potion": 10},
        "result": "Fortune Potion I", "result_display": "Fortune Potion I",
    },
    "craft_fortune_potion_2": {
        "aura_reqs": {}, "item_reqs": {"Lucky Potion": 20},
        "result": "Fortune Potion II", "result_display": "Fortune Potion II",
    },
    "craft_fortune_potion_3": {
        "aura_reqs": {}, "item_reqs": {"Lucky Potion": 30},
        "result": "Fortune Potion III", "result_display": "Fortune Potion III",
    },
    "craft_jewellery_potion": {
        "aura_reqs": {"Aquamarine": 3, "Sapphire": 3, "Gilded": 3, "Emerald": 3, "Ruby": 3, "Topaz": 3},
        "item_reqs": {"Lucky Potion": 23},
        "result": "Jewellery Potion", "result_display": "Jewellery Potion",
    },
    "craft_zombie_potion": {
        "aura_reqs": {"Undead": 3, "Bleeding": 3},
        "item_reqs": {"Lucky Potion": 17},
        "result": "Zombie Potion", "result_display": "Zombie Potion",
    },
    "craft_hades_godly_potion": {
        "aura_reqs": {"Hades": 1, "Diaboli": 15, "Bleeding": 12},
        "item_reqs": {"Lucky Potion": 50},
        "result": "Hades Godly Potion", "result_display": "Hades Godly Potion",
    },
    "craft_zeus_godly_potion": {
        "aura_reqs": {"Zeus": 1, "Stormal": 4, "Wind": 30},
        "item_reqs": {"Lucky Potion": 40},
        "result": "Zeus Godly Potion", "result_display": "Zeus Godly Potion",
    },
    "craft_godlike_potion": {
        "aura_reqs": {}, "item_reqs": {"Zeus Godly Potion": 2, "Hades Godly Potion": 1, "Lucky Potion": 250},
        "result": "Godlike Potion", "result_display": "Godlike Potion",
    },
    # --- WORKSHOP ---
    "craft_luckglove": {
        "aura_reqs": {"Common": 50, "Uncommon": 35, "Rare": 10, "Crystallised": 3, "Sapphire": 1},
        "item_reqs": {},
        "result": "[T1] 🧤 Luck Glove", "result_display": "[T1] 🧤 Luck Glove",
    },
    "craft_desireglove": {
        "aura_reqs": {"Rage": 20, "Ruby": 10, "Diaboli": 4, "Bleeding": 2},
        "item_reqs": {},
        "result": "[T1] 🔥 Desire Glove", "result_display": "[T1] 🔥 Desire Glove",
    },
    "craft_solardevice": {
        "aura_reqs": {"Solar": 1, "Rare": 100, "Divinus": 50, "Uncommon": 300},
        "item_reqs": {},
        "result": "[T1] ☀️ Solar Device", "result_display": "[T1] ☀️ Solar Device",
    },
    "craft_shiningstar": {
        "aura_reqs": {"Starlight": 2, "Star Rider": 2, "Wind": 50},
        "item_reqs": {},
        "result": "[T2] ⭐ Shining Star", "result_display": "[T2] ⭐ Shining Star",
    },
    "craft_exogauntlet": {
        "aura_reqs": {"Gilded": 20, "Precious": 10, "Magnetic": 7, "Sidereum": 3, "Undead": 1, "Exotic": 1},
        "item_reqs": {},
        "result": "[T3] 💠 Exo Gauntlet", "result_display": "[T3] 💠 Exo Gauntlet",
    },
    "craft_windstormdevice": {
        "aura_reqs": {"Wind": 90, "Stormal": 2, "Aquatic": 2, "Sidereum": 14, "Precious": 28},
        "item_reqs": {},
        "result": "[T3] 🌪️ Windstorm Device", "result_display": "[T3] 🌪️ Windstorm Device",
    },
    "craft_subzerodevice": {
        "aura_reqs": {"Permafrost": 3, "Aquatic": 1, "Glacier": 20},
        "item_reqs": {},
        "result": "[T4] ❄️ Subzero Device", "result_display": "[T4] ❄️ Subzero Device",
    },
    "craft_galacticdevice": {
        "aura_reqs": {"Galaxy": 1, "Sapphire": 320, "Solar": 30, "Magnetic": 100, "Comet": 4, "Diaboli": 150},
        "item_reqs": {"[T1] ☀️ Solar Device": 2},
        "result": "[T5] 🌌 Galactic Device", "result_display": "[T5] 🌌 Galactic Device",
    },
    "craft_volcanicdevice": {
        "aura_reqs": {"Hades": 1, "Rage : Heated": 30, "Diaboli": 200, "Rage": 3000, "Bleeding": 133},
        "item_reqs": {"[T1] ☀️ Solar Device": 3, "[T3] 🌪️ Windstorm Device": 1},
        "result": "[T5] 🌋 Volcanic Device", "result_display": "[T5] 🌋 Volcanic Device",
    },
    "craft_exoflexdevice": {
        "aura_reqs": {"Arcane": 5, "Jade": 15, "Exotic": 80, "Undead": 67, "Sidereum": 500, "Starlight": 140},
        "item_reqs": {"[T3] 💠 Exo Gauntlet": 1},
        "result": "[T6] 🔮 Exoflex Device", "result_display": "[T6] 🔮 Exoflex Device",
    },
    "craft_hologrammer": {
        "aura_reqs": {"Virtual": 5, "Magnetic : Reverse Polarity": 5, "Twilight": 6, "Kyawthuite": 5, "Comet": 60},
        "item_reqs": {},
        "result": "[T6] 🌈 Hologrammer", "result_display": "[T6] 🌈 Hologrammer",
    },
    "craft_ragnaroker": {
        "aura_reqs": {"Zeus": 7, "Hades": 7, "Poseidon": 7, "Star Rider": 175, "Solar": 300, "Lunar": 300},
        "item_reqs": {},
        "result": "[T7] ⚡ Ragnaröker", "result_display": "[T7] ⚡ Ragnaröker",
    },
    "craft_starshaper": {
        "aura_reqs": {"Starscourge": 4, "Hyper-Volt": 6, "Galaxy": 6, "Comet": 270, "Star Rider": 600, "Solar": 3000},
        "item_reqs": {"[T5] 🌌 Galactic Device": 2, "[T1] ☀️ Solar Device": 30},
        "result": "[T8] ✨ Starshaper", "result_display": "[T8] ✨ Starshaper",
    },
    "craft_neurolyzer": {
        "aura_reqs": {"Chromatic": 5, "Origin": 12, "Virtual": 30, "Twilight": 18, "Bounded : Unbound": 50},
        "item_reqs": {"[T6] 🌈 Hologrammer": 1},
        "result": "[T9] 🔬 Neurolyzer", "result_display": "[T9] 🔬 Neurolyzer",
    },
    "craft_genesisdrive": {
        "aura_reqs": {"Chromatic : Genesis": 2, "Matrix": 5, "Chromatic": 10, "Hyper-Volt": 30, "Origin": 30},
        "item_reqs": {"[T9] 🔬 Neurolyzer": 1},
        "result": "[T10] 🌀 Genesis Drive", "result_display": "[T10] 🌀 Genesis Drive",
    },
}


# ============================================================
# МАСТЕР-СЛОВАРЬ ПРЕДМЕТОВ WORKSHOP
# Чтобы добавить новый предмет — добавь ОДНУ запись сюда.
# Всё остальное (меню, крафт, бонусы) генерируется автоматически.
# ============================================================
WORKSHOP_ITEMS = {
    "[T1] 🧤 Luck Glove": {
        "craft_key": "craft_luckglove",
        "luck_bonus": 0.25,
        "desc": "[T1] 🧤 Luck Glove\n+25% (+0.25) luck\n\nRequirements:\nx50 Common\nx35 Uncommon\nx10 Rare\nx3 Crystallised\nx1 Sapphire",
        "biome_bonus": None,  # {"biome": "Starfall", "bonus": 6.0} или None
    },
    "[T1] 🔥 Desire Glove": {
        "craft_key": "craft_desireglove",
        "luck_bonus": 0.4,
        "desc": "[T1] 🔥 Desire Glove\n+40% (+0.4) luck\n\nRequirements:\nx20 Rage\nx10 Ruby\nx4 Diaboli\nx2 Bleeding",
        "biome_bonus": None,
    },
    "[T1] ☀️ Solar Device": {
        "craft_key": "craft_solardevice",
        "luck_bonus": 0.5,
        "desc": "[T1] ☀️ Solar Device\n+50% (+0.5) luck\n\nRequirements:\nx1 Solar\nx100 Rare\nx50 Divinus\nx300 Uncommon",
        "biome_bonus": None,
    },
    "[T2] ⭐ Shining Star": {
        "craft_key": "craft_shiningstar",
        "luck_bonus": 0.5,
        "desc": "[T2] ⭐ Shining Star\n+50% luck (when Starfall biome: +250%)\n\nRequirements:\nx2 Starlight\nx2 Star Rider\nx50 Wind",
        "biome_bonus": {"biome": "Starfall", "bonus": 2.5},
    },
    "[T3] 💠 Exo Gauntlet": {
        "craft_key": "craft_exogauntlet",
        "luck_bonus": 1.0,
        "desc": "[T3] 💠 Exo Gauntlet\n+100% (+1.0) luck\n\nRequirements:\nx20 Gilded\nx10 Precious\nx7 Magnetic\nx3 Sidereum\nx1 Undead\nx1 Exotic",
        "biome_bonus": None,
    },
    "[T3] 🌪️ Windstorm Device": {
        "craft_key": "craft_windstormdevice",
        "luck_bonus": 1.15,
        "desc": "[T3] 🌪️ Windstorm Device\n+115% (+1.15) luck\n\nRequirements:\nx90 Wind\nx2 Stormal\nx2 Aquatic\nx14 Sidereum\nx28 Precious",
        "biome_bonus": None,
    },
    "[T4] ❄️ Subzero Device": {
        "craft_key": "craft_subzerodevice",
        "luck_bonus": 1.5,
        "desc": "[T4] ❄️ Subzero Device\n+150% (+1.5) luck\n\nRequirements:\nx3 Permafrost\nx1 Aquatic\nx20 Glacier",
        "biome_bonus": None,
    },
    "[T5] 🌌 Galactic Device": {
        "craft_key": "craft_galacticdevice",
        "luck_bonus": 2.5,
        "desc": "[T5] 🌌 Galactic Device\n+250% (+2.5) luck\n\nRequirements:\nx1 Galaxy\nx320 Sapphire\nx30 Solar\nx100 Magnetic\nx4 Comet\nx150 Diaboli\nx2 [T1] Solar Device",
        "biome_bonus": None,
    },
    "[T5] 🌋 Volcanic Device": {
        "craft_key": "craft_volcanicdevice",
        "luck_bonus": 2.9,
        "desc": "[T5] 🌋 Volcanic Device\n+290% (+2.9) luck\n\nRequirements:\nx1 Hades\nx30 Rage : Heated\nx200 Diaboli\nx3000 Rage\nx133 Bleeding\nx3 [T1] Solar Device\nx1 [T3] Windstorm Device",
        "biome_bonus": None,
    },
    "[T6] 🔮 Exoflex Device": {
        "craft_key": "craft_exoflexdevice",
        "luck_bonus": 3.4,
        "desc": "[T6] 🔮 Exoflex Device\n+340% (+3.4) luck\n\nRequirements:\nx5 Arcane\nx15 Jade\nx80 Exotic\nx67 Undead\nx500 Sidereum\nx140 Starlight\nx2000 Aquamarine\nx70000 Rare\nx1 [T3] Exo Gauntlet",
        "biome_bonus": None,
    },
    "[T6] 🌈 Hologrammer": {
        "craft_key": "craft_hologrammer",
        "luck_bonus": 3.95,
        "desc": "[T6] 🌈 Hologrammer\n+395% (+3.95) luck\n\nRequirements:\nx5 Virtual\nx5 Magnetic : Reverse Polarity\nx6 Twilight\nx5 Kyawthuite\nx60 Comet\nx100 Starlight\nx250 Rage : Heated\nx1000 Player\nx1350 Magnetic\nx5000 Diaboli\nx8000 Forbidden",
        "biome_bonus": None,
    },
    "[T7] ⚡ Ragnaröker": {
        "craft_key": "craft_ragnaroker",
        "luck_bonus": 4.55,
        "desc": "[T7] ⚡ Ragnaröker\n+455% (+4.55) luck\n\nRequirements:\nx7 Zeus\nx7 Hades\nx7 Poseidon\nx175 Star Rider\nx300 Solar\nx300 Lunar\nx400 Rage : Heated\nx600 Lost Soul\nx1000 Sidereum\nx4000 Ash\nx7000 Diaboli\nx50000 Rage",
        "biome_bonus": {"biome": "Windy/Rainy/Hell", "bonus": 0.45},
    },
    "[T8] ✨ Starshaper": {
        "craft_key": "craft_starshaper",
        "luck_bonus": 7.0,
        "desc": "[T8] ✨ Starshaper\n+700% (+7) luck\n\nRequirements:\nx2 [T5] Galactic Device\nx30 [T1] Solar Device\nx4 Starscourge\nx6 Hyper-Volt\nx6 Galaxy\nx270 Comet\nx600 Star Rider\nx3000 Solar\nx3000 Lunar\nx5000 Sidereum\nx10000 Magnetic",
        "biome_bonus": None,
    },
    "[T9] 🔬 Neurolyzer": {
        "craft_key": "craft_neurolyzer",
        "luck_bonus": 8.5,
        "desc": "[T9] 🔬 Neurolyzer\n+850% (+8.5) luck\n\nRequirements:\nx1 [T6] Hologrammer\nx5 Chromatic\nx12 Origin\nx30 Virtual\nx18 Twilight\nx50 Bounded : Unbound\nx800 Exotic\nx1200 Starlight\nx5000 Flushed\nx7500 Lost Soul",
        "biome_bonus": None,
    },
    "[T10] 🌀 Genesis Drive": {
        "craft_key": "craft_genesisdrive",
        "luck_bonus": 12.0,
        "desc": "[T10] 🌀 Genesis Drive\n+1200% (+12) luck\n\nRequirements:\nx1 [T9] Neurolyzer\nx2 Chromatic : Genesis\nx5 Matrix\nx10 Chromatic\nx30 Hyper-Volt\nx30 Origin\nx100 Virtual\nx600 Bounded\nx600 Aether\nx1000 Exotic\nx7500 WATT\nx10000 Powered",
        "biome_bonus": None,
    },
}

# Автогенерация из WORKSHOP_ITEMS — не редактировать вручную
gear_items = list(WORKSHOP_ITEMS.keys())
luck_bonuses = {name: item["luck_bonus"] for name, item in WORKSHOP_ITEMS.items()}


def do_craft(msg, uid, name, craft_key):
    # Универсальная логика крафта. Возвращает True если обработал.
    recipe = CRAFT_RECIPES.get(craft_key)
    if not recipe:
        return False
    aura_reqs = recipe.get("aura_reqs", {})
    item_reqs = recipe.get("item_reqs", {})
    result = recipe["result"]
    result_display = recipe["result_display"]
    can_craft = True
    fail_message = "❌ Not enough materials."
    with data_lock:
        user = get_user_data(uid, name)
        for a, amt in aura_reqs.items():
            if user.get("auras", {}).get(a, 0) < amt:
                can_craft = False
                break
        if can_craft and item_reqs:
            inventory_count = {}
            for item in user.get("inventory", []):
                inventory_count[item] = inventory_count.get(item, 0) + 1
            for item, amt in item_reqs.items():
                if inventory_count.get(item, 0) < amt:
                    can_craft = False
                    fail_message = f"❌ Not enough {item}."
                    break
        if can_craft:
            for a, amt in aura_reqs.items():
                user["auras"][a] -= amt
            if item_reqs:
                items_to_remove = item_reqs.copy()
                new_inventory = []
                for item in user.get("inventory", []):
                    if item in items_to_remove and items_to_remove[item] > 0:
                        items_to_remove[item] -= 1
                    else:
                        new_inventory.append(item)
                user["inventory"] = new_inventory
            user.setdefault("inventory", []).append(result)
            save_data()
    if can_craft:
        bot.send_message(msg.chat.id, f"✅ Successfully crafted {result_display}.",
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row("⬅️ Back"))
        user_last_command[uid] = None
    else:
        bot.send_message(msg.chat.id, fail_message, reply_markup=back_menu())
    return True

def handle_limbo_exit(msg, uid, user):
    # Обрабатывает выход из Лимбо и разморозку таймеров зелий.
    if not user.get("in_limbo", False):
        bot.send_message(msg.chat.id, "YOU\'RE NOT WORTHY TO PASS.", reply_markup=back_menu())
        return
    user["in_limbo"] = False
    pause_start_str = user.get("limbo_pause_start")
    if pause_start_str:
        try:
            pause_start = datetime.fromisoformat(pause_start_str)
            time_in_limbo = datetime.now() - pause_start
            potion_end_str = user.get("potion_end_time")
            if potion_end_str:
                old_end = datetime.fromisoformat(potion_end_str)
                user["potion_end_time"] = (old_end + time_in_limbo).isoformat()
        except Exception as e:
            print(f"Error calculating time shift: {e}")
        user["limbo_pause_start"] = None
    save_data()
    bot.send_message(msg.chat.id, "Returning to reality...\nTime flows again.", reply_markup=main_menu(uid))

@bot.message_handler(commands=["help"])
def admin_help(msg):
    uid = msg.from_user.id

    if str(uid) not in admin_ids:
        bot.send_message(msg.chat.id, user_help_text, parse_mode="Markdown")
        return
    bot.send_message(msg.chat.id, admin_help_text, parse_mode="Markdown")


@bot.message_handler(commands=["end"])
def end_cmd(msg):
    uid = str(msg.from_user.id)
    if uid not in admin_ids:
        bot.send_message(msg.chat.id, "❌ No permission.")
        return
    parts = msg.text.split(" ", 1)
    reason = parts[1] if len(parts) > 1 else "No reason provided"
    pending_confirmations[uid] = {
        "cmd": msg.text,
        "action": lambda: _do_end(reason)
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"confirm_yes_{uid}"),
        types.InlineKeyboardButton("❌ No", callback_data=f"confirm_no_{uid}")
    )
    bot.send_message(msg.chat.id, f"⚠️ Confirm: shut down the bot?\nReason: {reason}", reply_markup=markup)


def _do_end(reason):
    notify_all_users(
        f"━━━━━━━━━━━━━━━\n🔴 BOT OFFLINE\n💬 Reason: {reason}\n━━━━━━━━━━━━━━━",
        message_type="default"
    )
    save_data()
    bot.stop_polling()
    return f"✅ Bot shutting down. Reason: {reason}"

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def handle_confirm_callback(call):
    parts = call.data.split("_", 3)  # confirm_yes_uid or confirm_no_uid
    action = parts[1]  # "yes" or "no"
    admin_uid = parts[2]
    # Only the admin who triggered the confirm can click
    if str(call.from_user.id) != admin_uid:
        bot.answer_callback_query(call.id, "❌ Not your confirmation.")
        return
    pending = pending_confirmations.pop(admin_uid, None)
    if not pending:
        bot.edit_message_text("⚠️ Confirmation expired.", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    if action == "yes":
        # call.from_user — это реальный пользователь нажавший кнопку
        # создаём объект-обёртку чтобы передать в log_admin_action
        class _FakeMsg:
            from_user = call.from_user
        log_admin_action(_FakeMsg(), pending["cmd"])
        result = pending["action"]()
        bot.edit_message_text(result, call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text("❌ Cancelled.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    
@bot.callback_query_handler(func=lambda call: True)
def intro_continue(call):
    if call.data == "btn_continue":
        bot.answer_callback_query(call.id, "🍀 Good luck!", show_alert=False)
        
        uid = str(call.from_user.id)
        event_info = ""
        MaintanceText = ""
        if is_event_active():
            event_info = f"\n\n🎉 X{EVENT_DATA['event_multiplier']} LUCK EVENT ACTIVE! 🎉\nTime left: {get_time_remaining()}"
            
        if MaintanceActive:
            MaintanceText = f"\n\n⚠️ Sol's rng bot is Going down for Scheduled Maintenance soon."

        biome_info = f"\nBIOME: {BIOME_DATA['current_biome']}"
        if BIOME_DATA['current_biome'] != "Normal":
            biome_info += f" (ends in: {get_biome_time_remaining()})"

        bot.send_message(call.message.chat.id,
                        f"Welcome to Sol's RNG 🎰\nTime: {'DAYTIME ☀️' if is_day else 'NIGHTTIME 🌙'}{biome_info}{event_info}{MaintanceText}",
                        reply_markup=main_menu(uid))

@bot.message_handler(func=lambda m: True)
def handle(msg):

    global lucky_potion_active  # Нужно для обработки нажатия

    # 1. СНАЧАЛА ПОЛУЧАЕМ ДАННЫЕ (Это должно быть самым первым!)
    text = msg.text.strip()
    uid = str(msg.from_user.id)
    name = msg.from_user.first_name or "User"
    user = get_user_data(uid, name)  # Получаем пользователя
    user["last_active"] = datetime.now().isoformat()

    # 2. Блокировка команд, если Auto Roll включен (Это тоже должно быть в начале)
    if user.get("auto_roll_enabled", False) and text != "Disable Auto Roll":
        return

    # --- ТЕПЕРЬ ВСТАВЛЯЕМ ЛОГИКУ ЛИМБО (Когда переменные уже существуют) ---

    # 1. Триггер "???"
    if text == "???":
        # Проверяем бафф
        buff_active = False
        unknown_end_str = user.get("unknown_potion_end")
        if unknown_end_str:
            try:
                if datetime.fromisoformat(unknown_end_str) > datetime.now():
                    buff_active = True
            except:
                pass

        # Проверяем биом Null
        if buff_active and BIOME_DATA["current_biome"] == "Null" and not user.get("in_limbo"):
            # ENTER SEQUENCE
            phrases = ["FINE", "YOU'RE", "WORTHY", "TO", "ENTER", "THE LIMBO."]
            for phrase in phrases:
                bot.send_message(msg.chat.id, phrase)
                time.sleep(0.5)

            user["in_limbo"] = True
            user["limbo_unlocked"] = True
            # ЗАМОРОЗКА ВРЕМЕНИ: Сохраняем время входа
            user["limbo_pause_start"] = datetime.now().isoformat()

            save_data()
            bot.send_message(msg.chat.id, "🌌 You are now in The Limbo.", reply_markup=main_menu(uid))
            return
        elif not buff_active and BIOME_DATA["current_biome"] == "Null":
            # Если просто пишешь в Null без баффа - ничего или загадка
            pass

    # 2. Вход в Лимбо (Кнопка)
    if text == "🌌 Enter The Limbo":
        if not user.get("limbo_unlocked", False):
            bot.send_message(msg.chat.id, "YOU'RE NOT WORTHY TO PASS.", reply_markup=back_menu())
            return

        user["in_limbo"] = True
        # ЗАМОРОЗКА ВРЕМЕНИ: Сохраняем время входа
        user["limbo_pause_start"] = datetime.now().isoformat()

        save_data()
        bot.send_message(msg.chat.id, "Welcome back to the void.", reply_markup=main_menu(uid))
        return

    # 3. Выход из Лимбо (Кнопка)
    if text == "🌌 Exit The Limbo":
        handle_limbo_exit(msg, uid, user)
        return
    pending_potion = user.get("pending_potion_amount")
    if pending_potion:
        potion_map = {
            "lucky": "Lucky Potion",
            "godlike": "Godlike Potion",
            "heavenly": "Heavenly Potion",
            "bound": "Potion of Bound",
            "fortune_1": "Fortune Potion I",
            "fortune_2": "Fortune Potion II",
            "fortune_3": "Fortune Potion III",
            "jewellery": "Jewellery Potion",
            "zombie": "Zombie Potion",
            "hades_godly": "Hades Godly Potion",
            "zeus_godly": "Zeus Godly Potion"
        }
        potion_name = potion_map.get(pending_potion)

        try:
            amount = int(text)
            if amount <= 0:
                raise ValueError("Amount must be positive.")

            potion_count = user.get("inventory", []).count(potion_name)

            if amount > potion_count:
                bot.send_message(msg.chat.id, f"❌ You don't have that much {potion_name}", reply_markup=back_menu())
                user["pending_potion_amount"] = None
                save_data()
                return

            # Списываем зелья
            current_inventory = user.get("inventory", [])
            new_inventory = []
            removed_count = 0
            for item in current_inventory:
                if item == potion_name and removed_count < amount:
                    removed_count += 1
                else:
                    new_inventory.append(item)
            user["inventory"] = new_inventory

            # Применяем эффект
            response_msg = ""
            if pending_potion == "lucky":
                # +1 luck, 1 min (60s) per potion
                response_msg = apply_timed_potion(user, 1.0, 60 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Lucky Potions. {response_msg}", reply_markup=back_menu())

            # --- НОВЫЕ ВРЕМЕННЫЕ ЗЕЛЬЯ ---
            elif pending_potion == "fortune_1":
                # +2 luck, 5 min (300s) per potion
                response_msg = apply_timed_potion(user, 0.5, 300 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Fortune Potion I. {response_msg}",
                                 reply_markup=back_menu())
            elif pending_potion == "fortune_2":
                # +3.5 luck, 5 min (300s) per potion
                response_msg = apply_timed_potion(user, 0.75, 300 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Fortune Potion II. {response_msg}",
                                 reply_markup=back_menu())
            elif pending_potion == "fortune_3":
                # +5 luck, 5 min (300s) per potion
                response_msg = apply_timed_potion(user, 1.0, 300 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Fortune Potion III. {response_msg}",
                                 reply_markup=back_menu())
            elif pending_potion == "jewellery":
                # +6 luck, 10 min (600s) per potion
                response_msg = apply_timed_potion(user, 1.2, 600 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Jewellery Potion. {response_msg}",
                                 reply_markup=back_menu())
            elif pending_potion == "zombie":
                # +8 luck, 10 min (600s) per potion
                response_msg = apply_timed_potion(user, 1.5, 600 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Zombie Potion. {response_msg}", reply_markup=back_menu())
            elif pending_potion == "hades_godly":
                # +12 luck, 4 hours (14400s) per potion
                response_msg = apply_timed_potion(user, 3.0, 14400 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Hades Godly Potion. {response_msg}",
                                 reply_markup=back_menu())
            elif pending_potion == "zeus_godly":
                # +10 luck, 4 hours (14400s) per potion
                response_msg = apply_timed_potion(user, 2.0, 14400 * amount)
                bot.send_message(msg.chat.id, f"Used {amount} Zeus Godly Potion. {response_msg}",
                                 reply_markup=back_menu())

            # --- ЗЕЛЬЯ НА РОЛЛЫ ---
            elif pending_potion == "godlike":
                user["godlike_potion_active"] = user.get("godlike_potion_active", 0) + amount
                bot.send_message(msg.chat.id, f"You used {amount} Godlike Potions. +400000 luck for {amount} rolls.",
                                 reply_markup=back_menu())
            elif pending_potion == "heavenly":
                user["heavenly_potion_active"] = user.get("heavenly_potion_active", 0) + amount
                bot.send_message(msg.chat.id, f"You used {amount} Heavenly Potions. +150000 luck for {amount} rolls.",
                                 reply_markup=back_menu())
            elif pending_potion == "bound":
                user["bound_potion_active"] = user.get("bound_potion_active", 0) + amount
                bot.send_message(msg.chat.id, f"You used {amount} Potions of Bound. +50000 luck for {amount} rolls.",
                                 reply_markup=back_menu())

            user["pending_potion_amount"] = None
            save_data()

        except ValueError:
            bot.send_message(msg.chat.id, "❌ Invalid amount. Please enter a number.", reply_markup=back_menu())
        user["pending_potion_amount"] = None  # Сбрасываем, чтобы избежать цикла
        save_data()

        return  # Завершаем обработку, так как это было число для зелья
    if user_last_command.get(uid) == "set_auto_pin":
        try:
            rarity_threshold = int(text)
            if rarity_threshold <= 0:
                user["auto_pin_rarity"] = None
                bot.send_message(msg.chat.id, "Auto-pin disabled.", reply_markup=main_menu(uid))
            else:
                user["auto_pin_rarity"] = rarity_threshold
                bot.send_message(msg.chat.id, f"✅ Auto-pin enabled for rarities > 1 in {rarity_threshold}",
                                 reply_markup=main_menu(uid))

            user_last_command[uid] = None
            save_data()

        except ValueError:
            bot.send_message(msg.chat.id, "❌ Invalid number. Enter rarity (e.g., 1000000) or 0 to disable.",
                             reply_markup=types.ReplyKeyboardRemove())
            # Не сбрасываем user_last_command, ждем правильного ввода

        return  # Завершаем обработку
    if user_last_command.get(uid) == "set_gif_rarity":
        try:
            rarity_threshold = int(text)
            if rarity_threshold < 1000000:  # Если ввели 0 или число < 1M
                # Устанавливаем очень большое число, чтобы гифки не показывались
                user["gif_rarity_threshold"] = 10000000000
                bot.send_message(msg.chat.id, "Gif cutscenes disabled.", reply_markup=main_menu(uid))
            else:
                user["gif_rarity_threshold"] = rarity_threshold
                bot.send_message(msg.chat.id, f"✅ Gif cutscenes will show for rarities > 1 in {rarity_threshold}",
                                 reply_markup=main_menu(uid))

            user_last_command[uid] = None
            save_data()

        except ValueError:
            bot.send_message(msg.chat.id, "❌ Invalid number. Enter rarity (e.g., 1000000) or 0 to disable.",
                             reply_markup=types.ReplyKeyboardRemove())
            # Не сбрасываем user_last_command, ждем правильного ввода

        return  # Завершаем обработку

    # --- БЛОКИРОВКА ЗЕЛИЙ В ЛИМБО ---
    # Список команд использования зелий
    use_commands = ["Use", "Use All", "Use amount", "Use Unknown"]

    # Если пользователь пытается нажать Use...
    if text in use_commands and user.get("in_limbo", False):
        # Проверяем, что это именно обычные зелья (контекст через user_last_command)
        cmd = user_last_command.get(uid)
        # Разрешаем Unknown Potion (оно для лимбо), запрещаем остальные
        if cmd != "use_unknown_potion":
            bot.send_message(msg.chat.id, "It doesn't seem to be working right now...", reply_markup=back_menu())
            return

    # Если пользователь пишет число для Use Amount в Лимбо
    if user.get("pending_potion_amount") and user.get("in_limbo", False):
        user["pending_potion_amount"] = None  # Сбрасываем
        save_data()
        bot.send_message(msg.chat.id, "It doesn't seem to be working right now...", reply_markup=back_menu())
        return
    # --------------------------------

    # --- Обработка нажатия кнопки "Use amount" ---
    if text == "Use amount":
        last_cmd = user_last_command.get(uid)
        potion_to_set = None
        potion_name = ""

        if last_cmd == "use_potion":
            potion_to_set = "lucky"
            potion_name = "Lucky Potion"
        elif last_cmd == "use_godlike_potion":
            potion_to_set = "godlike"
            potion_name = "Godlike Potion"
        elif last_cmd == "use_heavenly_potion":
            potion_to_set = "heavenly"
            potion_name = "Heavenly Potion"
        elif last_cmd == "use_bound_potion":
            potion_to_set = "bound"
            potion_name = "Potion of Bound"
        elif last_cmd == "use_fortune_potion_1":
            potion_to_set = "fortune_1"
            potion_name = "Fortune Potion I"
        elif last_cmd == "use_fortune_potion_2":
            potion_to_set = "fortune_2"
            potion_name = "Fortune Potion II"
        elif last_cmd == "use_fortune_potion_3":
            potion_to_set = "fortune_3"
            potion_name = "Fortune Potion III"
        elif last_cmd == "use_jewellery_potion":
            potion_to_set = "jewellery"
            potion_name = "Jewellery Potion"
        elif last_cmd == "use_zombie_potion":
            potion_to_set = "zombie"
            potion_name = "Zombie Potion"
        elif last_cmd == "use_hades_godly_potion":
            potion_to_set = "hades_godly"
            potion_name = "Hades Godly Potion"
        elif last_cmd == "use_zeus_godly_potion":
            potion_to_set = "zeus_godly"
            potion_name = "Zeus Godly Potion"

        if potion_to_set:
            user["pending_potion_amount"] = potion_to_set
            save_data()
            # Отправляем сообщение с кастомной клавиатурой, чтобы убрать кнопки
            bot.send_message(msg.chat.id, f"How much {potion_name} do you want to use?",
                             reply_markup=types.ReplyKeyboardRemove())
            return

    if text == "🎲 Roll":
        threading.Thread(target=process_manual_roll, args=(msg,), daemon=True).start()
        return

    # --- Auras ---
    elif text == "💫 Auras":
        user_last_command[uid] = "Auras"
        user_pages[uid] = 0

        user_auras_owned = user.get("auras", {})

        # 1. Проверяем, есть ли у пользователя ХОТЯ БЫ ОДНА аура из limbo_auras
        has_at_least_one_limbo_aura = False
        for limbo_aura_name in limbo_auras.keys():
            if limbo_aura_name in user_auras_owned and user_auras_owned[limbo_aura_name] > 0:
                has_at_least_one_limbo_aura = True
                break

        aura_list = []

        # 2. Если у него есть хотя бы одна, показываем ВСЕ ауры Лимбо (разблокированные и нет)
        if has_at_least_one_limbo_aura:
            aura_list.append("--- 🌌 Limbo Auras ---")
            for a_name in limbo_auras.keys():
                if a_name in user_auras_owned and user_auras_owned.get(a_name, 0) > 0:
                    aura_list.append(f"{a_name} ✨ x{user_auras_owned.get(a_name, 0)}")
                else:
                    # Показываем LOCKED только если есть хотя бы одна аура лимбо
                    aura_list.append(f"🔒 LOCKED")
            aura_list.append("---------------------")

        # 3. Добавляем обычные ауры
        # Используем auras_default, чтобы список был полным, а не зависел от дня/ночи
        main_aura_dict = auras_default if 'auras_default' in globals() else auras

        for a_name in main_aura_dict.keys():
            if a_name in user_auras_owned and user_auras_owned.get(a_name, 0) > 0:
                aura_list.append(f"{a_name} ✨ x{user_auras_owned.get(a_name, 0)}")
            else:
                aura_list.append(f"🔒 LOCKED")

        send_paginated_list(msg.chat.id, uid, aura_list)
        return

    # --- Stats ---
    elif text == "📊 Stats":
        rare = user["rarest"] or "None"

        # Если в Лимбо - удача от зелий не работает, берем только базу + предметы
        # (get_calculated_luck уже учитывает это, если ты заменил auto_roll и manual_roll,
        # но для красивого отображения делаем так:)

        if user.get("in_limbo", False):
            # В Лимбо удача считается без учета зелий
            # (функция get_calculated_luck у тебя уже имеет проверку "if not in_limbo" для зелий, так что тут ок)
            pass

        calculated_luck = get_calculated_luck(user)
        effective_luck = get_effective_luck(calculated_luck)
        display_luck = int(effective_luck) if effective_luck == int(effective_luck) else round(effective_luck, 2)

        # Добавляем информацию о событии и биоме
        event_info = ""
        MaintanceText = ""
        if is_event_active():
            event_info = f"\n\n🎉 X{EVENT_DATA['event_multiplier']} LUCK EVENT\nTIME LEFT: {get_time_remaining()}"
        if MaintanceActive:
            MaintanceText = f"\n\n⚠️ Sol's rng bot is Going down for Scheduled Maintenance soon."

        biome_info = f"\n🌍 BIOME: {BIOME_DATA['current_biome']}"
        if BIOME_DATA['current_biome'] != "Normal":
            biome_info += f" (ends in: {get_biome_time_remaining()})"

        # Информация о зельях
        active_effects = ""
        in_limbo = user.get("in_limbo", False)

        # 1. Временные зелья
        potion_end_time_str = user.get("potion_end_time")
        if potion_end_time_str:
            try:
                potion_end_time = datetime.fromisoformat(potion_end_time_str)
                now = datetime.now()

                # ЛОГИКА ОТОБРАЖЕНИЯ
                if in_limbo:
                    # Если в Лимбо, считаем время относительно момента ЗАМОРОЗКИ
                    pause_start_str = user.get("limbo_pause_start")
                    if pause_start_str:
                        pause_start = datetime.fromisoformat(pause_start_str)
                        # Сколько оставалось на момент входа?
                        if potion_end_time > pause_start:
                            remaining = potion_end_time - pause_start
                            minutes = int(remaining.total_seconds() // 60)
                            seconds = int(remaining.total_seconds() % 60)
                            potion_bonus = user.get("potion_luck_bonus", 0.0)
                            display_bonus = int(potion_bonus) if potion_bonus == int(potion_bonus) else potion_bonus

                            active_effects += f"\n\n🧪 Timed Potion (+{display_bonus} luck) [DISABLED]\n  TIME LEFT: {minutes:02d}:{seconds:02d} (Paused)"
                else:
                    # Обычный режим
                    if potion_end_time > now:
                        remaining = potion_end_time - now
                        minutes = int(remaining.total_seconds() // 60)
                        seconds = int(remaining.total_seconds() % 60)
                        potion_bonus = user.get("potion_luck_bonus", 0.0)
                        display_bonus = int(potion_bonus) if potion_bonus == int(potion_bonus) else potion_bonus
                        active_effects += f"\n\n🧪 Timed Potion (+{display_bonus} luck)\n  TIME LEFT: {minutes:02d}:{seconds:02d}"
                    else:
                        # Зелье истекло, очищаем
                        user["potion_end_time"] = None
                        user["potion_luck_bonus"] = 0.0
                        save_data()
            except:
                pass

        # 2. Зелья на роллы
        roll_potion_effects = []
        godlike_rolls = user.get("godlike_potion_active", 0)
        heavenly_rolls = user.get("heavenly_potion_active", 0)
        bound_rolls = user.get("bound_potion_active", 0)

        # Статус [DISABLED] если в Лимбо
        disabled_tag = " [DISABLED]" if in_limbo else ""

        if godlike_rolls > 0:
            roll_potion_effects.append(f"  • Godlike (+1000000 luck){disabled_tag}: {godlike_rolls} rolls")
        if heavenly_rolls > 0:
            roll_potion_effects.append(f"  • Heavenly (+425000 luck){disabled_tag}: {heavenly_rolls} rolls")
        if bound_rolls > 0:
            roll_potion_effects.append(f"  • Bound (+200000 luck){disabled_tag}: {bound_rolls} rolls")

        if roll_potion_effects:
            active_effects += "\n\n⚡ Roll-Based Potions:"
            active_effects += "\n" + "\n".join(roll_potion_effects)

        bot.send_message(msg.chat.id,
                         f"🎲 Rolls: {user['rolls']}\n💎 Rarest: {rare}\n🍀 Luck: x{display_luck}{biome_info}{event_info}{active_effects}{MaintanceText}",
                         reply_markup=back_menu())
        return

    # --- Leaderboard ---
    elif text == "🏆 Leaderboard":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("🏅 Roll Leaderboard"))
        markup.row(types.KeyboardButton("💎 RNG Leaderboard"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Choose leaderboard:", reply_markup=markup)
        return

    elif text == "🏅 Roll Leaderboard":
        leaderboard = [(u.get("name", "User"), u.get("rolls", 0)) for u in data["auras"].values()]
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        leaderboard_strings = [f"{i + 1}. {name} — {rolls} rolls" for i, (name, rolls) in enumerate(leaderboard)]
        user_last_command[uid] = "LeaderboardRoll"
        user_pages[uid] = 0
        send_paginated_list(msg.chat.id, uid, leaderboard_strings)
        return

    elif text == "💎 RNG Leaderboard":
        leaderboard = []
        for u in data["auras"].values():
            rarest_aura = u.get("rarest")
            if rarest_aura and rarest_aura in auras_default:
                leaderboard.append((u.get("name", "User"), rarest_aura, auras_default[rarest_aura]))
        leaderboard.sort(key=lambda x: x[2], reverse=True)
        leaderboard_strings = [f"{i + 1}. {name} — {aura}" for i, (name, aura, _) in enumerate(leaderboard)]
        user_last_command[uid] = "LeaderboardRNG"
        user_pages[uid] = 0
        send_paginated_list(msg.chat.id, uid, leaderboard_strings)
        return

    # --- Change Logs ---
    elif text == "📝 Change Logs":
        bot.send_message(msg.chat.id, "📝 Change Logs", reply_markup=back_menu())
        markup = types.InlineKeyboardMarkup(row_width=1)    
        seefull = types.InlineKeyboardButton("See all added auras", "https://telegra.ph/Sols-rng-bot-Added-auras-10-08-19")
        markup.add(seefull)
        bot.send_message(msg.chat.id, changelogs_text, reply_markup=markup)
        return

    # --- Credits ---
    elif text == "📜 Credits":
        credits_text = """

-= CREDITS =-

--= 🔨 Main developers =--

⭐👑🔨 @underrosta - Owner, Developer
⭐👑🔨🧪 @DimdumXD - Co-Owner, Developer, Tester

--= 🧪 Testers =--

🧪 ener - Tester

━━━━━━━━━━━━━━━━━━━━━━━━

🌸 Original Idea - Sol's RNG Team
📩 For help Write to - @underrosta · @DimdumXD

"""

        bot.send_message(msg.chat.id, credits_text, reply_markup=back_menu())
        return

    # --- Potions Menu ---
    elif text == "🧪 Potions":
        # 1. СНАЧАЛА СОЗДАЕМ MARKUP
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # 2. Добавляем стандартные зелья
        markup.row(types.KeyboardButton("[🧪] Heavenly Potion"))
        markup.row(types.KeyboardButton("[🧪] Potion of Bound"))
        markup.row(types.KeyboardButton("[🧪] Fortune Potion I"), types.KeyboardButton("[🧪] Fortune Potion II"),
                   types.KeyboardButton("[🧪] Fortune Potion III"))
        markup.row(types.KeyboardButton("[🧪] Jewellery Potion"), types.KeyboardButton("[🧪] Zombie Potion"))
        markup.row(types.KeyboardButton("[🧪] Hades Godly Potion"), types.KeyboardButton("[🧪] Zeus Godly Potion"))
        markup.row(types.KeyboardButton("[🧪] Godlike Potion"))

        # 3. ТЕПЕРЬ Добавляем Unknown Potion (если условия выполнены)
        if user.get("rolls", 0) > 99999:
            if not user.get("limbo_unlocked", False):
                markup.row(types.KeyboardButton("[❔] Unknown Potion"))
            # Если unlocked, можно не показывать или добавить кнопку "Owned"

        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "All available potions to craft:", reply_markup=markup)
        return

    # unknown potion recipe
    # --- МЕНЮ ЗЕЛИЙ: показ рецепта + кнопка крафта ---
    _potion_menu_map = {
        "[❔] Unknown Potion": ("craft_unknown_potion", "use_unknown_potion",
            "Unknown Potion\nMystery effect...\n\nRequirements:\n"
            "x20 Undefined\nx15 Shift lock\nx10 Nihility",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft Unknown").row("⬅️ Back")),
        "[🧪] Heavenly Potion": ("craft_heavenly_potion", "use_heavenly_potion",
            "Heavenly Potion\n+15000000% (+150000) luck for 1 roll\n\nRequirements:\n"
            "x3 Celestial\nx70 Lucky Potion\nx2 Divinus : Angel\nx5 Powered\nx15 Quartz",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Potion of Bound": ("craft_potion_of_bound", "use_bound_potion",
            "Potion of Bound\n+5000000% (+50000) luck for 1 roll\n\nRequirements:\n"
            "x2 Bounded\nx5 Permafrost\nx35 Lucky Potion\nx15 Lost Soul",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Fortune Potion I": ("craft_fortune_potion_1", "use_fortune_potion_1",
            "Fortune Potion I\n+50% (+0.5) luck for 5 minutes\n\nRequirements:\n"
            "x10 Lucky Potion",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Fortune Potion II": ("craft_fortune_potion_2", "use_fortune_potion_2",
            "Fortune Potion II\n+75% (+0.76) luck for 5 minutes\n\nRequirements:\n"
            "x20 Lucky Potion",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Fortune Potion III": ("craft_fortune_potion_3", "use_fortune_potion_3",
            "Fortune Potion III\n+100% (+1) luck for 5 minutes\n\nRequirements:\n"
            "x30 Lucky Potion",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Jewellery Potion": ("craft_jewellery_potion", "use_jewellery_potion",
            "Jewellery Potion\n+120% (+1.2) luck for 10 minutes\n\nRequirements:\n"
            "x23 Lucky Potion\nx3 Aquamarine\nx3 Sapphire\nx3 Gilded\nx3 Emerald\nx3 Ruby\nx3 Topaz",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Zombie Potion": ("craft_zombie_potion", "use_zombie_potion",
            "Zombie Potion\n+150% (+1.5) luck for 10 minutes\n\nRequirements:\n"
            "x17 Lucky Potion\nx3 Undead\nx3 Bleeding",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Hades Godly Potion": ("craft_hades_godly_potion", "use_hades_godly_potion",
            "Hades Godly Potion\n+300% (+3) luck for 4 hours\n\nRequirements:\n"
            "x50 Lucky Potion\nx1 Hades\nx15 Diaboli\nx12 Bleeding",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Zeus Godly Potion": ("craft_zeus_godly_potion", "use_zeus_godly_potion",
            "Zeus Godly Potion\n+200% (+2) luck for 4 hours\n\nRequirements:\n"
            "x40 Lucky Potion\nx1 Zeus\nx4 Stormal\nx30 Wind",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
        "[🧪] Godlike Potion": ("craft_godlike_potion", "use_godlike_potion",
            "Godlike Potion\n+40000000% (+400000) luck for 1 roll\n\nRequirements:\n"
            "x2 Zeus Godly Potion\nx1 Hades Godly Potion\nx250 Lucky Potion",
            types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back")),
    }
    if text in _potion_menu_map:
        craft_key, use_key, desc, markup = _potion_menu_map[text]
        if user_last_command.get(uid) != use_key:
            bot.send_message(msg.chat.id, desc, reply_markup=markup)
            user_last_command[uid] = craft_key
            return
    # craft unknown potion
    if text == "🛠 Craft Unknown" and user_last_command.get(uid) == "craft_unknown_potion":
        if user.get("limbo_unlocked", False):
            bot.send_message(msg.chat.id, "Already unlocked.", reply_markup=back_menu())
            return

        can_craft = True
        reqs = {"Undefined": 20, "Shift lock": 15, "Nihility": 10}

        with data_lock:
            user = get_user_data(uid, name)
            for a, amt in reqs.items():
                if user.get("auras", {}).get(a, 0) < amt:
                    can_craft = False
                    break

            if can_craft:
                for a, amt in reqs.items():
                    user["auras"][a] -= amt

                user["limbo_unlocked"] = True  # НАВСЕГДА
                # Добавляем предмет в инвентарь для использования
                user.setdefault("inventory", []).append("Unknown Potion")
                save_data()

        if can_craft:
            bot.send_message(msg.chat.id, "👁️ You have crafted the Unknown Potion.", reply_markup=back_menu())
        else:
            bot.send_message(msg.chat.id, "❌ You are not ready yet...", reply_markup=back_menu())
        return

    # --- КРАФТ (все рецепты в CRAFT_RECIPES) ---
    if text == "🛠 Craft":
        craft_key = user_last_command.get(uid, "")
        if craft_key and craft_key.startswith("craft_"):
            if do_craft(msg, uid, name, craft_key):
                return

    elif text == "⚙️ Settings":
        dn_status = "ON" if user.get("notify_day_night", True) else "OFF"
        global_status = "ON" if user.get("notify_global", True) else "OFF"

        pin_rarity = user.get("auto_pin_rarity")
        pin_status = f"({pin_rarity})" if pin_rarity else "(OFF)"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton(f"DAY/NIGHT Notifications ({dn_status})"))
        markup.row(types.KeyboardButton(f"Global Messages ({global_status})"))
        markup.row(types.KeyboardButton(f"Auto Pin Rarities {pin_status}"))
        gif_rarity = user.get('gif_rarity_threshold', 1000000)
        # Если порог < 1M, считаем что гифки выключены
        gif_status = f"({gif_rarity})" if gif_rarity >= 1000000 else "(OFF)"
        markup.row(types.KeyboardButton(f"Gif rarity cutscenes {gif_status}"))

        # Новая логика для кнопки Auto Roll
        rolls = user.get("rolls", 0)
        if rolls > 9999:
            # Если Auto Roll уже включен, показываем только статус ON
            if user.get("auto_roll_enabled", False):
                markup.row(types.KeyboardButton("Auto Roll (ON)"))
            else:
                markup.row(types.KeyboardButton("Auto Roll (OFF)"))
        else:
            markup.row(types.KeyboardButton("Auto Roll (10000 Rolls Required)"))

        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "User Settings:", reply_markup=markup)
        return

    elif text == "Auto Roll (10000 Rolls Required)":
        bot.send_message(msg.chat.id, "10000 Rolls Required for this option!", reply_markup=main_menu(uid))
        return

    elif text == "Auto Roll (OFF)":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Enable Auto Roll"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Do you want to enable Auto Roll?", reply_markup=markup)
        return

    elif text == "Auto Roll (ON)":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Disable Auto Roll"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Auto Roll is active. Do you want to disable it?", reply_markup=markup)
        return

    elif text == "Enable Auto Roll":
        if user.get("rolls", 0) < 9999:
            bot.send_message(msg.chat.id, "10000 Rolls Required for this option!", reply_markup=main_menu(uid))
            return
        
        user["auto_roll_enabled"] = True
        save_data()
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Disable Auto Roll"))
        bot.send_message(msg.chat.id, "Auto Roll enabled. Starting...", reply_markup=markup)

        # Запускаем поток для этого пользователя
        threading.Thread(target=auto_roll_thread, args=(uid, msg.chat.id), daemon=True).start()
        return

    elif text == "Disable Auto Roll":
        user["auto_roll_enabled"] = False
        save_data()
        bot.send_message(msg.chat.id, "Auto Roll disabled.", reply_markup=main_menu(uid))
        return

    elif text.startswith("Auto Pin Rarities"):
        user_last_command[uid] = "set_auto_pin"
        save_data()
        bot.send_message(msg.chat.id, "Enter the rarity you want to auto pin (e.g., 1000000).\nEnter 0 to disable.",
                         reply_markup=types.ReplyKeyboardRemove())
        return

    elif text.startswith("Gif rarity cutscenes"):
        user_last_command[uid] = "set_gif_rarity"
        save_data()
        bot.send_message(msg.chat.id,
                         "Enter the minimum rarity that you want to see cutscenes from (e.g., 1000000).\nEnter lower than 1000000 or a large number (like 999999999999) to disable all cutscenes.",
                         reply_markup=types.ReplyKeyboardRemove())
        return

    elif text.startswith("DAY/NIGHT Notifications"):
        user = get_user_data(uid, name)
        current_status = user.get("notify_day_night", True)
        user["notify_day_night"] = not current_status  # Переключаем
        save_data()

        # Обновляем меню, чтобы показать новое состояние
        dn_status = "ON" if user["notify_day_night"] else "OFF"
        global_status = "ON" if user.get("notify_global", True) else "OFF"
        pin_rarity = user.get("auto_pin_rarity")
        pin_status = f"({pin_rarity})" if pin_rarity else "(OFF)"
        gif_rarity = user.get('gif_rarity_threshold', 1000000)
        gif_status = f"({gif_rarity})" if gif_rarity >= 1000000 else "(OFF)"  # <--- Добавим это для фичи №5

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton(f"DAY/NIGHT Notifications ({dn_status})"))
        markup.row(types.KeyboardButton(f"Global Messages ({global_status})"))
        markup.row(types.KeyboardButton(f"Auto Pin Rarities {pin_status}"))
        markup.row(types.KeyboardButton(f"Gif rarity cutscenes {gif_status}"))  # <--- Добавим это для фичи №5

        rolls = user.get("rolls", 0)
        if rolls > 9999:
            if user.get("auto_roll_enabled", False):
                markup.row(types.KeyboardButton("Auto Roll (ON)"))
            else:
                markup.row(types.KeyboardButton("Auto Roll (OFF)"))
        else:
            markup.row(types.KeyboardButton("Auto Roll (10000 Rolls Required)"))

        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, f"DAY/NIGHT Notifications set to {dn_status}", reply_markup=markup)
        return

    elif text.startswith("Global Messages"):
        user = get_user_data(uid, name)
        current_status = user.get("notify_global", True)
        user["notify_global"] = not current_status  # Переключаем
        save_data()

        # Обновляем меню, чтобы показать новое состояние
        dn_status = "ON" if user.get("notify_day_night", True) else "OFF"
        global_status = "ON" if user["notify_global"] else "OFF"
        pin_rarity = user.get("auto_pin_rarity")
        pin_status = f"({pin_rarity})" if pin_rarity else "(OFF)"
        gif_rarity = user.get('gif_rarity_threshold', 1000000)
        gif_status = f"({gif_rarity})" if gif_rarity >= 1000000 else "(OFF)"  # <--- Добавим это для фичи №5

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton(f"DAY/NIGHT Notifications ({dn_status})"))
        markup.row(types.KeyboardButton(f"Global Messages ({global_status})"))
        markup.row(types.KeyboardButton(f"Auto Pin Rarities {pin_status}"))
        markup.row(types.KeyboardButton(f"Gif rarity cutscenes {gif_status}"))  # <--- Добавим это для фичи №5

        rolls = user.get("rolls", 0)
        if rolls > 9999:
            if user.get("auto_roll_enabled", False):
                markup.row(types.KeyboardButton("Auto Roll (ON)"))
            else:
                markup.row(types.KeyboardButton("Auto Roll (OFF)"))
        else:
            markup.row(types.KeyboardButton("Auto Roll (10000 Rolls Required)"))

        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, f"Global Messages set to {global_status}", reply_markup=markup)
        return

        # --- Back / Pagination ---
    elif text == "⬅️ Back":
        event_info = ""
        MaintanceText = ""
        if is_event_active():
            event_info = f"\n\n🎉 X{EVENT_DATA['event_multiplier']} LUCK EVENT ACTIVE! 🎉\nTime left: {get_time_remaining()}"
        if MaintanceActive:
                MaintanceText = f"\n\n⚠️ Sol's rng bot is Going down for Scheduled Maintenance soon."

        biome_info = f"\nBIOME: {BIOME_DATA['current_biome']}"
        if BIOME_DATA['current_biome'] != "Normal":
            biome_info += f" (ends in: {get_biome_time_remaining()})"

        bot.send_message(msg.chat.id,
                         f"Sol's RNG 🎰\nTime: {'DAYTIME ☀️' if is_day else 'NIGHTTIME 🌙'}{biome_info}{event_info}{MaintanceText}",
                         reply_markup=main_menu(uid)
                         )
        return
    elif text == "⬅️ Previous page":
        if uid in user_pages and user_pages[uid] > 0:
            user_pages[uid] -= 1
            redo_last_list(uid, msg.chat.id)
        return
    elif text == "➡️ Next page":
        user_pages[uid] = user_pages.get(uid, 0) + 1
        redo_last_list(uid, msg.chat.id)
        return

    # --- Lucky Potion Claim ---
    elif text == "🍀 Lucky Potion spawned!":
        if lucky_potion_active:
            lucky_potion_active = False  # Забираем зелье
            user.setdefault("inventory", [])
            user["inventory"].append("Lucky Potion")
            save_data()
            bot.send_message(msg.chat.id, "🍀 Lucky Potion added to your Inventory.", reply_markup=main_menu(uid))
        else:
            bot.send_message(msg.chat.id, "There is no Lucky Potion around here...", reply_markup=main_menu(uid))
        return

    # --- WORKSHOP ---
    if text == "🛠️ Workshop":
        user_current_menu[uid] = "workshop"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Все предметы всегда доступны для крафта
        items_tiers = list(WORKSHOP_ITEMS.keys())  # Автогенерация из WORKSHOP_ITEMS

        for item in items_tiers:
            markup.row(item)
        markup.row("⬅️ Back")
        bot.send_message(msg.chat.id, "Welcome to the workshop! What do you wish to craft?", reply_markup=markup)
        return

    # --- WORKSHOP ITEMS: показ описания + кнопка крафта (из WORKSHOP_ITEMS) ---
    _workshop_info = {name: (item["craft_key"], item["desc"]) for name, item in WORKSHOP_ITEMS.items()}
    if text in _workshop_info and user_current_menu.get(uid) == "workshop":
        craft_key, desc = _workshop_info[text]
        bot.send_message(msg.chat.id, desc,
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row("🛠 Craft").row("⬅️ Back"))
        user_last_command[uid] = craft_key
        return

    # --- INVENTORY ---
    if text == "🎒 Inventory":
        user_current_menu[uid] = "inventory"
        inv = user.get("inventory", [])
        if not inv:
            bot.send_message(msg.chat.id, "You don't have anything in your inventory.", reply_markup=back_menu())
            return

        # Сортируем инвентарь по тирам
        tier_order = {"[T1]": 1, "[T2]": 2, "[T3]": 3, "[T4]": 4, "[T5]": 5, "[T6]": 6, "[T7]": 7, "[T8]": 8, "[T9]": 9,
                      "[T10]": 10}

        def get_tier(item):
            for tier in tier_order:
                if item.startswith(tier):
                    return tier_order[tier]
            return 0  # Для зелий и других не-тир предметов

        sorted_gear = sorted([item for item in inv if item in gear_items], key=get_tier)
        potion_count = inv.count("Lucky Potion")
        heavenly_potion_count = inv.count("Heavenly Potion")
        bound_potion_count = inv.count("Potion of Bound")
        fortune_1_count = inv.count("Fortune Potion I")
        fortune_2_count = inv.count("Fortune Potion II")
        fortune_3_count = inv.count("Fortune Potion III")
        jewellery_count = inv.count("Jewellery Potion")
        zombie_count = inv.count("Zombie Potion")
        hades_godly_count = inv.count("Hades Godly Potion")
        zeus_godly_count = inv.count("Zeus Godly Potion")
        godlike_count = inv.count("Godlike Potion")

        # Считаем количество каждого предмета
        item_counts = {}
        for item in sorted_gear:
            item_counts[item] = item_counts.get(item, 0) + 1

        msg_inv = "Your inventory:\n"
        if item_counts:
            msg_inv += "\n".join([f"{item} x{count}" for item, count in item_counts.items()])

        if potion_count > 0:
            item_counts["Lucky Potion"] = potion_count
            msg_inv += f"\n\nLucky Potion x{potion_count}"
        if heavenly_potion_count > 0:
            item_counts["Heavenly Potion"] = heavenly_potion_count
            msg_inv += f"\nHeavenly Potion x{heavenly_potion_count}"
        if bound_potion_count > 0:
            item_counts["Potion of Bound"] = bound_potion_count
            msg_inv += f"\nPotion of Bound x{bound_potion_count}"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Добавляем кнопки для каждого уникального предмета
        unique_gear = list(item_counts.keys())
        if "Lucky Potion" in unique_gear:
            unique_gear.remove("Lucky Potion")
        if "Heavenly Potion" in unique_gear:
            unique_gear.remove("Heavenly Potion")
        if "Potion of Bound" in unique_gear:
            unique_gear.remove("Potion of Bound")
        if fortune_1_count > 0:
            item_counts["Fortune Potion I"] = fortune_1_count
            msg_inv += f"\nFortune Potion I x{fortune_1_count}"
        if fortune_2_count > 0:
            item_counts["Fortune Potion II"] = fortune_2_count
            msg_inv += f"\nFortune Potion II x{fortune_2_count}"
        if fortune_3_count > 0:
            item_counts["Fortune Potion III"] = fortune_3_count
            msg_inv += f"\nFortune Potion III x{fortune_3_count}"
        if jewellery_count > 0:
            item_counts["Jewellery Potion"] = jewellery_count
            msg_inv += f"\nJewellery Potion x{jewellery_count}"
        if zombie_count > 0:
            item_counts["Zombie Potion"] = zombie_count
            msg_inv += f"\nZombie Potion x{zombie_count}"
        if hades_godly_count > 0:
            item_counts["Hades Godly Potion"] = hades_godly_count
            msg_inv += f"\nHades Godly Potion x{hades_godly_count}"
        if zeus_godly_count > 0:
            item_counts["Zeus Godly Potion"] = zeus_godly_count
            msg_inv += f"\nZeus Godly Potion x{zeus_godly_count}"
        if godlike_count > 0:
            item_counts["Godlike Potion"] = godlike_count
            msg_inv += f"\nGodlike Potion x{godlike_count}"

        new_potions_list = [
            "Fortune Potion I", "Fortune Potion II", "Fortune Potion III",
            "Jewellery Potion", "Zombie Potion", "Hades Godly Potion",
            "Zeus Godly Potion", "Godlike Potion"
        ]
        for potion_name in new_potions_list:
            if potion_name in unique_gear:
                unique_gear.remove(potion_name)

        for i in range(0, len(unique_gear), 2):
            row = unique_gear[i:i + 2]
            markup.row(*row)

        if potion_count > 0:
            markup.row(types.KeyboardButton("Lucky Potion"))
        if heavenly_potion_count > 0:
            markup.row(types.KeyboardButton("Heavenly Potion"))
        if bound_potion_count > 0:
            markup.row(types.KeyboardButton("Potion of Bound"))
        if fortune_1_count > 0:
            markup.row(types.KeyboardButton("Fortune Potion I"))
        if fortune_2_count > 0:
            markup.row(types.KeyboardButton("Fortune Potion II"))
        if fortune_3_count > 0:
            markup.row(types.KeyboardButton("Fortune Potion III"))
        if jewellery_count > 0:
            markup.row(types.KeyboardButton("Jewellery Potion"))
        if zombie_count > 0:
            markup.row(types.KeyboardButton("Zombie Potion"))
        if hades_godly_count > 0:
            markup.row(types.KeyboardButton("Hades Godly Potion"))
        if zeus_godly_count > 0:
            markup.row(types.KeyboardButton("Zeus Godly Potion"))
        if godlike_count > 0:
            markup.row(types.KeyboardButton("Godlike Potion"))

        unknown_count = inv.count("Unknown Potion")
        if unknown_count > 0:
            msg_inv += f"\n\n[❔] Unknown Potion x{unknown_count}"
            markup.row(types.KeyboardButton("Unknown Potion"))

        markup.row("⬅️ Back")
        bot.send_message(msg.chat.id, msg_inv, reply_markup=markup)
        return

    # --- Обработка нажатия на Unknown Potion в инвентаре ---
    if text == "Unknown Potion":
        # Проверяем наличие
        if "Unknown Potion" not in user.get("inventory", []):
            bot.send_message(msg.chat.id, "You don't have this item.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).row("Use Unknown").row("⬅️ Back")
        bot.send_message(msg.chat.id, "Do you want to use Unknown Potion?", reply_markup=markup)
        user_last_command[uid] = "use_unknown_potion"
        return

    # --- Обработка кнопки Use Unknown ---
    if text == "Use Unknown" and user_last_command.get(uid) == "use_unknown_potion":
        # ПОВТОРНАЯ Проверка наличия перед использованием
        if "Unknown Potion" in user.get("inventory", []):
            # Проверяем, не активен ли уже бафф
            unknown_end_str = user.get("unknown_potion_end")
            if unknown_end_str:
                try:
                    if datetime.fromisoformat(unknown_end_str) > datetime.now():
                        bot.send_message(msg.chat.id, "You already feel strange...", reply_markup=back_menu())
                        return
                except:
                    pass

            # Активируем бафф
            user["unknown_potion_end"] = (datetime.now() + timedelta(minutes=2)).isoformat()
            save_data()
            bot.send_message(msg.chat.id, "You drink the potion...\nYou feel detached from reality for 2 minutes.",
                             reply_markup=back_menu())
        else:
            bot.send_message(msg.chat.id, "❌ You don't have the Unknown Potion!", reply_markup=back_menu())
        return

    # --- Lucky Potion ---
    if text == "Lucky Potion":
        potion_count = user.get("inventory", []).count("Lucky Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any Lucky Potions.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Lucky Potion\n+100% luck for 1 minute", reply_markup=markup)
        user_last_command[uid] = "use_potion"  # Это для "Use" и "Use All"
        return

    if text == "Use" and user_last_command.get(uid) == "use_potion":
        if "Lucky Potion" in user.get("inventory", []):
            user["inventory"].remove("Lucky Potion")
            apply_potion_effect(user, 1)
            save_data()
            bot.send_message(msg.chat.id, "You used 1 Lucky Potion. +1 Luck for 1 minute.", reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_potion":
        potion_count = user.get("inventory", []).count("Lucky Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Lucky Potion"]
            apply_potion_effect(user, potion_count)
            save_data()
            bot.send_message(msg.chat.id,
                             f"You used {potion_count} Lucky Potions. +1 Luck for {potion_count} minutes.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Heavenly Potion (from Inventory) ---
    if text == "Heavenly Potion":
        potion_count = user.get("inventory", []).count("Heavenly Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any Heavenly Potions.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Heavenly Potion\n+15000000% (+150000) luck for 1 roll", reply_markup=markup)
        user_last_command[uid] = "use_heavenly_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_heavenly_potion":
        if "Heavenly Potion" in user.get("inventory", []):
            user["inventory"].remove("Heavenly Potion")
            user["heavenly_potion_active"] = user.get("heavenly_potion_active", 0) + 1
            save_data()
            bot.send_message(msg.chat.id, "You used 1 Heavenly Potion. +150000 luck for 1 roll.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_heavenly_potion":
        potion_count = user.get("inventory", []).count("Heavenly Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Heavenly Potion"]
            user["heavenly_potion_active"] = user.get("heavenly_potion_active", 0) + potion_count
            save_data()
            bot.send_message(msg.chat.id,
                             f"You used {potion_count} Heavenly Potions. +150000 luck for {potion_count} rolls.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Potion of Bound (from Inventory) ---
    if text == "Potion of Bound":
        potion_count = user.get("inventory", []).count("Potion of Bound")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any Potions of Bound.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))  # <--- НОВАЯ КНОПКА
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Potion of Bound\n+5000000% (+50000) luck for 1 roll", reply_markup=markup)
        user_last_command[uid] = "use_bound_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_bound_potion":
        if "Potion of Bound" in user.get("inventory", []):
            user["inventory"].remove("Potion of Bound")
            user["bound_potion_active"] = user.get("bound_potion_active", 0) + 1
            save_data()
            bot.send_message(msg.chat.id, "You used 1 Potion of Bound. +50000 luck for 1 roll.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_bound_potion":
        potion_count = user.get("inventory", []).count("Potion of Bound")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Potion of Bound"]
            user["bound_potion_active"] = user.get("bound_potion_active", 0) + potion_count
            save_data()
            bot.send_message(msg.chat.id,
                             f"You used {potion_count} Potions of Bound. +50000 luck for {potion_count} rolls.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Fortune Potion I (from Inventory) ---
    if text == "Fortune Potion I":
        potion_count = user.get("inventory", []).count("Fortune Potion I")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Fortune Potion I\n+50% (+0.5) luck for 5 minutes", reply_markup=markup)
        user_last_command[uid] = "use_fortune_potion_1"
        return

    if text == "Use" and user_last_command.get(uid) == "use_fortune_potion_1":
        if "Fortune Potion I" in user.get("inventory", []):
            user["inventory"].remove("Fortune Potion I")
            # +2 luck for 5 minutes (300 seconds)
            response_msg = apply_timed_potion(user, 0.5, 300)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_fortune_potion_1":
        potion_count = user.get("inventory", []).count("Fortune Potion I")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Fortune Potion I"]
            # +2 luck, 5 min (300s) per potion
            response_msg = apply_timed_potion(user, 0.5, 300 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Fortune Potion I. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Fortune Potion II (from Inventory) ---
    if text == "Fortune Potion II":
        potion_count = user.get("inventory", []).count("Fortune Potion II")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Fortune Potion II\n+75% (+0.75) luck for 5 minutes", reply_markup=markup)
        user_last_command[uid] = "use_fortune_potion_2"
        return

    if text == "Use" and user_last_command.get(uid) == "use_fortune_potion_2":
        if "Fortune Potion II" in user.get("inventory", []):
            user["inventory"].remove("Fortune Potion II")
            # +3.5 luck for 5 minutes (300 seconds)
            response_msg = apply_timed_potion(user, 0.75, 300)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_fortune_potion_2":
        potion_count = user.get("inventory", []).count("Fortune Potion II")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Fortune Potion II"]
            response_msg = apply_timed_potion(user, 0.75, 300 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Fortune Potion II. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Fortune Potion III (from Inventory) ---
    if text == "Fortune Potion III":
        potion_count = user.get("inventory", []).count("Fortune Potion III")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Fortune Potion III\n+100% (+1) luck for 5 minutes", reply_markup=markup)
        user_last_command[uid] = "use_fortune_potion_3"
        return

    if text == "Use" and user_last_command.get(uid) == "use_fortune_potion_3":
        if "Fortune Potion III" in user.get("inventory", []):
            user["inventory"].remove("Fortune Potion III")
            # +5 luck for 5 minutes (300 seconds)
            response_msg = apply_timed_potion(user, 1.0, 300)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_fortune_potion_3":
        potion_count = user.get("inventory", []).count("Fortune Potion III")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Fortune Potion III"]
            response_msg = apply_timed_potion(user, 1.0, 300 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Fortune Potion III. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Jewellery Potion (from Inventory) ---
    if text == "Jewellery Potion":
        potion_count = user.get("inventory", []).count("Jewellery Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Jewellery Potion\n+120% (+1.2) luck for 10 minutes", reply_markup=markup)
        user_last_command[uid] = "use_jewellery_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_jewellery_potion":
        if "Jewellery Potion" in user.get("inventory", []):
            user["inventory"].remove("Jewellery Potion")
            # +6 luck for 10 minutes (600 seconds)
            response_msg = apply_timed_potion(user, 1.2, 600)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_jewellery_potion":
        potion_count = user.get("inventory", []).count("Jewellery Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Jewellery Potion"]
            response_msg = apply_timed_potion(user, 1.2, 600 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Jewellery Potion. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Zombie Potion (from Inventory) ---
    if text == "Zombie Potion":
        potion_count = user.get("inventory", []).count("Zombie Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Zombie Potion\n+150% (+1.5) luck for 10 minutes", reply_markup=markup)
        user_last_command[uid] = "use_zombie_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_zombie_potion":
        if "Zombie Potion" in user.get("inventory", []):
            user["inventory"].remove("Zombie Potion")
            # +8 luck for 10 minutes (600 seconds)
            response_msg = apply_timed_potion(user, 1.5, 600)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_zombie_potion":
        potion_count = user.get("inventory", []).count("Zombie Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Zombie Potion"]
            response_msg = apply_timed_potion(user, 1.5, 600 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Zombie Potion. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Hades Godly Potion (from Inventory) ---
    if text == "Hades Godly Potion":
        potion_count = user.get("inventory", []).count("Hades Godly Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Hades Godly Potion\n+300% (+3) luck for 4 hours", reply_markup=markup)
        user_last_command[uid] = "use_hades_godly_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_hades_godly_potion":
        if "Hades Godly Potion" in user.get("inventory", []):
            user["inventory"].remove("Hades Godly Potion")
            # +12 luck for 4 hours (14400 seconds)
            response_msg = apply_timed_potion(user, 3.0, 14400)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_hades_godly_potion":
        potion_count = user.get("inventory", []).count("Hades Godly Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Hades Godly Potion"]
            response_msg = apply_timed_potion(user, 3.0, 14400 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Hades Godly Potion. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Zeus Godly Potion (from Inventory) ---
    if text == "Zeus Godly Potion":
        potion_count = user.get("inventory", []).count("Zeus Godly Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))

        bot.send_message(msg.chat.id, "Zeus Godly Potion\n+200% (+2) luck for 4 hours", reply_markup=markup)
        user_last_command[uid] = "use_zeus_godly_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_zeus_godly_potion":
        if "Zeus Godly Potion" in user.get("inventory", []):
            user["inventory"].remove("Zeus Godly Potion")
            # +10 luck for 4 hours (14400 seconds)
            response_msg = apply_timed_potion(user, 2.0, 14400)
            save_data()
            bot.send_message(msg.chat.id, response_msg, reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_zeus_godly_potion":
        potion_count = user.get("inventory", []).count("Zeus Godly Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Zeus Godly Potion"]
            response_msg = apply_timed_potion(user, 2.0, 14400 * potion_count)
            save_data()
            bot.send_message(msg.chat.id, f"Used {potion_count} Zeus Godly Potion. {response_msg}",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- Godlike Potion (from Inventory) ---
    if text == "Godlike Potion":
        potion_count = user.get("inventory", []).count("Godlike Potion")
        if potion_count == 0:
            bot.send_message(msg.chat.id, "You don't have any Godlike Potions.", reply_markup=back_menu())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("Use"))
        if potion_count > 1:
            markup.row(types.KeyboardButton("Use All"))
            markup.row(types.KeyboardButton("Use amount"))
        markup.row(types.KeyboardButton("⬅️ Back"))
        bot.send_message(msg.chat.id, "Godlike Potion\n+100000000% (+1000000) luck for 1 roll", reply_markup=markup)
        user_last_command[uid] = "use_godlike_potion"
        return

    if text == "Use" and user_last_command.get(uid) == "use_godlike_potion":
        if "Godlike Potion" in user.get("inventory", []):
            user["inventory"].remove("Godlike Potion")
            user["godlike_potion_active"] = user.get("godlike_potion_active", 0) + 1
            save_data()
            bot.send_message(msg.chat.id, "You used 1 Godlike Potion. +1000000 luck for 1 roll.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    if text == "Use All" and user_last_command.get(uid) == "use_godlike_potion":
        potion_count = user.get("inventory", []).count("Godlike Potion")
        if potion_count > 0:
            user["inventory"] = [item for item in user["inventory"] if item != "Godlike Potion"]
            user["godlike_potion_active"] = user.get("godlike_potion_active", 0) + potion_count
            save_data()
            bot.send_message(msg.chat.id,
                             f"You used {potion_count} Godlike Potions. +1000000 luck for {potion_count} rolls.",
                             reply_markup=back_menu())
            user_last_command[uid] = None
        else:
            bot.send_message(msg.chat.id, "You don't have any potions.", reply_markup=back_menu())
        return

    # --- EQUIP ITEMS (Checking from inventory) ---
    if text in gear_items:
        # Проверяем, есть ли хотя бы один такой предмет в инвентаре
        item_count = sum(1 for item in user.get("inventory", []) if item == text)
        if item_count == 0:
            bot.send_message(msg.chat.id, "You don't have this item.", reply_markup=back_menu())
            return

        if text in user.get("equipped", []):
            bot.send_message(
                msg.chat.id,
                f"Do you want to unequip {text}?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(f"❌ Unequip {text}").row("⬅️ Back")
            )
        else:
            bot.send_message(
                msg.chat.id,
                f"Do you want to equip {text}?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(f"✅ Equip {text}").row("⬅️ Back")
            )
        return

    # --- EQUIP / UNEQUIP (Action) ---
    if text.startswith("✅ Equip "):
        item = text.replace("✅ Equip ", "")
        if text.startswith("✅ Equip "):
            item = text.replace("✅ Equip ", "")
        # Проверяем, есть ли у пользователя этот предмет в инвентаре
        if item not in user.get("inventory", []):
            bot.send_message(msg.chat.id, f"❌ You don't have {item} in your inventory.", reply_markup=main_menu(uid))
            return  # Выходим, не давая экипировать

        if "equipped" not in user:
            user["equipped"] = []
        if "equipped" not in user:
            user["equipped"] = []

        # Проверяем, есть ли уже экипированная перчатка
        equipped_glove = next((g for g in gear_items if g in user.get("equipped", [])), None)

        # Если уже надета другая перчатка — снимаем её
        if equipped_glove and equipped_glove != item:
            user["equipped"].remove(equipped_glove)
            bot.send_message(msg.chat.id, f"⚠️ {equipped_glove} has been unequipped.")

        # Экипируем новую
        if item not in user["equipped"]:
            user["equipped"].append(item)
            save_data()
            bot.send_message(msg.chat.id, f"✅ You equipped {item}!", reply_markup=back_menu())
        return

    if text.startswith("❌ Unequip "):
        item = text.replace("❌ Unequip ", "")
        if item in user.get("equipped", []):
            user["equipped"].remove(item)
            save_data()
            bot.send_message(msg.chat.id, f"You unequipped {item}.", reply_markup=back_menu())
        return

# Запускаем проверку Auto Roll в отдельном потоке, чтобы не блокировать старт

threading.Thread(target=restart_auto_rollers, daemon=True).start()

while True:

    try:
        bot.polling(non_stop=True, interval=0, skip_pending=True)
        print("[✓] Polling stopped gracefully.")
        break  # Выходим из цикла, чтобы скрипт завершился

    except requests .exceptions.ReadTimeout:
        print("[⚠️] Read Timeout. Waiting for [1s]")
        time.sleep(1)
    except requests.exceptions.ConnectionError:
        print("[⚠️] Connection Error. Waiting for [1s]")
        time.sleep(1)
    except Exception as e:
        print(f"[❌] Critical error. {e}")
        time.sleep(5)  # Спим дольше при неизвестных ошибках

print("[✓] Bot shut down complete.")
