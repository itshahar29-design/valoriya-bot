# =====================================================================
# VALORIYA: TAVERNA MINI-O'YINLARI VA QIMORXONASI (RETENTION LOOPS)
# =====================================================================
# 1. Omad G'ildiragi (Lucky Wheel) — Har 8 soatda 1 ta BEPUL aylantirish!
# 2. Suyak Tashlash (Dice Duel / Barbut) — Tezkor stavkali duel.
# 3. Qirollik 21 O'yini (Blackjack) — Taverna qarta stoli.
# =====================================================================

import random
import time
from typing import Dict, Any, Tuple

WHEEL_SLOTS = [
    {"id": "w_gold_small", "name": "🪙 250 Oltin", "type": "gold", "amount": 250, "weight": 30},
    {"id": "w_gold_med", "name": "🪙 600 Oltin", "type": "gold", "amount": 600, "weight": 20},
    {"id": "w_gems_small", "name": "💎 3 Javohir", "type": "gems", "amount": 3, "weight": 15},
    {"id": "w_potions", "name": "🧪 2x G'azab Eliksiri", "type": "potion", "amount": 2, "weight": 14},
    {"id": "w_rune", "name": "⚡️ Oliy Olov Runasi", "type": "rune", "amount": 1, "weight": 10},
    {"id": "w_pet_egg", "name": "🥚 Sirli Hamroh Tuxumi", "type": "egg", "amount": 1, "weight": 5},
    {"id": "w_procedural_gear", "name": "🗡 Afsonaviy Protsessual Qurol", "type": "gear", "amount": 1, "weight": 4},
    {"id": "w_jackpot", "name": "👑 JACKPOT: 10,000 🪙 + 50 💎", "type": "jackpot", "gold": 10000, "gems": 50, "weight": 2}
]

WHEEL_COOLDOWN_SECONDS = 8 * 3600  # 8 hours

def spin_wheel() -> Dict[str, Any]:
    """Omad g'ildiragini tasodifiy aylantiradi."""
    weights = [slot["weight"] for slot in WHEEL_SLOTS]
    chosen = random.choices(WHEEL_SLOTS, weights=weights, k=1)[0]
    return chosen

def play_dice_duel(bet_gold: int) -> Dict[str, Any]:
    """
    Suyak tashlash o'yini (Barbut):
    O'yinchi 2 ta suyak tashlaydi (2-12).
    Mayxonachi 2 ta suyak tashlaydi (2-12).
    """
    d1_p = random.randint(1, 6)
    d2_p = random.randint(1, 6)
    player_score = d1_p + d2_p

    d1_d = random.randint(1, 6)
    d2_d = random.randint(1, 6)
    dealer_score = d1_d + d2_d

    if player_score > dealer_score:
        win_gold = int(bet_gold * 1.9)
        result = "win"
        msg = f"🎉 *G'ALABA!* Siz: 🎲 {player_score} ({d1_p}+{d2_p}) | Mayxonachi: 🎲 {dealer_score} ({d1_d}+{d2_d}). Yutuq: +{win_gold:,} 🪙!"
    elif player_score < dealer_score:
        win_gold = 0
        result = "loss"
        msg = f"😢 *MAG'LUBIYAT!* Siz: 🎲 {player_score} ({d1_p}+{d2_p}) | Mayxonachi: 🎲 {dealer_score} ({d1_d}+{d2_d}). Siz {bet_gold:,} 🪙 yo'qotdingiz."
    else:
        win_gold = bet_gold
        result = "tie"
        msg = f"🤝 *DURRANG!* Har ikki tomon 🎲 {player_score} tashladi. Tikilgan {bet_gold:,} 🪙 qaytarildi."

    return {
        "result": result,
        "player_score": player_score,
        "dealer_score": dealer_score,
        "win_gold": win_gold,
        "msg": msg
    }
