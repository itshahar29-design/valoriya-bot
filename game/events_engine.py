import random
from typing import Tuple, Dict

WILDERNESS_EVENTS = [
    {
        "id": "event_shrine",
        "title": "🕊 QADIMIY NURIY BULOQ (MUQADDAS CHASHMA)",
        "desc": "Tog'lar oralab ketar ekansiz, moviy nur taratib turgan toza buloqqa duch keldingiz. "
                "Buloq bo'yida qadimiy shifo duolari bitilgan tosh haykal turibdi.",
        "options": [
            ("pray", "🙏 Muqaddas suvdan ichish va duo qilish"),
            ("coin", "🪙 Buloqqa 20 oltin tashlab omad tilash"),
            ("leave", "🚶‍♂️ Yo'lingizda davom etish")
        ]
    },
    {
        "id": "event_wagon",
        "title": "📦 TASHLANDIQ SAVDOGAR ARAVASI",
        "desc": "Yo'l chetida ag'darilgan, atrofiga singan bochkalar sochilgan boy karvon aravasini ko'rdingiz. "
                "Atrofda qon izlari bor, qaroqchilar yaqin atrofda poylab turgan bo'lishi mumkin.",
        "options": [
            ("loot", "🔍 Aravani ehtiyotkorlik bilan tintuv qilish"),
            ("burn", "🔥 Xavfli izlarni yo'qotish uchun yoqib yuborish"),
            ("ignore", "🐎 Shoshilinch ravishda o'tib ketish")
        ]
    },
    {
        "id": "event_hermit",
        "title": "🧙‍♂️ O'RMONNING SIRLI QARI DARVESHI",
        "desc": "Qalin eman tagida oppoq soqolli, ko'zlari donolikdan porlayotgan keksa darvesh o'tiribdi. "
                "U sizga qarab: 'Ey yosh ritsar, dunyo nafsi orqasidan quvib qayerga shoshasan?' deya xitob qildi.",
        "options": [
            ("listen", "🧎‍♂️ Ta'zim qilib hikmatli maslahat tinglash"),
            ("share_food", "🍞 Yo'l ozuqangizni darvesh bilan bo'lishish"),
            ("threaten", "⚔️ Qilich sug'urib boyligini talab qilish")
        ]
    },
    {
        "id": "event_obelisk",
        "title": "🌑 ZULMAT VA LA'NATLI QORA OBELISK",
        "desc": "Taqir dasht o'rtasida qora bazalt toshidan yo'nilgan, binafsharang yozuvlar yonib-o'chayotgan ustun turibdi. "
                "Obeliskdan g'alati shivir-shivir ovozlar kelmoqda.",
        "options": [
            ("touch", "🩸 Qo'l tegizib qorong'u qudratni his qilish"),
            ("destroy", "🔨 Cho'qmor bilan obeliskni parchalab tashlash"),
            ("run", "🏃‍♂️ Quloqlarni yopib orqaga qochish")
        ]
    },
    {
        "id": "event_chest",
        "title": "🗝 QADIMIY O'YILGAN TEMIR SANDIQ",
        "desc": "Sharshara ostidagi g'orga kirganingizda, zanjirlar bilan toshga bog'langan sirli sandiqqa ko'zingiz tushdi. "
                "Qulf ustida qadimiy elflar tamg'asi bosilgan.",
        "options": [
            ("pick_lock", "🗡 Xanjar bilan qulfni buzib ochish"),
            ("smash", "🔨 Og'ir bolg'a bilan zanjirni uzish"),
            ("leave", "🚫 Tuzoq bo'lishi mumkin, teginmaslik")
        ]
    }
]

