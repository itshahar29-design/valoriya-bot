import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    p = doc.add_heading(text, level=level)
    run = p.runs[0]
    if level == 1:
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D) # Navy
    elif level == 2:
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0) # Blue
    elif level == 3:
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x74, 0x2A, 0x2A) # Dark Red/Burgundy
    return p

def create_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(10)

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    doc.add_paragraph() # Spacing
    return table

def build_full_documentation():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # TITLE BLOCK
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_run = title_p.add_run("🏰 VALORIYA: RITSARLAR QIROLLIGI\n")
    t_run.font.size = Pt(26)
    t_run.font.bold = True
    t_run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    sub_run = title_p.add_run("TO'LIQ VA MUKAMMAL MASTER ENSIKLOPEDIYA\nBarcha 250,000+ Mexanikalar, Formulalar, Endgame va Texnik Arxitektura\n")
    sub_run.font.size = Pt(14)
    sub_run.font.color.rgb = RGBColor(0x71, 0x80, 0x96)

    meta_run = title_p.add_run("Muallif / Yaratuvchi: @nakama_02 (ID: 648616238) | Versiya: 2.5 Ultimate Grand Release | 2026")
    meta_run.font.size = Pt(10)
    meta_run.font.italic = True
    meta_run.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    doc.add_paragraph("―" * 55)

    # 1. UMUMIY KONSEPSIYA VA TEXNIK PASPORT
    add_styled_heading(doc, "1. LOYIHA PASPORTI VA TEXNIK ARXITEKTURA", level=1)
    doc.add_paragraph(
        "Valoriya: Ritsarlar Qirolligi — Telegram Bot platformasida yaratilgan, keng ko'lamli hardkor text-based MMORPG o'yini bo'lib, "
        "o'yinchilarga 12 ta imperiya o'rtasidagi shafqatsiz janglar, siyosiy intriga, diplomatiya, erkin P2P bozor, qal'alar qamali, "
        "chuqur zindonlar, cheksiz minoralar va 120,000+ runalar sintezini taklif qiladi."
    )

    tech_info = [
        ["Dasturlash Tili", "Python 3.12+ (Asinxron aiogram 3.x arxitekturasi)"],
        ["Ma'lumotlar Bazasi", "aiosqlite (Asinxron relyatsion SQLite3, 23 ta jadval, tranzaksiyalar xavfsizligi)"],
        ["Hosting & Deploy", "Render PaaS (24/7 doimiy Webhook / Polling, Render Free-Tier Low-RAM optimallashtirilgan)"],
        ["Grafik Dvigatel", "Pillow (PIL) — 800x530 o'lchamli yuqori aniqlikdagi dinamik Ritsar Pasport Kartasi"],
        ["Yaratuvchi (Owner)", "@nakama_02 (Telegram ID: 648616238) — Mutloq daxlsiz, Reytingdan yashiringan"],
        ["Avtomatlashtirilgan Testlar", "19 ta keng qamrovli sinov (tests/test_all.py), 100% muvaffaqiyatli pass rate"],
        ["Jami Kontent Hajmi", "250,000+ protsessual va kombinatorik birliklar (60+ kunlik retention)"],
        ["Git Repository", "https://github.com/itshahar29-design/valoriya-bot.git (Branch: main)"]
    ]
    create_table(doc, ["Parametr", "Tavsif va Texnik Qiymat"], tech_info, [2.5, 4.5])

    # 2. MA'LUMOTLAR BAZASI SXEMASI
    add_styled_heading(doc, "2. BAZA SXEMASI (23 TA ASINXRON SQL JADVAL)", level=1)
    doc.add_paragraph("O'yin relatsion ma'lumotlar bazasi SQLite aiosqlite orqali 23 ta mustahkam jadvalga tayanadi:")
    db_tables = [
        ["1. characters", "Barcha qahramonlar (HP, stamina, sanity, gold, gems, prestige, wounds, bloodline)"],
        ["2. equipment", "8-slotli kiyimlar (slot_type, rarity, attack, defense, durability, runes_json)"],
        ["3. battles", "PvP va PvE duel jurnallari, raundlar va g'alabalar"],
        ["4. auction_items", "Auksiondagi anjomlar va stavkalar tizimi"],
        ["5. p2p_trades", "O'yinchilar o'rtasida to'g'ridan-to'g'ri xavfsiz almashinuv (Escrow)"],
        ["6. pigeon_mails", "Kaptar pochtasi orqali xat va sovg'alar yuborish"],
        ["7. captives", "Asirlar, zindonlar va qutqaruv to'lovlari (Ransom)"],
        ["8. diplomacy", "12 imperiya o'rtasidagi urush va tinchlik munosabatlari"],
        ["9. player_reputation", "O'yinchining 12 ta imperiya oldidagi hurmati va unvonlari"],
        ["10. inventory_items", "Sumkadagi anjomlar va tovarlar ro'yxati"],
        ["11. guild_members", "Gildiya a'zolari va ularning mansablari"],
        ["12. guilds", "Klanlar, xazinalar, qal'a egaligi va darajalari"],
        ["13. dungeon_progress", "O'yinchining oddiy zindonlardagi o'tgan qavatlari"],
        ["14. castles", "12 ta imperiyadagi qal'alar, mudofaa kuchi va kunlik soliqlar"],
        ["15. tournament_throne", "Valoriya Oliy Taxti, amaldagi Qirol va saltanat davri"],
        ["16. market_listings", "Jonli ochiq P2P bozor (narx, miqdor, kategoriya, 3% soliq)"],
        ["17. daily_quests", "Kundalik 3 ta vazifa (Arena, Shaxta, Bozor) va mukofotlar"],
        ["18. achievements", "Faxriy medallar va yutuqlar (title, unlocked_at)"],
        ["19. character_skills", "Mahoratlar shajarasi (subklass, skill_id, rank 1..5)"],
        ["20. character_pets", "960 ta jangovar hamrohlar (species, aspect, stage 1..4, hunger)"],
        ["21. battle_pass_progress", "50 darajali mavsumiy Battle Pass (total_exp, claimed_rewards)"],
        ["22. promo_redemptions", "Reklama promokodlari tarixi (character_id, code, anti-abuse)"],
        ["23. tower_progress", "100 qavatli Cheksiz Tubsizlik Minorasi (max_floor, completed_at)"]
    ]
    create_table(doc, ["Jadval Nomi", "Maqsadi va Saqlanadigan Ma'lumotlar"], db_tables, [2.5, 4.5])

    # 3. 12 TA IMPERIYA VA AI LORE
    add_styled_heading(doc, "3. 12 TA IMPERIYA VA AI HUKMDORLAR", level=1)
    doc.add_paragraph(
        "Har bir imperiya o'zining AI his-tuyg'ulariga ega. O'yinchi 'Paxta qo'yish' (xushomad qilish) yoki haqorat qilish orqali "
        "hukmdorlardan sovg'alar olishi yoki g'azabiga duchor bo'lishi mumkin:"
    )
    kingdoms_data = [
        ["🦁 Oltin Sher", "Imperator Valter V", "Kibrli (Pride)", "Paladinlar, qalin po'lat sovutlar (+15 DEF, +25% Honor)"],
        ["🦅 Qishki Qoya", "Ragnar Temirqo'l", "G'azabli (Anger)", "Berserklar, 2 qo'lli bolg'alar (+20 ATK, 30% Bleed res)"],
        ["🐻 Oq Ayiq", "Knyaz Boris", "Vazmin (Calm)", "Monolit og'ir zirhlar (+60 Max HP, +15% Shield block)"],
        ["⚖️ Temir Bastion", "Usta Torin", "Ochko'z (Greed)", "Elita metallurgiya (Craft -30%, Durability +50%)"],
        ["⚜️ Moviy Nilufar", "Gersoginya Izabella", "Diplomat", "Bank tizimi va auksion (+30% Oltin, Bozor soliqlari -50%)"],
        ["🐉 Qizil Ajdaho", "Sulton Sulaymon", "Qahrli (Wrath)", "Alanga nayzadorlari (+25 Fire DMG, +20% Crit)"],
        ["🐺 Dasht Bo'rilari", "Botirxon Bahodir", "Yovvoyi (Wild)", "Tezkor otliqlar (+40% Ot tezligi, +12 Evasion)"],
        ["🐍 Zulmat Soyasi", "Soya Knyazi Moros", "Xoin (Treason)", "Zaharli xanjarlar (+20 Poison DMG, +15% Crit)"],
        ["🏴‍☠️ Qora Qon", "Kapitan Qora Soqol", "Taloqchi (Pirate)", "Karvonlarni talash (+40% O'lja, -10% Stamina sarfi)"],
        ["💀 Kultepa O'liklar", "Lich Malakor", "Muzdek (Cold)", "Suyak ritsarlari (+12% Lifesteal, +50% Zulmatga qarshilik)"],
        ["☀️ Quyosh Sohiblari", "Patriarx Avreliy", "Mutassib (Fanatic)", "Muqaddas shifo (+35% Shifo kuchi, O'liklarga 2x zarar)"],
        ["🌙 Kumush O'rmon", "Qirolicha Elenor", "Donishmand (Wise)", "Elf kamonchilari (+25 Accuracy, +15 Evasion)"]
    ]
    create_table(doc, ["Qirollik", "Hukmdor", "AI Persona", "Maxsus Bonus & Imtiyoz"], kingdoms_data, [1.5, 1.5, 1.3, 2.7])

    # 4. 12 ANATOMIK ZONA VA JANG FIZIKASI
    add_styled_heading(doc, "4. 12-ZONALI ANATOMIK JANG FIZIKASI VA STAMINA", level=1)
    doc.add_paragraph(
        "Jang harakati har bir zarbani inson anatomiyasining nozik nuqtalariga yo'naltiradi. "
        "Zarar hisobi: Base ATK x Skill Mult x Zone Mult x Stamina Penalty x Crit x Sanity x RNG - Defense."
    )
    zones_data = [
        ["head", "Bosh / Miya", "2.2x", "+25%", "concussion (Og'ir bosh chayqalishi, -30% AGI)"],
        ["face", "Yuz va Ko'zlar", "1.9x", "+20%", "one_eyed (Ko'z jarohati, 0% Crit)"],
        ["neck", "Bo'yin / Uyqu tomiri", "2.5x", "+30%", "arterial_bleed (Halokatli arterial qon ketish)"],
        ["torso", "Ko'krak Qafasi", "1.4x", "+10%", "broken_ribs (Qovurg'a sinishi, -20% Max HP)"],
        ["r_shoulder", "O'ng Yelka", "1.0x", "+5%", "arm_fracture (Qo'l jarohati, -25% ATK)"],
        ["l_shoulder", "Chap Yelka", "1.0x", "+5%", "shield_arm_damage (Qalqon tushib ketishi)"],
        ["r_arm", "O'ng Bilak", "0.85x", "+5%", "hand_injury (Qurolni tushirib yuborish)"],
        ["l_arm", "Chap Bilak", "0.85x", "+5%", "hand_injury (Zaiflashgan zarba)"],
        ["stomach", "Qorin va Jigarlar", "1.3x", "+15%", "internal_bleed (Ichki qon ketishi)"],
        ["groin", "Chov Sohasi", "1.7x", "+20%", "stamina_collapse (Staminani 0 ga tushirish)"],
        ["r_leg", "O'ng Tizza va Oyoq", "0.9x", "+5%", "leg_fracture (Oyoq sinishi, -40% AGI)"],
        ["l_leg", "Chap Tizza va Oyoq", "0.9x", "+5%", "leg_fracture (Oyoq payi uzilishi)"]
    ]
    create_table(doc, ["Zona ID", "Tana Qismi", "Multiplikator", "Crit Bonusi", "Halokatli Travma (Wound)"], zones_data, [1.0, 1.8, 1.0, 1.0, 2.2])

    doc.add_paragraph("⚔️ Jang Mexanikalarining Muhim Qoidalari:")
    doc.add_paragraph("• Stamina Sarfi: Oddiy zarba -15, Og'ir zarba -25, Qalqon -10, Maxsus mahorat -30 stamina.")
    doc.add_paragraph("• Hansirash (Exhaustion): Stamina 0 ga tushganda o'yinchining zarbasi -50% pasayadi, dushmandan esa +80% ortiqcha zarar oladi.")
    doc.add_paragraph("• Qalqon Bloklash (Shield Block): Qalqon tutganda zarar 70% ga qaytariladi. Ammo Momaqaldiroq runasi bo'lsa qalqonni teshib, staminani 0 qiladi.")
    doc.add_paragraph("• Qochish (Dodge/Evasion): Agility farqiga qarab 5% dan 40% gacha. Qalqon tutgan yoki Muz runasi tekkan raqib qocholmaydi (0% Dodge).")

    # 5. ZULMAT TIZIMI VA SANITY
    add_styled_heading(doc, "5. ZULMAT TIZIMI: SANITY, 15 TRAVMA VA QONLI AHD", level=1)
    doc.add_paragraph(
        "Mag'lubiyat o'yinchiga jazolarsiz o'tmaydi. Har bir mag'lubiyatda o'yinchi 10% dan 25% gacha oltin yo'qotadi, "
        "anjomlar eskiradi, Sanity (aql) -15% ga pasayadi va og'ir travmalar paydo bo'ladi."
    )
    doc.add_paragraph("🧠 Sanity Bosqichlari:")
    doc.add_paragraph("• 100% - 75%: Sokin Ruh (Normal holat, hech qanday salbiy ta'sir yo'q).")
    doc.add_paragraph("• 74% - 40%: Xavotir & Qo'rquv (Janglarda qo'llar qaltiraydi, -15% aniqlik).")
    doc.add_paragraph("• 39% - 1%: Dahshat (Dushman zarbalaridan dahshatga tushish, -30% zarba).")
    doc.add_paragraph("• 0%: TELBALIK (Madness) — Qahramon o'z qurolini sindirib qo'yishi, jangda qochib ketishi yoki o'ziga zarar yetkazishi mumkin.")

    doc.add_paragraph("🩸 Iblis Morvath bilan Qonli Ahd (Blood Pact):")
    doc.add_paragraph("• In'om: +45 Doimiy Dark ATK va janglarda 20% Lifesteal (dushman qonidan jon tiklash).")
    doc.add_paragraph("• To'lov: Maksimal jon -25 ga kamayadi, Sanity 30% yo'qoladi, tabiblar davolashdan bosh tortadi.")
    doc.add_paragraph("• Poklanish: Nur Ibodatxonasida 1,500 🪙 Oltin evaziga tavba qilib poklanish mumkin.")

    # 6. KLASSLAR VA 675 TA TALANT
    add_styled_heading(doc, "6. KLASSLAR VA 675 TA TALANT (MAHORAT SHAJARASI)", level=1)
    doc.add_paragraph(
        "O'yinda 3 ta boshlang'ich sinf va 9 ta maxsus mutaxassislik mavjud. Har bir mutaxassislik 15 tadan mahorat tuguni va "
        "har biri 5 tagacha darajaga ega (jami 675 ta talant darajasi):"
    )
    specs = [
        ["Paladin", "Jangchi", "Muqaddas Nur, O'zini davolash, Ilohiy qalqon, O'liklarga qahr"],
        ["Berserk", "Jangchi", "Qonli Quturish, Jon kamayganda 2x zarba, Lifesteal, Titan kuchi"],
        ["Qora Ritsar", "Jangchi", "Zulmat Qahri, Zirhni yemiruvchi zang, Qonli qasamyod"],
        ["Snayper", "Mergan", "100% Tanqidiy o'q, Masofadan nishonga olish, Zirhni teshish"],
        ["Assasin", "Mergan", "Soyada yashirinish, Zaharlangan tig'lar, Kutilmagan qotillik"],
        ["Ovchi (Trapper)", "Mergan", "Yirtqich hayvonlarni chaqirish, Po'lat qopqonlar, Chaqqonlik"],
        ["Elementalist", "Sehrgar", "Olov alangasi, Muzlatuvchi qahraton, Zanjirli chaqmoq"],
        ["Nekromant", "Sehrgar", "Skeletlar armiyasi, Ruh o'g'irlash, Qarag'ish la'nati"],
        ["Xaos Sehrgari", "Sehrgar", "Vaqtni sekinlashtirish, Fazoviy portallar, Portlovchi meteor"]
    ]
    create_table(doc, ["Mutaxassislik", "Asosiy Sinf", "Asosiy Sehrlar va Qobiliyatlar"], specs, [1.5, 1.2, 4.3])

    # 7. 960 TA HAMROH VA MINIKLAR
    add_styled_heading(doc, "7. 960 TA JANGOVAR HAMROH VA MINIKLAR (PETS & MOUNTS)", level=1)
    doc.add_paragraph("Formulasi: 30 Zot x 4 Evolyutsiya Bosqichi x 8 Element Aspekti = 960 ta noyob variant!")
    doc.add_paragraph("• 30 Ta Asosiy Zot: Arslon, Qora Bo'ri, Qor Barsi, Olov Feniksi, Magma Iloni, Gipotam, Qanotli Pegas, Qorong'u Grifon, Tubsizlik Qarg'asi, Mamont, Karkidon, Qonxo'r Ko'rshapalak, Oltin Burgut va boshqalar.")
    doc.add_paragraph("• 4 Evolyutsiya Bosqichi: 1-Baby (+10%), 2-Juvenile (+25%), 3-Adult (+50%), 4-Legendary Alpha (+100% va Maxsus qobiliyat).")
    doc.add_paragraph("• 8 Element Aspekti: Olov, Muz, Chaqmoq, Zahar, Yorug'lik, Zulmat, Shamol, Yer.")
    doc.add_paragraph("• Oziqlantirish: 50 oltin evaziga go'sht beriladi. To'qlik darajasi 100% bo'lsa egasiga to'liq bonus beradi.")

    # 8. 250,000+ KONTENT MATRITSASI
    add_styled_heading(doc, "8. 250,000+ PROTSESSUAL KONTENT MATRITSASI", level=1)
    doc.add_paragraph("O'yin hech qachon bir xil bo'lib qolmasligi uchun protsessual kombinatsiyalar ishlaydi:")
    doc.add_paragraph("1. 125,000+ Noyob Qurol-Aslaha: 25 ta Prefiks (Qonxo'r, Muzlagan, Ilohiy...) x 200 ta Baza Anjomlari x 25 ta Suffiks (...Ajdaho Qotili, ...Zulmat Fotihi).")
    doc.add_paragraph("2. 4,600+ Mutant Dushmanlar: 40 ta Baza maxluq x 5 Unvon (Oddiy, Elita, Chempion, Boss, Afsonaviy) x 20 ta Mutatsiya (Olovli tikanlar, Muz sovut, Lifesteal, Zahar).")
    doc.add_paragraph("3. 1,000 ta Zindon Xonalari: 10 ta Mavzu x 10 ta Xona Turi x 10 ta Joylashuv tartibi.")

    # 9. 120,000+ R長NOZUVLAR (RUNEWORDS)
    add_styled_heading(doc, "9. 120,000+ QADIMIY R長NOZUVLAR (RUNEWORDS) VA ALXIMIYA", level=1)
    doc.add_paragraph("20 ta qadimiy runani 3 teshikli qurollarga joylash orqali yangi afsonaviy qurollar kashf etiladi:")
    runes_list = [
        ["el", "☀️ El", "+10 ATK, Nur ko'rish"],
        ["eld", "🛡 Eld", "+15 DEF, Qalqon mustahkamligi"],
        ["tir", "⚡️ Tir", "+5 Mana har bir o'ldirilgan dushmandan"],
        ["nef", "🌪 Nef", "+8 ATK, Dushmanni orqaga surish (Knockback)"],
        ["eth", "🌱 Eth", "+10 Jon tiklanishi (Regen), +8 DEF"],
        ["ith", "🗡 Ith", "+20 Maksimal zarba, +5% Crit"],
        ["tal", "🧪 Tal", "+18 Neyrotoksin zahar zarari"],
        ["ral", "🔥 Ral", "+22 Olovli kuydirish zarari"],
        ["ort", "🌩 Ort", "+25 Zanjirli chaqmoq zarari"],
        ["thul", "❄️ Thul", "+20 Muz zarari, raqibni sekinlashtirish"],
        ["amn", "🧛 Amn", "+10% Vampirizm (zarbadan jon olish)"],
        ["sol", "🧱 Sol", "-12 Kiruvchi zararni kamaytirish, +18 DEF"],
        ["shael", "👟 Shael", "+25% Hujum va harakat tezligi"],
        ["dol", "😱 Dol", "20% Dushmanga dahshat solib qochirish"],
        ["hel", "🪶 Hel", "-20% Stamina sarfini kamaytirish"],
        ["io", "🧠 Io", "+25% Ruhiy travmalarga (Sanity) chidamlilik"],
        ["lum", "🌟 Lum", "+50 Maksimal Mana, +15% Sehr kuchi"],
        ["ko", "🎯 Ko", "+15% Tanqidiy zarba (Crit), +20 Aniqlik"],
        ["fal", "🗿 Fal", "+20 Quvvat (STR), +80 Maksimal Salomatlik"],
        ["zod", "👑 Zod", "BUZILMASLIK (Qurol sinmaydi va eskirmaydi), +50 ATK, +50 DEF"]
    ]
    create_table(doc, ["ID", "Runa Nomi", "Xususiyati va Ta'siri"], runes_list, [1.0, 1.8, 4.2])

    doc.add_paragraph("Mashhur Qadimiy Runozuvlar (Retseptlar):")
    doc.add_paragraph("• Ral + Ort + Tal ➔ Ancient Pledge: Barcha elementlarga +50% doimiy qarshilik, +45 Mudofaa.")
    doc.add_paragraph("• Amn + Ral + Thul ➔ Bloodfrost: Har zarbada dushmanni muzlatadi va 20% hayotini o'zlashtiradi.")
    doc.add_paragraph("• Ith + Shael + Ort ➔ Zephyr Storm: Harakat tezligini 2x oshiradi va chaqmoq chaqnaydi.")
    doc.add_paragraph("• Fal + Sol + Eld ➔ Stone Bastion: Zarbalarni 40% qaytaradi va +150 HP beradi.")
    doc.add_paragraph("• Zod + Fal + Ith ➔ Breath of the Dying: Afsonaviy qudrat! +100 Zarba, dushman mudofaasini 0 ga tushirish.")

    # 10. 60+ KUNLIK RETENTION VA ENDGAME
    add_styled_heading(doc, "10. 60+ KUNLIK RETENTION VA ENDGAME TIZIMLARI", level=1)
    doc.add_paragraph("O'yinchilarni kamida 60 kun davomida o'ynashga majbur qiluvchi 5 ta ustun:")

    doc.add_paragraph("1. 🌟 Prestij / Ascension (Tiers I - X):")
    prestiges = [
        ["I: Ritsar-Kapitan", "1.20x", "50", "+100 💎", "Boshlang'ich qayta tug'ilish"],
        ["II: Qirollik Paladini", "1.40x", "50", "+200 💎", "Paladinlik sharafi"],
        ["III: Imperiya Marshali", "1.65x", "50", "+350 💎", "Armiya bosh qo'mondoni"],
        ["IV: Afsonaviy Qahramon", "1.95x", "50", "+500 💎", "Olamlararo mashhurlik"],
        ["V: Ajdaho Qotili", "2.30x", "50", "+750 💎", "Ajdaho qonini ichgan ritsar"],
        ["VI: Yarim-Xudo", "2.75x", "50", "+1,000 💎", "Ilohiy qudrat darajasi"],
        ["VII: Mangu Qo'riqchi", "3.30x", "50", "+1,500 💎", "Vaqtga bo'ysunmas qo'riqchi"],
        ["VIII: Kosmik Monarx", "4.00x", "50", "+2,000 💎", "Yulduzlararo hukmdor"],
        ["IX: Borliq Yaratuvchisi", "4.80x", "50", "+3,000 💎", "Koinot qonunlarini o'zgartiruvchi"],
        ["X: Oliy Valoriya Mutloqi", "6.00x", "50", "+5,000 💎", "SERVERNING ENG OLIY MUTLOQ CHEMPIONI"]
    ]
    create_table(doc, ["Prestij Darajasi", "Zarba & DEF Multiplikatori", "Talab Darajasi", "Sovg'a", "Unvon"], prestiges, [2.0, 1.5, 0.8, 1.2, 1.5])

    doc.add_paragraph("2. 🗼 100 Qavatli Cheksiz Tubsizlik Minorasi (Abyssal Tower):")
    doc.add_paragraph("• 100 qavatli qiyinlashib boruvchi vertikal minora.")
    doc.add_paragraph("• Har 10-qavatda Milestone Boss: 10-Granit Qo'riqchi, 20-Qonli Berserk, 30-Gidra Malikasi, 40-Magma Titan, 50-Muz Qiroli Arktas, 60-Soya Klani, 70-Xaos, 80-Oltin Ajdaho Beliar, 90-Azrail, 100-Tubsizlik Oliy Monarxi (+150k Oltin, +1,000 💎).")

    doc.add_paragraph("3. 🎟 50 Darajali Mavsumiy Battle Pass: Har bir jang va kvestdan EXP. Bepul va Qirollik mukofot liniyalari.")
    doc.add_paragraph("4. 🎡 Taverna Omad G'ildiragi: Har 4 soatda bepul aylantirish (Oltin, Javohir, Tuxum, Jekpot) va Suyak jangi.")
    doc.add_paragraph("5. ⛺️ Oflayn AFK Ekspeditsiyalar: 5 hudud (2h, 4h, 8h, 12h, 24h). O'yinchi botdan chiqqanda ham boylik yig'iladi.")

    # 11. IQTISODIYOT VA MULTIPLAYER
    add_styled_heading(doc, "11. MULTIPLAYER, IQTISODIYOT VA GILDIYALAR", level=1)
    doc.add_paragraph("• Jonli P2P Bozor (Marketplace): O'yinchilar o'z narsalarini sotadi, xaridordan 3% qirollik solig'i olinadi, sotuvchiga bot xabar beradi.")
    doc.add_paragraph("• Gildiyalar va Qal'alar: 1,000 oltin evaziga klan tuzish, qal'alarni qamal qilish va kunlik 1,500 - 3,500 oltin passiv soliq yig'ish.")
    doc.add_paragraph("• Valoriya Oliy Taxti: Butun serverda faqat 1 ta Qirol bo'ladi. Duel orqali taxtni tortib olish mumkin.")
    doc.add_paragraph("• Shaharlararo Savdo (Arbitraj): Samarqand, Muzli Cho'qqi, Temir Bastion va Moviy Nilufar o'rtasida ipak, ziravorlar, mo'yna savdosi.")

    # 12. MARKETING VA REKLAMA
    add_styled_heading(doc, "12. REKLAMA TRAFIGI VA VIRUSLI REFERAL", level=1)
    doc.add_paragraph("• Virusli Referal: Do'st chaqirgan ritsarga +500 🪙 Oltin va +1 💎 Javohir, hamda do'sti yutgan har bir oltindan 5% umrbod passiv keshbek!")
    doc.add_paragraph("• Rasmiy Marketing Promokodlari:")
    doc.add_paragraph("  - VALORIYA2026: 2,500 Oltin + 20 Javohir + 5 Eliksir")
    doc.add_paragraph("  - NAKAMA: 5,000 Oltin + 50 Javohir (Yaratuvchi kodi)")
    doc.add_paragraph("  - START100: 1,500 Oltin + 10 Javohir")
    doc.add_paragraph("  - TELEGRAM: 2,000 Oltin + 15 Javohir")
    doc.add_paragraph("  - TIKTOK: 3,000 Oltin + 25 Javohir")
    doc.add_paragraph("  - YOUTUBE: 3,500 Oltin + 30 Javohir")

    # 13. OWNER GOD-MODE
    add_styled_heading(doc, "13. YARATUVCHI (OWNER) MUTLOQ VAKOLATLARI (GOD-MODE)", level=1)
    doc.add_paragraph("Ownerlik kodi darajasida FAQAT @nakama_02 (Telegram ID: 648616238) ga bog'langan:")
    doc.add_paragraph("• Cheksiz Resurslar: +50k Oltin, +1k Javohir, 99k HP, 999 ATK Qilich, 999 DEF Zirh.")
    doc.add_paragraph("• 2-Sahifali Global Dunyo Hodisalari:")
    doc.add_paragraph("  - 🩸 Qonli Oy (Blood Moon): 2x agressiya va xavf.")
    doc.add_paragraph("  - 🌧 Oltin Yomg'iri (Golden Rain): 2x o'lja butun server bo'ylab.")
    doc.add_paragraph("  - 🐉 Ajdaho Reydi: Serverga global drakonni chaqirish.")
    doc.add_paragraph("  - ☄️ Meteor Qulashi: Dunyoni larzaga solish.")
    doc.add_paragraph("  - 💖 Global Shifo: Barcha jarohatlangan o'yinchilarni davolash.")
    doc.add_paragraph("  - 🎁 Server Airdrop: Barcha onlayn ritsarlarga oltin va eliksir tarqatish.")
    doc.add_paragraph("• Boshqaruv & Xavfsizlik: Bozorni tozalash, Qal'alarni tortib olish, Taxtni bo'shatish, 1-soatlik Snapshot bilan bazani Rollback qilish.")

    # 14. BUYRUQLAR RO'YXATI
    add_styled_heading(doc, "14. ASOSIY BUYRUQLAR VA MENYU TUGMALARI", level=1)
    cmds = [
        ["/start", "Qahramon yaratish va FTUE boshlanishi"],
        ["/arena", "1v1 Shon-sharaf dueli"],
        ["/tower", "100 Qavatli Cheksiz Tubsizlik Minorasi"],
        ["/promo [KOD]", "Reklama promokodlarini kiritish"],
        ["/prestige / /ascend", "Prestij darajalari va qayta tug'ilish"],
        ["/runewords", "120,000+ Qadimiy runozuvlar retseptlari"],
        ["/profile", "Profil va Pillow 800x530 ritsar pasporti"],
        ["/inventory", "8-slotli sumka va avto-kiyinish"],
        ["/market", "Jonli P2P o'yinchilar bozori"],
        ["/guild", "Gildiyalar va Qal'a qamallari"],
        ["/trade", "Shaharlararo karvon savdosi"],
        ["/throne", "Valoriya Oliy Taxtiga da'vogarlik"],
        ["/afk / /expedition", "Oflayn avtomatik ekspeditsiya"],
        ["/forge", "Temirchilik, toblash va runa ulash"],
        ["/daily", "Kundalik sovg'alar va streak"],
        ["/god", "Oliy Yaratuvchi boshqaruv paneli (faqat @nakama_02)"]
    ]
    create_table(doc, ["Buyruq", "Vazifasi va Ta'rifi"], cmds, [2.0, 5.0])

    # 15. 19 TA MEGA-TEST
    add_styled_heading(doc, "15. 19 TA AVTOMATLASHGAN TESTLAR NATIJASI", level=1)
    doc.add_paragraph(
        "Loyiha sifatini kafolatlash maqsadida yaratilgan tests/test_all.py test skripti "
        "barcha 19 ta mega-sinovdan 100% muvaffaqiyat bilan o'tgan:"
    )
    doc.add_paragraph("✅ Test 1: Baza initsializatsiyasi va 12 imperiya.")
    doc.add_paragraph("✅ Test 2: Qahramon va 3 ta kiyim.")
    doc.add_paragraph("✅ Test 3: Owner @nakama_02 daxlsizligi.")
    doc.add_paragraph("✅ Test 4: 12-zonali kinetik jang va stamina.")
    doc.add_paragraph("✅ Test 5: Protsessual bot ritsarlar va 4 ta persona.")
    doc.add_paragraph("✅ Test 6: AI hissiyotlar matritsasi va xushomad.")
    doc.add_paragraph("✅ Test 7: QoL avto-kiyinish, ta'mirlash, eritish.")
    doc.add_paragraph("✅ Test 8: FTUE kvesti va qurolbardor maktubi.")
    doc.add_paragraph("✅ Test 9: 1-soatlik snapshot xavfsizlik arxivi.")
    doc.add_paragraph("✅ Test 10: Zulmat tizimi, Sanity, 15 travma, Qonli Ahd.")
    doc.add_paragraph("✅ Test 11: Gildiyalar, Qal'alar, Referal, Shaxta, Alximiya, Taxt.")
    doc.add_paragraph("✅ Test 12: P2P Bozor (3% soliq), Kvestlar, Pillow karta, Runalar, Karvon.")
    doc.add_paragraph("✅ Test 13: Owner cheksiz vakolatlari va jazolash.")
    doc.add_paragraph("✅ Test 14: Doimiy menyu tugmalari (ReplyKeyboard).")
    doc.add_paragraph("✅ Test 15: 1,000+ kontent (200 anjom, bestiariy, kvestlar).")
    doc.add_paragraph("✅ Test 16: 10,000+ protsessual kontent (130,600+ birlik).")
    doc.add_paragraph("✅ Test 17: 675 talant va 960 ta hamrohlar.")
    doc.add_paragraph("✅ Test 18: Battle Pass, Omad G'ildiragi, AFK Ekspeditsiyalar.")
    doc.add_paragraph("✅ Test 19: 60+ kunlik Endgame, Prestige X, 100-qavat Tower, 100k+ Runewords, Promo Engine.")

    # Save destinations
    dest_paths = [
        r"C:\Users\User11\Desktop\VALORIYA_BOT_MASTER_QOLLANMA.docx",
        r"C:\Users\User11\Desktop\NOMALUM\VALORIYA_BOT_MASTER_QOLLANMA.docx",
        r"C:\Users\User11\.gemini\antigravity\scratch\ritsarlar_qirolligi\VALORIYA_BOT_MASTER_QOLLANMA.docx"
    ]

    for p in dest_paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            doc.save(p)
            print(f"SUCCESS: Saved docx to {p}")
        except Exception as e:
            print(f"ERROR saving to {p}: {e}")

if __name__ == "__main__":
    build_full_documentation()
