import random

class RetentionEngine:
    @staticmethod
    def get_ftue_tutorial():
        """
        2-daqiqalik boshlang'ich interaktiv kvest (Ser Artur ssenariysi).
        """
        return {
            "story": (
                "🩸 *NAFASINGIZNI ROSTLANG, YOSH JANGCHI!* 🩸\n\n"
                "Ko'zingizni ochsangiz, yoningizga yarador ritsar *Ser Artur* sudralib kelmoqda:\n\n"
                "💬 *Ser Artur:* 'Shogirdim... Qaroqchilar karvonimizni qurshab oldi! "
                "Mening qo'lim sindi... Mana, otamdan qolgan po'lat qilichni ol! "
                "Qaroqchilar boshlig'i senga qarab chopmoqda! TEZ QILICHING BILAN UNING BOSHIGA UR!'"
            ),
            "starter_enemy": {
                "name": "👹 Qonxo'r Qaroqchi Qoplon",
                "hp": 40,
                "max_hp": 40,
                "stamina": 50,
                "strength": 8,
                "constitution": 4,
                "agility": 5,
                "weapon_attack": 4,
                "armor_defense": 2,
                "persona": "berserk"
            }
        }

    @staticmethod
    def check_random_dervish_encounter():
        """
        Tasodifiy Dopamin Qopqoni (Kutilmagan Darbadar Dervish sovg'asi).
        15% ehtimol bilan harakatlar paytida kutilmagan qimmatbaho sovg'a tushadi.
        """
        if random.random() < 0.20:
            rewards = [
                {"type": "gold", "val": 150, "text": "🪙 150 Oltin tanga to'la xaltacha!"},
                {"type": "gems", "val": 3, "text": "💎 3 ta Qimmatbaho Qizil Yoqut!"},
                {"type": "potion", "val": 1, "text": "🧪 Qadimiy Shifobaxsh Qirollik Eliksiri!"},
                {"type": "ring", "val": 1, "text": "💍 Yulduz Toshli Runali Uzuk (+10 Kuch)!"}
            ]
            gift = random.choice(rewards)
            msg = (
                "✨ *KUTILMAGAN MO'JIZA!* ✨\n\n"
                "Ko'chada ketayotganingizda, oppoq soqolli bir Darbadar Dervish yo'lingizni to'sdi:\n\n"
                "🧙‍♂️ *Dervish:* 'Ey yosh ritsar! Peshonangda boqiy Valoriya xaloskorining nurini ko'ryapman! "
                "Ushbu sovg'ani ol, kelajakda butun qit'a sening nomingni ulug'laydi!'\n\n"
                f"🎁 *Sizga topshirildi:* {gift['text']}"
            )
            return True, gift, msg
        return False, None, ""

    @staticmethod
    def generate_guilt_trip_letter(player_name: str, hours_away: int = 12):
        """
        O'yinchi kirmaganda AI qurolbardor tomonidan yuboriladigan psixologik xat.
        """
        return (
            f"📜 *QUROLBARDORINGIZDAN G'AMGIN MAKTUB* 📜\n\n"
            f"Lordim {player_name}... Qayerdasiz? Siz yo'qligingizda dushman ritsarlar qal'amiz "
            f"darvozasi oldiga kelib, sizni 'qo'rqoqlikda' ayblashdi va gerbimizga loy sochishdi!\n\n"
            f"Men ularga javob qaytardim, ammo meni do'pposlashdi... "
            f"Iltimos, tezroq qayting va oilamiz sha'nini qon bilan yuving!"
        )
