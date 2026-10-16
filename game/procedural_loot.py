# =====================================================================
# VALORIYA: PROTSSESSUAL QUROL-ASLAHA GENERATORI (125,000+ KOMBINATSIYA)
# =====================================================================
# 200 ta tayanch anjom x 25 Prefiks x 25 Suffiks = 125,000 ta unikal buyum!
# Har bir buyum unikal ID, nom, qo'shimcha statistikalar va runa slotlariga ega.
# =====================================================================

import random
from typing import Dict, Any, Optional
from game.items_db import ITEMS_CATALOG

ITEM_PREFIXES = {
    "ancient": {
        "name_uz": "Qadimiy",
        "atk": 15, "def": 12, "hp": 40, "crit": 5, "price_mult": 2.2,
        "desc": "Yo'qolgan sivilizatsiyaning muqaddas qo'llari bilan yasalgan."
    },
    "bloodthirsty": {
        "name_uz": "Qonxo'r",
        "atk": 22, "def": -3, "lifesteal": 8, "crit": 6, "price_mult": 1.9,
        "desc": "Dushman qoni bilan to'yinib, egasining jarohatlarini bitkazadi."
    },
    "frozen": {
        "name_uz": "Muzlagan",
        "atk": 12, "def": 10, "chill": 15, "crit": 3, "price_mult": 1.7,
        "desc": "Mangu qorli cho'qqilar sovuqligi bilan qoplangan."
    },
    "flaming": {
        "name_uz": "Olovli",
        "atk": 25, "burn": 20, "price_mult": 1.8,
        "desc": "Magma alangasi bilan yonib turadi, dushmanga olovli jarohat yetkazadi."
    },
    "thunder": {
        "name_uz": "Chaqmoqli",
        "atk": 18, "crit": 12, "speed": 10, "price_mult": 2.0,
        "desc": "Osmondagi chaqmoq shiddatini o'zida saqlaydi."
    },
    "black_knight": {
        "name_uz": "Qora Ritsarlik",
        "atk": 20, "def": 16, "dark_res": 20, "price_mult": 2.1,
        "desc": "Zulmat ritsarlarining sovuq po'latidan quyilgan."
    },
    "venomous": {
        "name_uz": "Zaharlangan",
        "atk": 14, "poison": 18, "price_mult": 1.6,
        "desc": "Qora chayon zahari shimdirilgan halokatli tig'."
    },
    "stone_solid": {
        "name_uz": "Toshday Mustahkam",
        "atk": 5, "def": 28, "hp": 70, "price_mult": 1.75,
        "desc": "Granit qoyadek og'ir va buzilmas mudofaa beradi."
    },
    "soul_stealer": {
        "name_uz": "Ruhlar O'g'risi",
        "atk": 16, "mana_drain": 12, "crit": 7, "price_mult": 2.3,
        "desc": "Yiqilgan raqibning ruhiy energiyasini o'ziga tortadi."
    },
    "titan": {
        "name_uz": "Titan",
        "atk": 30, "def": 20, "hp": 90, "price_mult": 3.0,
        "desc": "Qadimiy titanlar qoldirgan afsonaviy metall parchasidan yasalgan."
    },
    "radiant": {
        "name_uz": "Nurli",
        "atk": 16, "holy_dmg": 20, "dark_res": 30, "price_mult": 2.0,
        "desc": "Ilohiy quyosh nuri bilan jilvalanuvchi muqaddas anjom."
    },
    "berserk": {
        "name_uz": "Telba Berserk",
        "atk": 35, "def": -10, "crit": 15, "price_mult": 1.8,
        "desc": "Egasiga cheksiz g'azab va mislsiz zarba kuchi baxsh etadi."
    },
    "calamity": {
        "name_uz": "Falokatli",
        "atk": 26, "crit": 10, "poison": 10, "price_mult": 2.4,
        "desc": "Yovuz qarg'ish bilan qoplangan, fojiaviy oqibatlarga yetaklovchi qurol."
    },
    "resilient": {
        "name_uz": "Barqaror",
        "atk": 8, "def": 22, "hp": 50, "price_mult": 1.6,
        "desc": "Eng qattiq zarbalarga ham bardosh beruvchi mukammal quyma."
    },
    "razor_sharp": {
        "name_uz": "O'tkir Tig'li",
        "atk": 24, "crit": 8, "armor_penetration": 15, "price_mult": 1.7,
        "desc": "Hatto qalin plitali sovutlarni ham osonlikcha tilib o'tadi."
    },
    "swift": {
        "name_uz": "Shiddatli",
        "atk": 12, "speed": 22, "crit": 9, "price_mult": 1.8,
        "desc": "Juda yengil, harakatlarni shamoldan-da tezlashtiradi."
    },
    "dragon_breath": {
        "name_uz": "Ajdaho Nafasi",
        "atk": 32, "burn": 30, "fire_res": 40, "price_mult": 3.5,
        "desc": "Qizil ajdaho alangasi tomchilari metallga singdirilgan."
    },
    "abyssal_dark": {
        "name_uz": "Qorong'u Zulmat",
        "atk": 25, "def": 14, "shadow_dmg": 25, "price_mult": 2.6,
        "desc": "Qora o'ra tubining tubsiz energiyasi bilan to'yingan."
    },
    "limitless": {
        "name_uz": "Cheksiz",
        "atk": 25, "def": 25, "hp": 80, "crit": 10, "price_mult": 3.2,
        "desc": "Cheksizlik kuchini mujassam etgan sirli relikviya."
    },
    "holy_sanctuary": {
        "name_uz": "Muqaddas Qasamyod",
        "atk": 15, "def": 24, "holy_dmg": 22, "hp": 60, "price_mult": 2.5,
        "desc": "Muqaddas ibodatxona rohiblari tomonidan duo o'qib quyilgan."
    },
    "chaotic": {
        "name_uz": "Xaos Bo'roni",
        "atk": 28, "crit": 14, "chaos_rng": 25, "price_mult": 2.2,
        "desc": "Oldindan aytib bo'lmas, tasodifiy yuqori halokatli kuch chiqaradi."
    },
    "phantom": {
        "name_uz": "Binafsha Arvoh",
        "atk": 18, "evasion": 15, "speed": 16, "price_mult": 2.3,
        "desc": "Egasini qisman ko'rinmas qilib, dushman zarbalaridan asraydi."
    },
    "lightning_dash": {
        "name_uz": "Yashin Shiddati",
        "atk": 20, "crit": 15, "speed": 25, "price_mult": 2.4,
        "desc": "Zarba berish tezligini ko'z ochib yumguncha darajada oshiradi."
    },
    "indestructible": {
        "name_uz": "Buzilmas",
        "atk": 10, "def": 35, "hp": 110, "price_mult": 2.8,
        "desc": "Hech qanday qurol sindira olmaydigan titan po'lati."
    },
    "victorious": {
        "name_uz": "G'olib",
        "atk": 20, "def": 18, "gold_boost": 20, "xp_boost": 15, "price_mult": 2.5,
        "desc": "Yuzlab janglarda zafar quchgan qahramonlar merosi."
    }
}

