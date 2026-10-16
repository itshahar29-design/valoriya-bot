# =====================================================================
# VALORIYA: PRESTIJ VA QAHRAMONLIK QAYTA TUG'ILISHI (ASCENSION - 10 TIERS)
# =====================================================================
# 60+ kunlik uzoq muddatli o'yin siklini (Endgame retention) ta'minlovchi tizim.
# 50-darajaga yetgan ritsarlar qayta tug'ilib, doimiy multiplikatorlar va shon-sharaf oladilar.
# =====================================================================

from typing import Dict, Any, Optional, Tuple

PRESTIGE_TIERS = {
    1: {"name": "🌟 Prestij I: Ritsar-Kapitan", "stat_mult": 1.20, "bonus_gems": 100, "title": "Ritsar-Kapitan", "req_level": 50},
    2: {"name": "🌟🌟 Prestij II: Qirollik Paladini", "stat_mult": 1.40, "bonus_gems": 200, "title": "Qirollik Paladini", "req_level": 50},
    3: {"name": "🌟🌟🌟 Prestij III: Imperiya Marshali", "stat_mult": 1.65, "bonus_gems": 350, "title": "Imperiya Marshali", "req_level": 50},
    4: {"name": "💫 Prestij IV: Afsonaviy Qahramon", "stat_mult": 1.95, "bonus_gems": 500, "title": "Afsonaviy Qahramon", "req_level": 50},
    5: {"name": "💫💫 Prestij V: Ajdaho Yenguvchi", "stat_mult": 2.30, "bonus_gems": 750, "title": "Ajdaho Qotili", "req_level": 50},
    6: {"name": "👑 Prestij VI: Valoriya Yarim-Xudosi", "stat_mult": 2.75, "bonus_gems": 1000, "title": "Yarim-Xudo", "req_level": 50},
    7: {"name": "🔱 Prestij VII: Mangu Qo'riqchi", "stat_mult": 3.30, "bonus_gems": 1500, "title": "Mangu Qo'riqchi", "req_level": 50},
    8: {"name": "🌌 Prestij VIII: Kosmik Monarx", "stat_mult": 4.00, "bonus_gems": 2000, "title": "Kosmik Monarx", "req_level": 50},
    9: {"name": "⚡️ Prestij IX: Borliq Yaratuvchisi", "stat_mult": 4.80, "bonus_gems": 3000, "title": "Borliq Yaratuvchisi", "req_level": 50},
    10: {"name": "👑 Prestij X: Oliy Valoriya Mutloqi", "stat_mult": 6.00, "bonus_gems": 5000, "title": "Oliy Mutloq", "req_level": 50}
}

def can_ascend(character: Dict[str, Any]) -> Tuple[bool, str]:
    """Qahramon qayta tug'ilish (Prestige) qila oladimi?"""
    cur_prestige = character.get("prestige_level", 0) or 0
    if cur_prestige >= 10:
        return False, "Siz maksimal Prestij X darajasiga yetgansiz! Olamning eng oliy pallasidasiz."

    next_prestige = cur_prestige + 1
    req = PRESTIGE_TIERS[next_prestige]

    level = character.get("level", 1)
    if level < req["req_level"]:
        return False, f"Qayta tug'ilish uchun kamida {req['req_level']}-darajaga yetishingiz kerak! Hozirgi darajangiz: {level}."

    return True, f"Siz *{req['name']}* darajasiga qayta tug'ilishga tayyorsiz!"
