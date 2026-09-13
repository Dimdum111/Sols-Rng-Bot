# Config.py
# We store auras, items, big texts here so it would not make main.py 1 big blob of a code!!

# Все ауры в игре
auras = {
    "Common": 2,
    "Uncommon": 4,
    "Good": 5,
    "Natural": 8,
    "Rare": 16,
    "Divinus": 32,
    "Crystallised": 64,
    "Rage": 128,
    "Dizzy": 123,
    "Topaz": 150,
    "Ruby": 350,
    "Forbidden": 404,
    "Emerald": 500,
    "Gilded": 512,
    "Ink": 700,
    "Jackpot": 777,
    "Sapphire": 800,
    "Aquamarine": 900,
    "Wind": 900,
    "Diaboli": 1004,
    "Penumbra": 1010,
    "Umbra": 1010,
    "Precious": 1024,
    "Hydrogen": 1111,
    "Atomic": 1180,
    "Glock": 1700,
    "Magnetic": 2048,
    "Ash": 2300,
    "Glacier": 2304,
    "Player": 3000,
    "Flora": 3700,
    "Cola": 3999,
    "Sidereum": 4096,
    "Bleeding": 4444,
    "Flutter": 5000,
    "Targeted": 5000,
    "Flushed": 6900,
    "Hazard": 7000,
    "Doodle": 7500,
    "Quartz": 8192,
    "Honey": 8335,
    "Lost Soul": 9200,
    "Atomic : Riboneucleic": 9876,
    "Undead": 12000,
    "Corrosive": 12000,
    "Kawaii": 12300,
    "Rage : Heated": 12800,
    "Ink : LEAK": 14000,
    "Powered": 16384,
    "Gilded : Crowned": 20000,
    "Marsh": 25000,
    "Copper": 29000,
    "WATT": 32768,
    "Aquatic": 40000,
    "Solar": 50000,
    "Lunar": 50000,
    "Starlight": 50000,
    "Star Rider": 50000,
    "Flushed : Lobotomy": 69000,
    "Hazard : Rays": 70000,
    "Nautilus": 70000,
    "Permafrost": 73500,
    "Flow": 87000,
    "Stormal": 90000,
    "Exotic": 99999,
    "Diaboli : Void": 100400,
    "Comet": 120000,
    "Divinus : Angel": 120000,
    "Jade": 125000,
    "Spectre": 140000,
    "Jazz": 160000,
    "Aether": 180000,
    "Bounded": 200000,
    "Lantern": 333333,
    "Celestial": 350000,
    "Vortex": 399999,
    "Terror": 400000,
    "Hope": 488725,
    "Warlock": 666000,
    "Undead : Devil": 666666,
    "Kyawthuite": 850000,
    "Arcane": 1000000,
    "Starlight : Kunzite": 1000000,
    "Magnetic : Reverse Polarity": 1024000,
    "Undefined": 1111000,
    "Rage : Brawler": 1280000,
    "Symbiosis": 1331201,
    "Astral": 1336000,
    "Cosmos": 1520000,
    "Archmage": 1766000,
    "Respawn": 1999999,
    "Gravitational": 2000000,
    "Bounded : Unbound": 2000000,
    "Flutter : Buggify": 2000000,
    "Flowed": 2121121,
    "Virtual": 2500000,
    "Parasite": 3000000,
    "Orion": 3000000,
    "Apatite": 3133133,
    "Savior": 3200000,
    "Shift lock": 3325000,
    "Cosmos : Alice": 3500000,
    "Evanescent": 3360000,
    "Crystallized : Bejeweled": 3600000,
    "Aquatic : Flame": 4000000,
    "Poseidon": 4000000,
    "Metabytes": 4000000,
    "Wraith": 4100000,
    "Zeus": 4500000,
    "Solar : Solstice": 5000000,
    "Galaxy": 5000000,
    "Lunar : Full Moon": 5000000,
    "Twilight": 6000000,
    "Origin": 6500000,
    "Hades": 6666666,
    "Celestial : Divine": 7000000,
    "Anubis": 7200000,
    "Refraction": 7242000,
    "Hyper-Volt": 7500000,
    "Faith": 7250000,
    "Velocity": 7630000,
    "Nautilus : Lost": 7700000,
    "Divinus : Guardian": 7777777,
    "Outlaw": 8000000,
    "Soultorn": 8333333,
    "Harnessed": 8500000,
    "Nihility": 9000000,
    "Helios": 9000000,
    "Stargazer": 9200000,
    "Amethyst": 9333700,
    "Starscourge": 10000000,
    "Sharkyn": 10000000,
    "Guardian": 10000000,
    "Melodic": 11300000,
    "Sailor": 12000000,
    "Borealis": 13333333,
    "Stormal : Hurricane": 13500000,
    "Sirius": 14000000,
    "Arcane : Legacy": 15000000,
    "Icarus": 15660000,
    "Lullaby": 17000000,
    "Chromatic": 20000000,
    "Plasma": 20600000,
    "Oculus": 23233340,
    "Aviator": 24000000,
    "Ruby : Brimstone": 24060000,
    "Apotheosis": 24691356,
    "Blizzard": 27315000,
    "Arcane : Dark": 30000000,
    "Flora : Florest": 32800000,
    "Ethereal": 35000000,
    "Virtual : Fatal Error": 40413000,
    "Overseer": 45000000,
    "Exotic : Apex": 49999500,
    "Matrix": 50000000,
    "Runic": 50000000,
    "Sentinel": 60000000,
    "Twilight : Iridescent Memory": 60000000,
    "Antivirus": 62500000,
    "Dominion": 70000000,
    "Starborn": 72000000,
    "Melodic : Serenade": 77000000,
    "Carriage": 80000000,
    "Aquaria": 80000000,
    "Virtual : Full Control": 80000000,
    "Sailor : Flying Dutchman": 80000000,
    "Harnessed : Elements": 85000000,
    "Hellbound": 85000000,
    "Virtual : WorldWide": 87500000,
    "Atomic : Nucleus": 92118000,
    "Quartz : Rose": 97500000,
    "Chromatic : Genesis": 99999999,
    "Starscourge : Radiant": 100000000,
    "Spectraflow": 100000000,
    "Lily": 112000000,
    "Overture": 150000000,
    "Bounded : Aichmalotos": 170000000,
    "Symphony": 175000000,
    "Twilight : Withering Grace": 180000000,
    "Felled": 180000000,
    "Impeached": 200000000,
    "Lumenpool": 220000000,
    "Hyper-Volt : Ever-Storm": 225000000,
    "Virtual Memory": 232232232,
    "Archangel": 250000000,
    "Astral : Zodiac": 267000000,
    "Prophecy": 275649430,
    "Exotic : Void": 299999999,
    "Overture : History": 300000000,
    "Bloodlust": 300000000,
    "Maelstrom": 309999999,
    "Dreamer": 315000000,
    "Perpetual": 315000000,
    "Lotusfall": 320000000,
    "Cytokinesis": 330400472,
    "Jazz : Orchestra": 336870912,
    "Atlas": 360000000,
    "Flora : Evergreen": 370073730,
    "Chillsear": 375000000,
    "Celestial : Eclipse": 384400000,
    "Abyssal Hunter": 400000000,
    "Gargantua": 430000000,
    "Apostolos": 444000000,
    "Kyawthuite : Remembrance": 450000000,
    "Ruins": 500000000,
    "Matrix : Overdrive": 503000000,
    "Sailor : Admiral": 540000000,
    "Sophyra": 570000000,
    "Matrix : Reality": 601020102,
    "Sloth": 650000000,
    "Pythios": 666666666,
    "Sovereign": 750000000,
    "Ruins : Withered": 800000000,
    "Aegis": 825000000,
    "Ascendant": 935000000,
    "Pixelation": 1073741824,
    "Luminosity": 1200000000,
    "Leviathan": 1730400000,
    "Breakthrough": 1999999999,
    "Dream Catcher": 2222222222,
    "Equinox": 2500000000,
    "Monarch": 3000000000,
    "Oppression": 220000000,
    "Glitch": 12210110,
    "Fault": 3000,
    "⭐": 100,
    "⭐⭐": 1000,
    "⭐⭐⭐": 10000,
    "Dreammetric": 520000000,
    "Illusionary": 10000000, # Special Cyberspace aura: It's chance is ALWAYS 1/10,000,000. Any luck bonuses, effects, etc.. Don't apply. (See main.py)
}

