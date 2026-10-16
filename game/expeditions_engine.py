# =====================================================================
# VALORIYA: OFLAYN EKSPEDITSIYALAR DASTURI (AFK IDLE RETENTION)
# =====================================================================
# O'yinchi yo'qligida ham qahramon va uning hamrohi sarguzashtga chiqadi.
# 5 ta hudud: 2 soat, 4 soat, 8 soat, 12 soat va 24 soatlik safarlar.
# O'yinchini botga qayta-qayta kirishini kafolatlovchi eng kuchli retention loop!
# =====================================================================

import random
import time
from typing import Dict, Any, List, Optional
from game.procedural_loot import generate_procedural_loot

EXPEDITION_REGIONS = {
    "exp_dark_forest": {
        "name_uz": "🌲 Tumanli Qorong'u O'rmon",
        "duration_hours": 2,
        "duration_seconds": 2 * 3600,
        "gold_reward": (200, 450),
        "xp_reward": 80,
        "pet_exp": 60,
        "desc": "O'rmon yirtqichlari va dorivor o'tlar hududi. Tezkor o'ljalar uchun mos."
    },
    "exp_crystal_mines": {
        "name_uz": "⛏ Kristalli Qadimiy Shaxtalar",
        "duration_hours": 4,
        "duration_seconds": 4 * 3600,
        "gold_reward": (500, 1100),
        "xp_reward": 180,
        "pet_exp": 140,
        "desc": "Yer osti rudalari va kristallar makoni. Mo'l oltin va temir beradi."
    },
    "exp_crypt_ruins": {
        "name_uz": "🪦 La'natlangan Qabr Qoldiqlari",
        "duration_hours": 8,
        "duration_seconds": 8 * 3600,
        "gold_reward": (1200, 2500),
        "xp_reward": 400,
        "pet_exp": 320,
        "desc": "Kechasi uxlashdan oldin jo'natish uchun eng a'lo tanlov (8 soatlik qidiruv)."
    },
    "exp_dragon_peaks": {
        "name_uz": "🌋 Ajdarho Cho'qqilari",
        "duration_hours": 12,
        "duration_seconds": 12 * 3600,
        "gold_reward": (2500, 4800),
        "xp_reward": 800,
        "pet_exp": 650,
        "desc": "Qizigan qoyalar va magma yoriqlari. Nodir va epik o'ljalar ehtimoli yuqori."
    },
    "exp_abyssal_rift": {
        "name_uz": "🌌 Tubsizlik Qora Yorig'i",
        "duration_hours": 24,
        "duration_seconds": 24 * 3600,
        "gold_reward": (6000, 12000),
        "xp_reward": 2000,
        "pet_exp": 1800,
        "desc": "24 soatlik ulkan safar! Afsonaviy protsessual qurol va javohirlar kafolatlangan."
    }
}

def calculate_expedition_rewards(region_key: str, companion_mult: float = 1.0) -> Dict[str, Any]:
    """Ekspeditsiya yakunlangandagi tushumlarni hisoblaydi."""
    reg = EXPEDITION_REGIONS.get(region_key, EXPEDITION_REGIONS["exp_dark_forest"])
    raw_gold = random.randint(reg["gold_reward"][0], reg["gold_reward"][1])
    final_gold = int(raw_gold * companion_mult)
    final_xp = int(reg["xp_reward"] * companion_mult)
    final_pet_exp = int(reg["pet_exp"] * companion_mult)

    # Shans bo'yicha protsessual qurol
    gear_drop = None
    if random.random() < (0.25 * reg["duration_hours"]):
        gear_drop = generate_procedural_loot(player_level=reg["duration_hours"] * 3)

    return {
        "gold": final_gold,
        "xp": final_xp,
        "pet_exp": final_pet_exp,
        "gear_drop": gear_drop,
        "region_name": reg["name_uz"]
    }
