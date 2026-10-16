# 🔍 VALORIYA — KOD BAZASI AUDITI VA ARXITEKTURA XARITASI (FAZA 0)

**Hujjat maqsadi:** `docs/NPC_PLAN.md` talabiga asosan mavjud kod bazasini to'liq xaritalashtirish, NPC/AI qismlarini aniqlash, ma'lumotlar bazasi va asinxron fond jarayonlarini tahlil qilish hamda `npc/` paketini qo'shish xavflarini baholash.

**Qoida:** Ushbu fazada mavjud o'yin kodiga hech qanday o'zgartirish kiritilmaydi. Faqat tahlil va hujjatlashtirish.

---

## 1. REPO FAYLLAR XARITASI (FILE MAP)

```
ritsarlar_qirolligi/
├── main.py                     # Asosiy kirish nuqtasi, aiohttp web-server (Render port), routerlar, bot polling
├── config.py                   # Konfiguratsiya: BOT_TOKEN, DB_PATH, OWNER_ID (648616238), OWNER_USERNAME ("nakama_02")
├── requirements.txt            # Bog'liqliklar: aiogram, aiosqlite, aiohttp, pillow, python-dotenv, python-docx
├── Procfile                    # Render deploy: worker: python main.py
├── generate_master_doc.py      # Word (.docx) formatidagi master ensiklopediya generatori
├── VALORIYA_BOT_MASTER_QOLLANMA.docx # Generatsiya qilingan rasmiy Word qo'llanma
├── database/
│   ├── db.py                   # 23 ta SQL jadvali, migratsiyalar, barcha DB yordamchi asinxron funksiyalari (2700+ qator)
│   └── valoriya.db             # SQLite ma'lumotlar bazasi fayli
├── game/
│   ├── constants.py            # 12 ta imperiya (KINGDOMS), 12 tana zonasi (HIT_ZONES), klasslar, bot nomlari
│   ├── emotions_engine.py      # 12 hukmdor AI hissiyotlari, "Paxta qo'yish" va haqorat tahlili (Test 6)
│   ├── npc_engine.py           # Bot ritsarlar generatsiyasi, 4 ta persona (berserk, defender, poisoner, coward) (Test 5)
│   ├── npc_broadcaster.py      # Guruhlar uchun avtonom kutilmagan duel, dervish drop va farmonlar
│   ├── battle_engine.py        # 12-zonali kinetik jang fizikasi, stamina, qalqon, runalar va qon ketishi (Test 4)
│   ├── dark_engine.py          # Sanity (0-100%), 15 ta og'ir travmalar, Iblis Morvath bilan Qonli Ahd (Test 10)
│   ├── procedural_loot.py      # 125,000+ protsessual qurollar generatori (25 prefiks x 200 baza x 25 suffiks) (Test 16)
│   ├── mutation_engine.py      # 4,600+ mutant maxluqlar generatori (5 unvon x 20 mutatsiya) (Test 16)
│   ├── dungeon_generator.py    # 1,000 ta protsessual zindon xonalari generatori (Test 16)
│   ├── skills_engine.py        # 9 ta mutaxassislik, 135 ta mahorat tuguni, 675 ta talant darajalari (Test 17)
│   ├── pets_engine.py          # 960 ta jangovar hamroh va miniklar (30 zot x 4 evolyutsiya x 8 aspekt) (Test 17)
│   ├── battle_pass.py          # 50 ta darajali mavsumiy Battle Pass hisob-kitoblari (Test 18)
│   ├── tavern_games.py         # Omad G'ildiragi (8 slot) va Suyak jangi (Dice duel) (Test 18)
│   ├── expeditions_engine.py   # 5 ta oflayn AFK ekspeditsiya hududlari va o'ljalari (Test 18)
│   ├── promo_engine.py         # 6 ta rasmiy reklama promokodlari dvigateli (Test 19)
│   ├── ascension_engine.py     # 10 darajali Prestij / Ascension (I–X) tizimi (Test 19)
│   ├── tower_engine.py         # 100 qavatli Cheksiz Tubsizlik Minorasi va 10 ta Milestone Bosslari (Test 19)
│   ├── runewords_engine.py     # 20 qadimiy runa, 8,000 formula, 120,000+ runozuvlar sintezi (Test 19)
│   ├── items_db.py             # 200 ta katalog anjomlari bazasi (Test 15)
│   ├── bestiary.py             # 40+ maxluqlar ensiklopediyasi (Test 15)
│   ├── alchemy_db.py           # Rudalar (25), o'tlar (20), eliksirlar (14) (Test 15)
│   ├── quest_db.py             # 25 ta asosiy kvest, 10 ta global qidiruvdagi jinoyatchi (Test 15)
│   ├── lore_db.py              # Taverna mish-mishlari, qadimiy bitiklar, xazina xaritalari (Test 15)
│   └── retention_engine.py     # Kundalik streak va retention hisoblash yordamchilari
├── handlers/                   # 21 ta aiogram Router() modullari
│   ├── start_handler.py        # /start, yangi o'yinchi va sinf tanlash
│   ├── menu_buttons_handler.py # Asosiy reply va inline menyular, 1400+ qator (Tower, Promo, Prestige, AFK, Pets...)
│   ├── arena_handler.py        # 1v1 PvP / PvE duel janglari
│   ├── kingdom_handler.py      # 12 imperiya saroyi va hukmdor bilan muloqot
│   ├── inventory_handler.py    # 8-slotli anjomlar sumkasi va avto-kiyinish
│   ├── market_handler.py       # Jonli o'yinchilar P2P bozori (3% soliq)
│   ├── guild_handler.py        # Gildiyalar va qal'a qamallari
│   ├── trade_travel_handler.py # Shaharlararo karvon tijorati (Samarqand, Muzli Cho'qqi...)
│   ├── tournament_handler.py   # Valoriya Oliy Taxti va qirolga duel
│   ├── owner_handler.py        # Owner God-Mode buyruqlari (faqat @nakama_02)
│   └── ... (boshqa yordamchi routerlar)
├── keyboards/
│   ├── reply_keyboards.py      # Doimiy pastki ReplyKeyboardMarkup (O'yinchi va Owner menyulari)
│   └── inline_menus.py         # Asosiy inline menyular, arena, kiyim, God-Mode (1 va 2-sahifa)
├── services/
│   └── card_generator.py       # Pillow bilan 800x530 o'lchamli dinamik Ritsar Pasportini chizish
├── tests/
│   └── test_all.py             # 19 ta yirik testlar majmuasi (hammasi 100% yashil)
└── docs/
    ├── NPC_PLAN.md             # Yangi NPC Aql (Tirik Dunyo) mega rejasi
    └── AUDIT.md                # Ushbu audit hisoboti
```