class EventsEngine:
    @staticmethod
    def get_random_event() -> dict:
        return random.choice(WILDERNESS_EVENTS)

    @staticmethod
    def resolve_event(event_id: str, choice: str, char: dict) -> Tuple[str, dict]:
        """
        Natijani va o'zgarishlarni qaytaradi:
        changes: {"gold": int, "hp": int, "sanity": int, "xp": int, "items": list}
        """
        changes = {"gold": 0, "hp": 0, "sanity": 0, "xp": 0}

        if event_id == "event_shrine":
            if choice == "pray":
                changes["hp"] = 50
                changes["sanity"] = 25
                return "✨ *ILOHIY SHIFO!* Chashma suvidan ichib, vujudingizdagi barcha charchoq va dardlardan forig' bo'ldingiz! (+50 HP, +25% Sanity)", changes
            elif choice == "coin":
                changes["gold"] = -20
                changes["xp"] = 150
                return "🌟 *OMAD MARHAMATI!* Buloqqa oltin tashlaganingizda suv yuzida oq kabutar ko'rindi. Ritsarlik tajribangiz oshdi (+150 XP).", changes
            else:
                return "Yo'lingizda xotirjam davom etdingiz.", changes

        elif event_id == "event_wagon":
            if choice == "loot":
                if random.random() < 0.65:
                    found_gold = random.randint(120, 350)
                    changes["gold"] = found_gold
                    changes["xp"] = 80
                    return f"💰 *OMADLI O'LJA!* Aravaning yashirin bo'lmasidan {found_gold} 🪙 Oltin va qimmatbaho xazina topib oldingiz!", changes
                else:
                    changes["hp"] = -30
                    changes["sanity"] = -10
                    return "⚠️ *PISTIRMA!* Qutilarni ochayotganingizda pistirmadagi qaroqchilar kamondan o'q uzib sizni jarohatladi! (-30 HP, -10% Sanity)", changes
            elif choice == "burn":
                changes["xp"] = 50
                return "🔥 Aravani yoqib yubordingiz. Qaroqchilar sizni ta'qib qila olmadi.", changes
            else:
                return "Xatarga bosh qo'shmasdan tezlik bilan o'tib ketdingiz.", changes

        elif event_id == "event_hermit":
            if choice == "listen":
                changes["sanity"] = 30
                changes["xp"] = 200
                return "📜 *HIKMAT VA SAKINAT:* Qari darveshning so'zlari qalbingizdagi g'uborlarni yuvib tashladi. Sanity +30% tiklandi va +200 XP oldingiz!", changes
            elif choice == "share_food":
                changes["gold"] = 100
                return "🎁 *DARVESH DUOSI:* Darvesh noningizni qabul qilib, cho'ntagidan qadimgi oltin tangalar chiqarib berdi (+100 🪙).", changes
            else:
                changes["sanity"] = -25
                changes["hp"] = -20
                return "⚡️ *LA'NAT:* Qilich sug'urganingizda darvesh tutunga aylanib g'oyib bo'ldi va chaqmoq urib sizni jazoladi! (-20 HP, -25% Sanity)", changes

        elif event_id == "event_obelisk":
            if choice == "touch":
                changes["sanity"] = -35
                changes["xp"] = 300
                return "🩸 *ZULMAT QUDRATI:* Toshdan vujudingizga muzdek qora quvvat yugurdi! Aql 35% ga sindi, ammo buyuk qora bilim oldingiz (+300 XP).", changes
            elif choice == "destroy":
                changes["gold"] = 250
                changes["sanity"] = 15
                return "🔨 *MUQADDAS G'ALABA:* Qora ustunni parchalab yubordingiz! Tosh ichidan 250 🪙 oltin tushdi va botiniy xotirjamlik topdingiz.", changes
            else:
                return "Xatarli qora sehrdan uzoqroq yurishni ma'qul ko'rdingiz.", changes

        elif event_id == "event_chest":
            if choice == "pick_lock":
                if random.random() < 0.60:
                    found_gold = random.randint(300, 600)
                    changes["gold"] = found_gold
                    changes["xp"] = 150
                    return f"🗝 *QULF OCHILDI!* Qadimgi elflar xazinasi ochildi: +{found_gold} 🪙 Oltin!", changes
                else:
                    changes["hp"] = -25
                    return "💥 *ZAHARLI TUZOQ:* Qulf ichidan zaharli igna otilib barmog'ingizga sanchildi! (-25 HP)", changes
            elif choice == "smash":
                changes["gold"] = 150
                return "🔨 Bolg'a bilan sandiqni sindirdingiz, ko'p qimmatbaho idishlar sinsa-da, 150 🪙 oltin qoldi.", changes
            else:
                return "Shubhali sandiqqa teginmasdan o'tib ketdingiz.", changes

        return "Hodisa yakunlandi.", changes
