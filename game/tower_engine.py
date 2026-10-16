# =====================================================================
# VALORIYA: CHEKSIZ TUBSIZLIK MINORASI (ABYSSAL TOWER - 100 FLOORS)
# =====================================================================
# 100 qavatli vertikal sinov minorasi.
# Har 10-qavatda epik boss va ulkan xazina sandig'i kutadi.
# Minora reytingi har hafta yangilanib, eng zo'r 3 ta ritsarga unvonlar beradi.
# =====================================================================

from typing import Dict, Any, List, Optional
from game.procedural_loot import generate_procedural_loot

TOWER_MILESTONES = {
    10: {"name": "🗿 10-Qavat: Granit Qo'riqchi", "reward_gold": 2500, "reward_gems": 15, "title": "Minoraning Birinchi Qahramoni"},
    20: {"name": "🩸 20-Qavat: Qonli Berserk Boss", "reward_gold": 5000, "reward_gems": 30, "title": "Qon Zallarini Yenguvchi"},
    30: {"name": "🐍 30-Qavat: Zaharli Gidra Malikasi", "reward_gold": 8000, "reward_gems": 50, "title": "Zahar Yutuvchi"},
    40: {"name": "🔥 40-Qavat: Magma Titan Lordi", "reward_gold": 12000, "reward_gems": 75, "title": "Olov Fotihi"},
    50: {"name": "❄️ 50-Qavat: Muz Qiroli Arktas", "reward_gold": 18000, "reward_gems": 100, "title": "Muzlik Hukmdori"},
    60: {"name": "👤 60-Qavat: Soya Qora Klani Boshlig'i", "reward_gold": 25000, "reward_gems": 150, "title": "Zulmat Qotili"},
    70: {"name": "🌀 70-Qavat: Xaos Singulyarligi", "reward_gold": 35000, "reward_gems": 200, "title": "Fazo Buzuvchisi"},
    80: {"name": "🐉 80-Qavat: Oltin Ajdaho Beliar", "reward_gold": 50000, "reward_gems": 300, "title": "Ajdaholar Xojasi"},
    90: {"name": "💀 90-Qavat: O'lim O'rog'i Azrail", "reward_gold": 75000, "reward_gems": 500, "title": "O'limni Yenggan Ritsar"},
    100: {"name": "👑 100-Qavat: Tubsizlik Oliy Monarxi", "reward_gold": 150000, "reward_gems": 1000, "title": "Valoriya Oliy Afsonasi"}
}

def generate_tower_floor(floor: int) -> Dict[str, Any]:
    """100 qavatli minora dushmanini va parametrlarini generatsiya qiladi."""
    base_hp = 100 + (floor * 35) + (floor ** 2 // 3)
    base_atk = 18 + int(floor * 4.2)
    base_def = 5 + int(floor * 2.1)

    is_boss = (floor % 10 == 0)
    if is_boss:
        base_hp = int(base_hp * 2.2)
        base_atk = int(base_atk * 1.5)
        name = TOWER_MILESTONES[floor]["name"]
    else:
        name = f"⚔️ {floor}-Qavat Qo'riqchisi (Minorachi Askari)"

    return {
        "floor": floor,
        "name": name,
        "hp": base_hp,
        "max_hp": base_hp,
        "atk": base_atk,
        "def": base_def,
        "is_boss": is_boss,
        "gold_reward": 50 * floor if not is_boss else TOWER_MILESTONES[floor]["reward_gold"],
        "xp_reward": 40 * floor
    }
