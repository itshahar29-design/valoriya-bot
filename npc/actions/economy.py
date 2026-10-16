import math
import json
import logging
from typing import Dict, Any, Optional

# =====================================================================
# VALORIYA: OCHKO'ZLIK MODULI VA IQTISODIY HARAKATLAR (FAZA 3)
# =====================================================================
# Ushbu modul 12 ta ochko'zlik harakatini, matematik formulalarni va
# harakatlarni npc_actions_log jadvaliga qayd etishni boshqaradi.
# Owner (@nakama_02, ID 648616238) barcha ta'sirlardan 100% himoyalangan.
# =====================================================================

OWNER_TELEGRAM_ID = 648616238
OWNER_USERNAME = "nakama_02"

ECONOMY_COOLDOWNS = {
    "soliq_oshirish": 12 * 3600,       # 12 soat
    "xiroj_talab": 24 * 3600,          # 24 soat
    "pora_qabul": 0,                   # har so'rov
    "narx_shishirish": 6 * 3600,       # 6 soat
    "zahira_yigish": 8 * 3600,         # 8 soat
    "qarz_berish": 0,                  # har so'rov
    "qarz_undirish": 24 * 3600,        # 24 soat
    "asir_narxi": 0,                   # har asir
    "ikki_tomonlama_savdo": 48 * 3600, # 48 soat
    "karvon_tolli": 0,                 # doimiy
    "auksion_snayper": 0,              # har auksion
    "xazina_sarfi": 24 * 3600          # 24 soat
}

def clamp_float(val: float, low: float, high: float) -> float:
    """Suzuvchi sonni [low, high] oralig'ida chegaralaydi."""
    return max(low, min(high, val))

def calculate_greed_need(treasury: float, target_treasury: float) -> float:
    """Ehtiyoj formulasi: need = clamp(1 - xazina / maqsad, 0, 1)"""
    if target_treasury <= 0:
        return 0.0
    return clamp_float(1.0 - (treasury / target_treasury), 0.0, 1.0)

def calculate_greed_drive(greed: float, treasury: float, target_treasury: float) -> float:
    """
    Ochko'zlik drayvi: GD = (Och/100) * (0.4 + 0.6 * need)
    To'yish: xazina >= 120% maqsad bo'lsa, GD 50% ga pasayadi (GD * 0.5).
    """
    need = calculate_greed_need(treasury, target_treasury)
    gd = (greed / 100.0) * (0.4 + 0.6 * need)
    if target_treasury > 0 and treasury >= 1.2 * target_treasury:
        gd *= 0.5
    return gd

def calculate_tax_surcharge(gd: float) -> int:
    """Soliq ustamasi: +floor(GD * 10)%, cap +10%"""
    surcharge = math.floor(gd * 10)
    return max(0, min(10, int(surcharge)))

def calculate_bribe_probability(
    greed: float, loyalty: float, suspicion: float, offer: float, ask: float
) -> float:
    """
    Pora qabul ehtimoli:
    P = clamp(0.10 + 0.60*(Och/100) + 0.30*(taklif/narx - 1) - 0.25*(Sad/100) - 0.30*(shubha/100), 0.02, 0.95)
    """
    ratio_diff = (offer / ask - 1.0) if ask > 0 else 0.0
    p = 0.10 + 0.60 * (greed / 100.0) + 0.30 * ratio_diff - 0.25 * (loyalty / 100.0) - 0.30 * (suspicion / 100.0)
    return clamp_float(p, 0.02, 0.95)

def calculate_tribute_rate(gd: float) -> float:
    """Xiroj foizi: 2% + 8% * GD, maksimal 15% (0.15)"""
    return min(0.15, 0.02 + 0.08 * gd)

def calculate_tribute_amount(gold: float, gd: float) -> int:
    """O'yinchidan talab qilinadigan xiroj oltin miqdori"""
    return int(gold * calculate_tribute_rate(gd))

def calculate_ask_price(base_price: float, greed: float) -> float:
    """Hukmdor do'koni narxi: baza * (1 + Och/100)"""
    return base_price * (1.0 + greed / 100.0)

async def is_owner_target(db, target: Any) -> bool:
    """Nishon Owner (@nakama_02 yoki 648616238) ekanligini tekshiradi."""
    if not target:
        return False
    if str(target) == str(OWNER_TELEGRAM_ID) or str(target).lower() == OWNER_USERNAME:
        return True
    try:
        if isinstance(target, int) or (isinstance(target, str) and target.isdigit()):
            tid = int(target)
            async with db.execute("SELECT user_id, telegram_id FROM characters WHERE id = ? OR user_id = ?;", (tid, tid)) as cur:
                row = await cur.fetchone()
                if row and (row[0] == OWNER_TELEGRAM_ID or row[1] == OWNER_TELEGRAM_ID):
                    return True
    except Exception:
        pass
    return False

