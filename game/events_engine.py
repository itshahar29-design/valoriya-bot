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
    },
    {
        "id": "event_hanging_knight",
        "title": "💀 DORGANING SIRLI JALLODI VA RITSAR",
        "desc": "Chorrahada qari chinor shoxiga osilgan qora ritsar jasadini ko'rdingiz. Uning belida qimmatbaho charm xalta va qilich yarqirab turibdi.",
        "options": [
            ("cut_down", "🗡 Arqonni kesib ritsarga hurmat ko'rsatish va ko'mish"),
            ("loot_pockets", "💰 Cho'ntaklarini shoshib tintib ketish"),
            ("pray_pass", "🙏 Uzoqdan duo qilib o'tib ketish")
        ]
    },
    {
        "id": "event_witch_hut",
        "title": "🛖 BOTQOQLIKDAGI SIRLI YALMOG'IZ UYCHASI",
        "desc": "Qora botqoq o'rtasida tovuq oyoqli g'alati yog'och kulba turibdi. Derazadan qozonda qaynab turgan yashil damlama hidi kelmoqda.",
        "options": [
            ("drink_brew", "🧪 Qozondagi g'alati damlamadan ichib ko'rish"),
            ("steal_herbs", "🌿 Quritilgan sehrli o'tlarni o'g'irlash"),
            ("flee", "🏃‍♂️ Botqoq yalmog'izi qaytmasidan qochish")
        ]
    },
    {
        "id": "event_bandit_camp",
        "title": "⛺️ QAROQCHILARNING TUNGI GULXANI",
        "desc": "Qorong'u jarlikda bir to'da qaroqchilar mast bo'lib uxlab yotganini payqadingiz. O'rtadagi qozon yonida o'lja to'la qoplar turibdi.",
        "options": [
            ("stealth_steal", "🤫 Bildirmasdan eng katta qopni o'g'irlash"),
            ("ambush_attack", "⚔️ G'aflatda qolgan qaroqchilarga to'satdan hujum qilish"),
            ("leave_quietly", "🚶‍♂️ Shovqin solmasdan uzoqlashish")
        ]
    },
    {
        "id": "event_cursed_mirror",
        "title": "🪞 QADIMIY XAROBALAR ICHIDAGI SIRLI KO'ZGU",
        "desc": "Tosh zal markazida chang bosgan baland kumush ko'zgu turibdi. Ko'zguga qaraganingizda, aksingiz sizga qarab kulib ko'z qismoqda!",
        "options": [
            ("touch_glass", "🖐 Oynaga qo'l tekkizib aksingiz bilan birlashish"),
            ("break_glass", "🔨 Cho'qmor bilan la'natli oynani sindirib tashlash"),
            ("turn_away", "🚫 Ko'zlarni yumib xonadan chiqib ketish")
        ]
    },
    {
        "id": "event_desert_oasis",
        "title": "🌴 SAHRO AFSONAVIY OAZISI (SAROB)",
        "desc": "Jazirama qumlar orasida to'satdan xurmo daraxtlari va billurdek tiniq ko'l paydo bo'ldi. Suv bo'yida moviy xalatli maftunkor qiz turibdi.",
        "options": [
            ("dive_in", "🏊‍♂️ Suvga sakrab tashnalikni qondirish"),
            ("talk_maiden", "🗣 Qiz bilan gaplashib yo'l so'rash"),
            ("sand_check", "👁 Bu sarob ekanligini anglab qum sepib tekshirish")
        ]
    },
    {
        "id": "event_dragon_nest",
        "title": "🥚 TOG' CHO'QQISIDAGI AJDAHO UYASI",
        "desc": "Qoyalar ustida ulkan suyaklar bilan o'ralgan uya topdingiz. Uya markazida olovdek qizigan bahaybat qora ajdaho tuxumi yotibdi!",
        "options": [
            ("steal_egg", "🎒 Ajdaho tuxumini xaltaga solib o'g'irlash"),
            ("warm_hands", "🔥 Tuxum taftida sovuqdan qotgan qo'llarni isitish"),
            ("retreat_fast", "🦅 Ona ajdaho qaytmasidan tezda pastga tushish")
        ]
    },
    {
        "id": "event_wounded_paladin",
        "title": "🛡 YARALANGAN MUQADDAS SALIBCHI",
        "desc": "Yo'l yoqasida qonga botgan, qilichiga suyanib arang nafas olayotgan imperator paladini yotibdi. U sizga uzatilgan qo'li bilan yordam so'ramoqda.",
        "options": [
            ("heal_him", "🩹 O'z bint va eliksiringiz bilan unga shifo berish"),
            ("finish_him", "🗡 Uni o'ldirib qurol-yarog'ini yechib olish"),
            ("comfort_words", "🤲 Unga dalda berib so'nggi vasiyatini tinglash")
        ]
    },
    {
        "id": "event_black_market",
        "title": "🐫 XUFIYONA SAYYOR QORA BOZOR SAVDOGARI",
        "desc": "Qorong'u o'rmon oralab ketayotganingizda qora tuyali niqobdor savdogar ro'parangizdan chiqdi: 'Ritsar, taqiqlangan sehrli xazina kerakmi?'",
        "options": [
            ("buy_mystery_box", "📦 200 oltin berib sirli sandiqcha sotib olish"),
            ("arrest_bandit", "⚔️ Uni noqonuniy savdoda ayblab qurol tortish"),
            ("decline_politely", "🚶‍♂️ Xushmuomalalik bilan rad etish")
        ]
    },
    {
        "id": "event_ghost_army",
        "title": "👻 TUNGI ARVOHLAR QO'SHINI PARADI",
        "desc": "Tungi soat 03:00 da tuman orasidan ovozsiz qadam tashlab ketayotgan yuzlab shaffof qadimiy ritsarlar armiyasi paydo bo'ldi.",
        "options": [
            ("salute_army", "🫡 Qilichni ko'tarib qadimiy ajdodlarga salom berish"),
            ("hide_bushes", "🌿 Butalar orasiga berkinib nafas chiqarmaslik"),
            ("challenge_leader", "⚔️ Arvohlar qo'mondoniga duel taklif qilish")
        ]
    },
    {
        "id": "event_fallen_meteor",
        "title": "☄️ YERGA QULAGAN MOVİY METEORIT",
        "desc": "Yaqin oradagi jarlikdan ko'kka moviy tutun ko'tarilmoqda. Chuqur o'rtasida osmondan tushgan, yaltirab turgan issiq yulduz toshi yotibdi.",
        "options": [
            ("extract_ore", "⛏ Bolg'a bilan meteoritdan qimmatbaho ruda urib olish"),
            ("absorb_magic", "🧘‍♂️ Tosh ustiga o'tirib kosmik energiyani tanaga yutish"),
            ("cool_with_water", "💧 Suv sepib toshni sovutish")
        ]
    }
]

