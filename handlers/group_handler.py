import random
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, create_character, update_character, register_group
from game.npc_engine import NPCEngine
from game.battle_engine import BattleEngine
from game.npc_broadcaster import ACTIVE_DROPS, NPCBroadcaster
from config import OWNER_ID, OWNER_USERNAME

group_router = Router()

# Guruh uchun faol reyd boss holati (xotirada saqlanadi)
ACTIVE_GROUP_BOSSES = {}

# NPC larning guruhga tashlaydigan provokatsion gaplari (Trash Talk)
NPC_GROUP_TAUNTS = {
    "berserk": [
        "🩸 '{name}': 'Hey, bu guruhdagi barcha ritsarlar qo'rqoqmi?! Kim men bilan qonli maydonga chiqadi?!'",
        "🩸 '{name}': 'Mening bolg'am bugun mayda suyaklarni maydalashni istayapti! Qani, kimning yuragi bor?!'",
        "🩸 '{name}': 'Sizlarni ritsar deb kim aytdi? Menga teng keladigan bittasi bormi o'zi bu yerda?!'"
    ],
    "defender": [
        "🛡 '{name}': 'Men 12 ta imperiya sarhadlarini qo'riqlagan gvardiyachiman. Qani, qilich ushlashni biladigan bormi?'",
        "🛡 '{name}': 'Mening qalqonimga bitta zarba berib ko'rishga jur'atingiz yetadimi, janoblar?'"
    ],
    "poisoner": [
        "🐍 '{name}': 'Hehehe... Shovqin qilmanglar, go'daklar. Zaharli xanjarim kimning bo'ynini nishonga olsin?'",
        "🐍 '{name}': 'Guruhda o'zini botir olib yurganlar ko'p ekan. Qani, bittang maydonga tush-chi, tomirlaringdagi qonni ko'raylik!'"
    ],
    "coward": [
        "🏃 '{name}': 'Men shunchaki o'tib ketayotgandim... Lekin agar birontangiz menga tashlansangiz, imperator armiyasini chaqiraman!'"
    ]
}

def is_owner_user(user_id: int, username: str | None) -> bool:
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return False