limbo_auras = {
    "Nothing": 1,
    # Ауры из Null биома (базовый шанс / 1000, так как в Null множитель x1000)
    "Undefined": 1111,
    "Shift lock": 3325,
    "Nihility": 9000,
    "Flowed": 2121,
    # Эксклюзивы Лимбо
    "Raven": 500000,
    "Gothic": 1000001,
    "Anima": 5500000,
    "Empty": 11111111,
    "Imaginary": 12200000,
    "Juxtaposition": 40440400,
    "Raven : Plague": 200000000,
    "Unknown": 444444444,
    "Elude": 555555555,
    "Prologue": 666616111,
    "dreamscape": 850000000,
    "NYCTOPHOBIA": 1011111010
}

# Все крафтовые предметы в игре
items = [
    "[T1] 🧤 Luck Glove", "[T1] 🔥 Desire Glove", "[T1] ☀️ Solar Device",
    "[T2] ⭐ Shining Star", "[T3] 💠 Exo Gauntlet", "[T3] 🌪️ Windstorm Device",
    "[T4] ❄️ Subzero Device", "[T5] 🌌 Galactic Device", "[T5] 🌋 Volcanic Device",
    "[T6] 🔮 Exoflex Device", "[T6] 🌈 Hologrammer", "[T7] ⚡ Ragnaröker",
    "[T8] ✨ Starshaper", "[T9] 🔬 Neurolyzer", "[T10] 🌀 Genesis Drive",
    "[T11] 😇 Heavenly Device",
    "Lucky Potion", "Heavenly Potion", "Potion of Bound",
    "Fortune Potion I", "Fortune Potion II", "Fortune Potion III",
    "Jewellery Potion", "Zombie Potion", "Hades Godly Potion",
    "Zeus Godly Potion", "Godlike Potion", "Unknown Potion"
]

