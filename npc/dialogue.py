import os
import json
import random
import logging
from typing import Dict, Any, Optional, List

# =====================================================================
# VALORIYA: DIALOG DVIGATELI (DIALOGUE ENGINE) (FAZA 5)
# =====================================================================
# Xabar = Ochilish + Mazmun + Persona bo'yog'i + Yopilish
# Ton: iliq / neytral / dushmanona (anger > 60 yoki trust < -30 -> dushmanona)
# Anti-takror: Har bir juftlik uchun oxirgi 5 satr takrorlanmaydi.
# Lazy loading: JSON fayllar faqat so'ralganda xotiraga yuklanadi.
# =====================================================================

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "dialogue")

RULER_TO_FILE: Dict[str, str] = {
    "lionguard": "valter",
    "valter": "valter",
    "frost_peak": "ragnar",
    "ragnar": "ragnar",
    "ursus_peak": "boris",
    "boris": "boris",
    "iron_bastion": "torin",
    "torin": "torin",
    "azure_lily": "izabella",
    "izabella": "izabella",
    "crimson_sultanate": "sulaymon",
    "sulaymon": "sulaymon",
    "iron_steppe": "botirxon",
    "botirxon": "botirxon",
    "shadowfang": "moros",
    "moros": "moros",
    "blood_tide": "qora_soqol",
    "qora_soqol": "qora_soqol",
    "ash_necropolis": "malakor",
    "malakor": "malakor",
    "dawn_citadel": "avreliy",
    "avreliy": "avreliy",
    "silver_glade": "elenor",
    "elenor": "elenor",
}

# Xotirada lazy kesh
_DIALOGUE_CACHE: Dict[str, Dict[str, Any]] = {}

# Oxirgi 5 satr takrorlanmasligi uchun kesh: key -> list of last 5 lines
_RECENT_HISTORY: Dict[str, List[str]] = {}