ITEM_SUFFIXES = {
    "slayer": {
        "name_uz": "Qotili",
        "desc_uz": "Maxluqlar va yirtqichlarga qarshi +25% qo'shimcha zarar yetkazadi.",
        "atk": 15, "pve_bonus": 25
    },
    "guardian": {
        "name_uz": "Qo'riqchisi",
        "desc_uz": "Salomatlik 25% dan kamayganda qahramonga 60 quvvatli himoya qalqoni beradi.",
        "def": 18, "shield_trigger": 60
    },
    "tears": {
        "name_uz": "Ko'z Yoshi",
        "desc_uz": "Har bir jang raundida 15 salomatlikni doimiy tiklab boradi.",
        "regen": 15, "hp": 40
    },
    "avenger": {
        "name_uz": "Qasoskori",
        "desc_uz": "Dushmandan qabul qilingan har bir zarbaning 15% ini ularga qaytaradi.",
        "reflect": 15, "def": 10
    },
    "willpower": {
        "name_uz": "Irodasi",
        "desc_uz": "Jang paytidagi ruhiy travmalar va qo'rquvga 50% mustahkam chidamlilik beradi.",
        "dark_res": 25, "mind_shield": 50
    },
    "bloodline": {
        "name_uz": "Qon Tomiri",
        "desc_uz": "Qahramonning maksimal hayot zaxirasini sezilarli oshiradi (+90 HP).",
        "hp": 90
    },
    "executioner": {
        "name_uz": "O'lim O'rog'i",
        "desc_uz": "Dushman salomatligi 15% dan tushganda bir zarbada yakunlash ehtimoli.",
        "atk": 25, "execute_chance": 20
    },
    "triumph": {
        "name_uz": "Zafari",
        "desc_uz": "G'alaba qozonilganda olinadigan tajriba miqdorini 30% oshiradi.",
        "xp_boost": 30
    },
    "clamor": {
        "name_uz": "Nidosi",
        "desc_uz": "Dushmanning zarba kuchini 12% ga zaiflashtiradi.",
        "atk_debuff": 12
    },
    "curse": {
        "name_uz": "Qarg'ishi",
        "desc_uz": "Har bir muvaffaqiyatli zarbada dushmanning sovutini yemirib boradi.",
        "armor_shred": 8
    },
    "mystery": {
        "name_uz": "Siri",
        "desc_uz": "Kutilmagan manevrlar evaziga dushman zarbalaridan qochish ehtimoli (+15%).",
        "evasion": 15
    },
    "shadow": {
        "name_uz": "Soyasi",
        "desc_uz": "Kritik zarba berilganda dushmanni 1 navbatga karaxt qilib qo'yadi.",
        "stun_chance": 20, "crit": 8
    },
    "phoenix": {
        "name_uz": "Humosi",
        "desc_uz": "Jangda halok bo'lganda bir marta 35% salomatlik bilan qayta tiriltiradi.",
        "revive": 1, "hp": 50
    },
    "ironclad": {
        "name_uz": "Po'lati",
        "desc_uz": "Barcha kiruvchi zarbalarni 12% ga qisqartirib yengillashtiradi.",
        "damage_reduction": 12, "def": 15
    },
    "fury": {
        "name_uz": "G'azabi",
        "desc_uz": "Qahramon yaralangan sari zarbasi kuchayadi (kam qonda +35% Atk).",
        "low_hp_fury": 35, "atk": 15
    },
    "starlight": {
        "name_uz": "Yulduzi",
        "desc_uz": "Zulmatli zindonlarda va tunda barcha ko'rsatkichlarga +20% bonus beradi.",
        "night_bonus": 20, "atk": 10, "def": 10
    },
    "storm": {
        "name_uz": "Bo'roni",
        "desc_uz": "Har bir zarbada yaqin atrofdagi barcha dushmanlarga 20 zanjirli elektr zarari.",
        "chain_lightning": 20, "crit": 10
    },
    "legend": {
        "name_uz": "Afsonasi",
        "desc_uz": "Qahramonning shon-shuhratini yuksaltirib, +35% Oltin tushishini ta'minlaydi.",
        "gold_boost": 35, "atk": 10
    },
    "sultan": {
        "name_uz": "Sultoni",
        "desc_uz": "Savdogarlardan narsalar xarid qilganda 20% gacha ulkan chegirma beradi.",
        "merchant_discount": 20, "charisma": 15
    },
    "hangman": {
        "name_uz": "Jallodi",
        "desc_uz": "Tanqidiy zarba (Crit Dmg) ko'paytiruvchisini 1.5x dan 2.2x gacha oshiradi.",
        "crit_dmg_mult": 0.7, "crit": 12
    },
    "sunburst": {
        "name_uz": "Oftobi",
        "desc_uz": "Eng qorong'u zulmatlarni ham yoritib, ko'r qiluvchi ilohiy nur purkaydi.",
        "holy_dmg": 25, "blind_chance": 15
    },
    "earthquake": {
        "name_uz": "Zilzilasi",
        "desc_uz": "Dushmanni zarb bilan yiqitib, navbatdagi harakatini o'tkazib yubortiradi.",
        "knockdown": 18, "atk": 18
    },
    "frostbite": {
        "name_uz": "Nafasi",
        "desc_uz": "Dushmanning qonini tomirlarida muzlatib, harakat tezligini 40% ga pasaytiradi.",
        "slow_potency": 40, "chill": 20
    },
    "vitality": {
        "name_uz": "Qalbi",
        "desc_uz": "Jangdan tashqarida ham salomatlik va charchoqni 3 barobar tez tiklaydi.",
        "regen_world": 30, "hp": 70
    },
    "judgment": {
        "name_uz": "Hukmi",
        "desc_uz": "Dushmanning barcha ijobiy auralari va qalqonlarini bir zumda yo'q qiladi.",
        "dispel_shield": 100, "atk": 20
    }
}

