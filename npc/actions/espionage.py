import json
import logging
from typing import Dict, Any, Optional
from npc.actions.economy import is_owner_target, log_npc_action

# =====================================================================
# VALORIYA: JOSUSLIK HARAKATLARI VA IMZO QOBILIYATLAR (FAZA 4)
# =====================================================================
# Josuslik, mish-mishlar, axborot savdosi va 24-soatlik telegraf bilan
# ogohlantiriluvchi xiyonat mexanizmi (Moros, Elenor, Izabella).
# Owner (@nakama_02, ID 648616238) barcha josuslik hujumlaridan 100% himoyalangan.
# =====================================================================

ESPIONAGE_COOLDOWNS = {
    "josus_yuborish": 12 * 3600,
    "mish_mish_tarqatish": 6 * 3600,
    "sabotaj": 24 * 3600,
    "pora_berish": 12 * 3600,
    "malumot_sotish": 12 * 3600,
    "xiyonat": 72 * 3600,
    "ittifoqni_sotish": 48 * 3600,
    "mish_mish_zaharlash": 12 * 3600,
    "maslahat_berish": 6 * 3600,
    "tarixni_eslash": 12 * 3600,
    "izchilga_mukofot": 24 * 3600,
    "bank_qarzi": 24 * 3600,
}

# ---------------------------------------------------------------------
# JOSUSLIK IMZO HARAKATLAR
# ---------------------------------------------------------------------

async def execute_malumot_sotish(db, ruler_id: str, target_buyer: Any, price: int = 1500) -> Dict[str, Any]:
    """Izabella (Diplomat): Maxfiy ma'lumot va josuslik hisobotini pullash"""
    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (price, ruler_id))
    params = {"buyer": str(target_buyer), "price": price}
    await log_npc_action(db, ruler_id, "malumot_sotish", target_buyer, params)
    return {"action": "malumot_sotish", "status": "info_sold", **params}

async def execute_bank_qarzi(db, ruler_id: str, target_char_id: int, amount: int = 5000) -> Dict[str, Any]:
    """Izabella (Diplomat): O'yinchiga yoki ittifoqchiga elita bank qarzi ajratish"""
    if await is_owner_target(db, target_char_id):
        return {"action": "bank_qarzi", "status": "blocked_owner_immunity"}

    params = {"target": target_char_id, "amount": amount, "interest_rate": 0.02}
    await log_npc_action(db, ruler_id, "bank_qarzi", target_char_id, params)
    return {"action": "bank_qarzi", "status": "bank_credit_issued", **params}

async def execute_ittifoqni_sotish(db, ruler_id: str, enemy_empire: str, secret_intel: str) -> Dict[str, Any]:
    """Moros (Xoin): Ittifoqchining harbiy sirlarini dushmanga sotish"""
    if await is_owner_target(db, enemy_empire):
        return {"action": "ittifoqni_sotish", "status": "blocked_owner_immunity"}

    reward = 2500
    await db.execute("UPDATE npc_rulers SET treasury = treasury + ? WHERE empire_id = ?;", (reward, ruler_id))
    params = {"enemy": enemy_empire, "intel": secret_intel, "reward": reward}
    await log_npc_action(db, ruler_id, "ittifoqni_sotish", enemy_empire, params)
    return {"action": "ittifoqni_sotish", "status": "alliance_secrets_sold", **params}

async def execute_mish_mish_zaharlash(db, ruler_id: str, target_subject: str, toxic_text: str) -> Dict[str, Any]:
    """Moros (Xoin): Provokatsion va yolg'on mish-mish tarqatish"""
    if await is_owner_target(db, target_subject):
        return {"action": "mish_mish_zaharlash", "status": "blocked_owner_immunity"}

    await db.execute("""
    INSERT INTO rumors (source_ruler, subject, text_key, is_true, spread, expires_at)
    VALUES (?, ?, ?, 0, 3, datetime('now', '+24 hours'));
    """, (ruler_id, target_subject, toxic_text))

    params = {"target": target_subject, "rumor": toxic_text}
    await log_npc_action(db, ruler_id, "mish_mish_zaharlash", target_subject, params)
    return {"action": "mish_mish_zaharlash", "status": "rumor_poisoned", **params}