---

## 2. HOZIRGI NPC, AI PERSONA VA BOT RITSARLARNING JOYLASHUVI

| Mexanika | Hozirgi Fayl | Hozirgi Amalga Oshirilishi |
|---|---|---|
| **12 Hukmdor Shaxsiyati** | `game/constants.py` | `KINGDOMS` lug'ati: `id`, `name`, `ruler`, `capital`, `motto`, `personality` (`pride`, `anger`, `calm`, `greed`, `diplomat`, `wrath`, `wild`, `treason`, `greedy_wild`, `cold`, `fanatic`, `wise`), `specialty`, `bonus`, `voice_style`. |
| **Hissiyotlar va "Paxta" Tahlili** | `game/emotions_engine.py` | `EmotionsEngine.evaluate_player_speech`: 19 ta `FLATTERY_KEYWORDS`, 11 ta `INSULT_KEYWORDS`. Hukmdor personasi bo'yicha `rage`, `pleased`, `disgusted` qaytaradi va oltin/hurmat beradi (Test 6). |
| **Bot Ritsarlar** | `game/npc_engine.py` | `NPCEngine.generate_bot_knight`: target level bo'yicha stats, nom va 4 ta personadan birini (`berserk`, `defender`, `poisoner`, `coward`) beradi (Test 5). `NPCEngine.choose_bot_action`: HP va personaga qarab zarba/qalqon/taslim bo'lishni tanlaydi. |
| **Guruhdagi NPC Avtonom Harakatlari** | `game/npc_broadcaster.py` | `NPCBroadcaster.generate_spontaneous_event`: tasodifiy duel taklifi, darvesh o'ljasi, taverna mish-mishi yoki sulton farmoni. |
| **Mavjud Testlar** | `tests/test_all.py` | `[TEST 5]` (Bot ritsarlar generatsiyasi) va `[TEST 6]` (AI his-tuyg'ulari va paxta/haqorat tahlili). |

---

## 3. MA'LUMOTLAR BAZASIGA KIRISH USLUBI (DB ACCESS PATTERN)

1. **Ulanish Usuli:**
   * `database/db.py` faylida `get_connection()` funksiyasi `aiosqlite.connect(DB_PATH)` obyektini qaytaradi.
   * Barcha so'rovlar `async with get_connection() as db:` kontekst menejeri orqali bajariladi.
2. **Jadvallar Soni:** Hozirda 23 ta jadval mavjud (jadvallar 1 dan 23 gacha `init_db()` ichida initsializatsiya qilinadi).
3. **Tranzaksiyalar va Xavfsizlik:**
   * SQLite da bir vaqtning o'zida bir nechta parallel ulanishlar yozishni boshlasa `database locked` xatosi kelib chiqmasligi uchun o'quv so'rovlari va yozuv so'rovlari qisqa ushlab turiladi.
   * `db.commit()` tranzaksiyani yopish uchun qo'llanadi.
   * Hozirda SQLite **WAL (Write-Ahead Logging)** rejimi yoqilmagan. Yangi `npc/` paketida foniy scheduler ko'p yozishini hisobga olsak, `PRAGMA journal_mode = WAL;` va `PRAGMA synchronous = NORMAL;` yoqilishi shart.

---

## 4. HANDLERLAR VA ROUTERLARNI RO'YXATDAN O'TKAZISH

* `main.py` barcha 21 ta routerni import qilib, `dp.include_router(...)` orqali Dispatcherga ulaydi.
* Har bir router mustaqil modul bo'lib, o'zining `CallbackQuery` va `Message` filtrlariga ega.
* Yangi NPC buyruqlari (`/court`, `/bribe`, `/loan`, `/rumors`, `/npc_mood`) Faza 8 da alohida `npc_router` sifatida `handlers/` ichida yaratiladi va `main.py` ga minimal 1 qatorlik diff bilan ulanadi.

---

## 5. BACKGROUND (FONIY) VAZIFALAR QANDAY ISHLAYDI?

* `main.py` da `await dp.start_polling(bot)` oldidan `asyncio.create_task(npc_periodic_broadcaster_loop(bot))` chaqiriladi.
* Render.com Free Tier servislari HTTP ping bo'lmasa uxlab qolishi sababli, `main.py` ichida engil `aiohttp.web.Application` ishga tushirilgan bo'lib, 8080-portda `/` va `/health` pinglarini qabul qiladi.
* Yangi `npc/scheduler.py` foni xuddi shu tarzda `asyncio.create_task(...)` orqali ishga tushadi va `NPC_PLAN.md` 14-bo'limidagi **Catch-up qoidasiga (uxlab qolib uyg'onganda maksimal 6 ta tick)** amal qilishi shart.

