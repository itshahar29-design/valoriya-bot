import math
import random
from typing import Dict, Any, Optional, List
from npc.actions.economy import ECONOMY_COOLDOWNS

# =====================================================================
# VALORIYA: QAROR DVIGATELI (UTILITY AI & SOFTMAX SELECTION) (FAZA 3)
# =====================================================================
# Har bir hukmdor xislatlari, ichki hissiyotlari va joriy vaziyatga qarab
# harakatlarni baholaydi (Score). Eng yaxshi 3 tasidan Softmax (T=0.3)
# orqali eng optimal harakat(lar)ni tanlaydi.
# Harakatlar cooldown'da bo'lsa, tanlovdan chetlashtiriladi.
# Determinik testlar uchun 'seed' parametri qo'llab-quvvatlanadi.
# =====================================================================

ALL_COOLDOWNS = dict(ECONOMY_COOLDOWNS)

async def is_action_on_cooldown(
    db, ruler_id: str, action: str, custom_cooldown: Optional[int] = None
) -> bool:
    """
    Harakatning joriy cooldown'da ekanligini npc_actions_log jadvalidan tekshiradi.
    """
    cd_seconds = custom_cooldown if custom_cooldown is not None else ALL_COOLDOWNS.get(action, 0)
    if cd_seconds <= 0:
        return False

    async with db.execute("""
    SELECT (strftime('%s', 'now') - strftime('%s', created_at))
    FROM npc_actions_log
    WHERE ruler_id = ? AND action = ?
    ORDER BY id DESC LIMIT 1;
    """, (ruler_id, action)) as cur:
        row = await cur.fetchone()

    if row and row[0] is not None:
        elapsed = row[0]
        if elapsed < cd_seconds:
            return True
    return False

def score_action(
    ruler_data: Dict[str, Any],
    action: str,
    context: Optional[Dict[str, Any]] = None,
    rng: Optional[random.Random] = None
) -> float:
    """
    Harakatning foydalilik ballini (Utility Score) hisoblaydi:
    Score = Σ(w_i × c_i) × persona_w + kontekst + rnd(0..0.1)
    """
    greed = ruler_data.get("greed", 50) / 100.0
    pride = ruler_data.get("pride", 50) / 100.0
    anger = ruler_data.get("anger", 50) / 100.0
    cunning = ruler_data.get("cunning", 50) / 100.0
    loyalty = ruler_data.get("loyalty", 50) / 100.0
    caution = ruler_data.get("caution", 50) / 100.0
    piety = ruler_data.get("piety", 50) / 100.0
    ambition = ruler_data.get("ambition", 50) / 100.0

    treasury = ruler_data.get("treasury", 20000)
    target_treasury = 40000.0
    need = max(0.0, min(1.0, 1.0 - (treasury / target_treasury)))
    gd = greed * (0.4 + 0.6 * need)
    if treasury >= 1.2 * target_treasury:
        gd *= 0.5

    base_score = 0.5

    if action == "soliq_oshirish":
        base_score = greed * 1.5 + need * 1.2
        if treasury < 0.5 * target_treasury:
            base_score += 1.0
    elif action == "xiroj_talab":
        base_score = greed * 1.3 + pride * 0.7
        if gd > 0.6:
            base_score += 1.0
    elif action == "pora_qabul":
        base_score = greed * 1.1 + cunning * 0.6 - loyalty * 0.4
    elif action == "narx_shishirish":
        base_score = greed * 0.9 + cunning * 0.8
    elif action == "zahira_yigish":
        base_score = greed * 0.8 + caution * 0.9
    elif action == "qarz_berish":
        base_score = greed * 1.0 + cunning * 0.7
    elif action == "qarz_undirish":
        base_score = greed * 1.1 + anger * 0.8
    elif action == "asir_narxi":
        base_score = greed * 1.0 + pride * 0.6
    elif action == "ikki_tomonlama_savdo":
        base_score = greed * 1.2 + cunning * 1.0 - loyalty * 0.8
    elif action == "karvon_tolli":
        base_score = greed * 0.9 + caution * 0.4
    elif action == "auksion_snayper":
        base_score = greed * 1.0 + ambition * 0.7
    elif action == "xazina_sarfi":
        if treasury >= 1.2 * target_treasury:
            base_score = ambition * 1.5 + pride * 1.0 + 1.5
        else:
            base_score = 0.05
    else:
        base_score = 0.5

    # Kontekst bonusi
    if context and context.get("preferred_action") == action:
        base_score += 0.8

    # Random shovqin (0..0.1)
    jitter = rng.uniform(0.0, 0.1) if rng else random.uniform(0.0, 0.1)
    return round(base_score + jitter, 4)

def softmax_select(
    candidates: List[Dict[str, Any]],
    temperature: float = 0.3,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> Optional[Dict[str, Any]]:
    """
    Nomzodlar orasidan eng yaxshi 3 tasini tanlab,
    Softmax (T=0.3) ehtimollik taqsimoti bo'yicha bittasini tanlaydi.
    """
    if not candidates:
        return None

    sorted_candidates = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
    top_3 = sorted_candidates[:3]

    if len(top_3) == 1:
        return top_3[0]

    picker = rng if rng is not None else (random.Random(seed) if seed is not None else random.Random())

    scores = [c.get("score", 0.0) for c in top_3]
    max_score = max(scores)
    t = max(0.01, temperature)
    exp_scores = [math.exp((s - max_score) / t) for s in scores]
    sum_exp = sum(exp_scores)
    probs = [e / sum_exp for e in exp_scores]

    chosen = picker.choices(top_3, weights=probs, k=1)[0]
    return chosen

async def decide_ruler_action(
    db,
    ruler_id: str,
    context: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None,
    max_actions: int = 1
) -> List[Dict[str, Any]]:
    """
    Hukmdor uchun navbatdagi harakat(lar)ni Utility AI va Softmax orqali tanlaydi.
    Cooldown'dagi harakatlar tanlovga kiritilmaydi.
    """
    async with db.execute("""
    SELECT empire_id, ruler_name, persona, greed, pride, anger, cunning,
           loyalty, caution, piety, ambition, joy, anger_current, fear,
           boredom, unrest, treasury, army
    FROM npc_rulers WHERE empire_id = ?;
    """, (ruler_id,)) as cur:
        row = await cur.fetchone()
        if not row:
            return []
        cols = [d[0] for d in cur.description]
        ruler_data = dict(zip(cols, row))

    rng = random.Random(seed) if seed is not None else None

    # Nomzod harakatlarni tekshirish va cooldown'dagilarni filtrlash
    candidates = []
    for action_name in ECONOMY_COOLDOWNS.keys():
        on_cd = await is_action_on_cooldown(db, ruler_id, action_name)
        if not on_cd:
            score = score_action(ruler_data, action_name, context, rng)
            candidates.append({"action": action_name, "score": score, "ruler_id": ruler_id})

    if not candidates:
        return []

    chosen_actions: List[Dict[str, Any]] = []
    pool = list(candidates)

    for _ in range(min(max_actions, len(pool))):
        chosen = softmax_select(pool, temperature=0.3, rng=rng)
        if chosen:
            chosen_actions.append(chosen)
            pool = [c for c in pool if c["action"] != chosen["action"]]
            if not pool:
                break

    return chosen_actions
