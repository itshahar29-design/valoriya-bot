from typing import Dict, Any, Optional, List

# =====================================================================
# VALORIYA: 12 HUKMDOR SHAXSIYAT MATRITSASI (8 XISLAT)
# =====================================================================
# Har bir xislat 0 dan 100 gacha bo'lgan o'zgarmas bazaviy asos (baseline).
# Ochko'zlik (Greed), Mag'rurlik (Pride), G'azab (Anger), Hiyla (Cunning),
# Sadoqat (Loyalty), Ehtiyotkorlik (Caution), Taqvo (Piety), Shuhrat (Ambition).
# =====================================================================

TRAIT_NAMES = [
    "greed",     # Ochko'zlik
    "pride",     # Mag'rurlik
    "anger",     # G'azab
    "cunning",   # Hiyla
    "loyalty",   # Sadoqat
    "caution",   # Ehtiyotkorlik
    "piety",     # Taqvo
    "ambition"   # Shuhratparastlik
]

RULER_PROFILES: Dict[str, Dict[str, Any]] = {
    "lionguard": {
        "empire_id": "lionguard",
        "ruler_name": "Imperator Valter V",
        "persona": "pride",
        "traits": {
            "greed": 40, "pride": 95, "anger": 50, "cunning": 40,
            "loyalty": 70, "caution": 50, "piety": 60, "ambition": 85
        },
        "treasury_base": 25000, "army_base": 1200
    },
    "frost_peak": {
        "empire_id": "frost_peak",
        "ruler_name": "Qonxo'r Ragnar Temirqo'l",
        "persona": "anger",
        "traits": {
            "greed": 30, "pride": 60, "anger": 95, "cunning": 20,
            "loyalty": 80, "caution": 15, "piety": 30, "ambition": 65
        },
        "treasury_base": 12000, "army_base": 950
    },
    "ursus_peak": {
        "empire_id": "ursus_peak",
        "ruler_name": "Knyaz Boris Qoraboy",
        "persona": "calm",
        "traits": {
            "greed": 35, "pride": 45, "anger": 20, "cunning": 50,
            "loyalty": 85, "caution": 90, "piety": 55, "ambition": 40
        },
        "treasury_base": 18000, "army_base": 1100
    },
    "iron_bastion": {
        "empire_id": "iron_bastion",
        "ruler_name": "Bosh Usta Torin Bolg'ador",
        "persona": "greed",
        "traits": {
            "greed": 98, "pride": 40, "anger": 35, "cunning": 75,
            "loyalty": 30, "caution": 70, "piety": 20, "ambition": 70
        },
        "treasury_base": 40000, "army_base": 800
    },
    "azure_lily": {
        "empire_id": "azure_lily",
        "ruler_name": "Gersoginya Izabella",
        "persona": "diplomat",
        "traits": {
            "greed": 70, "pride": 50, "anger": 15, "cunning": 90,
            "loyalty": 45, "caution": 75, "piety": 40, "ambition": 80
        },
        "treasury_base": 35000, "army_base": 700
    },
    "crimson_sultanate": {
        "empire_id": "crimson_sultanate",
        "ruler_name": "Sulton Sulaymon Olovsoz",
        "persona": "wrath",
        "traits": {
            "greed": 55, "pride": 80, "anger": 90, "cunning": 35,
            "loyalty": 55, "caution": 20, "piety": 45, "ambition": 85
        },
        "treasury_base": 22000, "army_base": 1300
    },
    "iron_steppe": {
        "empire_id": "iron_steppe",
        "ruler_name": "Botirxon Bahodir",
        "persona": "wild",
        "traits": {
            "greed": 45, "pride": 55, "anger": 70, "cunning": 45,
            "loyalty": 90, "caution": 25, "piety": 35, "ambition": 55
        },
        "treasury_base": 15000, "army_base": 1050
    },
    "shadowfang": {
        "empire_id": "shadowfang",
        "ruler_name": "Soya Knyazi Moros",
        "persona": "treason",
        "traits": {
            "greed": 65, "pride": 50, "anger": 45, "cunning": 98,
            "loyalty": 5, "caution": 80, "piety": 10, "ambition": 90
        },
        "treasury_base": 20000, "army_base": 650
    },
    "blood_tide": {
        "empire_id": "blood_tide",
        "ruler_name": "Kapitan Qora Soqol",
        "persona": "greedy_wild",
        "traits": {
            "greed": 90, "pride": 55, "anger": 60, "cunning": 70,
            "loyalty": 25, "caution": 30, "piety": 15, "ambition": 60
        },
        "treasury_base": 28000, "army_base": 750
    },
    "ash_necropolis": {
        "empire_id": "ash_necropolis",
        "ruler_name": "Boqiy Lich Malakor",
        "persona": "cold",
        "traits": {
            "greed": 40, "pride": 70, "anger": 30, "cunning": 80,
            "loyalty": 20, "caution": 85, "piety": 5, "ambition": 95
        },
        "treasury_base": 16000, "army_base": 1500
    },
    "sun_order": {
        "empire_id": "sun_order",
        "ruler_name": "Oliy Patriarx Avreliy",
        "persona": "fanatic",
        "traits": {
            "greed": 15, "pride": 75, "anger": 65, "cunning": 30,
            "loyalty": 75, "caution": 40, "piety": 100, "ambition": 60
        },
        "treasury_base": 19000, "army_base": 900
    },
    "silverleaf": {
        "empire_id": "silverleaf",
        "ruler_name": "Qirolicha Elenor",
        "persona": "wise",
        "traits": {
            "greed": 20, "pride": 40, "anger": 10, "cunning": 70,
            "loyalty": 80, "caution": 85, "piety": 70, "ambition": 45
        },
        "treasury_base": 21000, "army_base": 850
    }
}

