# 🏰 VALORIYA — NPC AQL (TIRIK DUNYO) MEGA REJA

**Versiya:** 1.0 | **Asos:** Valoriya v2.5 Ultimate → v3.0
**Joylash:** repo ichida `docs/NPC_PLAN.md` qilib saqlang

―――――――――――――――――――――――――――――

## 0. MAQSAD

- 12 hukmdor o'zi o'ylaydi, his qiladi, eslaydi.
- Ochko'z hukmdor soliq oshiradi, pora oladi, sudxo'rlik qiladi.
- Bot ritsarlar bozorda, arenada, gildiyada o'ynaydi.
- Dunyo o'yinchi yo'q paytda ham yashaydi.
- **LLM kerak emas.** Faqat qoida + formula + shablon.
- Sabab: Render Free-Tier RAM kam.

**Mavjudni buzmaymiz:**
- Test 5 (bot ritsarlar, 4 persona) — kengaytiriladi.
- Test 6 (AI hissiyot, xushomad) — kengaytiriladi.
- Owner (@nakama_02) — NPC unga hech qachon tegmaydi.

―――――――――――――――――――――――――――――

## 1. ANTIGRAVITY UCHUN QOIDALAR

Nega yomon ishlayapti: katta so'rov, kontekst yo'q, testsiz. Quyidagi qoidalar buni tuzatadi.

| # | Qoida | Sababi |
| --- | --- | --- |
| 1 | Bir faza = bir sessiya | Katta so'rovda adashadi |
| 2 | Avval reja, keyin kod | Xatoni oldindan ko'rasiz |
| 3 | Mavjud faylni qayta yozmasin | Faqat minimal diff |
| 4 | Har fazadan keyin pytest | 19 eski test buzilmasin |
| 5 | Bitta fayl ≤ 300 qator | O'qish va tuzatish oson |
| 6 | Faqat async + aiosqlite | Bot qotib qolmasin |
| 7 | Har faza = 1 git commit | Orqaga qaytish oson |
| 8 | Tushunmasa so'rasin | Taxmin qilib buzmasin |
| 9 | Faza oxirida qisqa hisobot | Nima o'zgardi ko'rinsin |

―――――――――――――――――――――――――――――

## 2. TIRIK DUNYO: 6 QATLAM

**Shaxsiyat → Hissiyot → Xotira → Qaror → Harakat → Dialog**

