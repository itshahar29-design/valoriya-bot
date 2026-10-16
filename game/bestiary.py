# =====================================================================
# VALORIYA: MAXLUQOTLAR VA DUSHMANLAR ENSIKLOPEDIYASI (BESTIARY)
# =====================================================================

BESTIARY_DATA = {
    # -----------------------------------------------------------------
    # ODDY VA O'RMON MAXLUQLARI (TIER 1)
    # -----------------------------------------------------------------
    "goblin_scout": {
        "id": "goblin_scout", "name": "👺 G'or Goblini Izquvari", "danger": "⭐️ (1/10)",
        "habitat": "Toshli g'orlar va qorong'i o'rmonlar",
        "hp": 90, "atk": 16, "def": 5, "weakness": "Olov va Muqaddas Nur",
        "desc": "Bo'yi 1 metrdan oshmaydigan, makkor va to'da bo'lib hujum qiluvchi maxluq. "
                "Yolg'iz ritsarlarga orqadan tosh va zaharli nayzalar bilan hujum qiladi.",
        "loot": "Temir parchasi, 25-45 🪙 Oltin, Goblin suyagi."
    },
    "dire_wolf": {
        "id": "dire_wolf", "name": "🐺 Qora Dasht Bo'risi", "danger": "⭐️⭐️ (2/10)",
        "habitat": "Dasht Bo'rilari Xonligi kengliklari",
        "hp": 140, "atk": 24, "def": 8, "weakness": "Bo'yin zarbasi va Olov",
        "desc": "Oddiy bo'ridan ikki barobar yirikroq, tishlari po'lat sovutni teshib yuboradigan yirtqich. "
                "Ular kechalari to'lin oy ostida ovga chiqadi.",
        "loot": "Qimmatbaho bo'ri mo'ynasi, Bo'ri qoziq tishi, 50-80 🪙 Oltin."
    },
    "swamp_crawler": {
        "id": "swamp_crawler", "name": "🕷 Botqoqlik Zaharli O'rgimchagi", "danger": "⭐️⭐️ (2/10)",
        "habitat": "Qora botqoqlik va tumanli daryo bo'ylari",
        "hp": 160, "atk": 28, "def": 6, "weakness": "Olov va Momaqaldiroq",
        "desc": "Odam bo'yidek keladigan ulkan o'rgimchak. Nishonini yopishqoq to'r bilan bog'lab, "
                "falajlovchi neyrotoksin zahari bilan qurbonini eritib ichadi.",
        "loot": "Zaharli o'rgimchak bezi, Ipak tola, 70-110 🪙 Oltin."
    },
    "desert_bandit": {
        "id": "desert_bandit", "name": "🗡 Sahro Qaroqchisi Qonxo'r", "danger": "⭐️⭐️⭐️ (3/10)",
        "habitat": "Karvon yo'llari va Qum barxanlari",
        "hp": 210, "atk": 34, "def": 14, "weakness": "Og'ir qalqon va Bosh zarbasi",
        "desc": "Karvonlarni talash bilan tirikchilik qiluvchi qonundan tashqari kimsalar. "
                "Egik shamshir va engil kiyimlarda qum bo'ronlaridan foydalanib pistirma qo'yadi.",
        "loot": "Sharq ziravorlari, 150-250 🪙 Oltin, Qaroqchi shamshiri."
    },
    "skeleton_warrior": {
        "id": "skeleton_warrior", "name": "💀 Qadimiy Qabr Skelet Jangchisi", "danger": "⭐️⭐️⭐️ (3/10)",
        "habitat": "Kultepa qabristoni va yerosti daxmalari",
        "hp": 220, "atk": 36, "def": 22, "weakness": "Og'ir Bolg'alar (Zarba) va Muqaddas Nur",
        "desc": "Yuz yillar avval jang maydonida halok bo'lgan va qora sehr bilan tiriltirilgan jonsiz suyaklar. "
                "Ularga qilich va nayza deyarli ta'sir qilmaydi, faqat og'ir cho'qmorlar bilan parchalash mumkin.",
        "loot": "Zangori xouberk halqalari, 120-190 🪙 Oltin, Suyak kukuni."
    },

    # -----------------------------------------------------------------
    # O'RTA VA ELITA DUSHMANLAR (TIER 2)
    # -----------------------------------------------------------------
    "frost_troll": {
        "id": "frost_troll", "name": "❄️ Muzlik Gigant Trolli", "danger": "⭐️⭐️⭐️⭐️ (4/10)",
        "habitat": "Muzli Cho'qqilar va Ayoz tog'lari",
        "hp": 450, "atk": 48, "def": 18, "weakness": "🔥 Olov Runasi va Yonuvchi Neft",
        "desc": "Uch metrlik bahaybat mahluq. Uning terisi toshdek qalin va tanasidagi har qanday yara "
                "bir necha soniyada qayta bitadi (Regeneratsiya). Faqat olov uning bitishini to'xtatadi.",
        "loot": "Troll yuragi, Qattiq muz kristallari, 300-500 🪙 Oltin."
    },
    "shadow_stalker": {
        "id": "shadow_stalker", "name": "🌑 Zulmat Sharpasi (Kamera Qotili)", "danger": "⭐️⭐️⭐️⭐️⭐️ (5/10)",
        "habitat": "Tumanli Qasr va Zindonlarning 3-qavati",
        "hp": 380, "atk": 62, "def": 12, "weakness": "☀️ Nur Ibodatxonasi Sehrlari",
        "desc": "Fizik tanaga deyarli ega bo'lmagan, soyalardan paydo bo'luvchi qora mavjudot. "
                "U o'yinchining aqlini (Sanity) bir zumda so'rib olib telba qiladi.",
        "loot": "Soya essensiyasi, Sehrli qora mato, 400-650 🪙 Oltin."
    },
    "wyvern_scout": {
        "id": "wyvern_scout", "name": "🦅 Qoya Vivernasi (Uchuvchi Yirtqich)", "danger": "⭐️⭐️⭐️⭐️⭐️ (5/10)",
        "habitat": "Tog' cho'qqilari va Olov qal'asi atrofi",
        "hp": 520, "atk": 58, "def": 25, "weakness": "Qanotiga kamon zarbasi va Muz",
        "desc": "Ikki oyoqli va bahaybat qanotli ajdahosimon yirtqich. Dumidagi zaharli tikan bilan "
                "ritsarni parchalab, o'z iniga olib qochadi.",
        "loot": "Viverna qanot terisi, Zaharli dumi, 500-800 🪙 Oltin."
    },
    "iron_golem": {
        "id": "iron_golem", "name": "🗿 Qadimiy Temir Golem", "danger": "⭐️⭐️⭐️⭐️⭐️⭐️ (6/10)",
        "habitat": "Temir Bastion xarobalari va yerosti ustaxonalari",
        "hp": 750, "atk": 65, "def": 55, "weakness": "⚡️ Chaqmoq Runasi va Sehrli portlash",
        "desc": "Sehrli ruda bilan harakatlantiriladigan ulkan po'lat haykal. "
                "U og'riq sezmaydi, charchamaydi va har bir qadami yerni larzaga keltiradi.",
        "loot": "Sof Mithril bo'lagi, 3x Temir rudasi, 700-1100 🪙 Oltin."
    },

    # -----------------------------------------------------------------
    # AFSONAVIY ZINDON VA DUNYO BOSSLARI (TIER 3 & 4)
    # -----------------------------------------------------------------
    "boss_goblin_king": {
        "id": "boss_goblin_king", "name": "👑 Goblinlar Oliy Hukmdori Grik", "danger": "⭐️⭐️⭐️⭐️⭐️ (5/10)",
        "habitat": "1-Zindon: Zulmat G'ori",
        "hp": 280, "atk": 35, "def": 20, "weakness": "Yurak va Bo'yin zarbalari",
        "desc": "Barcha g'or o'g'rilarining podshohi. O'ldirilgan ritsarlar suyaklaridan yasalgan toj kiyadi.",
        "loot": "👑 Grikning Oltin Qadahi, Kamon, 450 🪙 Oltin."
    },
    "boss_black_knight": {
        "id": "boss_black_knight", "name": "⚔️ La'nati Qora Ritsar Mordred", "danger": "⭐️⭐️⭐️⭐️⭐️⭐️⭐️ (7/10)",
        "habitat": "3-Zindon: Tashlandiq Qasr",
        "hp": 750, "atk": 75, "def": 45, "weakness": "Qalqon teshuvchi Chaqmoq",
        "desc": "O'z qiroliga xiyonat qilgani uchun abadiy qora sovut ichiga qamalgan la'natli ritsar.",
        "loot": "🛡 La'natli Qora Qalqon, 1,500 🪙 Oltin, 5 💎 Javohir."
    },
    "boss_red_dragon": {
        "id": "boss_red_dragon", "name": "🐉 Mag'rur Olov Ajdahosi Ignis", "danger": "⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️ (9/10)",
        "habitat": "Ajdaho Qoyasi va Global Reydlar",
        "hp": 1800, "atk": 125, "def": 65, "weakness": "❄️ Muz Runasi va Qorin sohasi",
        "desc": "Ming yillik uyqudan uyg'ongan ulkan qizil ajdaho. Uning nafasi butun shaharlarni "
                "kulga aylantirishga qodir. Terisidan afsonaviy imperator sovutlari yasaladi.",
        "loot": "🐉 Ajdaho Yuragi, Qizil tangachalar sovuti, 5,000 🪙 Oltin, 25 💎 Javohir."
    },
    "boss_malakor_lich": {
        "id": "boss_malakor_lich", "name": "💀 Boqiy Lich Malakor - Zulmat Egasi", "danger": "⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️ (10/10)",
        "habitat": "Valoriya Taqiqlangan Zindoni (5-Qavat)",
        "hp": 2500, "atk": 160, "def": 80, "weakness": "☀️ Muqaddas Quyosh Nuri",
        "desc": "O'lim ustidan g'alaba qozongan qadimiy qora sehrgar. Uning ko'zlariga qaragan har qanday "
                "ritsar bir zumda o'z aqlini yo'qotadi.",
        "loot": "🩸 Malakor O'rog'i, Zulmat Uzugi, 10,000 🪙 Oltin, 50 💎 Javohir."
    }
}