GLOBAL_THRESHOLD = 99_999_999

# Биомы и их настройки

BIOMES = {
    "Normal": {"chance": 0, "duration": 0, "multiplier": 1, "auras": []},
    "Windy": {"chance": 1 / 500, "duration": 120, "multiplier": 3,
              "auras": ["Wind", "Flow", "Vortex", "Stormal", "Stormal : Hurricane", "Aviator", "Maelstrom"]},
    "Snowy": {"chance": 1 / 600, "duration": 120, "multiplier": 3,
              "auras": ["Glacier", "Permafrost", "Blizzard", "Chillsear"]},
    "Rainy": {"chance": 1 / 750, "duration": 120, "multiplier": 4,
              "auras": ["Poseidon", "Sharkyn", "Sailor", "Evanescent", "Aquaria", "Sailor : Flying Dutchman", "Lumenpool", "Abyssal Hunter", "Sailor : Admiral"]},
    "Sand Storm": {"chance": 1 / 3000, "duration": 660, "multiplier": 4,
                   "auras": ["Gilded", "Jackpot", "Gilded : Crowned", "Anubis", "Outlaw", "Atlas"]},
    "Hell": {"chance": 1 / 6666, "duration": 660, "multiplier": 6,
             "auras": ["Undead", "Undead : Devil", "Hades", "Hellbound", "Felled", "Bloodlust", "Pythios"]},
    "Heaven": {"chance": 1 / 7777, "duration": 240, "multiplier": 5,
               "auras": ["Hope", "Faith", "Divinus : Guardian", "Icarus", "Oculus", "Dominion", "Prophecy", "Ascendant"]},
    "Starfall": {"chance": 1 / 7500, "duration": 600, "multiplier": 5,
                 "auras": ["Starlight", "Starlight : Kunzite", "Star Rider", "Orion", "Comet", "Astral", "Galaxy", "Stargazer", "Starborn", "Sirius",
                           "Starscourge : Radiant", "Astral : Zodiac", "Gargantua"]},
    "Corruption": {"chance": 1 / 9000, "duration": 660, "multiplier": 5,
                   "auras": ["Hazard", "Corrosive", "Symbiosis", "Hazard : Rays", "Parasite", "Impeached"]},
    "Null": {"chance": 1 / 10000, "duration": 99, "multiplier": 1000, "auras": ["Undefined", "Flowed", "Shift lock", "Nihility"]},
    "Glitched": {"chance": 1 / 6000000, "duration": 184, "multiplier": 1,
                 "auras": ["Oppression", "Glitch", "Fault", "⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"]},
    "Dreamspace": {"chance": 1 / 5000000, "duration": 128, "multiplier": 1, "auras": ["⭐", "⭐⭐", "⭐⭐⭐", "Dreammetric"]},
    "Cyberspace": {"chance": 0, "duration": 720, "multiplier": 2, "auras": ["Forbidden", "Player", "Respawn", "Virtual", "Metabytes", "Virtual : Fatal Error", "Matrix", "Antivirus", "Virtual : Full Control", "Virtual : WorldWide", "Virtual Memory", "Cytokinesis", "Matrix : Overdrive", "Aegis", "Pixelation"]}
}

