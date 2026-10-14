import re
from game.constants import KINGDOMS

class EmotionsEngine:
    FLATTERY_KEYWORDS = [
        "ulug'", "buyuk", "quyosh", "adolatli", "sher", "yengilmas", "ta'zim",
        "hukmdor", "podshoh", "afsona", "sharaf", "donishmand", "qilichingiz",
        "dono", "qudratli", "eng zo'r", "daho", "eng kuchli", "sodiqman"
    ]
    
    INSULT_KEYWORDS = [
        "ahmoq", "qo'rqoq", "it", "xasis", "zolim", "yolg'onchi", "cho'chqa",
        "zaif", "yutqazding", "hech kimsan", "qochqoq"
    ]

    @staticmethod
    def evaluate_player_speech(kingdom_id: str, speech_text: str):
        """
        O'yinchining AI Qirolga aytgan gapini (paxta yoki haqorat) tahlil qiladi.
        """
        k_data = KINGDOMS.get(kingdom_id, KINGDOMS["lionguard"])
        text_lower = speech_text.lower()
        
        # Paxta va haqorat ballari
        flattery_score = sum(1 for word in EmotionsEngine.FLATTERY_KEYWORDS if word in text_lower)
        insult_score = sum(1 for word in EmotionsEngine.INSULT_KEYWORDS if word in text_lower)
        
        # 1. Agar haqorat bo'lsa
        if insult_score > 0:
            return {
                "ruler": k_data["ruler"],
                "mood": "rage",
                "affection_change": -35,
                "anger_change": +40,
                "reward_gold": 0,
                "reply": f"😡 {k_data['ruler']}: 'Sen iflos qurt! Mening saroyimda menga til tekkizishga qanday jur'at etding?! Zindonga tashlansin!'"
            }
            
        # 2. Agar paxta qo'yilgan bo'lsa
        if flattery_score > 0:
            personality = k_data.get("personality", "pride")
            
            # Kibrli qirollar (Valter, Izabella)
            if personality in ["pride", "diplomat"]:
                reward = flattery_score * 40
                return {
                    "ruler": k_data["ruler"],
                    "mood": "pleased",
                    "affection_change": +15 * flattery_score,
                    "anger_change": -10,
                    "reward_gold": reward,
                    "reply": f"👑 {k_data['ruler']}: 'Ha-ha-ha! So'zlaring qulog'imga asaldek yoqdi, yosh ritsar! Sening donoliging menga ma'qul. Mana senga xazinamdan {reward} oltin va saroy marhamati!'"
                }
            # Qonxo'r va yovvoyi qirollar (Ragnar, Botirxon)
            elif personality in ["anger", "wrath"]:
                return {
                    "ruler": k_data["ruler"],
                    "mood": "disgusted",
                    "affection_change": -10,
                    "anger_change": +15,
                    "reward_gold": 0,
                    "reply": f"🩸 {k_data['ruler']}: 'Menga quruq paxta qo'yma, laganbardor! Menga shirin so'zlar emas, jang maydonida dushmanning to'kilgan qoni kerak! Bor, o'zingni jangda isbotla!'"
                }
            # Qolgan qirollar
            else:
                return {
                    "ruler": k_data["ruler"],
                    "mood": "neutral_pleased",
                    "affection_change": +10,
                    "anger_change": -5,
                    "reward_gold": 50,
                    "reply": f"✨ {k_data['ruler']}: 'Sadoqating uchun rahmat, ritsar. Qirolligimizga sen kabi jasur jangchilar kerak!'"
                }
                
        # 3. Oddiy so'roq yoki betaraf gap
        return {
            "ruler": k_data["ruler"],
            "mood": "neutral",
            "affection_change": 0,
            "anger_change": 0,
            "reward_gold": 0,
            "reply": f"👑 {k_data['ruler']}: 'Gapingni eshitdim. Valoriya qit'asida sharaf va qudrat o'z mehnating bilan qozoniladi!'"
        }