---

## 6. YANGI `npc/` PAKETINI QO'SHISH XAVFLARI VA ULARNING OLDINI OLISH

| Xavf | Nima sababdan bo'lishi mumkin | Oldini olish choralari |
|---|---|---|
| **SQLite Qulflanishi (Database Locked)** | Scheduler va o'yinchilar bir vaqtda DB ga yozganda. | Faza 1 da `PRAGMA journal_mode = WAL;` yoqiladi. Barcha NPC yozuvlari qisqa tranzaksiya va batch (to'p) rejimida bajariladi. |
| **Mavjud Testlar 5 va 6 ning buzilishi** | `npc_engine.py` yoki `emotions_engine.py` o'chirib yuborilsa. | Ushbu fayllar saqlanadi va yangi `npc/` dvigateli bilan integratsiya qilinadi. Test 5 va 6 100% yashil qoladi. |
| **Render Free-Tier RAM Yetishmasligi (OOM)** | Ko'p JSON xotirada ushlab turilsa yoki 200 ta bot bir vaqtda xotirani to'ldirsa. | JSON ma'lumotlar lazy-load (kerak bo'lganda yuklanib o'chiriladi), botlar esa batch rejimida (har tickda ko'pi bilan 20 ta) aylanadi. |
| **Doiraviy Import (Circular Imports)** | `npc/` paketi `database/db.py` ni import qilganda va aksincha. | Toza ierarxiya: `npc/` barcha kerakli funksiyalarni `database/db.py` dan oladi, ammo `db.py` global darajada `npc/` ni import qilmaydi (faqat funksiya ichida lazy import). |
| **Owner (@nakama_02) Shaxsiga Ta'sir** | NPC soliq, xiroj yoki botlar dueli adashib yaratuvchiga yo'nalsa. | `npc/safety.py` dagi qat'iy qoida: agar target ID `648616238` yoki username `nakama_02` bo'lsa, har qanday NPC salbiy harakati darhol abort qilinadi. |

---

## 7. FAZA 0 AUDIT XULOSASI VA QABUL QILISH

✅ **Audit yakuni:**
* Repo tuzilmasi, barcha bog'liqliklar va mexanikalar to'liq o'rganildi.
* Mavjud kodga hech qanday o'zgartirish kiritilmadi (Zero code changes).
* `docs/NPC_PLAN.md` va `docs/AUDIT.md` fayllari yaratildi.
* Barcha 19 ta mavjud testlar to'liq o'tish holatida.

**Keyingi qadam:** Faza 1 (Jadvallar 24–32 migratsiyasi + `npc/personality.py` + Test 20).