| Qatlam | Nima qiladi | Fayl |
| --- | --- | --- |
| Shaxsiyat | 8 xislat, o'zgarmas asos | `personality.py` |
| Hissiyot | Quvonch, g'azab, qo'rquv (o'zgaruvchan) | `state.py` |
| Xotira | O'yinchi bilan o'tmish | `memory.py` |
| Qaror | 42 harakatdan eng foydalisini tanlash | `utility.py` |
| Harakat | Soliq, urush, pora, reyd... | `actions/*.py` |
| Dialog | Holatga mos gap | `dialogue.py` |

―――――――――――――――――――――――――――――

## 3. PAPKA TUZILMASI

Eslatma: haqiqiy tuzilma Faza 0 audit'da aniqlanadi. Quyidagisi taklif.

```
npc/
  __init__.py
  personality.py
  state.py
  memory.py
  utility.py
  dialogue.py
  rumors.py
  bots.py
  scheduler.py
  safety.py
  actions/
    economy.py
    diplomacy.py
    military.py
    espionage.py
    player_facing.py
  data/dialogue/
    torin.json
    ragnar.json
    ... (12 ta)
docs/
  NPC_PLAN.md
  AUDIT.md
tests/
  test_npc.py
```

―――――――――――――――――――――――――――――

## 4. YANGI JADVALLAR (24–32)

Jami: 23 + 9 = **32 jadval**. Migratsiya idempotent bo'lsin (`schema_version`).

| # | Jadval | Asosiy ustunlar |
| --- | --- | --- |
| 24 | npc_rulers | empire_id, 8 xislat, joy, anger, fear, boredom, treasury, army, unrest, last_tick_at |
| 25 | npc_memory | id, ruler_id, character_id, event_type, trust_d, anger_d, grudge_d, created_at |
| 26 | npc_relations | ruler_id, character_id, trust, suspicion, respect, grudge, last_seen |
| 27 | npc_actions_log | id, ruler_id, action, target, params_json, result, created_at |
| 28 | world_state | key, value_json (embargo, urush, ocharchilik, faol hodisalar) |
| 29 | rumors | id, source_ruler, subject, text_key, is_true, spread, expires_at |
| 30 | npc_loans | id, ruler_id, character_id, principal, rate, due_at, status, collateral_item_id |
| 31 | bot_knights | character_id, archetype, schedule, wallet_limit, last_action_at, state_json |
| 32 | npc_quests | id, ruler_id, character_id, template_key, params_json, status, expires_at |

**Mavjud jadvallarga qo'shimcha:**

| Jadval | Qo'shiladigan ustun |
| --- | --- |
| diplomacy (8) | pact_type, is_secret, since, grievance |
| characters (1) | is_bot (agar yo'q bo'lsa) |

**SQLite qoidalari:** WAL rejimi, qisqa tranzaksiya, batch yozish.

―――――――――――――――――――――――――――――

## 5. SHAXSIYAT: 8 XISLAT × 12 HUKMDOR

Qiymatlar 0–100. Bu **asos** (baseline). Hissiyot unga qaytib turadi.

**Xislatlar:** Och = ochko'zlik, Mag = mag'rurlik, G'az = g'azab, Hiy = hiyla, Sad = sadoqat, Ehs = ehtiyotkorlik, Taq = taqvo, Shu = shuhratparastlik.

| Hukmdor | Persona | Och | Mag | G'az | Hiy | Sad | Ehs | Taq | Shu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Valter V | Kibrli | 40 | 95 | 50 | 40 | 70 | 50 | 60 | 85 |
| Ragnar | G'azabli | 30 | 60 | 95 | 20 | 80 | 15 | 30 | 65 |
| Boris | Vazmin | 35 | 45 | 20 | 50 | 85 | 90 | 55 | 40 |
| **Torin** | **Ochko'z** | **98** | 40 | 35 | 75 | 30 | 70 | 20 | 70 |
| Izabella | Diplomat | 70 | 50 | 15 | 90 | 45 | 75 | 40 | 80 |
| Sulaymon | Qahrli | 55 | 80 | 90 | 35 | 55 | 20 | 45 | 85 |
| Botirxon | Yovvoyi | 45 | 55 | 70 | 45 | 90 | 25 | 35 | 55 |
| Moros | Xoin | 65 | 50 | 45 | 98 | 5 | 80 | 10 | 90 |
| **Qora Soqol** | **Taloqchi** | **90** | 55 | 60 | 70 | 25 | 30 | 15 | 60 |
| Malakor | Muzdek | 40 | 70 | 30 | 80 | 20 | 85 | 5 | 95 |
| Avreliy | Mutassib | 15 | 75 | 65 | 30 | 75 | 40 | 100 | 60 |
| Elenor | Donishmand | 20 | 40 | 10 | 70 | 80 | 85 | 70 | 45 |

**Eslatma:** Izabella (70) va Moros (65) ham ochko'z. Faqat Torin va Qora Soqol ochko'zlikda ustun.

―――――――――――――――――――――――――――――

## 6. HISSIYOT VA MUNOSABAT

### 6.1 Hukmdorning o'z holati

| Holat | Diapazon | Nimaga ta'sir qiladi |
| --- | --- | --- |
| joy (quvonch) | 0–100 | Sovg'a, kechirimlilik |
| anger (g'azab) | 0–100 | Urush, jazo, dushmanona ton |
| fear (qo'rquv) | 0–100 | Mudofaa, zahira yig'ish |
| boredom (zerikish) | 0–100 | Tasodifiy harakat ehtimoli |
| unrest (norozilik) | 0–100 | To'ntarish xavfi |

**Decay (har tick):** `x ← x + (baza − x) × 0.10`

### 6.2 Hukmdor → o'yinchi (har juftlik uchun)

| Qiymat | Diapazon | Ma'nosi |
| --- | --- | --- |
| trust | −100..+100 | Ishonch |
| suspicion | 0..100 | Shubha (xushomad, pora ko'p bo'lsa oshadi) |
| respect | 0..100 | Hurmat (kuch, prestij) |
| grudge | 0..100 | Kek (sekin so'nadi, −1%/kun) |

### 6.3 Hodisa → ta'sir

| Hodisa | trust | anger | grudge |
| --- | --- | --- | --- |
| Katta sovg'a (≥500 🪙) | +5 | −5 | 0 |
| Kichik sovg'a | +1 | 0 | 0 |
| Xushomad | +3 × 0.6ⁿ | 0 | 0 |
| Haqorat | −10 | +20 | +5 |
| Shartnomani buzish | −30 | +15 | +20 |
| Karvonini talash | −20 | +25 | +15 |
| Urushda yordam | +15 | −10 | −10 |
| Pora (qabul qilindi) | −2 | 0 | 0 |

**n** = bugungi xushomadlar soni. Har 3-xushomaddan keyin suspicion +5.

**Persona ko'paytiruvchilari:**
- Haqoratga ta'sir × (1 + Mag/100)
- Sovg'aga ta'sir × (1 + Och/100)
- Xushomadga ta'sir × (1 − Hiy/150)

**Xotira hajmi:** har juftlik uchun ≤ 50 yozuv. Eskilari hisoblagichga siqiladi.

―――――――――――――――――――――――――――――

## 7. OCHKO'ZLIK MODULI (ASOSIY)

### 7.1 Formulalar

| Nima | Formula |
| --- | --- |
| Ehtiyoj | `need = clamp(1 − xazina / maqsad, 0, 1)` |
| Ochko'zlik drayvi | `GD = Och/100 × (0.4 + 0.6 × need)` |
| To'yish | xazina ≥ 120% maqsad → `GD × 0.5` va sarflash rejimi |
| Narx (ask) | `baza × (1 + Och/100)` |
| Pora qabul ehtimoli | `P = clamp(0.10 + 0.60×Och/100 + 0.30×(taklif/narx − 1) − 0.25×Sad/100 − 0.30×shubha/100, 0.02, 0.95)` |
| Xiroj miqdori | `oltin × (2% + 8% × GD)`, cap 15% |
| Soliq ustamasi | `+floor(GD × 10)%`, cap +10%, 24 soat |

**Misol (Torin, xazina 20%):**
need = 0.8 → GD = 0.98 × (0.4 + 0.48) = **0.86**. Soliq +8%, xiroj ~9%.

### 7.2 12 ta ochko'zlik harakati

| # | Harakat | Trigger | Ta'sir | Cooldown |
| --- | --- | --- | --- | --- |
| 1 | Soliq oshirish | xazina < 50% | O'z imperiyasida bozor solig'i +1..10% | 12 soat |
| 2 | Xiroj talab | GD > 0.6, o'yinchi boy | 2–15% oltin so'raydi, rad etsa kek | 24 soat |
| 3 | Pora qabul | O'yinchi taklif qilsa | Formula P. Chegirma yoki ruxsat | Har so'rov |
| 4 | Narx shishirish | Resurs tanqis | NPC do'kon narxi +20..60% | 6 soat |
| 5 | Zahira yig'ish | Narx past | Bot arzon oladi, spike'da sotadi | 8 soat |
| 6 | Sudxo'rlik | O'yinchi so'rasa | `/loan`: 2–5%/kun, ≤ 7 kun | — |
| 7 | Qarz undirish | Muddat o'tdi | Ogohlantirish → bounty (bot qasoskor) | 24 soat |
| 8 | Asir narxi | Asir bor | Ransom × (1 + Och/100) | Har asir |
| 9 | Ikki tomonlama savdo | Ikki taklif keldi | Ikkalasidan pora, fosh bo'lish 25% | 48 soat |
| 10 | Karvon tolli | `/trade` yo'li | Toll 3–12% | Doimiy |
| 11 | Auksion snayperi | Qiymat > narx × 1.3 | Oxirgi 10 soniyada stavka | Har auksion |
| 12 | Xazina sarfi | xazina ≥ 120% | Armiya, qal'a, turnirga sarflaydi | 24 soat |

### 7.3 Ochko'zlik halqasi (yopiq tsikl)

**Xazina kam** → soliq ↑ → norozilik ↑ → mish-mish → to'ntarish xavfi.
**Xazina to'ldi** → to'yish → sarflash → xazina kamayadi → yana boshidan.

**To'ntarish (unrest > 70):**
- Hukmdor 24 soat zaif (DEF −20%).
- Xazinaning 20% yo'qoladi.
- G'azab +30.
- Hukmdor almashmaydi (lore buzilmaydi).

―――――――――――――――――――――――――――――

## 8. QOLGAN 11 PERSONA

Har biri 3 ta imzo harakat.

| Persona | Imzo harakatlar | Trigger |
| --- | --- | --- |
| **Valter** (Kibr) | Turnir o'tkazish; zaif bilan ittifoq rad; kechirim talab qilish | Mag > 80, xazina to'la |
| **Ragnar** (G'azab) | Vendetta e'lon qilish; berserk reyd; sovg'a bilan tinchlanish | Jangda yutqazsa |
| **Boris** (Vazmin) | Vositachilik; arzon tinchlik shartnomasi; chegara patrul | Qo'shni urushda |
| **Izabella** (Diplomat) | Ittifoq broker; ma'lumot sotish; bank qarzi | Shu > 70 |
| **Sulaymon** (Qahr) | Urush e'lon; kuygan yer; olov yurishi | G'az > 70 va dushman zaif |
| **Botirxon** (Yovvoyi) | Karvon reydi; ittifoqchiga otliq berish; qabila chaqiruvi | Sad yuqori |
| **Moros** (Xoin) | Maxfiy pakt; ittifoqni sotish; mish-mish zaharlash | Foyda > Sad |
| **Qora Soqol** (Taloqchi) | Karvon talash; xavfsiz yo'l uchun xiroj; asir olish | Och > 80 |
| **Malakor** (Muzdek) | Fursatchi hujum; o'liklarni yig'ish; sovuq ultimatum | Qo'shnilar urushda |
| **Avreliy** (Mutassib) | Muqaddas urush; ushr yig'ish; taqvodorga shifo | Taq > 90 |
| **Elenor** (Donishmand) | Maslahat/hint berish; tarixni eslash; izchilga mukofot | Trust yuqori |

**Xiyonat qoidasi (Moros va boshqalar):** xiyonatdan **24 soat oldin** belgi chiqadi (g'alati elchi, mish-mish). O'yinchi tayyorlanishi mumkin.

―――――――――――――――――――――――――――――

## 9. QAROR DVIGATELI (UTILITY AI)

**Formula:**
`Score = Σ(w_i × c_i) × persona_w + kontekst − narx − cooldown + rnd(0..0.1)`

**Tanlash:** eng yaxshi 3 tasidan **softmax (T = 0.3)**.
**Limit:** hukmdor tickda ≤ 2 harakat. Dunyoga ta'sirli harakat ≤ 6/soat (global).
**Test uchun:** `seed` bilan deterministik.

### 9.1 42 harakat katalogi

| Guruh | Soni | Harakatlar |
| --- | --- | --- |
| Iqtisod | 10 | soliq_oshirish, soliq_kamaytirish, xiroj_talab, narx_shishirish, zahira_yigish, qarz_berish, qarz_undirish, karvon_tolli, auksion_snayper, xazina_sarfi |
| Diplomatiya | 10 | ittifoq_taklif, ittifoq_buzish, urush_elon, tinchlik_taklif, embargo, elchi_yuborish, sovga_yuborish, ultimatum, vositachilik, maxfiy_pakt |
| Harbiy | 8 | reyd, qamal, mudofaa_kuchaytirish, yollanma_yollash, karvon_talash, qasos_yurishi, muqaddas_urush, chegara_patrul |
| Josuslik | 6 | josus_yuborish, mish_mish_tarqatish, sabotaj, pora_berish, malumot_sotish, xiyonat |
| O'yinchi | 8 | kvest_berish, sovga_berish, jazo_ogohlantirish, pora_qabul, shantaj, mukofot, haqorat_javobi, ikki_tomonlama_taklif |

**Eslatma:** "shantaj" faqat o'yinchi o'zi xiyonat qilgan bo'lsa (masalan, ikki tomonlama pora fosh bo'lsa).

―――――――――――――――――――――――――――――

## 10. DIALOG DVIGATELI

**Xabar = Ochilish + Mazmun + Persona bo'yog'i + Yopilish**

| Element | Qoida |
| --- | --- |
| Ton | iliq / neytral / dushmanona (anger > 60 yoki trust < −30 → dushmanona) |
| Intentlar | salom, sovga_rahmat, xushomadga_javob, haqoratga_javob, pora_rad, pora_qabul, xiroj_talab, ogohlantirish, ultimatum, xayrlashuv |
| Slotlar | {player} {gold} {empire} {item} {days} |
| Saqlash | `data/dialogue/<persona>.json`, kerak bo'lganda yuklanadi (lazy) |
| Takror | Oxirgi 5 satr qaytarilmasin |

**Hajm:** 12 persona × 3 ton × 10 intent × 4 variant = **1,440 satr** (min).
Ochilish/Mazmun/Yopilish kombinatsiyasi bilan 10,000+ gap chiqadi.

**Persona so'z boyligi (misol):**
- Torin: oltin, hisob, foiz, qarz.
- Ragnar: qon, bolg'a, sharaf.
- Moros: soya, sir, vaqt.
- Avreliy: nur, gunoh, poklanish.

―――――――――――――――――――――――――――――

## 11. BOT RITSARLAR (NPC O'YINCHILAR)

| Arxetip | Xulqi | Qayerda |
| --- | --- | --- |
| Ochko'z Savdogar | Arzon oladi, qimmat sotadi | `/market` |
| Qasoskor | Arena navbatidagi o'yinchi bilan duel | `/arena` |
| Zindon Ovchisi | Minora qavatlarini chiqadi | `/tower` |
| Kolleksioner | Noyob runa/anjom yig'adi | Auksion |
| Siyosatchi | Gildiya ovozi, ittifoq | `/guild` |
| Qaroqchi | NPC karvonlarni talaydi | `/trade` |
| Skaut | Mish-mish tarqatadi | Taverna |
| Dehqon | Resurs sotadi, bozorga likvidlik | `/market` |

**Qoidalar:**

| Qoida | Qiymat |
| --- | --- |
| Botlar soni | ≤ 200 |
| Belgi | `is_bot = 1` |
| Online jadval | 08:00–23:00 (har botga o'zgacha) |
| Bozor ulushi | ≤ 25% hajm |
| Narx | Mediandan ±30% |
| Reyting | Real o'yinchilar top-10 ni egallamaydi |
| Owner | `/god bots` bilan yoqish/o'chirish |

―――――――――――――――――――――――――――――

## 12. DUNYO HODISALARI VA MISH-MISHLAR

### 12.1 NPC keltirib chiqaradigan hodisalar

| Hodisa | Trigger | Ta'sir | Davomi |
| --- | --- | --- | --- |
| Ocharchilik | zahira < 20% | Resurs narxi ×1.5 | 48 soat |
| Embargo | Urush + Diplomat/Ochko'z | Ikki imperiya savdosi −50% | 72 soat |
| Ittifoq | Umumiy dushman | A'zolarga +10% ATK | 7 kun |
| Xiyonat | Foyda > Sad | Ittifoq buziladi (24s oldin belgi) | — |
| To'ntarish | unrest > 70 | Hukmdor zaif, xazina −20% | 24 soat |
| Turnir | Valter, xazina to'la | Arena mukofoti ×1.5 | 24 soat |
| Muqaddas urush | Avreliy vs Zulmat/Kultepa | O'liklarga 2x, ushr | 3 kun |
| Qaroqchi mavsumi | Qora Soqol kuchli | Karvon xavfi +30% | 48 soat |
| Savdo bumi | Izabella banki boy | Bozor solig'i −25% | 24 soat |

**Muhim:** Owner hodisalari (Qonli Oy va boshqalar) NPC hodisalaridan ustun.

### 12.2 Mish-mishlar

| Tur | Ma'nosi |
| --- | --- |
| Haqiqat | Rost xabar |
| Yolg'on | Xoin tarqatgan |
| Bo'rttirilgan | Yarim rost |
| Tuzoq | Provokatsiya |

- Tarqatuvchi: Skaut botlar va taverna.
- O'yinchi **100 🪙** to'lab tekshirishi mumkin.
- Mish-mish `expires_at` bilan o'chadi.

―――――――――――――――――――――――――――――

## 13. O'YINCHI BILAN ALOQA

### 13.1 Yangi buyruqlar

| Buyruq | Vazifa |
| --- | --- |
| `/court` | Saroy: hukmdor kayfiyati (emoji bar), sovg'a, xushomad, so'rov, shikoyat |
| `/bribe` | Pora taklif qilish (formula P) |
| `/loan` | Sudxo'rdan qarz olish |
| `/rumors` | Mish-mishlar va tekshirish |
| `/npc_mood` | 12 hukmdor kayfiyati jadvali |

### 13.2 Hukmdor kvestlari

- Har persona uchun 6 shablon = **72 kvest**.
- Misol: Qora Soqol "karvon tala", Elenor "tarixiy relikvani top".
- Mukofot hukmdor xislatiga bog'liq (Torin oltin, Avreliy shifo).

### 13.3 Adolat qoidalari

| Qoida | Qiymat |
| --- | --- |
| Jazodan oldin ogohlantirish | 30 daqiqa muddat bilan |
| Yangi o'yinchi (lvl < 10) | Xiroj, qarz undirish, jazo YO'Q |
| Xabar limiti | ≤ 5 / kun / o'yinchi |
| Qarz | Faqat o'yinchi o'zi so'rasa |
| Owner | Hech qachon nishon emas |

―――――――――――――――――――――――――――――

## 14. SCHEDULER VA CATCH-UP

| Tick | Davr | Vazifa |
| --- | --- | --- |
| npc_tick | 10 daqiqa | Hukmdor qarori |
| bot_tick | 5 daqiqa | Bot harakati (batch 20) |
| economy_tick | 30 daqiqa | Xazina, bozor, bot savdo |
| rumor_tick | 15 daqiqa | Mish-mish tarqalishi |
| diplomacy_tick | 1 soat | Ittifoq / urush |
| daily_tick | 00:00 (UTC+5) | Decay, xotira siqish, hisobot |

**Catch-up qoidasi (muhim):**
Render Free-Tier uxlab qolishi mumkin. Uyg'onganda:
1. `last_tick_at` ni o'qi.
2. O'tkazib yuborilgan tickdan **ko'pi bilan 6 tasini** bajar.
3. Qolganini tashla.
4. Har tick idempotent bo'lsin (ikki marta ishlasa zarar yo'q).

**RAM qoidalari:**
- Katta kesh yo'q. Hamma narsa bazadan.
- Dialog JSON lazy yuklanadi.
- Tickda faqat 12 hukmdor + ≤ 20 bot.

―――――――――――――――――――――――――――――

## 15. BALANS VA XAVFSIZLIK

| Parametr | Chegara |
| --- | --- |
| Soliq ustamasi | ≤ +10% |
| Xiroj | ≤ 15% oltin, kuniga 1 marta |
| Qarz foizi | ≤ 5%/kun, ≤ 7 kun |
| Pora ehtimoli | 2%–95% |
| Hukmdor harakati | ≤ 2 / tick |
| Dunyo hodisasi | ≤ 6 / soat |
| Bot bozor ulushi | ≤ 25% |
| Xabar | ≤ 5 / kun / o'yinchi |
| Yangi o'yinchi | lvl < 10 himoyalangan |
| Kill-switch | `/god npc_off` hammasini to'xtatadi |

―――――――――――――――――――――――――――――

## 16. FAZALAR (10 TA)

| Faza | Nima quriladi | Qabul sharti |
| --- | --- | --- |
| 0 | Audit: mavjud kod xaritasi | `docs/AUDIT.md`, kod o'zgarmagan |
| 1 | Jadvallar 24–32 + shaxsiyat | Test 20 + eski 19 ta o'tadi |
| 2 | Hissiyot + xotira | Test 21–22 |
| 3 | Qaror dvigateli + ochko'zlik | Test 23–25 |
| 4 | Qolgan 11 persona | Test 26 |
| 5 | Dialog dvigateli + JSON | Test 28 |
| 6 | Bot ritsarlar | Test 31 |
| 7 | Dunyo hodisalari + mish-mish + scheduler | Test 29 |
| 8 | Buyruqlar + kvest + himoya | Test 27, 30 |
| 9 | `/god npc` paneli + balans + regressiya | Test 32, hammasi yashil |

―――――――――――――――――――――――――――――

## 17. YANGI TESTLAR (20–32)

Jami: 19 + 13 = **32 test**.

| # | Test |
| --- | --- |
| 20 | 12 profil: hamma xislat 0–100 oralig'ida |
| 21 | Mood decay baseline'ga yaqinlashadi |
| 22 | Xotira ≤ 50 yozuv, siqish ishlaydi |
| 23 | Ochko'zlik: soliq cap +10%, pora P 2–95% |
| 24 | To'yish: xazina ≥ 120% → GD yarimga tushadi |
| 25 | Utility: seed bilan bir xil natija, cooldown ishlaydi |
| 26 | Owner'ga hech qaysi NPC harakat qilmaydi |
| 27 | lvl < 10: xiroj/qarz/jazo yo'q |
| 28 | Dialog: slotlar to'lgan, oxirgi 5 satr takrorlanmaydi |
| 29 | Catch-up: 10 tick o'tdi → 6 tasi bajarildi, dublikat yo'q |
| 30 | Xabar limiti ≤ 5/kun |
| 31 | Bot bozor ulushi ≤ 25% |
| 32 | Kill-switch hamma tickni to'xtatadi |

―――――――――――――――――――――――――――――

## 18. XAVFLAR

| Xavf | Yechim |
| --- | --- |
| Ochko'z NPC o'yinchini bezdiradi | Capslar + ogohlantirish + yangi o'yinchi himoyasi |
| Render uxlab qoladi | Catch-up qoidasi (6 tick) |
| SQLite bloklanadi | WAL + qisqa tranzaksiya |
| Botlar bozorni buzadi | 25% cap + narx ±30% |
| Xushomad spam | 0.6ⁿ pasayish + shubha |
| Antigravity eski kodni buzadi | Minimal diff + har fazada pytest |
| Dialog zerikarli | Kombinatsiya + anti-takror |
| Xabar spami | 5/kun limit |

―――――――――――――――――――――――――――――

## 19. ANTIGRAVITY PROMPTLARI

Promptlar inglizcha: AI-kod agentlari shunda yaxshiroq tushunadi.

### MASTER PROMPT (har sessiyada boshida)

```
You are working on Valoriya, an async Telegram bot game (Python 3.12, aiogram 3, aiosqlite, Render Free-Tier).
Read docs/NPC_PLAN.md fully. Work on ONE phase only: the one I name.
Rules: show an implementation plan first and wait; make minimal diffs; never rewrite existing files; async only; files under 300 lines; run pytest after changes; the 19 existing tests must stay green; the owner (Telegram ID 648616238) must never be targeted by any NPC action; if anything is unclear, ask instead of guessing. End with a short report: files changed, tests run, open issues.
```

### FAZA PROMPTLARI

**Faza 0**
```
Phase 0. Read the whole repo. Do NOT change code. Write docs/AUDIT.md: file map, where ruler AI personas, emotions, flattery and bot knights live now, DB access pattern, how handlers are registered, how background tasks run. List risks of adding an npc/ package.
```

**Faza 1**
```
Phase 1. Create the npc/ package skeleton. Add an idempotent migration (schema_version) for tables 24-32 from section 4. Implement personality.py with the 12 ruler profiles from section 5 and seed npc_rulers. Add test 20. Run all tests.
```

**Faza 2**
```
Phase 2. Implement state.py (mood vector, decay 0.10 per tick) and memory.py (events from section 6.3, max 50 per pair with compression, flattery diminishing returns 0.6^n). Hook the existing flattery/gift/insult handlers to write memory events. Add tests 21-22.
```

**Faza 3**
```
Phase 3. Implement utility.py (score, softmax top-3 with T=0.3, cooldowns, seeded RNG) and actions/economy.py with the 12 greed actions and formulas from section 7. Do not send Telegram messages yet; log to npc_actions_log. Add tests 23-25.
```

**Faza 4**
```
Phase 4. Implement the persona behaviors from section 8 in actions/diplomacy.py, military.py, espionage.py. Each persona gets its 3 signature actions. Betrayal must be telegraphed 24h before. Add test 26.
```

**Faza 5**
```
Phase 5. Implement dialogue.py: lazy-loaded JSON lines and the 4-part message builder from section 10. Generate data/dialogue/*.json with at least 120 lines per persona. Add test 28.
```

**Faza 6**
```
Phase 6. Implement bots.py with the 8 archetypes from section 11: schedules, wallet limits, market share cap 25%, price within 30% of median. Add test 31.
```

**Faza 7**
```
Phase 7. Implement world events and rumors from section 12 and scheduler.py with the tick table and catch-up rule from section 14 (max 6 missed ticks, idempotent). Add test 29.
```

**Faza 8**
```
Phase 8. Add /court, /bribe, /loan, /rumors, /npc_mood handlers, ruler quests (72 templates), the 30-minute warning before punishment, the 5 messages/day cap and newbie protection (level < 10). Add tests 27 and 30.
```

**Faza 9**
```
Phase 9. Add the /god npc panel (npc_off kill-switch, bots toggle, force event, inspect mood). Do a balance pass using the caps in section 15. Add test 32. Run the full regression (32 tests). Update README and the encyclopedia.
```

―――――――――――――――――――――――――――――

## 20. KEYINGI QADAMLAR (REJADAN TASHQARI)

- Ixtiyoriy: hukmdor gaplarini LLM bilan boyitish (faqat Faza 9 dan keyin, kesh bilan).
- Ixtiyoriy: hukmdor portretlari (Pillow) kayfiyatga qarab o'zgaradi.
- Ixtiyoriy: haftalik "Dunyo yangiliklari" posti (kim kimga urush ochdi, kim to'ntarildi).
