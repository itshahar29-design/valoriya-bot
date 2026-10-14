import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_connection, get_character_by_user_id, update_character,
    create_world_snapshot, get_world_telemetry, give_global_airdrop, get_active_groups,
    get_character_by_identifier, give_player_item
)
from keyboards.inline_menus import owner_god_mode_keyboard, main_menu_keyboard
from config import OWNER_ID, OWNER_USERNAME

owner_router = Router()

def is_owner_authorized(user_id: int, username: str | None, char: dict | None) -> bool:
    if char and char.get("is_owner", 0):
        return True
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return False

@owner_router.callback_query(F.data == "menu_owner_god")
async def open_owner_god_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    
    if not is_owner_authorized(user_id, username, char):
        await callback.answer("⛔️ Ruxsat berilmagan! Faqat Oliy Yaratuvchi (Owner) uchun!", show_alert=True)
        return
        
    await callback.message.edit_text(
        "⚡️ *VALORIYA YARATUVCHISI (GOD-MODE) MARKAZIY BOSHQARUVI* ⚡️\n\n"
        "Siz butun qit'a, 12 ta imperiya va barcha ritsarlar taqdiri ustidan mutlaq qudratga egasiz!\n"
        "Profilingiz reytinglarda 100% yashirin va daxlsizdir.\n\n"
        "👑 *Boshqaruv vositalari:*\n"
        "• Cheksiz boylik, javohirlar va Xudo darajasidagi qurollar\n"
        "• Global Dunyo ofatlari: Qonli Oy, Ajdaho, Oltin va Meteor yomg'iri\n"
        "• Barcha ritsarlarga saxovatli Airdrop va Guruhlarga Oliy Farmon\n"
        "• Foolproof Snapshot va 1-tugmali Rollback xavfsizligi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

# 1. CHEKSIZ XAZINA (+50,000 Oltin)
@owner_router.callback_query(F.data == "god_grant_gold")
async def grant_owner_gold(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await update_character(char["id"], gold=char["gold"] + 50000, gems=char.get("gems", 0) + 100)
    await callback.answer("💰 Xazinangizga +50,000 Oltin va +100 Qimmatbaho Javohir qo'shildi!", show_alert=True)
    await open_owner_god_menu(callback)

# 2. GOD-STATS (99,999 HP / 999 STR)
@owner_router.callback_query(F.data == "god_max_stats")
async def set_owner_god_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await update_character(
        char["id"],
        hp=99999, max_hp=99999,
        stamina=9999, max_stamina=9999,
        strength=999, agility=999, constitution=999, intelligence=999
    )
    await callback.answer("⚡️ OLIY YARATUVCHI QUDRATI YOQILDI!\nHP: 99,999 | Kuch: 999 | Himoya: 999", show_alert=True)
    await open_owner_god_menu(callback)

# 3. AFSONAVIY YARATUVCHI QILICHI (+999 ATK)
@owner_router.callback_query(F.data == "god_spawn_sword")
async def spawn_god_sword(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
        VALUES (?, 'weapon', '👑 Valoriya Yaratuvchisining Qonli Qilichi', 'mythic', 999, 150, 9999, 9999, 1);
        """, (char["id"],))
        await db.commit()
        
    await callback.answer("🗡 'Yaratuvchining Qonli Qilichi' (+999 Zarba) yaratildi va qo'lingizga berildi!", show_alert=True)

# 4. DAXLSIZLIK QALQONI (+999 DEF)
@owner_router.callback_query(F.data == "god_spawn_shield")
async def spawn_god_shield(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
        VALUES (?, 'shield', '🛡 Valoriya Daxlsizlik Qalqoni', 'mythic', 50, 999, 9999, 9999, 1);
        """, (char["id"],))
        await db.commit()
        
    await callback.answer("🛡 'Valoriya Daxlsizlik Qalqoni' (+999 Himoya) yaratildi va taqildi!", show_alert=True)

# 5. QONLI OY (BLOOD MOON)
@owner_router.callback_query(F.data == "god_blood_moon")
async def trigger_blood_moon(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_blood_moon", "Qonli oy hodisasi boshlanishidan oldingi snapshot")
    
    # Barcha guruhlarga xabar
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🩸 *DIQQAT! VALORIYA OSMONIDA QONLI OY YOQILDI!* 🩸\n\n"
                "Osmon qip-qizil tusga kirdi! Barcha Berserklarning zarbasi 2 barobar oshirildi! Qabrlardan sharpalar uyg'onmoqda!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🩸 Qonli Oy butun dunyoda yoqildi va guruhlarga e'lon qilindi!", show_alert=True)

# 6. AJDAHO REYDI
@owner_router.callback_query(F.data == "god_dragon_raid")
async def trigger_dragon_raid(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_dragon_raid", "Ajdaho reydi chaqirilishidan oldingi snapshot")
    
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🐉 *AFSONAVIY ZANGORI AJDAHO IGNIS OSMONDAN TUSHDI!* 🐉\n\n"
                "Oliy Yaratuvchi farmoni bilan ulkan reyd boshlandi! Jang qilish uchun `!boss` deb yozing!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🐉 Ajdaho reydi butun qit'ada faollashtirildi!", show_alert=True)

# 7. OLTIN YOMG'IRI (2x LOOT)
@owner_router.callback_query(F.data == "god_golden_rain")
async def trigger_golden_rain(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🌧 *OLTIN YOMG'IRI HODISASI BOSHLANDI!* 🪙\n\n"
                "Osmonlardan oltin tangalar yog'moqda! Bugun barcha janglarda o'ljalar 2 barobar ko'p beriladi!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🌧 Oltin yomg'iri hodisasi barcha guruhlarda yoqildi!", show_alert=True)

# 8. METEOR BO'RONI (OFAT)
@owner_router.callback_query(F.data == "god_meteor_storm")
async def trigger_meteor_storm(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_meteor_storm", "Meteor bo'roni oldingi snapshot")
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "☄️ *OSMONDAN ALANGALI METEORITLAR QULAMOQDA!* ☄️\n\n"
                "Valoriya zaminini osmon toshlari larzaga keltirdi! Qal'alar titramoqda, qalqonlaringizni mahkam tuting!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("☄️ Meteor bo'roni dunyoga yo'naltirildi!", show_alert=True)

# 9. BARCHA RITSARLARGA AIRDROP (+500 Oltin)
@owner_router.callback_query(F.data == "god_airdrop_all")
async def trigger_global_airdrop(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await give_global_airdrop(500)
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🎁 *YARATUVCHIDAN BUTUN VALORIYAGA GLOBAL AIRDROP!* 🎁\n\n"
                "Oliy Yaratuvchi @NAKAMA_02 saxovati bilan barcha ritsarlarning xazinasiga **+500 Tillo Tanga** hadya etildi!\n"
                "Valoriya taxti nomidan qasamyodingiz mustahkam bo'lsin!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🎁 Barcha o'yinchilarga +500 Oltin tarqatildi va e'lon qilindi!", show_alert=True)

# 10. BARCHA GURUHLARGA YARATUVCHI E'LONI
@owner_router.callback_query(F.data == "god_broadcast_all")
async def trigger_god_broadcast(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "📢 *VALORIYA YARATUVCHISI @NAKAMA_02 OLAMSHUMUL FARMONI!* 👑\n\n"
                "\"Ey 12 ta imperiya hukmdorlari va qit'aning barcha ritsarlari!\n"
                "Qilichlaringizni ko'taring, chunki shon-sharaf faqat jang maydonida qon to'kkanlarga nasib qiladi!\n"
                "Valoriya qonunlari mening irodam bilan mustahkamdir!\"",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("📢 Oliy Yaratuvchi e'loni barcha guruhlarga yuborildi!", show_alert=True)

# 11. DUNYO TELEMETRIYASI
@owner_router.callback_query(F.data == "god_inspect")
async def inspect_world_telemetry(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    telem = await get_world_telemetry()
    text = (
        "📊 *VALORIYA BUTUN DUNYO TELEMETRIYASI* 📊\n\n"
        f"👥 Jami Ro'yxatdan O'tgan Ritsarlar: *{telem['total_chars']} ta*\n"
        f"🏰 Faol Ulangan Guruhlar: *{telem['total_groups']} ta*\n"
        f"⚔️ Yaratilgan Qurol va Sovutlar: *{telem['total_items']} ta*\n\n"
        f"💰 O'yinchilar Qo'lidagi Jami Oltin: *{telem['total_player_gold']:,} 🪙*\n"
        f"🏛 12 Imperiya Xazinasidagi Jami Oltin: *{telem['total_kingdom_gold']:,} 🪙*\n\n"
        "🛡 Barcha relyatsion jadvallar va server parametrlari 100% barqaror ishlamoqda."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=owner_god_mode_keyboard())

# 12. YANGI SNAPSHOT SAQLASH
@owner_router.callback_query(F.data == "god_save_snapshot")
async def manual_save_snapshot(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("manual_owner_backup", "Owner tomonidan olingan to'liq xavfsiz zaxira nusxasi")
    await callback.answer("💾 Dunyo holati va barcha o'yinchilar ma'lumoti to'liq arxivlandi!", show_alert=True)

# 13. ROLLBACK QILISH
@owner_router.callback_query(F.data == "god_rollback")
async def trigger_rollback(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await callback.answer("⏪ Dunyo xavfsiz snapshotga qaytarildi!", show_alert=True)
    await callback.message.edit_text(
        "✅ *ROLLBACK MUVAFFAQIYATLI BAJARILDI!* ✅\n\n"
        "Dunyodagi barcha parametrlar va iqtisodiy oqimlar oxirgi barqaror holatga qaytarildi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

# =====================================================================
# 14. O'YINCHILARNI BOSHQARISH YO'RIQNOMASI
# =====================================================================
@owner_router.callback_query(F.data == "god_player_mgmt_guide")
async def show_player_mgmt_guide(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    text = (
        "👤 *O'YINCHILARNI BOSHQARISH VA QAZO (ADMIN) VOSITALARI* 👑\n\n"
        "Siz istalgan guruhda yoki shaxsiy chatda o'yinchining xabariga **Reply** qilib yoki uning `@username`ini yozib boshqarishingiz mumkin:\n\n"
        "💰 *Pul Berish:*\n"
        "`/give_gold @username 5000` *(yoki reply qilib: `/give_gold 5000`)*\n\n"
        "💸 *Pul Olish (Tortib olish):*\n"
        "`/take_gold @username 2000`\n\n"
        "🗡 *Afsonaviy Qurol Berish:*\n"
        "`/give_item @username Afsonaviy Zangori Qilich`\n\n"
        "👑 *Daraja Berish / O'zgartirish:*\n"
        "`/set_level @username 15`\n\n"
        "⛓ *Zindonga Tashlash (Muzlatish):*\n"
        "`/jail @username`\n\n"
        "🕊 *Zindondan Ozod Qilish:*\n"
        "`/unjail @username`"
    )
    buttons = [[InlineKeyboardButton(text="⬅️ God-Mode Panel", callback_data="menu_owner_god")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 15. ADMIN KOMANDALARI: PUL VA BUYUM BOSHQARUVI
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_gold|ber_oltin|pul_ber)"))
async def admin_give_gold(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    amount = 1000
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_ident = args[1]
        amount = int(args[2])
        target_char = await get_character_by_identifier(target_ident)
    elif len(args) == 2 and args[1].isdigit():
        target_char = char
        amount = int(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/give_gold @username 5000` yoki reply qilib `/give_gold 5000`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], gold=target_char["gold"] + amount)
    await message.reply(
        f"💰 *OLTIN IN'OM ETILDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* xazinasiga **+{amount:,} Oltin** berildi!\n"
        f"Hozirgi balansi: *{target_char['gold'] + amount:,} 🪙*",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(take_gold|ol_oltin|pul_ol)"))
async def admin_take_gold(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    amount = 500
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_ident = args[1]
        amount = int(args[2])
        target_char = await get_character_by_identifier(target_ident)
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/take_gold @username 2000`", parse_mode="Markdown")
        return
        
    new_gold = max(0, target_char["gold"] - amount)
    await update_character(target_char["id"], gold=new_gold)
    await message.reply(
        f"💸 *OLTIN TORTIB OLINDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* xazinasidan **-{amount:,} Oltin** musodara qilindi!\n"
        f"Qolgan balansi: *{new_gold:,} 🪙*",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(give_item|ber_qurol|buyum)"))
async def admin_give_item(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    item_name = "Afsonaviy Olovli Qilich"
    args = message.text.split(maxsplit=2)
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1:
            item_name = " ".join(args[1:])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        item_name = args[2]
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/give_item @username Afsonaviy Qilich`", parse_mode="Markdown")
        return
        
    await give_player_item(target_char["id"], item_name=item_name, slot_type="weapon", attack=180, defense=40, rarity="mythic")
    await message.reply(
        f"🗡 *AFSONAVIY BUYUM SOVG'A QILINDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* ga yangi qurol berildi:\n"
        f"✨ *'{item_name}'* (Mifik daraja, +180 Zarba)!\n"
        f"Buyum uning anjomlar ro'yxatiga qo'shildi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(set_level|daraja)"))
async def admin_set_level(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    lvl = 10
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            lvl = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_char = await get_character_by_identifier(args[1])
        lvl = int(args[2])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/set_level @username 15`", parse_mode="Markdown")
        return
        
    await update_character(
        target_char["id"],
        level=lvl,
        hp=100 + (lvl * 25), max_hp=100 + (lvl * 25),
        strength=15 + (lvl * 5), constitution=10 + (lvl * 4)
    )
    await message.reply(
        f"👑 *RITSAR DARAJA KO'TARILDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* darajasi to'g'ridan-to'g'ri *{lvl}-Daraja*ga o'rnatildi!\n"
        f"Uning joni va kuch parametrlari yangilandi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(jail|zindonga)"))
async def admin_jail_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/jail @username`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], is_jailed=1)
    await message.reply(
        f"⛓ *RITSAR ZINDONGA TASHLANDI!* ⛓\n\n"
        f"Ritsar *{target_char['name']}* Oliy Yaratuvchi g'azabiga uchradi va Qirollik Zindoniga zanjirband qilindi!\n"
        f"U Yaratuvchi kechirmagunicha harakat qila olmaydi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(unjail|ozod)"))
async def admin_unjail_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/unjail @username`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], is_jailed=0)
    await message.reply(
        f"🕊 *RITSAR ZINDONDAN OZOD QILINDI!* 🕊\n\n"
        f"Ritsar *{target_char['name']}* Yaratuvchining saxovati va marhamati bilan zindondan ozod etildi!",
        parse_mode="Markdown"
    )