def get_ruler_profile(empire_id: str) -> Optional[Dict[str, Any]]:
    """Imperiya ID si bo'yicha hukmdor shaxsiyat profilini qaytaradi."""
    return RULER_PROFILES.get(empire_id)

def get_all_ruler_profiles() -> Dict[str, Dict[str, Any]]:
    """Barcha 12 ta hukmdor profillarini qaytaradi."""
    return RULER_PROFILES

def validate_profile(profile: Dict[str, Any]) -> bool:
    """Profil va xislatlarning 0-100 oralig'ida ekanligini tekshiradi."""
    traits = profile.get("traits", {})
    if len(traits) != 8:
        return False
    for t_name in TRAIT_NAMES:
        if t_name not in traits:
            return False
        val = traits[t_name]
        if not isinstance(val, (int, float)) or not (0 <= val <= 100):
            return False
    return True

async def seed_npc_rulers(db) -> int:
    """
    Ma'lumotlar bazasidagi npc_rulers jadvaliga 12 ta hukmdor boshlang'ich
    shaxsiyat profillarini idempotent tarzda kiritadi yoki yangilaydi.
    """
    count = 0
    for emp_id, p in RULER_PROFILES.items():
        t = p["traits"]
        await db.execute("""
        INSERT INTO npc_rulers (
            empire_id, ruler_name, persona,
            greed, pride, anger, cunning, loyalty, caution, piety, ambition,
            joy, anger_current, fear, boredom, unrest, treasury, army
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 50, 0, 0, 0, 0, ?, ?)
        ON CONFLICT(empire_id) DO UPDATE SET
            ruler_name = excluded.ruler_name,
            persona = excluded.persona,
            greed = excluded.greed,
            pride = excluded.pride,
            anger = excluded.anger,
            cunning = excluded.cunning,
            loyalty = excluded.loyalty,
            caution = excluded.caution,
            piety = excluded.piety,
            ambition = excluded.ambition;
        """, (
            emp_id, p["ruler_name"], p["persona"],
            t["greed"], t["pride"], t["anger"], t["cunning"],
            t["loyalty"], t["caution"], t["piety"], t["ambition"],
            p["treasury_base"], p["army_base"]
        ))
        count += 1
    return count