class EventsEngine:
    @staticmethod
    def get_random_event() -> dict:
        return random.choice(WILDERNESS_EVENTS)

    @staticmethod
    def resolve_event(event_id: str, choice: str, char: dict) -> Tuple[str, dict]:
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

        elif event_id == "event_hanging_knight":
            if choice == "cut_down":
                changes["xp"] = 180
                changes["sanity"] = 20
                changes["gold"] = 150
                return "✝️ *SAVOB ISH:* Ritsarni yerga tushirib munosib dafn etdingiz. Uning ruhidan rahmat va xaltasidagi 150 🪙 oltin sizga nasib etdi.", changes
            elif choice == "loot_pockets":
                changes["gold"] = 280
                changes["sanity"] = -15
                return "💀 *G'URURSIZ O'G'RILIK:* Cho'ntaklaridan 280 🪙 oltin oldingiz, ammo vijdonsizlik ruhingizni kemirdi (-15% Sanity).", changes
            else:
                return "O'lim manzarasiga qaramasdan o'tib ketdingiz.", changes

        elif event_id == "event_witch_hut":
            if choice == "drink_brew":
                if random.random() < 0.5:
                    changes["hp"] = 100
                    changes["xp"] = 250
                    return "🧪 *SEHRLI QUDRAT!* Damlama vujudingizni olov kabi qizdirdi! +100 HP va +250 XP oldingiz!", changes
                else:
                    changes["hp"] = -40
                    changes["sanity"] = -20
                    return "🤢 *ZAHARLANISH:* Damlama zaharli qurbaqa terisidan tayyorlangan ekan! (-40 HP, -20% Sanity)", changes
            elif choice == "steal_herbs":
                changes["gold"] = 200
                return "🌿 *QIMMATLI O'TLAR:* Yalmog'izning kamyob dorivor o'tlarini olib qochdingiz! (Bozor qiymati: +200 🪙).", changes
            else:
                return "Xatarli uychadan tezda uzoqlashdingiz.", changes

        elif event_id == "event_bandit_camp":
            if choice == "stealth_steal":
                if random.random() < 0.7:
                    found_gold = random.randint(250, 500)
                    changes["gold"] = found_gold
                    return f"🤫 *USTALIK:* Qaroqchilar uyg'onmadi! Siz +{found_gold} 🪙 oltinli xaltani sezdirmay ilib ketdingiz!", changes
                else:
                    changes["hp"] = -35
                    return "⚔️ *UYG'ONISH:* Qaroqchi itlari hurib qoldi! Qochishda orqangizga o'q tegdi (-35 HP).", changes
            elif choice == "ambush_attack":
                changes["xp"] = 350
                changes["gold"] = 400
                changes["hp"] = -25
                return "🩸 *JASORATLI JANG!* Barcha qaroqchilarni yakson qildingiz! (+400 🪙, +350 XP, -25 HP jang jarohati).", changes
            else:
                return "Xatarga yo'liqmaslik uchun yo'lda davom etdingiz.", changes

        elif event_id == "event_cursed_mirror":
            if choice == "touch_glass":
                changes["sanity"] = -30
                changes["xp"] = 400
                return "🌑 *SOYALAR BILIMI:* Oynadagi aksingiz sizga qadimiy qora sirni shivirladi (+400 XP, -30% Sanity).", changes
            elif choice == "break_glass":
                changes["sanity"] = 15
                return "🔨 *LA'NATNING SINISHI:* Ko'zgu maydalanib ketdi va atrof yorishdi. Qalbingiz tinchlandi (+15% Sanity).", changes
            else:
                return "Sehrli ko'zgudan ko'zingizni olib ketdingiz.", changes

        elif event_id == "event_desert_oasis":
            if choice == "dive_in":
                changes["hp"] = 80
                changes["sanity"] = 20
                return "🌴 *HAQIQIY OAZIS!* Bu sarob emas ekan! Salqin suv sizga yangi hayot bag'ishladi (+80 HP, +20% Sanity).", changes
            elif choice == "talk_maiden":
                changes["xp"] = 200
                changes["gold"] = 100
                return "🗣 Qiz sizga sahro yashirin yo'llarini ko'rsatdi va tilla uzuk sovg'a qildi (+100 🪙, +200 XP).", changes
            else:
                return "Sahro bo'ronidan ehtiyotkorlik bilan o'tib oldingiz.", changes

        elif event_id == "event_dragon_nest":
            if choice == "steal_egg":
                if random.random() < 0.6:
                    changes["gold"] = 1000
                    changes["xp"] = 500
                    return "🐉 *AFSONAVIY O'LJA!* Ajdaho tuxumini o'g'irlashga muvaffaq bo'ldingiz! Bozor qiymati: +1,000 🪙 Oltin!", changes
                else:
                    changes["hp"] = -70
                    changes["sanity"] = -25
                    return "🔥 *AJDAHO QAHRI!* Ona ajdaho yetib kelib ustingizga olov purkadi! Mo''jiza bilan qochib qoldingiz (-70 HP, -25% Sanity)!", changes
            elif choice == "warm_hands":
                changes["hp"] = 40
                return "🔥 Tuxumning issig'ida tanangiz iliydi va kuchga to'ldingiz (+40 HP).", changes
            else:
                return "Ajdaho uyasidan tezda uzoqlashdingiz.", changes

        elif event_id == "event_wounded_paladin":
            if choice == "heal_him":
                changes["hp"] = -10
                changes["sanity"] = 25
                changes["xp"] = 300
                changes["gold"] = 300
                return "🕊 *MINNATDORCHILIK:* Paladin oyoqqa turib sizga o'z xazinasidan 300 🪙 va shaxsiy duosini berdi (+25% Sanity, +300 XP).", changes
            elif choice == "finish_him":
                changes["gold"] = 500
                changes["sanity"] = -30
                return "🩸 *XUDOBEZORLIK:* Ojiz paladinni qatl qilib 500 🪙 oltinini oldingiz, ammo vijdoningiz sizni la'natladi (-30% Sanity).", changes
            else:
                return "Paladin yonidan jimgina o'tib ketdingiz.", changes

        elif event_id == "event_black_market":
            if choice == "buy_mystery_box":
                if char.get("gold", 0) >= 200:
                    changes["gold"] = -200
                    reward = random.choice([500, 800, 150])
                    changes["gold"] += reward
                    changes["xp"] = 150
                    return f"📦 *SIRLI SANDIQ:* Sandiq ichidan nodir javohirlar va {reward} 🪙 oltin chiqdi!", changes
                else:
                    return "Savdogar: 'Pulingiz yetmas ekan, ritsar!' deya yo'lida davom etdi.", changes
            elif choice == "arrest_bandit":
                changes["xp"] = 250
                changes["gold"] = 200
                return "⚔️ Qaroqchini qurolsizlantirib xazinasini musodara qildingiz (+200 🪙, +250 XP).", changes
            else:
                return "Shubhali savdogarga e'tibor bermadingiz.", changes

        elif event_id == "event_ghost_army":
            if choice == "salute_army":
                changes["sanity"] = 30
                changes["xp"] = 400
                return "👻 *AJ DODLAR BARAKASI:* Qadimiy qo'mondon sizga qilich bilan ehtirom ko'rsatdi. Ritsarlik irodangiz yuksaldi (+30% Sanity, +400 XP).", changes
            elif choice == "hide_bushes":
                return "Tuman tarqalguncha butalar orasida jimgina o'tirdingiz.", changes
            else:
                changes["hp"] = -50
                changes["sanity"] = -30
                return "💀 *SHAFQATSIZ JANG:* Arvohlar shamshiri suyaklaringizni muzlatib tashladi (-50 HP, -30% Sanity)!", changes

        elif event_id == "event_fallen_meteor":
            if choice == "extract_ore":
                changes["gold"] = 350
                changes["xp"] = 200
                return "⛏ *KOSMIK RUDA:* Meteoritdan qimmatbaho samoviy metall bo'laklarini qazib oldingiz (+350 🪙, +200 XP).", changes
            elif choice == "absorb_magic":
                changes["hp"] = 60
                changes["xp"] = 350
                return "💫 *ASTRAL QUDRAT:* Kosmik nurlar tanangizga singib barcha charchoqni ketkazdi (+60 HP, +350 XP).", changes
            else:
                return "Meteorit soviguncha uzoqdan kuzatib turdingiz.", changes

        return "Hodisa yakunlandi.", changes