def get_dialogue_data(ruler_key: str) -> Dict[str, Any]:
    """
    Hukmdorning dialog JSON ma'lumotlarini lazy yuklaydi.
    """
    file_stem = RULER_TO_FILE.get(ruler_key.lower(), ruler_key.lower())
    if file_stem in _DIALOGUE_CACHE:
        return _DIALOGUE_CACHE[file_stem]

    file_path = os.path.join(DATA_DIR, f"{file_stem}.json")
    if not os.path.exists(file_path):
        logging.warning(f"Dialog fayli topilmadi: {file_path}, standart valter.json yuklanadi.")
        file_path = os.path.join(DATA_DIR, "valter.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _DIALOGUE_CACHE[file_stem] = data
    return data

def resolve_dialogue_tone(
    mood_state: Optional[Dict[str, Any]] = None,
    relation: Optional[Dict[str, Any]] = None
) -> str:
    """
    Hukmdorning ichki hissiyoti va o'yinchi bilan munosabatiga qarab tonni aniqlaydi:
    - anger > 60 yoki trust < -30 -> dushmanona
    - joy > 60 va trust > 20 -> iliq
    - aks holda -> neytral
    """
    anger = 0
    joy = 50
    trust = 0

    if mood_state:
        anger = mood_state.get("anger_current", 0)
        joy = mood_state.get("joy", 50)
    if relation:
        trust = relation.get("trust", 0)

    if anger > 60 or trust < -30:
        return "dushmanona"
    elif joy > 60 and trust > 20:
        return "iliq"
    return "neytral"

def _safe_format(template: str, slots: Dict[str, Any]) -> str:
    """Slotlarni ({player}, {gold}, {empire}, {item}, {days}) xavfsiz to'ldiradi."""
    default_slots = {
        "player": "Ritsar",
        "gold": "100",
        "empire": "Valoriya",
        "item": "qilich",
        "days": "3"
    }
    merged = {**default_slots, **slots}
    res = template
    for k, v in merged.items():
        res = res.replace(f"{{{k}}}", str(v))
    return res

def _pick_non_repeating(
    pool: List[str], history_key: str, rng: Optional[random.Random] = None
) -> str:
    """
    Variantlar ro'yxatidan oxirgi 5 marta ishlatilmaganini tanlaydi.
    """
    if not pool:
        return ""

    history = _RECENT_HISTORY.setdefault(history_key, [])
    candidates = [p for p in pool if p not in history]
    if not candidates:
        # Agar hamma variant ishlatilgan bo'lsa, tarixdan eng eskisini bo'shatamiz
        candidates = pool

    picker = rng if rng is not None else random
    chosen = picker.choice(candidates)

    history.append(chosen)
    if len(history) > 5:
        history.pop(0)

    return chosen

def build_dialogue_message(
    ruler_key: str,
    intent: str,
    ton: Optional[str] = None,
    mood_state: Optional[Dict[str, Any]] = None,
    relation: Optional[Dict[str, Any]] = None,
    slots: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None
) -> str:
    """
    4 qismli xabar generatori:
    Xabar = Ochilish + Mazmun + Persona bo'yog'i + Yopilish
    """
    rng = random.Random(seed) if seed is not None else None
    data = get_dialogue_data(ruler_key)
    safe_slots = dict(slots or {})
    if "empire" not in safe_slots:
        safe_slots["empire"] = data.get("empire", "Valoriya")

    selected_tone = ton if ton in ["iliq", "neytral", "dushmanona"] else resolve_dialogue_tone(mood_state, relation)

    # 1. Ochilish (Opening)
    openings_pool = data.get("openings", {}).get(selected_tone, ["Salom, {player}."])
    opening_tmpl = _pick_non_repeating(openings_pool, f"{ruler_key}:opening:{selected_tone}", rng)

    # 2. Mazmun (Core Intent)
    intents_dict = data.get("intents", {})
    intent_pool = intents_dict.get(intent, {}).get(selected_tone, ["Sizni eshitmoqdaman, {player}."])
    intent_tmpl = _pick_non_repeating(intent_pool, f"{ruler_key}:intent:{intent}:{selected_tone}", rng)

    # 3. Persona bo'yog'i (Flavor)
    flavor_pool = data.get("flavor", {}).get(selected_tone, [""])
    flavor_tmpl = _pick_non_repeating(flavor_pool, f"{ruler_key}:flavor:{selected_tone}", rng)

    # 4. Yopilish (Closing)
    closings_pool = data.get("closings", {}).get(selected_tone, ["Omon bo'ling."])
    closing_tmpl = _pick_non_repeating(closings_pool, f"{ruler_key}:closing:{selected_tone}", rng)

    # Qismlarni birlashtirish
    parts = [p for p in [opening_tmpl, intent_tmpl, flavor_tmpl, closing_tmpl] if p]
    full_template = " ".join(parts)

    formatted = _safe_format(full_template, safe_slots)

    # Xabarning umumiy takrorlanmasligi uchun global tarixga yozish
    global_key = f"{ruler_key}:{intent}"
    g_hist = _RECENT_HISTORY.setdefault(global_key, [])
    g_hist.append(formatted)
    if len(g_hist) > 5:
        g_hist.pop(0)

    return formatted

def count_dialogue_templates(ruler_key: str) -> int:
    """Hukmdorning dialog faylidagi jami shablonlar sonini hisoblaydi."""
    data = get_dialogue_data(ruler_key)
    count = 0
    for cat in ["openings", "closings", "flavor"]:
        for t in ["iliq", "neytral", "dushmanona"]:
            count += len(data.get(cat, {}).get(t, []))
    for int_k, int_v in data.get("intents", {}).items():
        for t in ["iliq", "neytral", "dushmanona"]:
            count += len(int_v.get(t, []))
    return count

async def get_ruler_dialogue_from_db(
    db,
    ruler_id: str,
    intent: str,
    character_id: Optional[int] = None,
    slots: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None
) -> str:
    """
    Baza holatini hisobga olgan holda hukmdorning jonli dialogini yaratadi.
    """
    async with db.execute("SELECT joy, anger_current FROM npc_rulers WHERE empire_id = ?;", (ruler_id,)) as cur:
        r_mood = await cur.fetchone()
    mood_state = {"joy": r_mood[0], "anger_current": r_mood[1]} if r_mood else None

    relation = None
    if character_id:
        async with db.execute("SELECT trust, suspicion, respect, grudge FROM npc_relations WHERE ruler_id = ? AND character_id = ?;", (ruler_id, character_id)) as cur:
            r_rel = await cur.fetchone()
            if r_rel:
                relation = {"trust": r_rel[0], "suspicion": r_rel[1], "respect": r_rel[2], "grudge": r_rel[3]}

    return build_dialogue_message(
        ruler_key=ruler_id,
        intent=intent,
        mood_state=mood_state,
        relation=relation,
        slots=slots,
        seed=seed
    )