RARITY_COLORS = {
    "common": "⚪️ Oddiy",
    "rare": "🔵 Noyob",
    "epic": "🟣 Epik",
    "legendary": "🟠 Afsonaviy",
    "mythic": "🔴 Mistik / Qadimiy"
}

def generate_procedural_loot(base_item_id: Optional[str] = None, player_level: int = 1, force_rarity: Optional[str] = None) -> Dict[str, Any]:
    """
    200 ta tayanch qurol-aslahadan 125,000+ kombinatsiyali noyob buyum yaratadi.
    Prefiks va Suffikslar yordamida nom, ko'rsatkichlar va xususiyatlar hisoblanadi.
    """
    # 1. Base item tanlash
    if not base_item_id or base_item_id not in ITEMS_CATALOG:
        base_item_id = random.choice(list(ITEMS_CATALOG.keys()))
    
    base_item = ITEMS_CATALOG[base_item_id]
    
    # 2. Prefiks va Suffiks tasodifiy tanlanishi (yoki yo'qligi)
    prefix_key = random.choice(list(ITEM_PREFIXES.keys()))
    suffix_key = random.choice(list(ITEM_SUFFIXES.keys()))
    
    prefix = ITEM_PREFIXES[prefix_key]
    suffix = ITEM_SUFFIXES[suffix_key]
    
    # Runa teshiklari (Sockets)
    num_sockets = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
    
    # Statistikalarni hisoblash
    new_atk = base_item.get("attack", 0) + prefix.get("atk", 0) + suffix.get("atk", 0)
    new_def = base_item.get("defense", 0) + prefix.get("def", 0) + suffix.get("def", 0)
    new_hp = base_item.get("hp", 0) + prefix.get("hp", 0) + suffix.get("hp", 0)
    new_crit = base_item.get("crit", 0) + prefix.get("crit", 0) + suffix.get("crit", 0)
    
    # Narx multiplikatori
    price_mult = prefix.get("price_mult", 1.0) * (1.0 + (player_level * 0.08))
    new_price = int(base_item.get("price", 100) * price_mult)
    
    # Nomini shakllantirish (Masalan: "🗡 Qonxo'r Yosh Ritsar Po'lat Qilichi ...Qotili")
    clean_base_name = base_item["name"].split(maxsplit=1)[-1] if " " in base_item["name"] else base_item["name"]
    icon = base_item["name"].split()[0] if base_item["name"] else "⚔️"
    
    full_name = f"{icon} {prefix['name_uz']} {clean_base_name} {suffix['name_uz']}"
    
    # Rarity aniqlash
    if force_rarity:
        rarity = force_rarity
    else:
        total_power = new_atk + new_def + (new_hp // 5)
        if total_power > 120:
            rarity = "mythic"
        elif total_power > 80:
            rarity = "legendary"
        elif total_power > 50:
            rarity = "epic"
        elif total_power > 25:
            rarity = "rare"
        else:
            rarity = "common"
            
    unique_loot_id = f"proc_{base_item_id}_{prefix_key}_{suffix_key}_{random.randint(1000, 9999)}"
    
    return {
        "id": unique_loot_id,
        "base_id": base_item_id,
        "slot": base_item.get("slot", "main_hand"),
        "name": full_name,
        "rarity": rarity,
        "rarity_display": RARITY_COLORS.get(rarity, rarity),
        "tier": base_item.get("tier", 1),
        "attack": max(0, new_atk),
        "defense": max(0, new_def),
        "hp": max(0, new_hp),
        "crit": max(0, new_crit),
        "price": new_price,
        "sockets": num_sockets,
        "prefix_effect": prefix["desc"],
        "suffix_effect": suffix["desc_uz"],
        "desc": f"{prefix['name_uz']} va {suffix['name_uz']} qobiliyati bilan uyg'unlashgan noyob anjom. {suffix['desc_uz']}"
    }

def get_procedural_matrix_size() -> Dict[str, int]:
    """Kombinatorik hajmni qaytaradi."""
    base_count = len(ITEMS_CATALOG)
    pref_count = len(ITEM_PREFIXES)
    suff_count = len(ITEM_SUFFIXES)
    total_combinations = base_count * pref_count * suff_count
    return {
        "base_items": base_count,
        "prefixes": pref_count,
        "suffixes": suff_count,
        "total_unique_items": total_combinations
    }
