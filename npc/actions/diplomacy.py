import json
import logging
from typing import Dict, Any, Optional
from npc.actions.economy import is_owner_target, log_npc_action

# =====================================================================
# VALORIYA: DIPLOMATIYA HARAKATLARI VA IMZO QOBILIYATLAR (FAZA 4)
# =====================================================================
# 12 ta imperiya o'rtasidagi ittifoq, urush, pakt va vositachilik harakatlari.
# Owner (@nakama_02, ID 648616238) barcha diplomatik tazyiqlardan 100% himoyalangan.
# =====================================================================

DIPLOMACY_COOLDOWNS = {
    "ittifoq_taklif": 24 * 3600,
    "ittifoq_buzish": 24 * 3600,
    "urush_elon": 48 * 3600,
    "tinchlik_taklif": 12 * 3600,
    "embargo": 72 * 3600,
    "elchi_yuborish": 6 * 3600,
    "sovga_yuborish": 12 * 3600,
    "ultimatum": 24 * 3600,
    "vositachilik": 24 * 3600,
    "maxfiy_pakt": 48 * 3600,
    "zaif_ittifoq_rad": 6 * 3600,
    "kechirim_talab": 12 * 3600,
    "ittifoq_broker": 24 * 3600,
}

async def _upsert_diplomacy(db, e1: str, e2: str, status: str, pact_type: Optional[str] = None, is_secret: int = 0):
    """Imperiyalararo munosabat holatini diplomacy jadvaliga saqlaydi."""
    # Har doim e1 < e2 tartibida saqlash dublikatlarni oldini oladi
    emp_a, emp_b = sorted([e1, e2])
    await db.execute("""
    INSERT INTO diplomacy (empire1, empire2, status, pact_type, is_secret, since)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(empire1, empire2) DO UPDATE SET
        status = excluded.status,
        pact_type = excluded.pact_type,
        is_secret = excluded.is_secret,
        since = CURRENT_TIMESTAMP;
    """, (emp_a, emp_b, status, pact_type, is_secret))

# ---------------------------------------------------------------------
# DIPLOMATIK HARAKATLAR
# ---------------------------------------------------------------------