# --- СЛОВАРЬ ДЛЯ GIF ---
# Связывает название ауры с ID гифки.
# Логика ">= 1,000,000" все еще будет применяться.

aura_gif_map = {
    "Arcane": "https://t.me/solsrngbotcutscenes/3",
    "Starlight : Kunzite": "https://t.me/solsrngbotcutscenes/143",
    "Gothic": "https://t.me/solsrngbotcutscenes/144",
    "Magnetic : Reverse Polarity": "https://t.me/solsrngbotcutscenes/6",
    "Undefined": "https://t.me/solsrngbotcutscenes/7",
    "Rage : Brawler": "https://t.me/solsrngbotcutscenes/11",
    "Symbiosis": "https://t.me/solsrngbotcutscenes/145",
    "Astral": "https://t.me/solsrngbotcutscenes/8",
    "Cosmos": "https://t.me/solsrngbotcutscenes/9",
    "Archmage": "https://t.me/solsrngbotcutscenes/146",
    "Respawn": "https://t.me/solsrngbotcutscenes/147",
    "Gravitational": "https://t.me/solsrngbotcutscenes/10",
    "Bounded : Unbound": "https://t.me/solsrngbotcutscenes/12",
    "Flutter : Buggify": "https://t.me/solsrngbotcutscenes/160",
    "Flowed": "https://t.me/solsrngbotcutscenes/149",
    "Virtual": "https://t.me/solsrngbotcutscenes/87",
    "Parasite": "https://t.me/solsrngbotcutscenes/13",
    "Orion": "https://t.me/solsrngbotcutscenes/150",
    "Apatite": "https://t.me/solsrngbotcutscenes/151",
    "Savior": "https://t.me/solsrngbotcutscenes/14",
    "Shift lock": "https://t.me/solsrngbotcutscenes/49",
    "Cosmos : Alice": "https://t.me/solsrngbotcutscenes/34",
    "Evanescent": "https://t.me/solsrngbotcutscenes/152",
    "Crystallized : Bejeweled": "https://t.me/solsrngbotcutscenes/161",
    "Aquatic : Flame": "https://t.me/solsrngbotcutscenes/66",
    "Poseidon": "https://t.me/solsrngbotcutscenes/15",
    "Metabytes": "https://t.me/solsrngbotcutscenes/162",
    "Wraith": "https://t.me/solsrngbotcutscenes/163",
    "Zeus": "https://t.me/solsrngbotcutscenes/33",
    "Solar : Solstice": "https://t.me/solsrngbotcutscenes/39",
    "Galaxy": "https://t.me/solsrngbotcutscenes/35",
    "Lunar : Full Moon": "https://t.me/solsrngbotcutscenes/40",
    "Twilight": "https://t.me/solsrngbotcutscenes/36",
    "Origin": "https://t.me/solsrngbotcutscenes/38",
    "Hades": "https://t.me/solsrngbotcutscenes/88",
    "Celestial : Divine": "https://t.me/solsrngbotcutscenes/37",
    "Anubis": "https://t.me/solsrngbotcutscenes/41",
    "Refraction": "https://t.me/solsrngbotcutscenes/164",
    "Hyper-Volt": "https://t.me/solsrngbotcutscenes/42",
    "Faith": "https://t.me/solsrngbotcutscenes/166",
    "Velocity": "https://t.me/solsrngbotcutscenes/43",
    "Nautilus : Lost": "https://t.me/solsrngbotcutscenes/48",
    "Divinus : Guardian": "https://t.me/solsrngbotcutscenes/167",
    "Outlaw": "https://t.me/solsrngbotcutscenes/168",
    "Soultorn": "https://t.me/solsrngbotcutscenes/169",
    "Harnessed": "https://t.me/solsrngbotcutscenes/44",
    "Nihility": "https://t.me/solsrngbotcutscenes/45",
    "Helios": "https://t.me/solsrngbotcutscenes/46",
    "Stargazer": "https://t.me/solsrngbotcutscenes/47",
    "Amethyst": "https://t.me/solsrngbotcutscenes/170",
    "Starscourge": "https://t.me/solsrngbotcutscenes/17",
    "Sharkyn": "https://t.me/solsrngbotcutscenes/171",
    "Guardian": "https://t.me/solsrngbotcutscenes/172",
    "Empty": "https://t.me/solsrngbotcutscenes/173",
    "Melodic": "https://t.me/solsrngbotcutscenes/174",
    "Imaginary": "https://t.me/solsrngbotcutscenes/175",
    "Sailor": "https://t.me/solsrngbotcutscenes/18",
    "Borealis": "https://t.me/solsrngbotcutscenes/219",
    "Stormal : Hurricane": "https://t.me/solsrngbotcutscenes/19",
    "Sirius": "https://t.me/solsrngbotcutscenes/20",
    "Arcane : Legacy": "https://t.me/solsrngbotcutscenes/67",
    "Icarus": "https://t.me/solsrngbotcutscenes/180",
    "Lullaby": "https://t.me/solsrngbotcutscenes/21",
    "Chromatic": "https://t.me/solsrngbotcutscenes/22",
    "Plasma": "https://t.me/solsrngbotcutscenes/189",
    "Oculus": "https://t.me/solsrngbotcutscenes/190",
    "Aviator": "https://t.me/solsrngbotcutscenes/23",
    "Ruby : Brimstone": "https://t.me/solsrngbotcutscenes/191",
    "Apotheosis": "https://t.me/solsrngbotcutscenes/192",
    "Blizzard": "https://t.me/solsrngbotcutscenes/24",
    "Arcane : Dark": "https://t.me/solsrngbotcutscenes/68",
    "Flora : Florest": "https://t.me/solsrngbotcutscenes/194",
    "Ethereal": "https://t.me/solsrngbotcutscenes/25",
    "Virtual : Fatal Error": "https://t.me/solsrngbotcutscenes/86",
    "Overseer": "https://t.me/solsrngbotcutscenes/26",
    "Exotic : Apex": "https://t.me/solsrngbotcutscenes/85",
    "Matrix": "https://t.me/solsrngbotcutscenes/28",
    "Runic": "https://t.me/solsrngbotcutscenes/27",
    "Sentinel": "https://t.me/solsrngbotcutscenes/29",
    "Twilight : Iridescent Memory": "https://t.me/solsrngbotcutscenes/30",
    "Antivirus": "https://t.me/solsrngbotcutscenes/95",
    "Dominion": "https://t.me/solsrngbotcutscenes/195",
    "Starborn": "https://t.me/solsrngbotcutscenes/196",
    "Melodic : Serenade": "https://t.me/solsrngbotcutscenes/197",
    "Carriage": "https://t.me/solsrngbotcutscenes/82",
    "Aquaria": "https://t.me/solsrngbotcutscenes/198",
    "Virtual : Full Control": "https://t.me/solsrngbotcutscenes/200",
    "Sailor : Flying Dutchman": "https://t.me/solsrngbotcutscenes/31",
    "Harnessed : Elements": "https://t.me/solsrngbotcutscenes/32",
    "Hellbound": "https://t.me/solsrngbotcutscenes/205",
    "Virtual : WorldWide": "https://t.me/solsrngbotcutscenes/84",
    "Atomic : Nucleus": "https://t.me/solsrngbotcutscenes/206",
    "Quartz : Rose": "https://t.me/solsrngbotcutscenes/207",
    "Chromatic : Genesis": "https://t.me/solsrngbotcutscenes/90",
    "Starscourge : Radiant": "https://t.me/solsrngbotcutscenes/83",
    "Spectraflow": "https://t.me/solsrngbotcutscenes/201",
    "Lily": "https://t.me/solsrngbotcutscenes/202",
    "Overture": "https://t.me/solsrngbotcutscenes/50",
    "Bounded : Aichmalotos": "https://t.me/solsrngbotcutscenes/203",
    "Symphony": "https://t.me/solsrngbotcutscenes/52",
    "Twilight : Withering Grace": "https://t.me/solsrngbotcutscenes/65",
    "Felled": "https://t.me/solsrngbotcutscenes/96",
    "Impeached": "https://t.me/solsrngbotcutscenes/81",
    "Lumenpool": "https://t.me/solsrngbotcutscenes/97",
    "Hyper-Volt : Ever-Storm": "https://t.me/solsrngbotcutscenes/80",
    "Virtual Memory": "https://t.me/solsrngbotcutscenes/208",
    "Archangel": "https://t.me/solsrngbotcutscenes/53",
    "Astral : Zodiac": "https://t.me/solsrngbotcutscenes/79",
    "Prophecy": "https://t.me/solsrngbotcutscenes/209",
    "Exotic : Void": "https://t.me/solsrngbotcutscenes/75",
    "Overture : History": "https://t.me/solsrngbotcutscenes/51",
    "Bloodlust": "https://t.me/solsrngbotcutscenes/54",
    "Maelstrom": "https://t.me/solsrngbotcutscenes/55",
    "Dreamer": "https://t.me/solsrngbotcutscenes/210",
    "Perpetual": "https://t.me/solsrngbotcutscenes/211",
    "Lotusfall": "https://t.me/solsrngbotcutscenes/56",
    "Cytokinesis": "https://t.me/solsrngbotcutscenes/212",
    "Jazz : Orchestra": "https://t.me/solsrngbotcutscenes/78",
    "Atlas": "https://t.me/solsrngbotcutscenes/57",
    "Flora : Evergreen": "https://t.me/solsrngbotcutscenes/16",
    "Chillsear": "https://t.me/solsrngbotcutscenes/64",
    "Celestial : Eclipse": "https://t.me/solsrngbotcutscenes/213",
    "Abyssal Hunter": "https://t.me/solsrngbotcutscenes/58",
    "Gargantua": "https://t.me/solsrngbotcutscenes/77",
    "Apostolos": "https://t.me/solsrngbotcutscenes/59",
    "Kyawthuite : Remembrance": "https://t.me/solsrngbotcutscenes/76",
    "Ruins": "https://t.me/solsrngbotcutscenes/60",
    "Matrix : Overdrive": "https://t.me/solsrngbotcutscenes/74",
    "Sailor : Admiral": "https://t.me/solsrngbotcutscenes/214",
    "Sophyra": "https://t.me/solsrngbotcutscenes/61",
    "Matrix : Reality": "https://t.me/solsrngbotcutscenes/73",
    "Sloth": "https://t.me/solsrngbotcutscenes/215",
    "Pythios": "https://t.me/solsrngbotcutscenes/216",
    "Sovereign": "https://t.me/solsrngbotcutscenes/89",
    "Ruins : Withered": "https://t.me/solsrngbotcutscenes/72",
    "Aegis": "https://t.me/solsrngbotcutscenes/62",
    "Ascendant": "https://t.me/solsrngbotcutscenes/217",
    "Pixelation": "https://t.me/solsrngbotcutscenes/63",
    "Luminosity": "https://t.me/solsrngbotcutscenes/71",
    "Leviathan": "https://t.me/solsrngbotcutscenes/220",
    "Breakthrough": "https://t.me/solsrngbotcutscenes/221",
    "Dream Catcher": "https://t.me/solsrngbotcutscenes/222",
    "Equinox": "https://t.me/solsrngbotcutscenes/159",
    "Monarch": "https://t.me/solsrngbotcutscenes/223",
    "Glitch": "https://t.me/solsrngbotcutscenes/94",
    "Oppression": "https://t.me/solsrngbotcutscenes/91",
    "Dreammetric": "https://t.me/solsrngbotcutscenes/93",
    # -------------- limbo gifs ----------------- #
    "Anima": "https://t.me/solsrngbotcutscenes/104",
    "Juxtaposition": "https://t.me/solsrngbotcutscenes/105",
    "Raven : Plague": "https://t.me/solsrngbotcutscenes/204",
    "Unknown": "https://t.me/solsrngbotcutscenes/106",
    "Elude": "https://t.me/solsrngbotcutscenes/107",
    "Prologue": "https://t.me/solsrngbotcutscenes/108",
    "dreamscape": "https://t.me/solsrngbotcutscenes/109",
    "NYCTOPHOBIA": "https://t.me/solsrngbotcutscenes/110",
    "Illusionary": "https://t.me/solsrngbotcutscenes/113",
}

