import json
import datetime
from typing import Dict, Any, Optional, List
from npc.state import clamp, update_ruler_mood
from npc.personality import get_ruler_profile

# =====================================================================
# VALORIYA: NPC XOTIRA VA MUNOSABATLAR TIZIMI (MEMORY ENGINE)
# =====================================================================
# Hukmdor o'yinchi bilan o'tgan voqealarni eslab qoladi.
# Xotira hajmi: har juftlik (ruler_id, character_id) uchun ko'pi bilan 50 yozuv.
# Xushomad samaradorligi kun davomida kamayib boradi (0.6^n).
# =====================================================================

EVENT_IMPACTS = {
    "big_gift": {"trust": 5, "anger": -5, "grudge": 0},
    "small_gift": {"trust": 1, "anger": 0, "grudge": 0},
    "flattery": {"trust": 3, "anger": 0, "grudge": 0},
    "insult": {"trust": -10, "anger": 20, "grudge": 5},
    "break_treaty": {"trust": -30, "anger": 15, "grudge": 20},
    "raid_caravan": {"trust": -20, "anger": 25, "grudge": 15},
    "war_help": {"trust": 15, "anger": -10, "grudge": -10},
    "bribe_accepted": {"trust": -2, "anger": 0, "grudge": 0}
}

MAX_MEMORY_PER_PAIR = 50

async def get_player_relation(db, ruler_id: str, character_id: int) -> Dict[str, int]:
    """Hukmdor va o'yinchi o'rtasidagi munosabatlarni qaytaradi."""
    async with db.execute("""
    SELECT trust, suspicion, respect, grudge
    FROM npc_relations
    WHERE ruler_id = ? AND character_id = ?;
    """, (ruler_id, character_id)) as cur:
        row = await cur.fetchone()
        if not row:
            return {"trust": 0, "suspicion": 0, "respect": 0, "grudge": 0}
        return {"trust": row[0], "suspicion": row[1], "respect": row[2], "grudge": row[3]}

async def get_today_flattery_count(db, ruler_id: str, character_id: int) -> int:
    """Bugun o'yinchi ushbu hukmdorga necha marta xushomad qilganini hisoblaydi."""
    today_str = datetime.date.today().isoformat()
    async with db.execute("""
    SELECT count(*) FROM npc_memory
    WHERE ruler_id = ? AND character_id = ? AND event_type = 'flattery'
      AND date(created_at) = date('now');
    """, (ruler_id, character_id)) as cur:
        row = await cur.fetchone()
        return row[0] if row else 0

async def record_memory_event(
    db, ruler_id: str, character_id: int, event_type: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Yangi xotira voqeasini qayd etadi, personaning ko'paytiruvchilarini qo'llaydi,
    munosabatlarni (npc_relations) va hukmdor kayfiyatini yangilaydi.
    """
    if details is None:
        details = {}

    base_impact = EVENT_IMPACTS.get(event_type, {"trust": 0, "anger": 0, "grudge": 0})
    d_trust = float(base_impact["trust"])
    d_anger = float(base_impact["anger"])
    d_grudge = float(base_impact["grudge"])
    d_suspicion = 0

    profile = get_ruler_profile(ruler_id) or {"traits": {}}
    traits = profile.get("traits", {})
    greed = traits.get("greed", 50)
    pride = traits.get("pride", 50)
    cunning = traits.get("cunning", 50)

    # 1. Persona va hodisa modifikatorlari
    if event_type in ["big_gift", "small_gift"]:
        d_trust *= (1.0 + greed / 100.0)
    elif event_type == "insult":
        d_anger *= (1.0 + pride / 100.0)
    elif event_type == "flattery":
        n = await get_today_flattery_count(db, ruler_id, character_id)
        flattery_mult = (0.6 ** n)
        cunning_mod = max(0.1, 1.0 - cunning / 150.0)
        d_trust = d_trust * flattery_mult * cunning_mod
        # Har 3-xushomaddan keyin shubha +5 oshadi
        if (n + 1) % 3 == 0:
            d_suspicion += 5

    int_trust = int(round(d_trust))
    int_anger = int(round(d_anger))
    int_grudge = int(round(d_grudge))

    # 2. Xotira jadvaliga yozish
    await db.execute("""
    INSERT INTO npc_memory (ruler_id, character_id, event_type, trust_d, anger_d, grudge_d, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (ruler_id, character_id, event_type, int_trust, int_anger, int_grudge, json.dumps(details)))

    # 3. Munosabatlarni (npc_relations) yangilash
    rel = await get_player_relation(db, ruler_id, character_id)
    new_trust = clamp(rel["trust"] + int_trust, -100, 100)
    new_suspicion = clamp(rel["suspicion"] + d_suspicion, 0, 100)
    new_grudge = clamp(rel["grudge"] + int_grudge, 0, 100)

    await db.execute("""
    INSERT INTO npc_relations (ruler_id, character_id, trust, suspicion, respect, grudge, last_seen)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(ruler_id, character_id) DO UPDATE SET
        trust = excluded.trust,
        suspicion = excluded.suspicion,
        grudge = excluded.grudge,
        last_seen = CURRENT_TIMESTAMP;
    """, (ruler_id, character_id, new_trust, new_suspicion, rel["respect"], new_grudge))

    # 4. Hukmdor kayfiyatiga (state) ta'siri
    await update_ruler_mood(db, ruler_id, d_joy=(int_trust if int_trust > 0 else 0), d_anger=int_anger)

    # 5. Xotira hajmini tekshirish va siqish (<= 50 ta yozuv)
    await compress_memory_if_needed(db, ruler_id, character_id)

    return {
        "event_type": event_type,
        "delta_trust": int_trust,
        "delta_anger": int_anger,
        "delta_grudge": int_grudge,
        "new_trust": new_trust,
        "new_suspicion": new_suspicion
    }

async def compress_memory_if_needed(db, ruler_id: str, character_id: int, max_records: int = MAX_MEMORY_PER_PAIR):
    """
    Agar xotira yozuvlari 50 tadan oshsa, eskilari siqiladi (eng yangi 50 tasi saqlanadi).
    """
    async with db.execute("""
    SELECT count(*) FROM npc_memory
    WHERE ruler_id = ? AND character_id = ?;
    """, (ruler_id, character_id)) as cur:
        total_count = (await cur.fetchone())[0]

    if total_count > max_records:
        excess = total_count - max_records
        await db.execute("""
        DELETE FROM npc_memory
        WHERE id IN (
            SELECT id FROM npc_memory
            WHERE ruler_id = ? AND character_id = ?
            ORDER BY created_at ASC, id ASC
            LIMIT ?
        );
        """, (ruler_id, character_id, excess))