async def log_npc_action(
    db, ruler_id: str, action: str, target: Optional[Any], params: dict, result: str = "success"
) -> int:
    """Harakatni npc_actions_log jadvaliga qayd etadi."""
    async with db.execute("""
    INSERT INTO npc_actions_log (ruler_id, action, target, params_json, result)
    VALUES (?, ?, ?, ?, ?);
    """, (ruler_id, action, str(target) if target else None, json.dumps(params), result)) as cur:
        action_id = cur.lastrowid
    return action_id

# ---------------------------------------------------------------------
# 12 TA OCHKO'ZLIK HARAKATLARINING IJROCHILARI
# ---------------------------------------------------------------------

async def execute_soliq_oshirish(db, ruler_id: str) -> Dict[str, Any]:
    """1. Soliq oshirish (xazina < 50% da triggered, +1..10%, cooldown 12s)"""
    async with db.execute("SELECT greed, treasury FROM npc_rulers WHERE empire_id = ?;", (ruler_id,)) as cur:
        r = await cur.fetchone()
    greed, treasury = r if r else (50, 20000)
    target_treasury = 40000.0
    gd = calculate_greed_drive(greed, treasury, target_treasury)
    surcharge = calculate_tax_surcharge(gd)

    params = {"tax_surcharge_pct": surcharge, "gd": round(gd, 3)}
    await log_npc_action(db, ruler_id, "soliq_oshirish", "market", params)
    return {"action": "soliq_oshirish", "status": "executed", **params}

async def execute_xiroj_talab(db, ruler_id: str, target_char_id: int, player_gold: int) -> Dict[str, Any]:
    """2. Xiroj talab (GD > 0.6, o'yinchi boy, 2-15% xiroj)"""
    if await is_owner_target(db, target_char_id):
        return {"action": "xiroj_talab", "status": "blocked_owner_immunity"}

    async with db.execute("SELECT greed, treasury FROM npc_rulers WHERE empire_id = ?;", (ruler_id,)) as cur:
        r = await cur.fetchone()
    greed, treasury = r if r else (50, 20000)
    gd = calculate_greed_drive(greed, treasury, 40000.0)
    rate = calculate_tribute_rate(gd)
    amount = int(player_gold * rate)

    params = {"tribute_rate": round(rate, 4), "gold_demanded": amount}
    await log_npc_action(db, ruler_id, "xiroj_talab", target_char_id, params)
    return {"action": "xiroj_talab", "status": "demanded", **params}

async def execute_pora_qabul(
    db, ruler_id: str, target_char_id: int, offer_gold: int, ask_gold: int, current_suspicion: int = 0
) -> Dict[str, Any]:
    """3. Pora qabul (Formula P bo'yicha ehtimollik)"""
    async with db.execute("SELECT greed, loyalty FROM npc_rulers WHERE empire_id = ?;", (ruler_id,)) as cur:
        r = await cur.fetchone()
    greed, loyalty = r if r else (50, 50)

    p = calculate_bribe_probability(greed, loyalty, current_suspicion, offer_gold, ask_gold)
    params = {"offer": offer_gold, "ask": ask_gold, "p": round(p, 4)}
    await log_npc_action(db, ruler_id, "pora_qabul", target_char_id, params, result=f"prob_{round(p,2)}")
    return {"action": "pora_qabul", "probability": p, **params}

async def execute_narx_shishirish(db, ruler_id: str, resource_name: str, inflation_pct: int = 30) -> Dict[str, Any]:
    """4. Narx shishirish (NPC do'kon narxi +20..60%)"""
    clamped_inflation = max(20, min(60, inflation_pct))
    params = {"resource": resource_name, "inflation_pct": clamped_inflation}
    await log_npc_action(db, ruler_id, "narx_shishirish", resource_name, params)
    return {"action": "narx_shishirish", "status": "executed", **params}

async def execute_zahira_yigish(db, ruler_id: str, resource_name: str, amount: int = 100, cost: int = 500) -> Dict[str, Any]:
    """5. Zahira yig'ish (Bot arzon oladi, keyin sotadi)"""
    params = {"resource": resource_name, "amount": amount, "cost": cost}
    await log_npc_action(db, ruler_id, "zahira_yigish", resource_name, params)
    return {"action": "zahira_yigish", "status": "executed", **params}

