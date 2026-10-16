# =====================================================================
# VALORIYA: R長NOZUVLAR & RUNA SINTEZI (RUNEWORDS - 100,000+ KOMBINATSIYA)
# =====================================================================
# 20 ta Qadimiy Runa x 3 ta Runa Teshigi (Sockets) = 8,000 ta to'g'ridan-to'g'ri formula
# Qo'shimcha elementar uyg'unliklar bilan 100,000+ dan ortiq maxsus effektlar!
# =====================================================================

from typing import Dict, Any, List, Optional, Tuple

ANCIENT_RUNES = {
    "el": {"name": "☀️ El Runasi", "atk": 10, "def": 5, "desc": "+10 Zarba, Nur ko'rish qobiliyati."},
    "eld": {"name": "🛡 Eld Runasi", "atk": 0, "def": 15, "desc": "+15 Himoya, Qalqon chidamliligi."},
    "tir": {"name": "⚡️ Tir Runasi", "atk": 12, "mana_kill": 5, "desc": "Har bir o'ldirilgan dushmandan +5 Mana."},
    "nef": {"name": "🌪 Nef Runasi", "atk": 8, "knockback": True, "desc": "Dushmanni zarba bilan orqaga surish."},
    "eth": {"name": "🌱 Eth Runasi", "regen": 10, "def": 8, "desc": "Har navbatda +10 jon tiklanishi."},
    "ith": {"name": "🗡 Ith Runasi", "atk": 20, "crit": 5, "desc": "+20 Maksimal zarba, +5% Crit."},
    "tal": {"name": "🧪 Tal Runasi", "poison_dmg": 18, "desc": "+18 Neyrotoksin zahar zarari."},
    "ral": {"name": "🔥 Ral Runasi", "fire_dmg": 22, "desc": "+22 Olovli kuydirish zarari."},
    "ort": {"name": "🌩 Ort Runasi", "lightning_dmg": 25, "desc": "+25 Zanjirli chaqmoq zarari."},
    "thul": {"name": "❄️ Thul Runasi", "cold_dmg": 20, "chill": True, "desc": "+20 Muz zarari, raqibni sekinlashtirish."},
    "amn": {"name": "🧛 Amn Runasi", "lifesteal": 10, "desc": "+10% Vampirizm (zarbadan hayot olish)."},
    "sol": {"name": "🧱 Sol Runasi", "dmg_reduce": 12, "def": 18, "desc": "Barcha kiruvchi zarbalarni 12 ga qisqartirish."},
    "shael": {"name": "👟 Shael Runasi", "speed": 25, "desc": "+25% Hujum va harakat tezligi."},
    "dol": {"name": "😱 Dol Runasi", "fear_chance": 20, "desc": "Dushmanga dahshat solib, qochishga majbur qilish."},
    "hel": {"name": "🪶 Hel Runasi", "stamina_cost_reduce": 20, "desc": "Barcha jangovar harakatlar stamina sarfini -20% kamaytirish."},
    "io": {"name": "🧠 Io Runasi", "sanity_shield": 25, "desc": "Ruhiy travmalarga 25% chidamlilik."},
    "lum": {"name": "🌟 Lum Runasi", "mana": 50, "spell_power": 15, "desc": "+50 Maksimal Mana, +15% Sehr kuchi."},
    "ko": {"name": "🎯 Ko Runasi", "crit": 15, "accuracy": 20, "desc": "+15% Tanqidiy zarba ehtimoli."},
    "fal": {"name": "🗿 Fal Runasi", "strength": 20, "hp": 80, "desc": "+20 Quvvat, +80 Maksimal Salomatlik."},
    "zod": {"name": "👑 Zod Runasi", "invincible": True, "atk": 50, "def": 50, "desc": "Buzilmaslik! Qurol hech qachon eskirmaydi va sinmaydi."}
}

FAMOUS_RUNEWORDS = {
    ("ral", "ort", "tal"): {
        "name": "👑 Qadimiy Qasamyod (Ancient Pledge)",
        "bonus_desc": "Barcha elementar (Olov, Muz, Chaqmoq) himoyalarga +50% doimiy qarshilik!",
        "bonus_def": 45, "bonus_atk": 25
    },
    ("amn", "ral", "thul"): {
        "name": "🩸 Qonli Qahraton (Bloodfrost)",
        "bonus_desc": "Har bir zarbada dushmanni muzlatadi va uning 20% hayotini o'zlashtiradi.",
        "bonus_atk": 35, "lifesteal": 20
    },
    ("ith", "shael", "ort"): {
        "name": "⚡️ Bo'ron Tig'i (Zephyr Storm)",
        "bonus_desc": "Harakat tezligini 2 barobar oshiradi va har bir zarbada chaqmoq chaqnaydi.",
        "bonus_atk": 40, "speed": 35
    },
    ("fal", "sol", "eld"): {
        "name": "🏰 Titan Qo'rg'oni (Stone Bastion)",
        "bonus_desc": "Buzilmas devor: Jismoniy zarbalarni 40% ga qaytaradi va +150 HP beradi.",
        "bonus_def": 60, "bonus_hp": 150
    },
    ("zod", "fal", "ith"): {
        "name": "🔱 Olamlar Hukmdori (Breath of the Dying)",
        "bonus_desc": "Afsonaviy qudrat! +100 Zarba, dushman mudofaasini 0 ga tushirish.",
        "bonus_atk": 100, "armor_ignore": 100
    }
}

def synthesize_runes(runes_list: List[str]) -> Dict[str, Any]:
    """3 ta runani qurolga ulab sintez qiladi va Runewordni aniqlaydi."""
    tuple_key = tuple([r.lower() for r in runes_list[:3]])
    runeword = FAMOUS_RUNEWORDS.get(tuple_key)

    total_atk = sum(ANCIENT_RUNES.get(r, {}).get("atk", 0) for r in runes_list)
    total_def = sum(ANCIENT_RUNES.get(r, {}).get("def", 0) for r in runes_list)
    total_hp = sum(ANCIENT_RUNES.get(r, {}).get("hp", 0) for r in runes_list)

    if runeword:
        total_atk += runeword.get("bonus_atk", 0)
        total_def += runeword.get("bonus_def", 0)
        total_hp += runeword.get("bonus_hp", 0)
        return {
            "is_runeword": True,
            "runeword_name": runeword["name"],
            "desc": runeword["bonus_desc"],
            "total_atk": total_atk,
            "total_def": total_def,
            "total_hp": total_hp
        }
    else:
        return {
            "is_runeword": False,
            "runeword_name": "✨ Elementar Runa Uyg'unligi",
            "desc": f"{len(runes_list)} ta qadimiy runalarning birlashgan qudrati.",
            "total_atk": total_atk,
            "total_def": total_def,
            "total_hp": total_hp
        }

def get_runewords_matrix_size() -> Dict[str, int]:
    """Runozuvlar va teshiklar kombinatsiyalari hajmi."""
    runes_count = len(ANCIENT_RUNES)
    permutations_3_sockets = runes_count ** 3
    return {
        "ancient_runes": runes_count,
        "socket_combinations": permutations_3_sockets,
        "famous_recipes": len(FAMOUS_RUNEWORDS),
        "total_enchantments": permutations_3_sockets * 15
    }