event_gif_map = {
    "citadel": "https://t.me/solsrngbotcutscenes/227",
    "mastermind": "https://t.me/solsrngbotcutscenes/229"
}

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
    "craft_heavenlydevice": {
        "aura_reqs": {"Archangel": 1, "Prophecy": 2, "Icarus": 30, "Faith": 45, "Hope": 475, "Divinus : Angel": 2500},
        "item_reqs": {"[T10] 🌀 Genesis Drive": 1},
        "result": "[T11] 😇 Heavenly Device", "result_display": "[T11] 😇 Heavenly Device",
    },
# =====ITEMS=====
    "craft_biomerandomizer": {
        "aura_reqs": {"Undefined": 2, "Hades": 2, "Poseidon": 2, "Galaxy": 2,
                      "Astral": 2, "Permafrost": 2, "Stormal": 2, "Divinus : Guardian": 2},
        "item_reqs": {},
        "result": "🎲 Biome Randomizer", "result_display": "🎲 Biome Randomizer",
    },
}


# ============================================================
# МАСТЕР-СЛОВАРЬ ПРЕДМЕТОВ WORKSHOP
# Чтобы добавить новый предмет - добавь ОДНУ запись сюда.
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
  "[T11] 😇 Heavenly Device": {
        "craft_key": "craft_heavenlydevice",
        "luck_bonus": 15.0,
        "desc": "[T11] 😇 Heavenly Device\n+1500% (+15) luck\n\nRequirements:\nx1 [T10] Genesis Drive\nx1 Archangel\nx2 Prophecy\nx30 Icarus\nx45 Faith\nx475 Hope\nx2500 Divinus : Angel",
        "biome_bonus": None,
    },
}

