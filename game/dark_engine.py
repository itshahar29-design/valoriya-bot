import json
import random
from typing import Dict, List, Tuple, Any

# =====================================================================
# ZULMAT TIZIMI (DARK SOULS-STYLE HARDCORE MECHANICS)
# =====================================================================

WOUND_TYPES = {
    "broken_rib": {
        "id": "broken_rib",
        "name": "🦴 Sindirilgan qovurg'a",
        "desc": "Ko'krak qafasidagi og'ir sinish tufayli nafas olish qiyinlashgan.",
        "penalty_hp_pct": 20,
        "cure_cost": 150
    },
    "fractured_arm": {
        "id": "fractured_arm",
        "name": "🪓 Singan qo'l suyagi",
        "desc": "Qo'l suyagi darz ketgan, qurolni mahkam tutib bo'lmaydi (-25% ATK).",
        "penalty_atk_pct": 25,
        "cure_cost": 200
    },
    "deep_laceration": {
        "id": "deep_laceration",
        "name": "🩸 Chuqur qonli yara",
        "desc": "Bitmagan chuqur jarohat har harakatda qon sizib chiqishiga sabab bo'ladi (-15 Stamina har raund).",
        "stamina_cost_round": 15,
        "cure_cost": 180
    },
    "concussion": {
        "id": "concussion",
        "name": "🧠 Og'ir bosh chayqalishi",
        "desc": "Boshga tushgan og'ir zarba muvozanatni yo'qotadi (-30% Chaqqonlik / Evasion).",
        "penalty_agi_pct": 30,
        "cure_cost": 160
    },
    "void_curse": {
        "id": "void_curse",
        "name": "🌑 Zulmat Tamg'asi (Void Mark)",
        "desc": "Qorong'ulik ruhingizni yemirmoqda. Hamyondan oltin yo'qoladi va Sanity o'z-o'zidan pasayadi.",
        "gold_leak_pct": 5,
        "cure_cost": 300
    },
    "gouged_eye": {
        "id": "gouged_eye",
        "name": "👁 O'yilgan Ko'z Jarohati",
        "desc": "Ko'rish maydoni toraygan, kritik zarba berish imkoniyati 0 ga tushadi.",
        "penalty_crit_pct": 50,
        "cure_cost": 250
    },
    "torn_tendon": {
        "id": "torn_tendon",
        "name": "🦵 Uzilgan Boldir Payi",
        "desc": "Oyoq paylari uzilgani sababli chaqqon harakatlana olmaysiz (-40% AGI).",
        "penalty_agi_pct": 40,
        "cure_cost": 220
    },
    "shattered_knee": {
        "id": "shattered_knee",
        "name": "🦴 Maydalangan Tizza Qopqog'i",
        "desc": "Tizza suyagi singan, stamina tiklanishi 50% sekinlashadi.",
        "penalty_stamina_pct": 30,
        "cure_cost": 240
    },
    "broken_jaw": {
        "id": "broken_jaw",
        "name": "💀 Sinib Ketgan Jag' Suyagi",
        "desc": "Jag' singan, ovqatlanish va damlamalarni ichish qiyinlashgan.",
        "penalty_hp_pct": 15,
        "cure_cost": 170
    },
    "pierced_lung": {
        "id": "pierced_lung",
        "name": "🫁 Teshilgan O'pka Yara",
        "desc": "Har raundda ko'krakdan qon toshib -15 HP yo'qoladi.",
        "hp_loss_round": 15,
        "cure_cost": 350
    },
    "gangrene": {
        "id": "gangrene",
        "name": "🤢 Qorason / Chirigan Go'sht (Gangrena)",
        "desc": "Jarohat joyi qorayib chirigan, zudlik bilan davolanmasa tana parchalanadi.",
        "penalty_hp_pct": 35,
        "cure_cost": 400
    },
    "burned_skin": {
        "id": "burned_skin",
        "name": "🔥 3-Darajali Kuyish Jarohati",
        "desc": "Magma yoki olov ta'sirida teri kuygan, mudofaa -25% pasayadi.",
        "penalty_def_pct": 25,
        "cure_cost": 200
    },
    "paranoia_phobia": {
        "id": "paranoia_phobia",
        "name": "😱 Doimiy Ruhiy Paranoya",
        "desc": "Ritsar hamma narsadan hadiksiraydi, jangda dushmanning dastlabki zarbasi 2x kuchli tuyuladi.",
        "penalty_sanity_pct": 25,
        "cure_cost": 260
    },
    "tremor_hands": {
        "id": "tremor_hands",
        "name": "🧤 Qaltiroq Qo'llar Sindromi",
        "desc": "Asab tolalari zararlangani uchun qurol qo'ldan tushib ketish ehtimoli bor (-20% ATK).",
        "penalty_atk_pct": 20,
        "cure_cost": 190
    },
    "demon_possession": {
        "id": "demon_possession",
        "name": "😈 Iblisning Vujudga Joylashishi",
        "desc": "Morvath sharpasi ichingizga kirgan: zarba +30 oshadi, ammo har soatda Sanity tushadi.",
        "penalty_sanity_pct": 40,
        "cure_cost": 500
    }
}

