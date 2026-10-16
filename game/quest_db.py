# =====================================================================
# VALORIYA: ASOSIY KAMPANIYA, FRAKSIYA KVESTLARI VA GLOBAL FARMONLAR
# JAMI 80+ NOYOB TOPSHIRIQ VA QIDIRUVDAGI JINOYATCHILAR (BOUNTIES)
# =====================================================================

# 1. ASOSIY KAMPANIYA MISSİYALARI ("VALORIYA TOJI UCHUN KURASH" - 25 TA)
MAIN_CAMPAIGN_QUESTS = [
    # 1-Bob: Qasamyod va Xiyonat
    {"id": "camp_1_1", "chapter": 1, "title": "⚔️ Ritsarlik Qasamyodi", "goal": "Arenada birinchi jangda g'alaba qozonish", "reward_gold": 150, "reward_xp": 200, "desc": "Valoriya qit'asida o'z ismingizni oqlash uchun maydonga chiqing."},
    {"id": "camp_1_2", "chapter": 1, "title": "🛡 Qurol-aslahani Ta'mirlash", "goal": "Temirchiga borib anjomlarni sozlash", "reward_gold": 100, "reward_xp": 150, "desc": "Siniq qilich bilan dushmanga qarshi chiqib bo'lmaydi."},
    {"id": "camp_1_3", "chapter": 1, "title": "🗺 Zindonga Birinchi Qadam", "goal": "1-Qavat zindon maxluqini yengish", "reward_gold": 250, "reward_xp": 300, "desc": "Go'rkovlar qabriga tushib birinchi maxluqni yo'q qiling."},
    {"id": "camp_1_4", "chapter": 1, "title": "🍻 Taverna Sir-asrorlari", "goal": "Tavernada dervish suhbatini tinglash", "reward_gold": 200, "reward_xp": 250, "desc": "Qonli Qadah mayxonasida xufiyona gap-so'zlarga quloq soling."},
    {"id": "camp_1_5", "chapter": 1, "title": "👑 Gorrikning Boshini Keltirish", "goal": "1-Qavat bossi Gorrikni mahv etish", "reward_gold": 500, "reward_xp": 600, "desc": "Daxmalar xojasini mag'lub etib 2-qavat kalitini qo'lga kiriting."},

    # 2-Bob: 12 Qirollikning Tutashi
    {"id": "camp_2_1", "chapter": 2, "title": "🏰 Bayroq Tanlash", "goal": "12 ta imperiyadan biriga qasamyod qilish", "reward_gold": 300, "reward_xp": 350, "desc": "Valoriya taxti uchun kurashda o'z fraksiyangizni belgilang."},
    {"id": "camp_2_2", "chapter": 2, "title": "🐫 Birinchi Karvon Safari", "goal": "Boshqa shaharga tovar yetkazish", "reward_gold": 400, "reward_xp": 450, "desc": "Samarqanddan Ipak olib Muzli Cho'qqiga yetkazing."},
    {"id": "camp_2_3", "chapter": 2, "title": "⛏ Shaxtada Ter To'kish", "goal": "Shaxtadan 20 ta temir ruda qazish", "reward_gold": 350, "reward_xp": 400, "desc": "Qal'a qurollari uchun zarur bo'lgan po'lat rudasini toping."},
    {"id": "camp_2_4", "chapter": 2, "title": "🧪 Alximiya Sirini Ochish", "goal": "Birinchi shifobaxsh damlamani tayyorlash", "reward_gold": 300, "reward_xp": 350, "desc": "Yalpiz va moychechakdan dori tayyorlab ko'ring."},
    {"id": "camp_2_5", "chapter": 2, "title": "👑 Mumiyo Lordi Halokati", "goal": "2-Qavat bossi Fir'avnni mag'lub etish", "reward_gold": 800, "reward_xp": 900, "desc": "Ming yillik la'natlangan qabrni tozalang."},

    # 3-Bob: Zulmat Qonuni va Morvath Uyg'onishi
    {"id": "camp_3_1", "chapter": 3, "title": "🩸 Qonli Ahd Sinovi", "goal": "Iblis Morvath ibodatxonasiga borish", "reward_gold": 500, "reward_xp": 600, "desc": "Qora sehr ta'sirini o'rganing va Sanity'ni saqlang."},
    {"id": "camp_3_2", "chapter": 3, "title": "🩹 Mayiblikni Davolash", "goal": "Tabibxonada singan suyakni ulatish", "reward_gold": 400, "reward_xp": 500, "desc": "Jangda olingan og'ir travmani davolang."},
    {"id": "camp_3_3", "chapter": 3, "title": "🔥 Olovli Qassob Jallodi", "goal": "3-Qavat bossi Butcher'ni yiqitish", "reward_gold": 1200, "reward_xp": 1400, "desc": "Qonli laboratoriyadagi qassobni yo'q qiling."},
    {"id": "camp_3_4", "chapter": 3, "title": "🐂 Minotavr Labirinti", "goal": "4-Qavat labirintidan o'tish", "reward_gold": 1500, "reward_xp": 1700, "desc": "Asterionning labirintidan tirik chiqing."},
    {"id": "camp_3_5", "chapter": 3, "title": "❄️ Ayoz Qirolichasi Freya", "goal": "5-Qavat muz taxtini egallash", "reward_gold": 2000, "reward_xp": 2200, "desc": "Muzli Cho'qqi daxlsizligini sindiring."},

    # 4-Bob: Qal'alar Qamali va Qonli Taxt
    {"id": "camp_4_1", "chapter": 4, "title": "🏰 Ritsarlar Gildiyasi", "goal": "Gildiya tuzish yoki unga a'zo bo'lish", "reward_gold": 1000, "reward_xp": 1200, "desc": "Yolg'iz ritsar tez halok bo'ladi, qardoshlik safiga kiring."},
    {"id": "camp_4_2", "chapter": 4, "title": "⚔️ Qal'a Qamaliga Hujum", "goal": "Ajdaho Qal'asi devorlariga zarba berish", "reward_gold": 2500, "reward_xp": 2800, "desc": "Qal'a xazinasidan ulush olish uchun hujum qiling."},
    {"id": "camp_4_3", "chapter": 4, "title": "🛒 Bozor Monopoliyasi", "goal": "P2P bozorda 5 ta savdo bitimi tuzish", "reward_gold": 1500, "reward_xp": 1800, "desc": "Qirollik iqtisodiyotining asosiy tayanchiga aylaning."},
    {"id": "camp_4_4", "chapter": 4, "title": "👑 Valoriya Qiroli Bo'lish", "goal": "Turnirda g'alaba qozonib Taxtga o'tirish", "reward_gold": 5000, "reward_xp": 6000, "desc": "Barcha 12 qirollik ustidan mutloq toj kiying."},
    {"id": "camp_4_5", "chapter": 4, "title": "👑 O'lim Lordi Malgazarni Yengish", "goal": "9-Qavat do'zax darvozasini ochish", "reward_gold": 8000, "reward_xp": 9000, "desc": "Iblislar sarkardasini mag'lub eting."},

    # 5-Bob: Boqiy Imperatorlik
    {"id": "camp_5_1", "chapter": 5, "title": "🌌 Bo'shliqqa Qadam", "goal": "10-Qavat Zulmat Taxtiga yetib borish", "reward_gold": 10000, "reward_xp": 12000, "desc": "Valoriya qa'ridagi qora materiya sarhadlariga kiring."},
    {"id": "camp_5_2", "chapter": 5, "title": "🐉 Ajdaho Bahamut Reydi", "goal": "Dunyo bossi Bahamutga kamida 1,000 zarar berish", "reward_gold": 15000, "reward_xp": 18000, "desc": "Olamni vayron qiluvchi qora ajdahoga qarshi kurashing."},
    {"id": "camp_5_3", "chapter": 5, "title": "🔥 Feniks O'lmaslik Sirlari", "goal": "Olovli Feniksni mag'lub etish", "reward_gold": 20000, "reward_xp": 22000, "desc": "O'z kulidan qayta tiriluvchi qushni qulatish."},
    {"id": "camp_5_4", "chapter": 5, "title": "👑 QORA LORD MORVATH HALOKATI", "goal": "10-Qavat Bosh Bossi Morvathni yakson etish", "reward_gold": 50000, "reward_xp": 50000, "desc": "Zulmat xudosini yo'q qilib Valoriya qit'asini qutqaring!"},
    {"id": "camp_5_5", "chapter": 5, "title": "🏆 Boqiy Valoriya Afsonasi", "goal": "50-Darajaga erishish va barcha unvonlarni olish", "reward_gold": 100000, "reward_xp": 100000, "desc": "Oliy Yaratuvchi huzurida abadiy shon-sharafga erishing."}
]

