# =====================================================================
# VALORIYA: ALXIMIYA, RESURSLAR VA HUNARMANDCHILIK ENSIKLOPEDIYASI
# 120 TA RESURS, RUDALAR, DAMLAMALAR VA RUNIK RETSEPTLAR
# =====================================================================

# 1. RUDALAR VA METALLAR (25 TA)
ORES_DATABASE = {
    "ore_iron": {"id": "ore_iron", "name": "🔩 Xom Temir Rudasi", "tier": 1, "price": 15, "desc": "Oddiy qurollar va sovutlar uchun asosiy quyma xomashyo."},
    "ore_copper": {"id": "ore_copper", "name": "🥉 Mis Rudasi", "tier": 1, "price": 12, "desc": "Zargarlik va arzon qotishmalar tayyorlash uchun yumshoq metall."},
    "ore_tin": {"id": "ore_tin", "name": "🥫 Qalay Rudasi", "tier": 1, "price": 10, "desc": "Bronza quyishda misga qo'shiladigan komponent."},
    "ore_lead": {"id": "ore_lead", "name": "🗿 Qo'rg'oshin Rudasi", "tier": 1, "price": 18, "desc": "Og'ir to'qmoqlar va muhrlar tayyorlash uchun ishlatiladi."},
    "ore_zinc": {"id": "ore_zinc", "name": "🪙 Rux Rudasi", "tier": 1, "price": 14, "desc": "Metallarni zanglashdan asraydigan qoplama xomashyosi."},

    "ore_silver": {"id": "ore_silver", "name": "🥈 Sof Kumush", "tier": 2, "price": 45, "desc": "Vampir va qorong'ulik maxluqlariga qarshi qurollar yasash uchun muqaddas metall."},
    "ore_gold": {"id": "ore_gold", "name": "🪙 Oltin Ruda", "tier": 2, "price": 60, "desc": "Qirollik tangalari va oliy ritsar anjomlarini bezash uchun qimmatbaho metall."},
    "ore_steel_ingot": {"id": "ore_steel_ingot", "name": "⚔️ Damashq Po'lati Quyma", "tier": 2, "price": 50, "desc": "Temir va uglerod qorishmasidan olingan o'ta mustahkam tig' xomashyosi."},
    "ore_pyrite": {"id": "ore_pyrite", "name": "✨ Pirit (Soxta Oltin)", "tier": 2, "price": 30, "desc": "Uchqun chiqaruvchi mineral, olovli damlamalar uchun kerak bo'ladi."},
    "ore_magnetite": {"id": "ore_magnetite", "name": "🧲 Magnit Tosh", "tier": 2, "price": 40, "desc": "Kompuslar va temir tortuvchi qalqonlar yasashda ishlatiladi."},

    "ore_mithril": {"id": "ore_mithril", "name": "💎 Moviy Mithril Rudasi", "tier": 3, "price": 120, "desc": "Ipakdek yengil, ammo po'latdan 10 barobar qattiq sehrli tog' metalli."},
    "ore_obsidian": {"id": "ore_obsidian", "name": "🌋 Qora Vulqon Obsidiyani", "tier": 3, "price": 140, "desc": "Magma tez sovishidan hosil bo'lgan, shishadek o'tkir qora tosh."},
    "ore_titanium": {"id": "ore_titanium", "name": "🥊 Titan Bo'lagi", "tier": 3, "price": 160, "desc": "Tog' gigantlarining zirhlariga teng keladigan yengil va mustahkam metall."},
    "ore_cobalt": {"id": "ore_cobalt", "name": "🔷 Moviy Kobalt Tosh", "tier": 3, "price": 110, "desc": "Muzli runalarni o'zida ushlab turish uchun mos keluvchi sovuq ruda."},
    "ore_blood_iron": {"id": "ore_blood_iron", "name": "🩸 Qonli Temir", "tier": 3, "price": 150, "desc": "Qonxo'r ritsarlar qurollari uchun maxsus qizil rangli ruda."},

    "ore_adamantite": {"id": "ore_adamantite", "name": "💠 Yashil Adamantit", "tier": 4, "price": 350, "desc": "Dunyoning eng qadimiy qatlamlaridan olinadigan sinmas kristall metall."},
    "ore_orichalcum": {"id": "ore_orichalcum", "name": "🟠 Orixalk Quyma", "tier": 4, "price": 380, "desc": "Yo'qolgan Atlantida qirollarining quyosh nurlarini o'zida jamlovchi sarg'ish metalli."},
    "ore_dragonstone": {"id": "ore_dragonstone", "name": "🐉 Ajdaho Toshi", "tier": 4, "price": 420, "desc": "Ajdaho uyasidan topilgan, ichida olov yonib turadigan issiq tosh."},
    "ore_void_shard": {"id": "ore_void_shard", "name": "🌌 Bo'shliq Kristall Parchasi", "tier": 4, "price": 450, "desc": "Zulmat tubidan yig'ib olingan, gravitatsiyani o'zgartiruvchi materiya."},
    "ore_meteorite": {"id": "ore_meteorite", "name": "☄️ Samoviy Meteorit Po'lati", "tier": 4, "price": 500, "desc": "Osmondan qulagan yulduz toshidan eritilgan afsonaviy xomashyo."},

    "ore_aetherium": {"id": "ore_aetherium", "name": "💫 Efirium Sof Donasi", "tier": 5, "price": 1200, "desc": "Farishtalar temirxonasida osmon nuri bilan toblangan ilohiy metall."},
    "ore_chronocite": {"id": "ore_chronocite", "name": "⏳ Xronotsit (Vaqt Toshi)", "tier": 5, "price": 1500, "desc": "Vaqt oqimini sekinlashtirish yoki tezlashtirish qobiliyatiga ega qum kristall."},
    "ore_chaos_core": {"id": "ore_chaos_core", "name": "💥 Xaos Magma Yadrosi", "tier": 5, "price": 1800, "desc": "Portlash xavfi yuqori bo'lgan, qurollarga halokatli zarar beruvchi yadro."},
    "ore_genesis_matter": {"id": "ore_genesis_matter", "name": "🌟 Borliq Ibtidosi Materiyasi", "tier": 5, "price": 2500, "desc": "Dunyoni yaratilishida ishlatilgan birinchi moddiy zarra."},
    "ore_oblivion_ingot": {"id": "ore_oblivion_ingot", "name": "💀 Fano va Yo'qlik Qora Quymasi", "tier": 5, "price": 3000, "desc": "Barcha narsani o'z domiga tortib yo'q qiluvchi mutloq qora jism."}
}