class DarkEngine:
    @staticmethod
    def get_sanity_status(sanity: int) -> Tuple[str, str, str]:
        """
        Sanity darajasiga qarab holat, tavsif va ogohlantirish qaytaradi.
        """
        sanity = max(0, min(100, sanity))
        if sanity >= 80:
            return "🌟 Ruh Mustahkam", "🟢 Sog'lom", "Aqlingiz joyida va jangovar ruhingiz baland."
        elif sanity >= 50:
            return "😰 Xavotir va Sarosima", "🟡 Xavotirli", "Qorong'ulik sizni bezovta qilmoqda. Taverna sharobi ichish tavsiya etiladi."
        elif sanity >= 25:
            return "👁 Dahshatli Gallyutsinatsiyalar", "🟠 Og'ir", "Ko'zingizga sharpalar ko'rinmoqda! Jangda sarosima va zarba pasayishi (-15% DMG)."
        else:
            return "💀 Telbalik va Falajlik (Madness)", "🔴 Xavfli", "Siz aql hushdan ozgansiz! Jangda 30% ehtimol bilan harakat qila olmaysiz!"

    @staticmethod
    def check_sanity_battle_effect(sanity: int) -> Tuple[bool, str, float]:
        """
        Jang paytida aql holatining salbiy ta'siri:
        Returns: (is_panicked, log_message, damage_multiplier)
        """
        sanity = max(0, min(100, sanity))
        if sanity < 25:
            # 30% ehtimol bilan falajlik yoki qurol tushirib yuborish
            if random.random() < 0.30:
                return True, "💀 *TELBALIK VA SAROSIMA:* Zulmat sharpalari qulog'ingizga pichirlab aqlingizni oldi! Qo'lingiz qaltirab qurolni tushirib yubordingiz va bu raundda zarba berolmadingiz!", 0.0
            return False, "⚠️ *VAHIMA:* Yuragingiz vahimadan qattiq urmoqda, zarbangiz kuchi 25% ga susaydi.", 0.75
        elif sanity < 50:
            if random.random() < 0.20:
                return False, "👁 *GALLYUTSINATSIYA:* Ko'zingizga ikki xil nishon ko'rindi va zarbangiz kuchi 15% ga pasaydi.", 0.85
        return False, "", 1.0

    @staticmethod
    def calculate_effective_stats(character: dict) -> dict:
        """
        Wounds (travmalar) va Bloodline hisobga olingan haqiqiy jangovar statlar.
        """
        wounds_list = []
        try:
            wounds_data = character.get("wounds_json", "[]")
            if isinstance(wounds_data, str):
                wounds_list = json.loads(wounds_data)
            elif isinstance(wounds_data, list):
                wounds_list = wounds_data
        except Exception:
            wounds_list = []

        eff_max_hp = character.get("max_hp", 120)
        eff_atk = character.get("strength", 15) * 1.5
        eff_agi = character.get("agility", 12)
        eff_def = character.get("constitution", 15) * 0.8
        stamina_drain = 0

        # Wounds debuff
        for w_id in wounds_list:
            w_info = WOUND_TYPES.get(w_id)
            if not w_info:
                continue
            if "penalty_hp_pct" in w_info:
                eff_max_hp = int(eff_max_hp * (1 - w_info["penalty_hp_pct"] / 100))
            if "penalty_atk_pct" in w_info:
                eff_atk = int(eff_atk * (1 - w_info["penalty_atk_pct"] / 100))
            if "penalty_agi_pct" in w_info:
                eff_agi = int(eff_agi * (1 - w_info["penalty_agi_pct"] / 100))
            if "stamina_cost_round" in w_info:
                stamina_drain += w_info["stamina_cost_round"]

        # Blood pact buff
        has_pact = character.get("bloodline_trait") == "demon_pact"
        if has_pact:
            eff_atk += 45
            eff_max_hp = max(50, eff_max_hp - 25)

        return {
            "eff_max_hp": max(30, eff_max_hp),
            "eff_atk": max(5, eff_atk),
            "eff_agi": max(3, eff_agi),
            "eff_def": max(3, eff_def),
            "stamina_drain_round": stamina_drain,
            "has_blood_pact": has_pact,
            "wounds_count": len(wounds_list)
        }