# ============================================================
# СЛОВАРЬ ПРЕДМЕТОВ ВКЛАДКИ "ITEMS" (не гиры)
# ============================================================
WORKSHOP_TOOLS = {
    "🎲 Biome Randomizer": {
        "craft_key": "craft_biomerandomizer",
        "desc": "🎲 Biome Randomizer\nRandomly changes the current biome when used.\n\nCooldown: 30 minutes\n\nRequirements:\nx2 Undefined\nx2 Hades\nx2 Poseidon\nx2 Galaxy\nx2 Astral\nx2 Permafrost\nx2 Stormal\nx2 Divinus : Guardian",
    },
}

# Шансы биомов при использовании Biome Randomizer
BIOME_RANDOMIZER_CHANCES = {
    "Windy": 0.11087,
    "Snowy": 0.11087,
    "Rainy": 0.11087,
    "Sand Storm": 0.11087,
    "Hell": 0.11087,
    "Heaven": 0.11087,
    "Corruption": 0.11087,
    "Null": 0.11087,
    "Starfall": 0.1097689,
    "Glitched": 0.0000333,
    "Cyberspace": 1/10
}

start_msg = """✧ Welcome to the <b>Sol's RNG bot!</b>
Sol's RNG bot is a bot based of a game called "Sol's RNG" on roblox!

In <b>Sol's RNG bot</b> you can Roll auras, craft gloves, craft potions, And much more that i can't just say here,
We have a small but friendly community!
If you want help us grow, You can invite your friends here!

You can ask a question, Talk to people, and see news about this bot in: @solsrngsimbotnews
Or if you find a bug? you can always tell us about it! (@DimdumXD or @underrosta)

Since it's your first time playing <b>Sol's Rng bot</b> Press continue And roll your first ever <b>aura</b>!

<b>Good luck and have fun!!</b>"""

