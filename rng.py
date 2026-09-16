import random
import math
from Config import limbo_auras, auras, BIOMES
from data_files import BIOME_DATA

def get_biome_multiplier(aura_name):

    # Возвращает множитель биома для конкретной ауры
    current_biome = BIOME_DATA["current_biome"]
    
    # Glitched ауры доступны ТОЛЬКО в Glitched биоме
    if aura_name in ["Oppression", "Glitch", "Fault"] and current_biome != "Glitched":
        return math.inf  # Сделать невозможным выпадение

    # Dreamspace ауры доступны только в Glitched и Dreamspace биомах
    if aura_name in ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"] and current_biome not in ["Glitched", "Dreamspace"]:
        return math.inf
    
    if aura_name == "Monarch" and current_biome not in ["Corruption", "Glitched"]:
        return math.inf
    
    if aura_name == "Leviathan" and current_biome not in ["Rainy", "Glitched"]:
        return math.inf
    
    if aura_name == "Borealis" and current_biome != "Dreamspace":
        return math.inf
    
    if aura_name == "Breakthrough" and current_biome == "Null":
        return math.inf

    # Illusionary никогда не проходит через обычную luck-систему.
    # Её шанс всегда фиксирован 1/10,000,000 и проверяется отдельно (см. roll-обработчики).
    if aura_name == "Illusionary":
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
        if aura == "Illusionary": continue  # только отдельная фиксированная проверка в Cyberspace

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