# 2. ALXIMIK O'TLAR VA MASALLIQLAR (35 TA)
HERBS_DATABASE = {
    "herb_wild_mint": {"id": "herb_wild_mint", "name": "🌿 Yovvoyi Tog' Yalpizi", "desc": "Oddiy tetiklashtiruvchi va og'riq qoldiruvchi o't."},
    "herb_dandelion": {"id": "herb_dandelion", "name": "🌼 Sariq Momaqaymoq", "desc": "Staminani tiklashga yordam beruvchi dala o'simligi."},
    "herb_chamomile": {"id": "herb_chamomile", "name": "🌾 Oq Moychechak", "desc": "Asablarni tinchlantirib, Sanity tushishini sekinlashtiradi."},
    "herb_nettle": {"id": "herb_nettle", "name": "🌱 Tikanli Qichitqi O't", "desc": "Qon aylanishini tezlashtiruvchi achchiq o'simlik."},
    "herb_clover": {"id": "herb_clover", "name": "🍀 To'rt Bargli Omadli Beda", "desc": "Kritik zarba berish imkonini biroz oshiruvchi kamyob giyoh."},

    "herb_wolfsbane": {"id": "herb_wolfsbane", "name": "🐺 Bo'ri Qotili Zaharli O'ti", "desc": "Yirtqichlarning hid bilish qobiliyatini yo'qotuvchi zaharli ildiz."},
    "herb_blood_berry": {"id": "herb_blood_berry", "name": "🍓 Qonli Rezavor Gilos", "desc": "Qon hosil bo'lishini tezlashtiruvchi qizil meva."},
    "herb_frost_lichen": {"id": "herb_frost_lichen", "name": "❄️ Muzlagan Qoya Qirishqi", "desc": "Kuyish jarohatlarini bir zumda sovituvchi ayozli mox."},
    "herb_desert_aloe": {"id": "herb_desert_aloe", "name": "🌵 Sahro Qaldirg'och Aloesi", "desc": "Chanqoqni bosuvchi va tanani quyoshdan asrovchi sharbatli o'simlik."},
    "herb_nightshade": {"id": "herb_nightshade", "name": "🌑 Qora Ituzum Zahari", "desc": "Kuchli zaharli qorishmalar uchun halokatli masalliq."},

    "herb_mandrake": {"id": "herb_mandrake", "name": "🌱 Chiyillovchi Mandragora Ildizi", "desc": "Yer ostidan sug'urilganda insonni qulog'ini qomatga keltiruvchi sehrli ildiz."},
    "herb_black_rose": {"id": "herb_black_rose", "name": "🌹 Qora Motam Atirguli", "desc": "Zulmat kultistlarining qonli rituallarida ishlatiladigan sirli gul."},
    "herb_fire_blossom": {"id": "herb_fire_blossom", "name": "🔥 Doim Yonuvchi Olov Gul", "desc": "Suvda ham o'chmaydigan, g'azab eliksirlari uchun asos."},
    "herb_ghost_mushroom": {"id": "herb_ghost_mushroom", "name": "🍄 Tungi Arvoh Qo'ziqorini", "desc": "Qorong'ida moviy nur taratuvchi, ko'rinmaslik eliksiriga qo'shiladigan zamburug'."},
    "herb_dragon_lily": {"id": "herb_dragon_lily", "name": "🐉 Ajdaho Nafasi Nilufari", "desc": "Ajdaho qoni to'kilgan tuproqda unib chiqadigan qudratli gul."},

    "herb_celestial_lotus": {"id": "herb_celestial_lotus", "name": "🪷 Samoviy Oq Lotos", "desc": "Muqaddas ko'llarda yuz yilda bir marta ochiladigan ruhiy gul."},
    "herb_void_orchid": {"id": "herb_void_orchid", "name": "🌌 Bo'shliq Qora Orxideyasi", "desc": "Quyosh nuri tushmaydigan zindon qa'rida o'suvchi g'alati o'simlik."},
    "herb_phoenix_ash_grass": {"id": "herb_phoenix_ash_grass", "name": "🌾 Feniks Kuli O'ti", "desc": "O'lgan jismni tiriltirish quvvatiga ega eng oliy eliksir komponenti."},
    "herb_snake_venom": {"id": "herb_snake_venom", "name": "🐍 Kobra Sof Zahri", "desc": "Qurollarni zahar bilan qoplash uchun quyuq konsentrat."},
    "herb_spider_silk_essence": {"id": "herb_spider_silk_essence", "name": "🕸 Bo'shliq O'rgimchagi Ipak Ekstrakti", "desc": "Tuzoqlar va yopishqoq damlamalar tayyorlash uchun."},

    "herb_honey_comb": {"id": "herb_honey_comb", "name": "🍯 Tog' Yovvoyi Asali", "desc": "Damlamalarni shirin qilish va darmon berish uchun tabiiy masalliq."},
    "herb_spring_water": {"id": "herb_spring_water", "name": "💧 Muqaddas Chashma Suvi", "desc": "Barcha eliksirlarning asosini tashkil etuvchi billur suv."},
    "herb_troll_fat": {"id": "herb_troll_fat", "name": "🧈 Muzlik Trolli Yog'i", "desc": "Yaralarni tezda choklab yuboruvchi qalin moy."},
    "herb_bone_dust": {"id": "herb_bone_dust", "name": "🦴 Oq Suyak Kukuni", "desc": "Kalsiy va mustahkamlik beruvchi qadimiy qabr kukuni."},
    "herb_sulfur": {"id": "herb_sulfur", "name": "🌋 Sof Oltingugurt", "desc": "Portlovchi va olovli aralashmalar uchun kimyoviy element."}
}

