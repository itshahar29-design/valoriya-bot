# =====================================================================
# VALORIYA: BOQIY QIROLLIKLAR URUSHI - O'YIN KONSTANTALARI
# =====================================================================

# 12 TA BUYUK AI IMPERIYA VA QIROLLIK
KINGDOMS = {
    "lionguard": {
        "id": "lionguard",
        "name": "🦁 Oltin Sher Imperiyasi",
        "ruler": "Imperator Valter V",
        "capital": "Oltin Qasr",
        "motto": "Sharaf va Boqiy Adolat!",
        "personality": "pride",  # Kibrli, lekin paxta qo'yganni sevadigan
        "specialty": "Paladinlar, qalin po'lat sovutlar va adolatli maosh.",
        "bonus": {"defense": 15, "honor_rate": 1.25},
        "voice_style": "Mag'rur, bariton va tantanali podshohona ovoz."
    },
    "frost_peak": {
        "id": "frost_peak",
        "name": "🦅 Qishki Qoya Qirolligi",
        "ruler": "Qonxo'r Ragnar Temirqo'l",
        "capital": "Muz Qal'a",
        "motto": "Po'lat va Qon bilan!",
        "personality": "anger",  # Doimiy g'azabda, laganbardorlarni yomon ko'radi
        "specialty": "Berserklar, og'ir ikki qo'lli bolg'alar va sovuqqa chidamlilik.",
        "bonus": {"attack": 20, "bleed_res": 0.3},
        "voice_style": "Bo'g'iq, g'azabdan bo'g'ilgan skandinavcha qichqiriq."
    },
    "ursus_peak": {
        "id": "ursus_peak",
        "name": "🐻 Oq Ayiq Knyazligi",
        "ruler": "Knyaz Boris Qoraboy",
        "capital": "O'rmon Qo'rg'oni",
        "motto": "Yengilmas Mudofaa!",
        "personality": "calm",
        "specialty": "Eng qalin monolit po'lat zirhlar va og'ir qalqonlar.",
        "bonus": {"max_hp": 60, "shield_block": 0.15},
        "voice_style": "Vazmin, bahaybat va past tembrli ovoz."
    },
    "iron_bastion": {
        "id": "iron_bastion",
        "name": "⚖️ Temir Bastion Ordeni",
        "ruler": "Bosh Usta Torin Bolg'ador",
        "capital": "Temir Shahar",
        "motto": "Olov va Po'lat Ittifoqi!",
        "personality": "greed",  # Foydali temir va rudalarni sevadi
        "specialty": "Elita metallurgiya, toblash bonuslari va artilleriya.",
        "bonus": {"craft_discount": 0.3, "durability_bonus": 0.5},
        "voice_style": "Qo'pol, temirchilar jarangidek baland ovoz."
    },
    "azure_lily": {
        "id": "azure_lily",
        "name": "⚜️ Moviy Nilufar Qirolligi",
        "ruler": "Gersoginya Izabella",
        "capital": "Zafaron Porti",
        "motto": "Oltin barcha darvozalarni ochadi!",
        "personality": "diplomat",
        "specialty": "Karvonlar, erkin auksion va bank tizimi.",
        "bonus": {"gold_income": 1.3, "market_fee_discount": 0.5},
        "voice_style": "Mayin, aristokrat va o'ta shirin ohangdor ovoz."
    },
    "crimson_sultanate": {
        "id": "crimson_sultanate",
        "name": "🐉 Qizil Ajdaho Sultonligi",
        "ruler": "Sulton Sulaymon Olovsoz",
        "capital": "Alanga Qasri",
        "motto": "Ajdaho olovi kuydiradi!",
        "personality": "wrath",
        "specialty": "Alanga nayzadorlari, olov sehrgarlari.",
        "bonus": {"fire_dmg": 25, "crit_power": 0.2},
        "voice_style": "Yondiruvchi, jarangdor va dabdabali sharqona ovoz."
    },
    "iron_steppe": {
        "id": "iron_steppe",
        "name": "🐺 Dasht Bo'rilari Xonligi",
        "ruler": "Botirxon Bahodir",
        "capital": "Oltin O'tov",
        "motto": "Shamoldek tez, bo'ridek qonxo'r!",
        "personality": "wild",
        "specialty": "Tezkor otliqlar, kamonchilar, kutilmagan bosqinlar.",
        "bonus": {"horse_speed": 1.4, "evasion": 12},
        "voice_style": "Yovvoyi, erkin va ot tuyoqlaridek qat'iy ovoz."
    },
    "shadowfang": {
        "id": "shadowfang",
        "name": "🐍 Zulmat Soyasi Knyazligi",
        "ruler": "Soya Knyazi Moros",
        "capital": "Tumanli Qasr",
        "motto": "Zulmat ichida yashaymiz!",
        "personality": "treason",  # Zahar va xiyonat ustasi
        "specialty": "Qotillar, zaharlovchilar va yashirin qaroqchilik.",
        "bonus": {"poison_dmg": 20, "crit_chance": 15},
        "voice_style": "Pichoqdek sovuq, pichirlab gapiruvchi makkor ovoz."
    },
    "blood_tide": {
        "id": "blood_tide",
        "name": "🏴‍☠️ Qora Qon Qaroqchilar Ittifoqi",
        "ruler": "Kapitan Qora Soqol",
        "capital": "Qaroqchilar Bandargohi",
        "motto": "Dengiz qonni yaxshi ko'radi!",
        "personality": "greedy_wild",
        "specialty": "Daryo va dengiz karvonlarini talash.",
        "bonus": {"raid_loot": 1.4, "stamina_cost_reduction": 0.1},
        "voice_style": "Mast, xirillagan va qo'rqinchli dengizchi ovozi."
    },
    "ash_necropolis": {
        "id": "ash_necropolis",
        "name": "💀 Kultepa O'liklar Saltanati",
        "ruler": "Boqiy Lich Malakor",
        "capital": "Suyaklar Saroyi",
        "motto": "O'lim faqat boshlanishi!",
        "personality": "cold",
        "specialty": "Suyak ritsarlari, o'liklarni tiriltirish.",
        "bonus": {"lifesteal": 0.12, "dark_res": 0.5},
        "voice_style": "Qabrdan kelayotgandek aks-sado beruvchi muzdek ovoz."
    },
    "sun_order": {
        "id": "sun_order",
        "name": "☀️ Quyosh Sohiblari Teokratiyasi",
        "ruler": "Oliy Patriarx Avreliy",
        "capital": "Nur Ibodatxonasi",
        "motto": "Nur barcha qorong'ulikni quvib chiqaradi!",
        "personality": "fanatic",
        "specialty": "Muqaddas shifo, inkvizitsiya, bid'atchilarni jazolash.",
        "bonus": {"heal_power": 1.35, "undead_slayer": 2.0},
        "voice_style": "Qiroatli, muqaddas va baland pardali va'z ovozi."
    },
    "silverleaf": {
        "id": "silverleaf",
        "name": "🌙 Kumush O'rmon Elf Gardi",
        "ruler": "Qirolicha Elenor",
        "capital": "Kumush Daraxt",
        "motto": "Tabiat qonuni abadiy!",
        "personality": "wise",
        "specialty": "O'rmon kamonchilari, o'q otish aniqligi.",
        "bonus": {"accuracy": 25, "evasion": 15},
        "voice_style": "Sehrli, nozik va jarangdor shabboda ovozi."
    }
}