user_help_text = """
```
🛠 COMMANDS

🔍 INFO
/profile <User_id|me>
    → Показывает информацию о пользователе.
/racoon
    → Показывает рандомный факт о енотах.. Не спрашивайте зачем

/help - это сообщение
```
"""



tester_help_text = """
```
🛠 TESTER COMMANDS

🔍 INFO
/profile <User_id|me>
    → Показывает информацию о пользователе.
/servstats
    → Показать статус сервера на котором запущен бот.
/racoon
    → Показывает рандомный факт о енотах.. Не спрашивайте зачем

/help - это сообщение
```
"""



admin_help_text = """
```
🛠 ADMIN COMMANDS

👤 PLAYER MANAGEMENT
/setluck <user_id|me> <value>
  → Установить базовую удачу игроку

/setmyluck <value>
  → Установить базовую удачу себе

/setRolls <user_id|me> <+/-/=> <amount>
  → Изменить кол-во роллов
  → Пример: /setRolls me = 0

/setAura <user_id|me> <aura_name> <+/-/=> <amount>
  → Изменить кол-во ауры у игрока
  → Пример: /setAura me Solar + 10

/giveItem <user_id|me> <Item Name> [amount]
  → Выдать предмет (amount по умолчанию = 1)
  → Пример: /giveItem me Lucky Potion 50

🎲 FORCED ROLLS
/addAuraQueue <user_id|me> <aura_name>
  → Следующий ролл игрока выдаст эту ауру

/addAuraQueueReason <user_id|me> <aura_name> <reason>
  → То же самое, но с указанием причины
  → Пример: /addAuraQueueReason me Solar победа в ивенте

⚠️ DANGEROUS
/giveMeAllAuras <amount>
  → Выдать себе все ауры × amount
/giveMeAllItems <amount>
  → Выдать себе все предметы × amount
/end <reason>
    → Выключить бота
/ScheduledMaintenance
    → Включить отсчет ScheduledMaintenance который при окончании
    выключает бота.

📢 BROADCASTS
/say <message>
  → Отправить сообщение всем игрокам

/sayPin <message>
  → Отправить и закрепить у всех игроков

🌍 WORLD
/setbiome <biome_name>
  → Сменить биом вручную

🎉 LUCK EVENT
/luckEventChange <multiplier> <HH:MM:SS>
  → Настроить ивент (не запускает)
  → Пример: /luckEventChange 2.5 05:00:00

/luckEventStart
  → Запустить ивент с текущими настройками

/luckEventStop
  → Остановить ивент
  
🌌 Events
/wereSorry <seconds>
  → Запускает Ивент We're sorry
  → дает 1.2 лака на Выбраное время
/mastermind
  → Запускает Ивент Mastermind
  → дает 2 лака на 2 часа
/CitadelOfOrder
    → Запускает Ивент Citadel of order
    → дает 1.2 лака на 1 час

🔍 INFO
/activeplayers
    → Показать активных игроков в некоторый промежутках времени.
/servstats
    → Показать статус сервера на котором запущен бот.
/profile <User_id|me>
    → Показывает информацию о пользователе.
/racoon
    → Показывает рандомный факт о енотах.. Не спрашивайте зачем

/help - это сообщение
```"""



