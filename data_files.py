import os
import json
from datetime import datetime

# Загрузка данных биома

BIOME_FILE = "biome_data.json"

def load_biome_data():

    if os.path.exists(BIOME_FILE):
        try:
            with open(BIOME_FILE, "r", encoding="utf-8") as f:
                biome_data = json.load(f)
                # Преобразуем строку времени обратно в datetime
                if "biome_end_time" in biome_data and biome_data["biome_end_time"]:
                    biome_data["biome_end_time"] = datetime.fromisoformat(biome_data["biome_end_time"])
                return biome_data
        except Exception as e:
            print(f"[⚠️] Error loading biome data: {e}")
            return {"current_biome": "Normal", "biome_end_time": None}
    return {"current_biome": "Normal", "biome_end_time": None}

def save_biome_data():

    biome_data_to_save = {
        "current_biome": BIOME_DATA["current_biome"],
        "biome_end_time": BIOME_DATA["biome_end_time"].isoformat() if BIOME_DATA["biome_end_time"] else None
    }
    with open(BIOME_FILE, "w", encoding="utf-8") as f:
        json.dump(biome_data_to_save, f, ensure_ascii=False)
        
BIOME_DATA = load_biome_data()