# 3 BOSQICHLI KASBLAR TIZIMI (CLASS TREE)
CLASSES = {
    # 1-Bosqich: Boshlang'ich
    "warrior": {
        "id": "warrior", "name": "⚔️ Oddiy Jangchi", "tier": 1,
        "desc": "Qilich va qalqon tutishni endi o'rganayotgan yosh ritsar.",
        "base_hp": 120, "base_atk": 22, "base_def": 12, "base_agi": 10,
        "promotes_to": ["knight", "berserk", "blacksmith_knight"]
    },
    "scout": {
        "id": "scout", "name": "🏹 Mergan Izquvar", "tier": 1,
        "desc": "O'rmonlarda yurgan chaqqon kamonboz va pichoqchi.",
        "base_hp": 95, "base_atk": 26, "base_def": 8, "base_agi": 18,
        "promotes_to": ["ranger", "forest_trapper", "shadow_assassin"]
    },
    "apprentice_mage": {
        "id": "apprentice_mage", "name": "🧙‍♂️ Shogird Sehrgar", "tier": 1,
        "desc": "Qadimiy qo'lyozmalardan olov va shifo sehrlarini o'rganuvchi.",
        "base_hp": 85, "base_atk": 28, "base_def": 6, "base_agi": 12,
        "promotes_to": ["paladin", "battlemage", "inquisitor"]
    },
    # 2-Bosqich: Ritsarlik Rangi
    "knight": {
        "id": "knight", "name": "⚔️ Qirollik Ritsari", "tier": 2,
        "desc": "Muvozanatli, og'ir zirh va po'lat qilich egasi.",
        "base_hp": 170, "base_atk": 38, "base_def": 28, "base_agi": 14,
        "promotes_to": ["dragon_rider"]
    },
    "paladin": {
        "id": "paladin", "name": "🛡️ Muqaddas Paladin", "tier": 2,
        "desc": "O'zini va ittifoqchilarini davolovchi temir qalqon ritsari.",
        "base_hp": 190, "base_atk": 32, "base_def": 36, "base_agi": 10,
        "promotes_to": ["holy_inquisitor"]
    },
    "berserk": {
        "id": "berserk", "name": "🩸 Qonli Berserk", "tier": 2,
        "desc": "Joni kamaygan sari zarbasi 2x oshib ketuvchi qonxo'r bahodir.",
        "base_hp": 160, "base_atk": 52, "base_def": 14, "base_agi": 16,
        "promotes_to": ["blood_champion"]
    },
    "ranger": {
        "id": "ranger", "name": "🏹 Qirollik Kamonchisi", "tier": 2,
        "desc": "Zirhni yorib o'tuvchi halokatli aniq o'qchi.",
        "base_hp": 130, "base_atk": 46, "base_def": 18, "base_agi": 28,
        "promotes_to": ["dragon_rider", "ghost_assassin"]
    },
    "shadow_assassin": {
        "id": "shadow_assassin", "name": "🌑 Soya Qotili", "tier": 2,
        "desc": "Zaharli xanjarlar bilan orqadan zarba beruvchi pinhoniy ritsar.",
        "base_hp": 120, "base_atk": 50, "base_def": 14, "base_agi": 32,
        "promotes_to": ["ghost_assassin"]
    },
    "blacksmith_knight": {
        "id": "blacksmith_knight", "name": "🔨 Temirchi Ritsar", "tier": 2,
        "desc": "Og'ir bolg'asi bilan dushman zirhini sindiruvchi usta.",
        "base_hp": 180, "base_atk": 42, "base_def": 32, "base_agi": 12,
        "promotes_to": ["titan_smith"]
    },
    "battlemage": {
        "id": "battlemage", "name": "⚡️ Elementar Sehrgar", "tier": 2,
        "desc": "Zirhga qaramasdan halokatli olov va chaqmoq otadi.",
        "base_hp": 135, "base_atk": 54, "base_def": 16, "base_agi": 18,
        "promotes_to": ["archmage"]
    },
    # 3-Bosqich: Afsonaviy Elita
    "dragon_rider": {
        "id": "dragon_rider", "name": "🐉 Ajdaho Chavandozi", "tier": 3,
        "desc": "Samolarda parvoz qilib olov yog'diruvchi qadimiy afsona.",
        "base_hp": 260, "base_atk": 85, "base_def": 55, "base_agi": 25,
        "promotes_to": []
    },
    "blood_champion": {
        "id": "blood_champion", "name": "👹 Qon Xudosi Bahodiri", "tier": 3,
        "desc": "O'lim oldida ham to'xtamaydigan qonli qasoskor.",
        "base_hp": 240, "base_atk": 105, "base_def": 30, "base_agi": 26,
        "promotes_to": []
    },
    "holy_inquisitor": {
        "id": "holy_inquisitor", "name": "👑 Quddus Inkvizitori", "tier": 3,
        "desc": "Barcha yovuzlik va qora sehr ustidan hukm chiqaruvchi nur jangchisi.",
        "base_hp": 280, "base_atk": 75, "base_def": 70, "base_agi": 18,
        "promotes_to": []
    },
    "archmage": {
        "id": "archmage", "name": "🌌 Fazoviy Archimage", "tier": 3,
        "desc": "Vaqt va makonni o'zgartiruvchi buyuk sehr donishmandi.",
        "base_hp": 200, "base_atk": 115, "base_def": 35, "base_agi": 28,
        "promotes_to": []
    },
    "ghost_assassin": {
        "id": "ghost_assassin", "name": "💀 O'lim Sharpasi", "tier": 3,
        "desc": "Dushman o'z qonini ko'rguncha ko'rinmaydigan afsonaviy soyador.",
        "base_hp": 190, "base_atk": 110, "base_def": 30, "base_agi": 50,
        "promotes_to": []
    }
}

