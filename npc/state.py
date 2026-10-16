from typing import Dict, Any, Optional, List
import logging

# =====================================================================
# VALORIYA: NPC HUKMDOR HISSIYOTLARI VA DECAY (STATE ENGINE)
# =====================================================================
# Hukmdorning ichki hissiyotlari dinamik o'zgaradi va har tickda
# o'zining tabiiy tinch holatiga (baseline) qaytishga intiladi (decay).
# Formula: x <- x + (baza - x) * 0.10
# =====================================================================

BASELINES: Dict[str, int] = {
    "joy": 50,           # Quvonch (baza: 50 - betaraf me'yor)
    "anger_current": 0,  # Hozirgi g'azab (baza: 0 - sokinlik)
    "fear": 0,           # Qo'rquv (baza: 0)
    "boredom": 0,        # Zerikish (baza: 0)
    "unrest": 0          # Norozilik / Isyon xavfi (baza: 0)
}

def clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    """Qiymatni [low, high] oralig'ida ushlab turadi."""
    return max(low, min(high, int(round(value))))

async def get_ruler_state(db, empire_id: str) -> Optional[Dict[str, Any]]:
    """Hukmdorning joriy hissiy holatini qaytaradi."""
    async with db.execute("""
    SELECT empire_id, ruler_name, persona, greed, pride, anger, cunning,
           loyalty, caution, piety, ambition, joy, anger_current, fear,
           boredom, unrest, treasury, army, last_tick_at
    FROM npc_rulers WHERE empire_id = ?;
    """, (empire_id,)) as cur:
        row = await cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

async def update_ruler_mood(
    db, empire_id: str,
    d_joy: int = 0, d_anger: int = 0, d_fear: int = 0,
    d_boredom: int = 0, d_unrest: int = 0
) -> Dict[str, int]:
    """Hukmdorning hissiyotlariga o'zgarishlar kiritadi va yangi qiymatlarni qaytaradi."""
    cur_state = await get_ruler_state(db, empire_id)
    if not cur_state:
        return {}

    new_joy = clamp(cur_state["joy"] + d_joy, 0, 100)
    new_anger = clamp(cur_state["anger_current"] + d_anger, 0, 100)
    new_fear = clamp(cur_state["fear"] + d_fear, 0, 100)
    new_boredom = clamp(cur_state["boredom"] + d_boredom, 0, 100)
    new_unrest = clamp(cur_state["unrest"] + d_unrest, 0, 100)

    await db.execute("""
    UPDATE npc_rulers SET
        joy = ?, anger_current = ?, fear = ?, boredom = ?, unrest = ?
    WHERE empire_id = ?;
    """, (new_joy, new_anger, new_fear, new_boredom, new_unrest, empire_id))

    return {
        "joy": new_joy, "anger_current": new_anger, "fear": new_fear,
        "boredom": new_boredom, "unrest": new_unrest
    }

async def apply_mood_decay(db, empire_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Decay formulasi: x <- x + (baza - x) * 0.10
    Har bir tickda hukmdorlarning vaqtinchalik hissiyotlarini bazaviy darajaga qaytaradi.
    """
    query = "SELECT empire_id, joy, anger_current, fear, boredom, unrest FROM npc_rulers"
    params = ()
    if empire_id:
        query += " WHERE empire_id = ?"
        params = (empire_id,)

    results = []
    async with db.execute(query, params) as cur:
        rows = await cur.fetchall()

    for row in rows:
        e_id, cur_joy, cur_anger, cur_fear, cur_boredom, cur_unrest = row

        # Decay hisobi
        new_joy = clamp(cur_joy + (BASELINES["joy"] - cur_joy) * 0.10)
        new_anger = clamp(cur_anger + (BASELINES["anger_current"] - cur_anger) * 0.10)
        new_fear = clamp(cur_fear + (BASELINES["fear"] - cur_fear) * 0.10)
        new_boredom = clamp(cur_boredom + (BASELINES["boredom"] - cur_boredom) * 0.10)
        new_unrest = clamp(cur_unrest + (BASELINES["unrest"] - cur_unrest) * 0.10)

        await db.execute("""
        UPDATE npc_rulers SET
            joy = ?, anger_current = ?, fear = ?, boredom = ?, unrest = ?,
            last_tick_at = CURRENT_TIMESTAMP
        WHERE empire_id = ?;
        """, (new_joy, new_anger, new_fear, new_boredom, new_unrest, e_id))

        results.append({
            "empire_id": e_id,
            "joy": new_joy,
            "anger_current": new_anger,
            "fear": new_fear,
            "boredom": new_boredom,
            "unrest": new_unrest
        })

    return results