# 2. QIDIRUVDAGI XAVFLI JINOYATCHILAR (GLOBAL BOUNTIES - 20 TA)
GLOBAL_BOUNTIES = [
    {"id": "bty_one_eye_jack", "name": "👁 Bir Ko'zli Jek", "crime": "Karvonlarni qirg'in qilgan va qizlarni o'g'irlagan", "reward_gold": 1500, "location": "Sahro yo'llari", "danger": "⭐️⭐️ (2/10)"},
    {"id": "bty_poisoner_vincent", "name": "🧪 Zaharchi Vinsent", "crime": "Qirol favvorasiga zahar quygan alximik", "reward_gold": 2200, "location": "Botqoqlik g'orlari", "danger": "⭐️⭐️⭐️ (3/10)"},
    {"id": "bty_grave_robber_sam", "name": "🦴 Go'rkov Sem", "crime": "Qadimiy fir'avnlar tobutini talagan", "reward_gold": 1800, "location": "Kultepa Qabristoni", "danger": "⭐️⭐️ (2/10)"},
    {"id": "bty_black_knight_renegade", "name": "🗡 Qochqin Qora Ritsar", "crime": "O'z generallari boshini kesib qochgan", "reward_gold": 3500, "location": "Qulagan Qal'a xarobalari", "danger": "⭐️⭐️⭐️⭐️ (4/10)"},
    {"id": "bty_witch_morgana", "name": "🧙‍♀️ Qonxo'r Morgana", "crime": "Qishloqlarga o'lat tarqatgan jodugar", "reward_gold": 4000, "location": "Zulmat O'rmoni", "danger": "⭐️⭐️⭐️⭐️ (4/10)"},
    {"id": "bty_butcher_boris", "name": "🪓 Qonli Boris", "crime": "Sayyohlarni poylab so'yib go'shtini sotgan", "reward_gold": 3200, "location": "Tog' dovoni", "danger": "⭐️⭐️⭐️ (3/10)"},
    {"id": "bty_pirate_kidd", "name": "🏴‍☠️ Qaroqchi Kapitan Kidd", "crime": "Dengiz savdo kemalarini cho'ktirgan", "reward_gold": 4500, "location": "Dengiz porti qoyalari", "danger": "⭐️⭐️⭐️⭐️ (4/10)"},
    {"id": "bty_cult_leader_malok", "name": "🩸 Qonli Kult Rahbari Malok", "crime": "Insonlarni qurbonlik qiluvchi sekta tuzgan", "reward_gold": 5500, "location": "7-Qavat Zulmat Ziyoratgohi", "danger": "⭐️⭐️⭐️⭐️⭐️ (5/10)"},
    {"id": "bty_false_king", "name": "👑 Soxta Qirol Lyudvig", "crime": "Taxtni aldov bilan egallab xazinani talon-taroj qilgan", "reward_gold": 7000, "location": "Yashirin Oltin Qal'a", "danger": "⭐️⭐️⭐️⭐️⭐️ (5/10)"},
    {"id": "bty_shadow_assassin", "name": "🌑 Soya Qotili Zephyr", "crime": "5 ta imperiya elchisini bir tunda qatl etgan", "reward_gold": 8500, "location": "Qora Arsh soyalari", "danger": "⭐️⭐️⭐️⭐️⭐️⭐️ (6/10)"}
]

def get_campaign_quest(quest_id: str):
    for q in MAIN_CAMPAIGN_QUESTS:
        if q["id"] == quest_id:
            return q
    return None

def get_bounty(bounty_id: str):
    for b in GLOBAL_BOUNTIES:
        if b["id"] == bounty_id:
            return b
    return None

def get_all_bounties():
    return GLOBAL_BOUNTIES