# =====================================================================
# 1. GURUHDA JANG VA DUEL CHAQIRUVI (/duel, !duel, !jang)
# =====================================================================
@group_router.message(F.chat.type.in_(["group", "supergroup"]), F.text.regexp(r"^(!|\/)(duel|jang|arena|fight)"))
async def group_duel_challenge(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Jasur Ritsar"
    
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply(
            f"⚔️ *Ser Artur:* '{user_name}, siz hali ritsarlik qasamyodini qabul qilmadingiz!\n"
            f"Avval botning shaxsiyiga [@ValoriyaRpgBot](https://t.me/ValoriyaRpgBot) kirib /start bosing!'",
            parse_mode="Markdown"
        )
        return

    # Raqib bot (NPC) yaratamiz
    npc = NPCEngine.generate_bot_knight(target_level=char["level"])
    persona = npc.get("persona", "berserk")
    taunt_list = NPC_GROUP_TAUNTS.get(persona, NPC_GROUP_TAUNTS["berserk"])
    taunt = random.choice(taunt_list).format(name=npc["name"], player_name=user_name)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ NPC Bilan Jang Qilish", callback_data=f"gfight_npc_{char['id']}_{npc['level']}_{persona}"),
            InlineKeyboardButton(text="👥 O'yinchi Chaqiruvi", callback_data=f"gfight_pvp_{char['id']}")
        ]
    ])

    await message.reply(
        f"🏰 *VALORIYA GURUH ARENASI E'LONI!* ⚔️\n\n"
        f"Ritsar *{char['name']}* (Lvl {char['level']}) maydonga chiqdi!\n\n"
        f"🚪 *Maydon eshigi zarb bilan ochilib, kutilmagan mehmon bostirib kirdi!*\n\n"
        f"🗣 {taunt}\n\n"
        f"Maydonda: *{npc['name']}* (Lvl {npc['level']})\n"
        f"❤️ Jon: *{npc['hp']}* | 🪙 O'lja: *+{npc['loot_gold']} Oltin*\n\n"
        f"Kim jang maydoniga tushadi?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# =====================================================================
# 2. GURUHDA NPC BILAN JANG QILISH TUGMASI
# =====================================================================
@group_router.callback_query(F.data.startswith("gfight_npc_"))
async def process_group_npc_fight(callback: CallbackQuery):
    parts = callback.data.split("_")
    char_id = int(parts[2])
    npc_lvl = int(parts[3])
    persona = parts[4] if len(parts) > 4 else "berserk"
    
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Ritsar"
    char = await get_character_by_user_id(user_id)
    
    if not char:
        await callback.answer("Avval botga kirib /start bosing!", show_alert=True)
        return

    # NPC ni generatsiya qilamiz
    npc = NPCEngine.generate_bot_knight(target_level=npc_lvl)
    npc["persona"] = persona
    
    # 3-Roundlik Kinetik Guruh Tomoshasi
    attacker = {
        "name": char["name"], "strength": char["strength"], "agility": char["agility"],
        "stamina": char["stamina"], "weapon_attack": 25, "is_defending": False
    }
    defender = {
        "name": npc["name"], "hp": npc["hp"], "constitution": npc["constitution"],
        "agility": npc["agility"], "stamina": npc["stamina"], "armor_defense": npc["armor_defense"],
        "is_defending": False
    }

    # Round 1
    dmg1, log1, crit1 = BattleEngine.calculate_round(attacker, defender, "neck", "heavy_strike")
    defender["hp"] -= dmg1

    # NPC javob reaksiyasi va guruhga gap otishi
    npc_reaction = ""
    if defender["hp"] <= 0:
        npc_reaction = f"💀 *{npc['name']}:* 'La'nat... Valoriya tuprog'iga qonim to'kildi... Ser Artur, seni qarg'ayman!'"
    elif persona == "berserk":
        npc_reaction = f"🩸 *{npc['name']}:* 'Shumi zarbang?! Men bu og'riqdan faqat kuch olaman, {char['name']}!'"
    elif persona == "coward":
        npc_reaction = f"🏃 *{npc['name']}:* 'Voy onajon! Bo'yin tomirimdan qon oqyapti! Qochinglar!'"
    else:
        npc_reaction = f"🐍 *{npc['name']}:* 'Yaxshi zarba, lekin mening zahrim seni yeydi!'"

    # Natija
    if defender["hp"] <= 0:
        await update_character(char["id"], gold=char["gold"] + npc["loot_gold"], xp=char["xp"] + npc["loot_xp"], wins=char["wins"] + 1)
        result_text = (
            f"⚔️ *GURUH ARENASI JANG NATIJASI!* 🏆\n\n"
            f"👤 *{char['name']}* VS 👹 *{npc['name']}*\n\n"
            f"{log1}\n\n"
            f"🗣 {npc_reaction}\n\n"
            f"🎉 *G'ALABA!* Dushman yer tishlatildi!\n"
            f"💰 *Topilgan O'lja:* +{npc['loot_gold']} Oltin | +{npc['loot_xp']} XP\n"
            f"👏 Butun guruh xalqi jasur *{char['name']}* sharafiga qadah ko'tarmoqda!"
        )
    else:
        result_text = (
            f"⚔️ *QIZG'IN JANG DAVOM ETMOQDA!* 🩸\n\n"
            f"👤 *{char['name']}* VS 👹 *{npc['name']}*\n\n"
            f"{log1}\n\n"
            f"🗣 {npc_reaction}\n\n"
            f"📊 *{npc['name']}* joni: *{max(0, defender['hp'])}/{npc['max_hp']}*\n"
            f"Jang shaxsiy xonada davom etishi mumkin: [@ValoriyaRpgBot](https://t.me/ValoriyaRpgBot)"
        )

    await callback.message.edit_text(result_text, parse_mode="Markdown")

# =====================================================================
# 3. GURUH GLOBAL REYD BOSSI (!boss, !ajdaho) - VIRAL KOOPERATIV JANG
# =====================================================================
@group_router.message(F.chat.type.in_(["group", "supergroup"]), F.text.regexp(r"^(!|\/)(boss|ajdaho|raid)"))
async def spawn_group_boss(message: Message):
    chat_id = message.chat.id
    
    # Guruh uchun yangi boss yaratamiz
    ACTIVE_GROUP_BOSSES[chat_id] = {
        "name": "🔥 Qora Qoya Ajdahosi Ignis",
        "hp": 1500,
        "max_hp": 1500,
        "participants": {}
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗡 Ajdahoga Hujum Qilish!", callback_data="hit_group_boss"),
            InlineKeyboardButton(text="🛡 Qalqon Tutish", callback_data="shield_group_boss")
        ]
    ])

    await message.answer(
        "🚨 *DIQQAT! GURUHGA GLOBAL REYD BOSSI HUJUM QILDI!* 🚨\n\n"
        "🌋 Osmon qorayib, alangali olov purkovchi **Qora Qoya Ajdahosi Ignis** osmondan tushdi!\n\n"
        "❤️ Ajdaho Umumiy Joni: *1500 / 1500 HP*\n"
        "👑 Butun guruh a'zolari birgalikda zarba berib, qit'ani qutqarishi kerak!\n\n"
        "Kim oxirgi hal qiluvchi zarbani bersa, *1000 Oltin va Afsonaviy Qilich* oladi!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@group_router.callback_query(F.data == "hit_group_boss")
async def hit_group_boss(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Ritsar"

    boss = ACTIVE_GROUP_BOSSES.get(chat_id)
    if not boss or boss["hp"] <= 0:
        await callback.answer("Ajdaho allaqachon mag'lub etilgan!", show_alert=True)
        return

    char = await get_character_by_user_id(user_id)
    dmg = random.randint(30, 85)
    if char:
        dmg += int(char["strength"] * 1.5)

    boss["hp"] -= dmg
    boss["participants"][user_name] = boss["participants"].get(user_name, 0) + dmg

    if boss["hp"] <= 0:
        boss["hp"] = 0
        if char:
            await update_character(char["id"], gold=char["gold"] + 1000, xp=char["xp"] + 800)
            
        ranking_text = "\n".join([f"🏅 *{p}*: {d} zarar" for p, d in sorted(boss["participants"].items(), key=lambda x: x[1], reverse=True)[:5]])
        
        await callback.message.edit_text(
            f"🏆 *AFSONAVIY G'ALABA! AJDAHO IGNIS MAG'LUB ETILDI!* 🏆\n\n"
            f"Oxirgi hal qiluvchi zarbani *{user_name}* berdi va 1000 Oltin mukofotini oldi!\n\n"
            f"📊 *Eng ko'p zarar bergan qahramonlar:*\n"
            f"{ranking_text}\n\n"
            f"Valoriya imperiyalari sizlarga bosh egadi!",
            parse_mode="Markdown"
        )
    else:
        await callback.answer(f"💥 Siz ajdahoga {dmg} zarar yetkazdingiz!", show_alert=False)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🗡 Yana Zarba Berish!", callback_data="hit_group_boss"),
                InlineKeyboardButton(text="🛡 Himoyalanish", callback_data="shield_group_boss")
            ]
        ])
        await callback.message.edit_text(
            f"🌋 *AJDAHO BILAN QIZG'IN JANG!* 🌋\n\n"
            f"⚔️ Oxirgi zarba: *{user_name}* ajdaho qanotiga *{dmg}* zarar berdi!\n"
            f"❤️ Ajdaho qolgan joni: *{boss['hp']} / {boss['max_hp']} HP*\n\n"
            f"Barcha ritsarlar, qurollarni ishga soling!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# =====================================================================
# 4. GURUHDA BOTGA GAPIRGANDA NPC VA ARTUR JAVOB BERISHI
# =====================================================================
@group_router.message(F.chat.type.in_(["group", "supergroup"]))
async def group_chatter_ai(message: Message):
    if not message.text:
        return
        
    text = message.text.lower()
    bot_info = await message.bot.get_me()
    bot_username = (bot_info.username or "").lower()
    
    is_mentioned = f"@{bot_username}" in text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id

    # Faqat botga murojaat qilinganda yoki teg qilinganda gapiradi
    if not (is_mentioned or is_reply_to_bot or text.startswith("!")):
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Ritsar"
    username = message.from_user.username
    is_owner = is_owner_user(user_id, username)

    # Owner guruhda gapirganda
    if is_owner and any(k in text for k in ["qonli oy", "ajdaho", "god", "amr"]):
        await message.reply(
            f"👑 *Ser Artur (Butun guruhga jar solib):*\n\n"
            f"'JIM BO'LING, EY QIT'A AHLI! Oliy Yaratuvchi {user_name} so'zlamoqda!\n"
            f"Uning har bir amri 12 ta imperiya uchun qonundir!'",
            parse_mode="Markdown"
        )
        return

    # Random NPC larning guruhdagi javobi
    npc_speakers = [
        ("🧙‍♂️ Sehrgar Elric", "Yulduzlar bugun bu guruhda buyuk jang bo'lishini bashorat qilmoqda..."),
        ("🩸 Qonxo'r Ragnar", f"Hoy {user_name}! Ko'p gapirmay, qo'lingdan kelsa !duel deb yoz va maydonga tush!"),
        ("🍻 Taverna Egasi Otto", f"Xush kelibsizlar, janoblar! 'Qonli Qadah' tavernasida eng yaxshi qora pivo tayyor!"),
        ("🛡 Ser Artur", f"Hazratim {user_name}, qilichingiz doimo charxlangan bo'lsin!")
    ]
    speaker, phrase = random.choice(npc_speakers)

    await register_group(message.chat.id, message.chat.title or "Guruh")
    await message.reply(f"{speaker}: \"{phrase}\"", parse_mode="Markdown")

# =====================================================================
# 5. DARVESH XAZINASINI BIRINCHI BO'LIB OLISH
# =====================================================================
@group_router.callback_query(F.data.startswith("claim_dervish_"))
async def handle_claim_dervish(callback: CallbackQuery):
    drop_id = callback.data.replace("claim_dervish_", "")
    drop = ACTIVE_DROPS.get(drop_id)
    
    if not drop or drop.get("claimed", False):
        await callback.answer("⏳ Kechikdingiz! Ushbu xazinani boshqa chaqqon ritsar olib ketdi!", show_alert=True)
        return
        
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Ritsar"
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Xazinani olish uchun avval botda /start bosing!", show_alert=True)
        return
        
    drop["claimed"] = True
    gold_won = drop["gold"]
    await update_character(char["id"], gold=char["gold"] + gold_won)
    
    await callback.message.edit_text(
        f"🎉 *XAZINA EGASI TOPILDI!* 💰\n\n"
        f"⚡️ Jasur ritsar *{user_name}* eng chaqqon chiqdi va "
        f"Darvesh Salmonning xaltasidan *+{gold_won} Oltin* oldi!\n\n"
        f"Darvesh Salmon guruh ahlini duo qilib, yo'lida davom etdi...",
        parse_mode="Markdown"
    )

# =====================================================================
# 6. SHOVQIN VA TASODIFIY NPC CHAQIRISH (!gapir, !shovqin)
# =====================================================================
@group_router.message(F.chat.type.in_(["group", "supergroup"]), F.text.regexp(r"^(!|\/)(shovqin|npc_gapir|gapir)"))
async def trigger_spontaneous_shovqin(message: Message):
    await register_group(message.chat.id, message.chat.title or "Guruh")
    text, keyboard = NPCBroadcaster.generate_spontaneous_event()
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