# 12 TA ANATOMIK TANA ZONASI
HIT_ZONES = {
    "head": {"name": "Bosh / Miya", "multiplier": 2.2, "crit_bonus": 25, "wound": "concussion"},
    "face": {"name": "Yuz va Ko'zlar", "multiplier": 1.9, "crit_bonus": 20, "wound": "one_eyed"},
    "neck": {"name": "Bo'yin / Uyqu Tomiri", "multiplier": 2.5, "crit_bonus": 30, "wound": "arterial_bleed"},
    "torso": {"name": "Ko'krak Qafasi / Yurak", "multiplier": 1.4, "crit_bonus": 10, "wound": "broken_ribs"},
    "r_shoulder": {"name": "O'ng Yelka", "multiplier": 1.0, "crit_bonus": 5, "wound": "arm_fracture"},
    "l_shoulder": {"name": "Chap Yelka", "multiplier": 1.0, "crit_bonus": 5, "wound": "shield_arm_damage"},
    "r_arm": {"name": "O'ng Bilak", "multiplier": 0.85, "crit_bonus": 5, "wound": "hand_injury"},
    "l_arm": {"name": "Chap Bilak", "multiplier": 0.85, "crit_bonus": 5, "wound": "hand_injury"},
    "stomach": {"name": "Qorin va Jigarlar", "multiplier": 1.3, "crit_bonus": 15, "wound": "internal_bleed"},
    "groin": {"name": "Chov Sohasi", "multiplier": 1.7, "crit_bonus": 20, "wound": "stamina_collapse"},
    "r_leg": {"name": "O'ng Tizza va Oyoq", "multiplier": 0.9, "crit_bonus": 5, "wound": "leg_fracture"},
    "l_leg": {"name": "Chap Tizza va Oyoq", "multiplier": 0.9, "crit_bonus": 5, "wound": "leg_fracture"}
}