async def execute_qarz_berish(
    db, ruler_id: str, target_char_id: int, principal: int = 1000, rate_per_day: float = 0.03, days: int = 7
) -> Dict[str, Any]:
    """6. Sudxo'rlik / Qarz berish (2-5%/kun, <= 7 kun)"""
    if await is_owner_target(db, target_char_id):
        return {"action": "qarz_berish", "status": "blocked_owner_immunity"}

    rate = max(0.02, min(0.05, rate_per_day))
    d = min(7, max(1, days))
    await db.execute("""
    INSERT INTO npc_loans (ruler_id, character_id, principal, rate, due_at, status)
    VALUES (?, ?, ?, ?, datetime('now', '+' || ? || ' days'), 'active');
    """, (ruler_id, target_char_id, principal, rate, d))

    params = {"principal": principal, "rate": rate, "days": d}
    await log_npc_action(db, ruler_id, "qarz_berish", target_char_id, params)
    return {"action": "qarz_berish", "status": "granted", **params}

async def execute_qarz_undirish(db, ruler_id: str, loan_id: int) -> Dict[str, Any]:
    """7. Qarz undirish (Muddat o'tganda ogohlantirish / bounty)"""
    params = {"loan_id": loan_id}
    await log_npc_action(db, ruler_id, "qarz_undirish", str(loan_id), params)
    return {"action": "qarz_undirish", "status": "collected", **params}

async def execute_asir_narxi(db, ruler_id: str, base_ransom: int = 1000) -> Dict[str, Any]:
    """8. Asir narxi: Ransom * (1 + Och/100)"""
    async with db.execute("SELECT greed FROM npc_rulers WHERE empire_id = ?;", (ruler_id,)) as cur:
        r = await cur.fetchone()
    greed = r[0] if r else 50
    final_ransom = int(base_ransom * (1.0 + greed / 100.0))
    params = {"base_ransom": base_ransom, "final_ransom": final_ransom, "greed": greed}
    await log_npc_action(db, ruler_id, "asir_narxi", None, params)
    return {"action": "asir_narxi", "ransom": final_ransom, **params}

async def execute_ikki_tomonlama_savdo(
    db, ruler_id: str, party_a: str, party_b: str, bribe_a: int = 500, bribe_b: int = 500
) -> Dict[str, Any]:
    """9. Ikki tomonlama savdo (Ikkalasidan pora oladi, 25% fosh bo'lish xavfi)"""
    params = {"party_a": party_a, "party_b": party_b, "bribe_total": bribe_a + bribe_b}
    await log_npc_action(db, ruler_id, "ikki_tomonlama_savdo", f"{party_a}:{party_b}", params)
    return {"action": "ikki_tomonlama_savdo", "status": "executed", **params}

async def execute_karvon_tolli(db, ruler_id: str, route_name: str, toll_pct: float = 0.05) -> Dict[str, Any]:
    """10. Karvon tolli (Toll 3-12%)"""
    toll = clamp_float(toll_pct, 0.03, 0.12)
    params = {"route": route_name, "toll_pct": round(toll, 3)}
    await log_npc_action(db, ruler_id, "karvon_tolli", route_name, params)
    return {"action": "karvon_tolli", "status": "applied", **params}

async def execute_auksion_snayper(db, ruler_id: str, item_id: str, max_bid: int = 2000) -> Dict[str, Any]:
    """11. Auksion snayperi (Oxirgi soniyalarda stavka urish)"""
    params = {"item_id": item_id, "bid": max_bid}
    await log_npc_action(db, ruler_id, "auksion_snayper", item_id, params)
    return {"action": "auksion_snayper", "status": "bid_placed", **params}

async def execute_xazina_sarfi(db, ruler_id: str, spend_type: str = "army", amount: int = 5000) -> Dict[str, Any]:
    """12. Xazina sarfi (xazina >= 120% da armiya yoki qal'aga sarflash)"""
    params = {"spend_type": spend_type, "amount": amount}
    await db.execute("""
    UPDATE npc_rulers SET treasury = MAX(0, treasury - ?) WHERE empire_id = ?;
    """, (amount, ruler_id))
    await log_npc_action(db, ruler_id, "xazina_sarfi", spend_type, params)
    return {"action": "xazina_sarfi", "status": "spent", **params}