async def execute_xiyonat(
    db, ruler_id: str, target_empire: str, force_execute_after_24h: bool = False
) -> Dict[str, Any]:
    """
    Moros (Xoin): Xiyonat harakati.
    Qoida: Xiyonatdan 24 soat oldin ogohlantiruvchi belgi chiqadi (g'alati elchilar, mish-mish).
    24 soat o'tmaguncha to'g'ridan-to'g'ri xiyonat sodir bo'lmaydi.
    """
    if await is_owner_target(db, target_empire):
        return {"action": "xiyonat", "status": "blocked_owner_immunity"}

    key = f"betrayal_warning_{ruler_id}_{target_empire}"

    # 1. Ogohlantirish bormi tekshirish
    async with db.execute("SELECT value_json, (strftime('%s', 'now') - strftime('%s', updated_at)) FROM world_state WHERE key = ?;", (key,)) as cur:
        row = await cur.fetchone()

    if not row:
        # Birinchi bosqich: 24 soat oldin telegraf belgisi chiqarish
        warning_info = {
            "traitor": ruler_id,
            "target": target_empire,
            "stage": "telegraphed_warning",
            "message": f"Saroydan g'alati elchilar ko'rindi. {ruler_id} xiyonatiga 24 soat qoldi!"
        }
        await db.execute("""
        INSERT INTO world_state (key, value_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, updated_at = CURRENT_TIMESTAMP;
        """, (key, json.dumps(warning_info)))

        # Mish-mishlar jadvaliga ham qayd etish
        await db.execute("""
        INSERT INTO rumors (source_ruler, subject, text_key, is_true, spread, expires_at)
        VALUES (?, ?, 'Xiyonat xavfi: saroydan g''alati elchilar ko''rindi!', 1, 5, datetime('now', '+24 hours'));
        """, (ruler_id, target_empire))

        params = {"traitor": ruler_id, "target": target_empire, "telegraph": "24h_warning"}
        await log_npc_action(db, ruler_id, "xiyonat", target_empire, params, result="telegraphed_24h_warning")
        return {
            "action": "xiyonat",
            "status": "telegraphed_24h_warning",
            "warning": warning_info["message"],
            "traitor": ruler_id,
            "target": target_empire
        }

    # 2. Ogohlantirish mavjud: 24 soat o'tganligini tekshirish
    elapsed_seconds = row[1] if row[1] is not None else 0
    twenty_four_hours = 24 * 3600

    if elapsed_seconds < twenty_four_hours and not force_execute_after_24h:
        # Hali 24 soat o'tmadi
        remaining = round((twenty_four_hours - elapsed_seconds) / 3600, 1)
        return {
            "action": "xiyonat",
            "status": "waiting_24h_telegraph",
            "remaining_hours": remaining,
            "message": f"Xiyonat telegrafi faol: 24 soatlik ogohlantirish muddati tugashiga {remaining} soat bor."
        }

    # 3. 24 soat o'tdi: Xiyonatni haqiqiy ijro etish
    await db.execute("DELETE FROM world_state WHERE key = ?;", (key,))

    # Diplomatiyada ittifoqni urushga aylantirish
    emp_a, emp_b = sorted([ruler_id, target_empire])
    await db.execute("""
    UPDATE diplomacy SET status = 'war', pact_type = 'broken_by_betrayal', grievance = grievance + 40
    WHERE empire1 = ? AND empire2 = ?;
    """, (emp_a, emp_b))

    params = {"traitor": ruler_id, "target": target_empire, "pact_broken": True}
    await log_npc_action(db, ruler_id, "xiyonat", target_empire, params, result="executed")
    return {
        "action": "xiyonat",
        "status": "executed",
        "traitor": ruler_id,
        "target": target_empire,
        "message": f"{ruler_id} xiyonat qildi va {target_empire} bilan ittifoqni sindirdi!"
    }

