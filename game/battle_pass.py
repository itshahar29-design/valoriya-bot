# =====================================================================
# VALORIYA: MAVSUMIY JANG CHIPTASI (BATTLE PASS - 50 TIERS)
# =====================================================================
# 1-Mavsum: "Valoriya Zulmati Uyg'onishi" (Season 1: Awakening of Darkness)
# 50 ta darajali bepul (Free) va Qirollik (Royal Pass) mukofotlar yo'lagi.
# Har kuni yangilanuvchi mavsumiy vazifalar va unikal kosmetik/jangovar sovrinlar.
# =====================================================================

from typing import Dict, Any, List, Optional

SEASON_INFO = {
    "season_number": 1,
    "title": "🌑 1-Mavsum: Zulmat Uyg'onishi",
    "days_left": 45,
    "max_tier": 50,
    "exp_per_tier": 100
}

# 50 ta daraja mukofotlari
BATTLE_PASS_TIERS = {}

for tier in range(1, 51):
    # Free track reward
    if tier % 10 == 0:
        free_reward = {"type": "gems", "amount": 10, "name": f"💎 {10} Javohir Xazinasi"}
    elif tier % 5 == 0:
        free_reward = {"type": "pet_egg", "amount": 1, "name": "🥚 Sirli Hamroh Tuxumi"}
    elif tier % 2 == 0:
        free_reward = {"type": "gold", "amount": 250 * tier, "name": f"🪙 {250 * tier:,} Oltin"}
    else:
        free_reward = {"type": "potion", "amount": 2, "name": "🧪 Oliy Shifo Eliksiri x2"}

    # Royal (VIP) track reward
    if tier == 50:
        royal_reward = {"type": "mythic_mount", "amount": 1, "name": "👑 Qora Zulmat Ajdarchasi (Mifik Minik)"}
    elif tier % 10 == 0:
        royal_reward = {"type": "gems", "amount": 50, "name": f"💎 {50} Qimmatbaho Javohir"}
    elif tier % 5 == 0:
        royal_reward = {"type": "legendary_gear", "amount": 1, "name": f"🗡 Afsonaviy Qirol Zirhi (Tier {tier // 10 + 1})"}
    elif tier % 2 == 0:
        royal_reward = {"type": "gold", "amount": 800 * tier, "name": f"💰 {800 * tier:,} Qirol Oltini"}
    else:
        royal_reward = {"type": "runes", "amount": 3, "name": "⚡️ Oliy Elementar Runa x3"}

    BATTLE_PASS_TIERS[tier] = {
        "tier": tier,
        "free": free_reward,
        "royal": royal_reward
    }

DAILY_SEASON_CHALLENGES = [
    {"id": "bp_arena_3", "desc": "⚔️ Arenada 3 ta duelda g'alaba qozonish", "target": 3, "exp": 40},
    {"id": "bp_dungeon_2", "desc": "🗺 Zindonda 2 ta yangi xonani tozalash", "target": 2, "exp": 45},
    {"id": "bp_mine_1", "desc": "⛏ Shaxtada 2 marta ruda qazish", "target": 2, "exp": 30},
    {"id": "bp_feed_pet", "desc": "🍗 Jangovar hamrohingizni ovqatlantirish", "target": 1, "exp": 25},
    {"id": "bp_tavern_gamble", "desc": "🍻 Taverna Omad G'ildiragini aylantirish", "target": 1, "exp": 35},
    {"id": "bp_market_trade", "desc": "🛒 Bozorda tovar sotish yoki xarid qilish", "target": 1, "exp": 30}
]

def calculate_bp_tier(total_exp: int) -> int:
    """Umumiy mavsumiy tajriba bo'yicha erishilgan Tierni hisoblaydi."""
    return min(SEASON_INFO["max_tier"], max(1, (total_exp // SEASON_INFO["exp_per_tier"]) + 1))