# 8 TA KIYIM SLOTI
EQUIPMENT_SLOTS = [
    ("helmet", "👑 Bosh: Dubulg'a"),
    ("amulet", "📿 Bo'yin: Tumor / Relikviya"),
    ("main_hand", "⚔️ O'ng Qo'l: Asosiy Qurol"),
    ("chestplate", "🥋 Tana: Og'ir Sovut"),
    ("off_hand", "🛡 Chap Qo'l: Qalqon / Qo'shimcha"),
    ("gauntlets", "🥊 Qo'llar: Po'lat Qo'lqop"),
    ("ring", "💍 Barmoq: Sehrli Uzuk"),
    ("boots", "👢 Oyoqlar: Ritsarlik Etigi")
]

# BOSHLANG'ICH DASTLABKI ANJOMLAR
STARTER_GEAR = [
    {
        "slot_type": "main_hand",
        "item_name": "🗡 Zangori Yosh Ritsar Qilichi",
        "rarity": "common",
        "attack": 12, "defense": 0, "durability": 100, "max_durability": 100
    },
    {
        "slot_type": "chestplate",
        "item_name": "🥋 Paxtali Qalin Gambeson",
        "rarity": "common",
        "attack": 0, "defense": 8, "durability": 100, "max_durability": 100
    },
    {
        "slot_type": "off_hand",
        "item_name": "🛡 Yog'och Ritsarlik Qalqoni",
        "rarity": "common",
        "attack": 0, "defense": 6, "durability": 100, "max_durability": 100
    }
]

# PROTSEDURAL BOT NOMI GENERATORI
BOT_FIRST_NAMES = [
    "Artur", "Lanselot", "Temurxon", "Roland", "Iskandar", "Galahad",
    "Richard", "Valter", "Tristan", "Bohemond", "Gotfrid", "Eduard",
    "Leon", "Baldvin", "Vilgelm", "Sardorbek", "Jaloliddin", "Ragnar",
    "Alp Arslon", "Subutoy", "Klodvig", "Genrix", "Albrext", "Knut"
]

BOT_TITLES = [
    "Ser", "Lord", "Baron", "Graf", "Gertsog", "Ritsar", "Don", "Bahodir", "Sarkarda"
]

BOT_EPITHETS = [
    "Sheryurak", "Temir Qo'l", "Qo'rqmas", "Soyalar Qotili", "Oltin Qalqon",
    "G'olib", "Adolatli", "Qonxo'r", "Yengilmas", "Zulmat Bahodiri",
    "Qal'alar Buzg'unchisi", "Saxovatli", "Keksa Bo'ri", "Chaqmoq"
]

# AI BOT XARAKTERLARI
BOT_PERSONAS = ["berserk", "defender", "poisoner", "coward"]