async def execute_maslahat_berish(db, ruler_id: str, target_char_id: int) -> Dict[str, Any]:
    """Elenor (Donishmand): O'yinchiga qimmatli donishmandlik va maslahat berish"""
    params = {"target": target_char_id, "hint": "Tog'lar ortidagi qadimiy g'orda sirli qurollar yashiringan"}
    await log_npc_action(db, ruler_id, "maslahat_berish", target_char_id, params)
    return {"action": "maslahat_berish", "status": "hint_given", **params}

async def execute_tarixni_eslash(db, ruler_id: str, relic_or_boss: str) -> Dict[str, Any]:
    """Elenor (Donishmand): Qadimiy yozuvlar va zaif nuqtalar tarixini ochish"""
    params = {"subject": relic_or_boss, "lore_unlocked": "Boss muz hujumlariga o'ta sezgir"}
    await log_npc_action(db, ruler_id, "tarixni_eslash", relic_or_boss, params)
    return {"action": "tarixni_eslash", "status": "history_revealed", **params}

async def execute_izchilga_mukofot(db, ruler_id: str, target_char_id: int, reward_gold: int = 1000) -> Dict[str, Any]:
    """Elenor (Donishmand): Sodiq va izchil ritsarga donishmandlik mukofoti berish"""
    await db.execute("UPDATE characters SET gold = gold + ? WHERE id = ?;", (reward_gold, target_char_id))
    params = {"target": target_char_id, "reward": reward_gold}
    await log_npc_action(db, ruler_id, "izchilga_mukofot", target_char_id, params)
    return {"action": "izchilga_mukofot", "status": "rewarded", **params}

async def execute_josus_yuborish(db, ruler_id: str, target_empire: str) -> Dict[str, Any]:
    """Standart josus yuborish"""
    if await is_owner_target(db, target_empire):
        return {"action": "josus_yuborish", "status": "blocked_owner_immunity"}

    params = {"target": target_empire}
    await log_npc_action(db, ruler_id, "josus_yuborish", target_empire, params)
    return {"action": "josus_yuborish", "status": "spy_dispatched", **params}

async def execute_mish_mish_tarqatish(
    db, ruler_id: str, subject: str, text_key: str, is_true: int = 1
) -> Dict[str, Any]:
    """Tavernalar orqali mish-mish tarqatish"""
    await db.execute("""
    INSERT INTO rumors (source_ruler, subject, text_key, is_true, spread, expires_at)
    VALUES (?, ?, ?, ?, 2, datetime('now', '+24 hours'));
    """, (ruler_id, subject, text_key, is_true))

    params = {"subject": subject, "text": text_key, "is_true": is_true}
    await log_npc_action(db, ruler_id, "mish_mish_tarqatish", subject, params)
    return {"action": "mish_mish_tarqatish", "status": "rumor_spread", **params}

async def execute_sabotaj(db, ruler_id: str, target: Any) -> Dict[str, Any]:
    """Dushman infratuzilmasini sabotaj qilish"""
    if await is_owner_target(db, target):
        return {"action": "sabotaj", "status": "blocked_owner_immunity"}

    params = {"target": str(target)}
    await log_npc_action(db, ruler_id, "sabotaj", target, params)
    return {"action": "sabotaj", "status": "sabotaged", **params}

async def execute_pora_berish(db, ruler_id: str, target: Any, amount: int = 1000) -> Dict[str, Any]:
    """Dushman amaldoriga pora berish"""
    if await is_owner_target(db, target):
        return {"action": "pora_berish", "status": "blocked_owner_immunity"}

    await db.execute("UPDATE npc_rulers SET treasury = MAX(0, treasury - ?) WHERE empire_id = ?;", (amount, ruler_id))
    params = {"target": str(target), "bribe_amount": amount}
    await log_npc_action(db, ruler_id, "pora_berish", target, params)
    return {"action": "pora_berish", "status": "bribe_sent", **params}
