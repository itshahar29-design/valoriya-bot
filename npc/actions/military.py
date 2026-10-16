import json
import logging
from typing import Dict, Any, Optional
from npc.actions.economy import is_owner_target, log_npc_action

# =====================================================================
# VALORIYA: HARBIY HARAKATLAR VA IMZO QOBILIYATLAR (FAZA 4)
# =====================================================================
# 12 ta imperiya hukmdorining harbiy yurishlari, reydlari va imzo taktikalari.
# Owner (@nakama_02, ID 648616238) barcha harbiy hujumlardan 100% himoyalangan.
# =====================================================================

MILITARY_COOLDOWNS = {
    "reyd": 12 * 3600,
    "berserk_reyd": 12 * 3600,
    "qamal": 48 * 3600,
    "mudofaa_kuchaytirish": 24 * 3600,
    "yollanma_yollash": 12 * 3600,
    "karvon_talash": 6 * 3600,
    "qasos_yurishi": 24 * 3600,
    "muqaddas_urush": 72 * 3600,
    "chegara_patrul": 12 * 3600,
    "kuygan_yer": 48 * 3600,
    "fursatchi_hujum": 24 * 3600,
    "turnir_otkazish": 48 * 3600,
    "sovga_bilan_tinchlanish": 6 * 3600,
    "otliq_yordam": 24 * 3600,
    "qabila_chaqiruvi": 48 * 3600,
    "xiroj_xavfsiz_yol": 12 * 3600,
    "asir_olish": 6 * 3600,
    "oliklarni_yigish": 24 * 3600,
    "ushr_yigish": 24 * 3600,
    "taqvodorga_shifo": 6 * 3600,
}

# ---------------------------------------------------------------------
# HARBIY IMZO HARAKATLAR
# ---------------------------------------------------------------------

async def execute_turnir_otkazish(db, ruler_id: str, cost: int = 5000) -> Dict[str, Any]:
    """Valter (Kibr): Qimmatbaho shohona ritsarlar turnirini o'tkazish"""
    await db.execute("UPDATE npc_rulers SET treasury = MAX(0, treasury - ?), joy = MIN(100, joy + 20) WHERE empire_id = ?;", (cost, ruler_id))
    params = {"cost": cost, "morale_bonus": "+20% joy"}
    await log_npc_action(db, ruler_id, "turnir_otkazish", "global", params)
    return {"action": "turnir_otkazish", "status": "tournament_held", **params}