async def execute_ittifoq_taklif(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Ittifoq taklif qilish"""
    if await is_owner_target(db, target_empire):
        return {"action": "ittifoq_taklif", "status": "blocked_owner_immunity"}

    params = {"target": target_empire}
    await _upsert_diplomacy(db, ruler_id, target_empire, status="allied", pact_type="mutual_defense")
    await log_npc_action(db, ruler_id, "ittifoq_taklif", target_empire, params)
    return {"action": "ittifoq_taklif", "status": "proposed", **params}

async def execute_zaif_ittifoq_rad(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Valter (Kibr): Zaif imperiya bilan ittifoqni mensimay rad etish"""
    if await is_owner_target(db, target_empire):
        return {"action": "zaif_ittifoq_rad", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "reason": "Zaiflik va kibr"}
    await log_npc_action(db, ruler_id, "zaif_ittifoq_rad", target_empire, params)
    return {"action": "zaif_ittifoq_rad", "status": "rejected_with_pride", **params}

async def execute_kechirim_talab(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Valter (Kibr): Haqorat yoki xatodan so'ng tiz cho'kib kechirim so'rashni talab qilish"""
    if await is_owner_target(db, target):
        return {"action": "kechirim_talab", "status": "blocked_owner_immunity"}

    params = {"target": str(target), "demand": "formal_apology_and_tribute"}
    await log_npc_action(db, ruler_id, "kechirim_talab", target, params)
    return {"action": "kechirim_talab", "status": "demanded", **params}

async def execute_vositachilik(db, ruler_id: str, empire_a: str, empire_b: str) -> Dict[str, Any]:
    """Boris (Vazmin): Qo'shni urushayotgan imperiyalar o'rtasida tinchlik vositachiligi"""
    if await is_owner_target(db, empire_a) or await is_owner_target(db, empire_b):
        return {"action": "vositachilik", "status": "blocked_owner_immunity"}

    params = {"mediator": ruler_id, "parties": [empire_a, empire_b]}
    await _upsert_diplomacy(db, empire_a, empire_b, status="truce", pact_type="mediated_peace")
    await log_npc_action(db, ruler_id, "vositachilik", f"{empire_a}:{empire_b}", params)
    return {"action": "vositachilik", "status": "truce_brokered", **params}

async def execute_tinchlik_taklif(db, ruler_id: str, target_empire: str, gold_offer: int = 1000) -> Dict[str, Any]:
    """Boris (Vazmin): Arzon va murosali tinchlik shartnomasi"""
    if await is_owner_target(db, target_empire):
        return {"action": "tinchlik_taklif", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "gold_offer": gold_offer}
    await _upsert_diplomacy(db, ruler_id, target_empire, status="truce", pact_type="peace_treaty")
    await log_npc_action(db, ruler_id, "tinchlik_taklif", target_empire, params)
    return {"action": "tinchlik_taklif", "status": "peace_offered", **params}

async def execute_ittifoq_broker(db, ruler_id: str, empire_a: str, empire_b: str, fee: int = 2000) -> Dict[str, Any]:
    """Izabella (Diplomat): Uchinchi tomonlarni kelishtirib, vositachilik komissiyasi olish"""
    if await is_owner_target(db, empire_a) or await is_owner_target(db, empire_b):
        return {"action": "ittifoq_broker", "status": "blocked_owner_immunity"}

    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (fee, ruler_id))
    await _upsert_diplomacy(db, empire_a, empire_b, status="allied", pact_type="commercial_alliance")
    params = {"parties": [empire_a, empire_b], "fee": fee}
    await log_npc_action(db, ruler_id, "ittifoq_broker", f"{empire_a}:{empire_b}", params)
    return {"action": "ittifoq_broker", "status": "brokered", **params}

async def execute_urush_elon(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Sulaymon (Qahr): Rasmiy urush e'lon qilish"""
    if await is_owner_target(db, target_empire):
        return {"action": "urush_elon", "status": "blocked_owner_immunity"}

    params = {"target": target_empire}
    await _upsert_diplomacy(db, ruler_id, target_empire, status="war", pact_type="total_war")
    await log_npc_action(db, ruler_id, "urush_elon", target_empire, params)
    return {"action": "urush_elon", "status": "war_declared", **params}

async def execute_maxfiy_pakt(db, ruler_id: str, target_empire: str, pact_type: str = "secret_pact") -> Dict[str, Any]:
    """Moros (Xoin): Boshqalardan yashirin fitna yoki maxfiy pakt tuzish"""
    if await is_owner_target(db, target_empire):
        return {"action": "maxfiy_pakt", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "pact_type": pact_type}
    await _upsert_diplomacy(db, ruler_id, target_empire, status="allied", pact_type=pact_type, is_secret=1)
    await log_npc_action(db, ruler_id, "maxfiy_pakt", target_empire, params)
    return {"action": "maxfiy_pakt", "status": "secret_pact_signed", **params}

async def execute_ultimatum(db, ruler_id: str, target_empire: str, demand_text: str = "Taslim bo'ling") -> Dict[str, Any]:
    """Malakor (Muzdek): Sovuq va shafqatsiz ultimatum"""
    if await is_owner_target(db, target_empire):
        return {"action": "ultimatum", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "demand": demand_text}
    await log_npc_action(db, ruler_id, "ultimatum", target_empire, params)
    return {"action": "ultimatum", "status": "ultimatum_delivered", **params}

async def execute_embargo(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Savdo embargosi joriy etish"""
    if await is_owner_target(db, target_empire):
        return {"action": "embargo", "status": "blocked_owner_immunity"}

    params = {"target": target_empire}
    await log_npc_action(db, ruler_id, "embargo", target_empire, params)
    return {"action": "embargo", "status": "embargo_active", **params}

async def execute_elchi_yuborish(db, ruler_id: str, target_empire: str, message: str) -> Dict[str, Any]:
    """Diplomatik elchi yuborish"""
    if await is_owner_target(db, target_empire):
        return {"action": "elchi_yuborish", "status": "blocked_owner_immunity"}

    params = {"target": target_empire, "message": message}
    await log_npc_action(db, ruler_id, "elchi_yuborish", target_empire, params)
    return {"action": "elchi_yuborish", "status": "envoy_dispatched", **params}

async def execute_sovga_yuborish(db, ruler_id: str, target_empire: str, gold_amount: int = 500) -> Dict[str, Any]:
    """Diplomatik sovg'a yuborish (ishonchni oshirish uchun)"""
    if await is_owner_target(db, target_empire):
        return {"action": "sovga_yuborish", "status": "blocked_owner_immunity"}

    await db.execute("UPDATE npc_rulers SET treasury = MAX(0, treasury - ?) WHERE empire_id = ?;", (gold_amount, ruler_id))
    params = {"target": target_empire, "gold": gold_amount}
    await log_npc_action(db, ruler_id, "sovga_yuborish", target_empire, params)
    return {"action": "sovga_yuborish", "status": "gift_sent", **params}

async def execute_ittifoq_buzish(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Mavjud ittifoq shartnomasini bekor qilish"""
    if await is_owner_target(db, target_empire):
        return {"action": "ittifoq_buzish", "status": "blocked_owner_immunity"}

    await _upsert_diplomacy(db, ruler_id, target_empire, status="neutral", pact_type=None)
    params = {"target": target_empire}
    await log_npc_action(db, ruler_id, "ittifoq_buzish", target_empire, params)
    return {"action": "ittifoq_buzish", "status": "alliance_broken", **params}