# 3. ELIKSIRLAR VA RETSEPTLAR (40 TA)
POTIONS_DATABASE = {
    # Shifobaxsh Damlamalar
    "pot_heal_small": {"id": "pot_heal_small", "name": "🧪 Kichik Shifo Damlamasi", "hp_restore": 50, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "+50 HP darhol davolaydi."},
    "pot_heal_medium": {"id": "pot_heal_medium", "name": "🧪 O'rta Shifo Damlamasi", "hp_restore": 120, "stamina_restore": 20, "sanity_restore": 0, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "+120 HP va +20 Stamina tiklaydi."},
    "pot_heal_great": {"id": "pot_heal_great", "name": "🧪 Buyuk Qirollik Eliksiri", "hp_restore": 300, "stamina_restore": 50, "sanity_restore": 20, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "+300 HP, +50 Stamina va +20 Sanity tiklaydi."},
    "pot_full_restore": {"id": "pot_full_restore", "name": "✨ Boqiy To'liq Qayta Tiklanish Zardobi", "hp_restore": 9999, "stamina_restore": 100, "sanity_restore": 100, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "Jon, Stamina va Sanity'ni 100% to'ldiradi."},

    # Jangovar Kuchaytirgichlar (Buffs)
    "pot_rage_potion": {"id": "pot_rage_potion", "name": "🔥 G'azab Damlamasi (+30% ATK)", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": 30, "def_buff": -10, "battles": 3, "desc": "Keyingi 3 ta jangda hujum kuchingizni +30% ga oshiradi."},
    "pot_stone_skin": {"id": "pot_stone_skin", "name": "🪨 Tosh Teri Damlamasi (+40% DEF)", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": -10, "def_buff": 40, "battles": 3, "desc": "Keyingi 3 ta jangda mudofaa kuchingizni +40% ga oshiradi."},
    "pot_speed_haste": {"id": "pot_speed_haste", "name": "💨 Shamol Tezligi Damlamasi (+50% Crit)", "hp_restore": 0, "stamina_restore": 50, "sanity_restore": 0, "atk_buff": 15, "def_buff": 10, "battles": 2, "desc": "Kritik zarba berish ehtimolini 2 barobarga oshiradi."},
    "pot_titan_strength": {"id": "pot_titan_strength", "name": "🥊 Titan Qudrati Eliksiri (+50 ATK, +50 DEF)", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": 50, "def_buff": 50, "battles": 5, "desc": "Keyingi 5 ta jangda mutloq ustunlik ta'minlaydi."},

    # Zulmat va Sanity Eliksirlari
    "pot_sanity_balm": {"id": "pot_sanity_balm", "name": "🧠 Tinchlik va Aql Balzami (+50 Sanity)", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": 50, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "Miyani vasvasalardan tozalaydi, Sanity'ni +50 ga oshiradi."},
    "pot_antidote_pure": {"id": "pot_antidote_pure", "name": "🧪 Universal Zahar Qaytargich", "hp_restore": 30, "stamina_restore": 0, "sanity_restore": 10, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "Barcha turdagi zaharlanishlarni darhol to'xtatadi."},
    "pot_bone_knitter": {"id": "pot_bone_knitter", "name": "🦴 Suyak Ulovchi Shifobaxsh Moy", "hp_restore": 80, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "Sinish va og'ir travmalarning 50% ni davolaydi."},
    "pot_demon_blood": {"id": "pot_demon_blood", "name": "🩸 Iblis Qoni Qorishmasi (+50% Lifesteal)", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": -15, "atk_buff": 40, "def_buff": 0, "battles": 3, "desc": "Jangda urilgan zarbaning yarmini jonga aylantiradi, ammo Sanity tushadi."},

    # O'ziga Xos Va Kamyob Damlamalar
    "pot_invisibility": {"id": "pot_invisibility", "name": "🌑 Ko'rinmaslik Soyasi Eliksiri", "hp_restore": 0, "stamina_restore": 0, "sanity_restore": 0, "atk_buff": 20, "def_buff": 30, "battles": 1, "desc": "1 ta jangda dushmanning dastlabki zarbasidan 100% chetlanadi."},
    "pot_phoenix_tears": {"id": "pot_phoenix_tears", "name": "🔥 Feniks Ko'z Yoshi (O'limdan Tirilish)", "hp_restore": 500, "stamina_restore": 100, "sanity_restore": 100, "atk_buff": 0, "def_buff": 0, "battles": 0, "desc": "Jangda halok bo'lganda to'liq jon bilan qayta oyoqqa turish imkoni."}
}

# 4. ELEMENTAR RUNALAR KOMBINATSIYASI (20 TA)
RUNES_RECIPES = {
    "flame_edge": {"name": "🔥 Olovli Tig' Afsuni", "runes": ["fire_rune", "fire_rune"], "effect": "+35 Olovli Zarba, dushman yonadi."},
    "ice_paralysis": {"name": "❄️ Ayoz Muzlatuvchi Afsuni", "runes": ["frost_rune", "frost_rune"], "effect": "Dushman 1 raund qimirlay olmaydi (Freeze)."},
    "thunder_pierce": {"name": "⚡️ Chaqmoq Qalqon Teshuvchi", "runes": ["lightning_rune", "lightning_rune"], "effect": "Dushman himoyasini e'tiborga olmaydi (100% Armor Pierce)."},
    "elemental_chaos": {"name": "🌪 Elementar Xaos To'lqini", "runes": ["fire_rune", "frost_rune", "lightning_rune"], "effect": "+75 Aralash Elementar Zarba va qon oqishi."},
    "vampiric_shadow": {"name": "🩸 Zulmat Qonxo'r Runasi", "runes": ["fire_rune", "lightning_rune"], "effect": "30% Lifesteal va dushman staminasini so'rish."},
    "frostfire_blast": {"name": "🔮 Muz-Olov Portlashi", "runes": ["fire_rune", "frost_rune"], "effect": "Dushmanning qurolini sindirish ehtimoli 25%."}
}

def get_ore(ore_id: str):
    return ORES_DATABASE.get(ore_id)

def get_herb(herb_id: str):
    return HERBS_DATABASE.get(herb_id)

def get_potion(potion_id: str):
    return POTIONS_DATABASE.get(potion_id)

def get_rune_recipe(recipe_id: str):
    return RUNES_RECIPES.get(recipe_id)