async def execute_vendetta_elon(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Ragnar (G'azab): Mag'lubiyatdan keyin qonli qasos (Vendetta) e'lon qilish"""
    if await is_owner_target(db, target):
        return {"action": "qasos_yurishi", "status": "blocked_owner_immunity"}

    params = {"target": str(target), "grudge": "+50"}
    await db.execute("UPDATE npc_rulers SET anger_current = MIN(100, anger_current + 30) WHERE empire_id = ?;", (ruler_id,))
    await log_npc_action(db, ruler_id, "qasos_yurishi", target, params)
    return {"action": "qasos_yurishi", "status": "vendetta_declared", **params}

async def execute_berserk_reyd(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Ragnar (G'azab): To'xtatib bo'lmas shafqatsiz berserk reydi"""
    if await is_owner_target(db, target):
        return {"action": "berserk_reyd", "status": "blocked_owner_immunity"}

    params = {"target": str(target), "damage_tier": "extreme"}
    await log_npc_action(db, ruler_id, "berserk_reyd", target, params)
    return {"action": "berserk_reyd", "status": "raided", **params}

async def execute_sovga_bilan_tinchlanish(db, ruler_id: str, gift_gold: int = 500) -> Dict[str, Any]:
    """Ragnar (G'azab): Katta sovg'a berilganda g'azabini bosish"""
    reduction = 20 if gift_gold >= 500 else 5
    await db.execute("UPDATE npc_rulers SET anger_current = MAX(0, anger_current - ?), joy = MIN(100, joy + 10) WHERE empire_id = ?;", (reduction, ruler_id))
    params = {"gift_gold": gift_gold, "anger_reduced": reduction}
    await log_npc_action(db, ruler_id, "sovga_bilan_tinchlanish", None, params)
    return {"action": "sovga_bilan_tinchlanish", "status": "pacified", **params}

async def execute_chegara_patrul(db, ruler_id: str) -> Dict[str, Any]:
    """Boris (Vazmin): Chegara soqchilarini kuchaytirish, tartib o'rnatish"""
    await db.execute("UPDATE npc_rulers SET unrest = MAX(0, unrest - 5) WHERE empire_id = ?;", (ruler_id,))
    params = {"unrest_reduced": 5, "defense_bonus": 10}
    await log_npc_action(db, ruler_id, "chegara_patrul", "borders", params)
    return {"action": "chegara_patrul", "status": "patrol_active", **params}

async def execute_kuygan_yer(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Sulaymon (Qahr): Olovli kuygan yer taktikasi, resurslarni yoqish"""
    if await is_owner_target(db, target):
        return {"action": "kuygan_yer", "status": "blocked_owner_immunity"}

    params = {"target": str(target), "effect": "production_halved_48h"}
    await log_npc_action(db, ruler_id, "kuygan_yer", target, params)
    return {"action": "kuygan_yer", "status": "scorched", **params}

async def execute_karvon_reydi(db, ruler_id: str, target_route: str = "desert_trail") -> Dict[str, Any]:
    """Botirxon (Yovvoyi): Chala ko'chmanchi otliqlar karvon reydi"""
    loot = 1200
    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (loot, ruler_id))
    params = {"route": target_route, "loot_gold": loot}
    await log_npc_action(db, ruler_id, "karvon_reydi", target_route, params)
    return {"action": "karvon_reydi", "status": "caravan_raided", **params}

async def execute_otliq_yordam(db, ruler_id: str, ally_empire: str) -> Dict[str, Any]:
    """Botirxon (Yovvoyi): Qardosh ittifoqchiga 200 otliq lashkar yuborish"""
    if await is_owner_target(db, ally_empire):
        return {"action": "otliq_yordam", "status": "blocked_owner_immunity"}

    params = {"ally": ally_empire, "cavalry_sent": 200}
    await log_npc_action(db, ruler_id, "otliq_yordam", ally_empire, params)
    return {"action": "otliq_yordam", "status": "cavalry_dispatched", **params}

async def execute_qabila_chaqiruvi(db, ruler_id: str) -> Dict[str, Any]:
    """Botirxon (Yovvoyi): Dasht qabilalarini umumiy bayroq ostiga yig'ish"""
    await db.execute("UPDATE npc_rulers SET army = army + 350 WHERE empire_id = ?;", (ruler_id,))
    params = {"army_boost": 350}
    await log_npc_action(db, ruler_id, "qabila_chaqiruvi", "steppe", params)
    return {"action": "qabila_chaqiruvi", "status": "horde_summoned", **params}

async def execute_karvon_talash(db, ruler_id: str, target_route: str) -> Dict[str, Any]:
    """Qora Soqol (Taloqchi): Dengiz va yo'l qaroqchiligi orqali karvon talash"""
    loot = 1500
    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (loot, ruler_id))
    params = {"target_route": target_route, "loot": loot}
    await log_npc_action(db, ruler_id, "karvon_talash", target_route, params)
    return {"action": "karvon_talash", "status": "plundered", **params}

async def execute_xiroj_xavfsiz_yol(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Qora Soqol (Taloqchi): Omonlik uchun qaroqchilik to'lovi talab qilish"""
    if await is_owner_target(db, target):
        return {"action": "xiroj_xavfsiz_yol", "status": "blocked_owner_immunity"}

    params = {"target": str(target), "ransom_toll": 800}
    await log_npc_action(db, ruler_id, "xiroj_xavfsiz_yol", target, params)
    return {"action": "xiroj_xavfsiz_yol", "status": "toll_demanded", **params}

async def execute_asir_olish(db, ruler_id: str, target_char_id: int) -> Dict[str, Any]:
    """Qora Soqol (Taloqchi): Jangdan so'ng asir olish va to'lov kutish"""
    if await is_owner_target(db, target_char_id):
        return {"action": "asir_olish", "status": "blocked_owner_immunity"}

    params = {"target": target_char_id, "ransom": 2000}
    await log_npc_action(db, ruler_id, "asir_olish", target_char_id, params)
    return {"action": "asir_olish", "status": "captive_taken", **params}

async def execute_fursatchi_hujum(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Malakor (Muzdek): Qo'shnilar zaiflashgan paytda fursatdan foydalanib zarba berish"""
    if await is_owner_target(db, target_empire):
        return {"action": "fursatchi_hujum", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "tactic": "cold_ambush"}
    await log_npc_action(db, ruler_id, "fursatchi_hujum", target_empire, params)
    return {"action": "fursatchi_hujum", "status": "ambush_launched", **params}

async def execute_oliklarni_yigish(db, ruler_id: str, corpses_count: int = 100) -> Dict[str, Any]:
    """Malakor (Muzdek): Jang maydonidagi jasadlarni nekromantiya armiyasiga qo'shish"""
    added_skeletons = corpses_count * 2
    await db.execute("UPDATE npc_rulers SET army = army + ? WHERE empire_id = ?;", (added_skeletons, ruler_id))
    params = {"corpses": corpses_count, "undead_added": added_skeletons}
    await log_npc_action(db, ruler_id, "oliklarni_yigish", "graveyards", params)
    return {"action": "oliklarni_yigish", "status": "undead_raised", **params}

async def execute_muqaddas_urush(db, ruler_id: str, target_enemy: str) -> Dict[str, Any]:
    """Avreliy (Mutassib): Zulmat va kofirlarga qarshi muqaddas urush (salib) e'lon qilish"""
    if await is_owner_target(db, target_enemy):
        return {"action": "muqaddas_urush", "status": "blocked_owner_immunity"}

    params = {"target": target_enemy, "holy_zeal": "+30% ATK"}
    await log_npc_action(db, ruler_id, "muqaddas_urush", target_enemy, params)
    return {"action": "muqaddas_urush", "status": "crusade_proclaimed", **params}

async def execute_ushr_yigish(db, ruler_id: str, tithe_gold: int = 1000) -> Dict[str, Any]:
    """Avreliy (Mutassib): Ibodatxona ehtiyojlari uchun 10% ushr yig'ish"""
    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (tithe_gold, ruler_id))
    params = {"tithe_gold": tithe_gold}
    await log_npc_action(db, ruler_id, "ushr_yigish", "temple", params)
    return {"action": "ushr_yigish", "status": "tithe_collected", **params}

async def execute_taqvodorga_shifo(db, ruler_id: str, target_char_id: int) -> Dict[str, Any]:
    """Avreliy (Mutassib): Taqvodor va sodiq ritsarga ilohiy shifo in'om etish"""
    params = {"target": target_char_id, "blessing": "divine_healing"}
    await log_npc_action(db, ruler_id, "taqvodorga_shifo", target_char_id, params)
    return {"action": "taqvodorga_shifo", "status": "blessing_granted", **params}

async def execute_reyd(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Standart harbiy reyd"""
    if await is_owner_target(db, target_empire):
        return {"action": "reyd", "status": "blocked_owner_immunity"}

    params = {"target": target_empire}
    await log_npc_action(db, ruler_id, "reyd", target_empire, params)
    return {"action": "reyd", "status": "raid_executed", **params}

async def execute_qamal(db, ruler_id: str, target_castle: str) -> Dict[str, Any]:
    """Qal'a qamali"""
    if await is_owner_target(db, target_castle):
        return {"action": "qamal", "status": "blocked_owner_immunity"}

    params = {"castle": target_castle}
    await log_npc_action(db, ruler_id, "qamal", target_castle, params)
    return {"action": "qamal", "status": "siege_started", **params}

async def execute_mudofaa_kuchaytirish(db, ruler_id: str) -> Dict[str, Any]:
    """Mudofaani mustahkamlash"""
    await db.execute("UPDATE npc_rulers SET fear = MAX(0, fear - 10) WHERE empire_id = ?;", (ruler_id,))
    params = {"defense_boost": "+15% garrison"}
    await log_npc_action(db, ruler_id, "mudofaa_kuchaytirish", "fortress", params)
    return {"action": "mudofaa_kuchaytirish", "status": "fortified", **params}

async def execute_yollanma_yollash(db, ruler_id: str, soldiers: int = 300, cost: int = 2000) -> Dict[str, Any]:
    """Yollanma askarlarni yollash"""
    await db.execute("UPDATE npc_rulers SET treasury = MAX(0, treasury - ?), army = army + ? WHERE empire_id = ?;", (cost, soldiers, ruler_id))
    params = {"soldiers": soldiers, "cost": cost}
    await log_npc_action(db, ruler_id, "yollanma_yollash", "mercenaries", params)
    return {"action": "yollanma_yollash", "status": "mercenaries_hired", **params}