changelogs_text = """--=[ Update 1.1.6 (HOTFIX) ]=--
    🛠️ Fixes:
    | Fixed some bugs
    | /profile instead of /Profile in help now
    ✨ New Stuff:
    | Added "Help" In settings!
    | Now Admins, Testers, And users have their own /help and commands!
    | /racoon command.. What?

    | ! Sol's RNG bot in now OPEN-SOURCE! https://github.com/Dimdum111/Sols-Rng-Bot

🛠️ Dimdum111:
Hi everyone! this small update was focused on bug fixes,
1.2 is currently in development, It will take longer that expected..

And, Please.. Subscribe to our new news channel!!! (@solsrngsimbotnews)
I will publish news, sneakpeaks, And much much more here!!!!!
Alright, Enjoy the small update! :D

[!] If you find any bugs, please, report them to @DimdumXD Or @underrosta, Thanks!"""



credits_text = """

-= CREDITS =-

--= 🔨 Main developers =--

⭐👑🔨 @underrosta - Owner, Developer
⭐👑🔨🧪 @DimdumXD - Co-Owner, Developer, Tester

--= 🧪 Testers =--

🧪 @DukeDvdforeverEm - Tester
🧪 ener - Tester

━━━━━━━━━━━━━━━━━━━━━━━━

🌸 Original Idea - Sol's RNG Team
📰 Subscribe to @solsrngbotnews for news, sneakpeaks, and more!
📩 For help Write to - @underrosta · @DimdumXD

❓ Sol's RNG bot is distributed as OPEN-SOURCE under GPL-3.0 license. You can view its source code <a href="https://github.com/Dimdum111/Sols-Rng-Bot">HERE!</a>
"""


CyberspaceMsg = "[STATUS : SENDING...]\n[LOCATION: TELEGRAM]\n[HOST: JAKE]\n[REQUEST: APPROVED]\n[STATUS: RECEIVED]\n\nWELCOME\nCYBERSPACE_\n\n[Cyberspace]: Signal_Received | From : TELEGRAM"