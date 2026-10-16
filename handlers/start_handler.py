import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from database.db import (
    get_character_by_user_id, create_character, get_character_equipment,
    update_character, handle_referral_signup, get_referral_stats
)
from config import OWNER_ID, OWNER_USERNAME, is_owner
from game.constants import CLASSES
from game.retention_engine import RetentionEngine
from game.dark_engine import DarkEngine, WOUND_TYPES
from keyboards.inline_menus import main_menu_keyboard, class_selection_keyboard
from keyboards.reply_keyboards import main_reply_keyboard
from services.channel_sub import is_subscribed_to_channel

start_router = Router()

PENDING_REFERRALS = {}

def is_user_owner(user_id: int, username: str | None) -> bool:
    return is_owner(user_id=user_id, username=username)

@start_router.message(CommandStart())
async def handle_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.first_name or "Ritsar"
    
    # 1. MAJBURIY KANALGA A'ZOLIK TEKSHIRUVI
    is_sub, req_channel = await is_subscribed_to_channel(message.bot, user_id, username)
    if not is_sub:
        clean_chan = req_channel.lstrip("@")
        channel_url = f"https://t.me/{clean_chan}"
        buttons = [
            [InlineKeyboardButton(text="📢 Rasmiy Kanalga A'zo Bo'lish", url=channel_url)],
            [InlineKeyboardButton(text="🔄 A'zolikni Tekshirish", callback_data="check_channel_sub")]
        ]
        await message.answer(
            "🛑 *VALORIYA SARHADLARIGA KIRISH CHEKLANGAN!* 🛑\n\n"
            "Qirollik darvozasidan o'tish va o'yinni boshlash uchun rasmiy kanalimizga a'zo bo'lishingiz shart!\n\n"
            f"📢 *Rasmiy Kanal:* {req_channel}\n\n"
            "Kanalga a'zo bo'lgach, pastdagi *'🔄 A'zolikni Tekshirish'* tugmasini bosing:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return

    # Check referral
    args = message.text.split()
    invited_by = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            invited_by = int(args[1].replace("ref_", ""))
            PENDING_REFERRALS[user_id] = invited_by
        except ValueError:
            pass

    character = await get_character_by_user_id(user_id)
    target_owner = is_user_owner(user_id, username)
    
    if character:
        clean_user = (username or "").lower().lstrip("@")
        if character.get("username") != clean_user:
            await update_character(character["id"], username=clean_user)
            
        if target_owner:
            if not character.get("is_owner", 0) or not character.get("hide_from_leaderboard", 0):
                await update_character(character["id"], is_owner=1, hide_from_leaderboard=1)
                character["is_owner"] = 1
                character["hide_from_leaderboard"] = 1
        else:
            if character.get("is_owner", 0) or character.get("hide_from_leaderboard", 0):
                await update_character(character["id"], is_owner=0, hide_from_leaderboard=0)
                character["is_owner"] = 0
                character["hide_from_leaderboard"] = 0
            
        is_owner = target_owner
        
        jail_notice = ""
        if character.get("is_jailed", 0):
            jail_notice = "\n\n⛓ *DIQQAT: Siz Qirollik Zindoniga tashlangansiz!* Yaratuvchi ozod etmagunicha harakatlaringiz cheklangan."
        
        await message.answer(
            f"👑 *Qaytganingiz bilan, {character['name']}!*\n\n"
            f"🏰 Daraja: *{character['level']}* | 🪙 Oltin: *{character['gold']:,}*\n"
            f"⚔️ Kasb: *{character['class_id'].upper()}* | ❤️ Jon: *{character['hp']}/{character['max_hp']}*{jail_notice}\n\n"
            f"Valoriya qit'asida qanday harbiy buyruq berasiz?\n"
            f"Pastdagi tugmalar orqali istalgan bo'limni bir zumda ochishingiz mumkin:",
            parse_mode="Markdown",
            reply_markup=main_reply_keyboard(is_owner)
        )
        await message.answer(
            "🏰 *Valoriya Harbiy Bosh Shtabi:*",
            reply_markup=main_menu_keyboard(is_owner)
        )
    else:
        # FTUE 2-daqiqalik Kvest
        ftue = RetentionEngine.get_ftue_tutorial()
        await message.answer(
            f"⚔️ *VALORIYA: BOQIY QIROLLIKLAR DUNYOSIGA XUSH KELIBSIZ!* ⚔️\n\n"
            f"{ftue['story']}\n\n"
            f"Qaysi yo'nalish bo'yicha qasamyod qilasiz?",
            parse_mode="Markdown",
            reply_markup=class_selection_keyboard()
        )

@start_router.callback_query(F.data == "check_channel_sub")
async def process_check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    is_sub, req_channel = await is_subscribed_to_channel(callback.bot, user_id, username)
    if not is_sub:
        await callback.answer("❌ Siz hali kanalga a'zo bo'lmadingiz! Iltimos, a'zo bo'ling va qayta bosing.", show_alert=True)
        return

    await callback.answer("✅ A'zolik muvaffaqiyatli tasdiqlandi!", show_alert=False)
    character = await get_character_by_user_id(user_id)
    if character:
        is_owner = is_user_owner(user_id, username)
        if is_owner and not character.get("is_owner", 0):
            await update_character(character["id"], is_owner=1, hide_from_leaderboard=1)
        elif not is_owner and character.get("is_owner", 0):
            await update_character(character["id"], is_owner=0, hide_from_leaderboard=0)
        await callback.message.answer(
            f"👑 *Qaytganingiz bilan, {character['name']}!*\n\n"
            f"Harbiy boshqaruv paneli faollashtirildi.",
            parse_mode="Markdown",
            reply_markup=main_reply_keyboard(is_owner)
        )
        await callback.message.edit_text(
            f"👑 *Qaytganingiz bilan, {character['name']}!*\n\n"
            f"🏰 Daraja: *{character['level']}* | 🪙 Oltin: *{character['gold']}*\n"
            f"⚔️ Kasb: *{character['class_id'].upper()}* | ❤️ Jon: *{character['hp']}/{character['max_hp']}*\n\n"
            f"Valoriya qit'asida qanday harbiy buyruq berasiz?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(is_owner)
        )
    else:
        ftue = RetentionEngine.get_ftue_tutorial()
        await callback.message.edit_text(
            f"⚔️ *VALORIYA: BOQIY QIROLLIKLAR DUNYOSIGA XUSH KELIBSIZ!* ⚔️\n\n"
            f"{ftue['story']}\n\n"
            f"Qaysi yo'nalish bo'yicha qasamyod qilasiz?",
            parse_mode="Markdown",
            reply_markup=class_selection_keyboard()
        )

@start_router.callback_query(F.data.startswith("select_class_"))
async def handle_class_selection(callback: CallbackQuery):
    class_id = callback.data.replace("select_class_", "")
    user_id = callback.from_user.id
    username = callback.from_user.username
    user_name = callback.from_user.first_name or "Jasur Ritsar"
    
    is_owner = is_user_owner(user_id, username)
    invited_by = PENDING_REFERRALS.pop(user_id, None)
    char_id = await create_character(user_id=user_id, name=user_name, class_id=class_id, invited_by=invited_by, is_owner=is_owner, username=username)
    
    # Referrer bonus
    if invited_by:
        ok, inv_name, bonus = await handle_referral_signup(user_id, invited_by)
        if ok:
            try:
                await callback.bot.send_message(
                    invited_by,
                    f"🎉 *YANGI DO'ST QASAMYOD QILDI!* 👥\n\n"
                    f"Siz taklif qilgan ritsar *{user_name}* saflarimizga qo'shildi!\n"
                    f"Xazinangizga: **+{bonus} 🪙 Oltin** va **+1 💎 Qimmatbaho Javohir** qo'shildi!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    class_name = CLASSES.get(class_id, {}).get("name", class_id)
    await callback.message.answer(
        f"👑 *Qasamyod qabul qilindi, {user_name}!* Harbiy buyruqlar paneli faollashtirildi.",
        reply_markup=main_reply_keyboard(is_owner=is_owner)
    )
    await callback.message.edit_text(
        f"🎉 *TABRIKLAYMIZ! QASAMYOD QABUL QILINDI!* 🎉\n\n"
        f"Siz *{class_name}* sifatida Valoriya qit'asiga qadam qo'ydingiz!\n\n"
        f"🛡 Sizga dastlabki zangori po'lat qilich, paxtali gambeson va ritsarlik qalqoni berildi.\n"
        f"Endi Arenada jang qilish, auksionda savdo qilish yoki 12 ta AI Qirollikdan biriga xizmatga kirishingiz mumkin!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_owner=is_owner)
    )

@start_router.callback_query(F.data == "menu_profile")
async def show_character_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return
        
    is_owner = is_user_owner(user_id, username)
    status_str = "👑 *Valoriya Yaratuvchisi (Owner - God-Mode)*" if is_owner else "🛡 *Qasamyod qilgan Ritsar*"
    
    sanity = char.get("sanity", 100)
    sanity_badge, sanity_mood, _ = DarkEngine.get_sanity_status(sanity)

    wounds_list = []
    try:
        w_raw = char.get("wounds_json", "[]")
        wounds_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
    except Exception:
        wounds_list = []

    if wounds_list:
        w_names = [WOUND_TYPES.get(w, {}).get("name", w) for w in wounds_list]
        wounds_display = "\n".join([f"  • {name}" for name in w_names])
    else:
        wounds_display = "  • _Jarohatlar yo'q (Tana butun)_"

    has_pact = char.get("bloodline_trait") == "demon_pact"
    pact_display = "🩸 *Iblis Morvath Ahdi* (+45 ATK, 20% Lifesteal, -25 Max HP)" if has_pact else "🌟 *Zulmatdan xoli (Ozod Ruh)*"

    text = (
        f"👤 *RITSAR SHAXSIY HUJJATI* 👤\n\n"
        f"Ism: *{char['name']}*\n"
        f"Maqom: {status_str}\n"
        f"Kasb: *{char['class_id'].upper()}* (Tier {char.get('tier', 1)})\n"
        f"Daraja: *{char['level']}* | Tajriba: *{char['xp']}/1000*\n\n"
        f"❤️ Jon (HP): *{char['hp']}/{char['max_hp']}*\n"
        f"⚡️ Stamina: *{char['stamina']}/{char['max_stamina']}*\n"
        f"🗡 Kuch (STR): *{char['strength']}* | 🏹 Chaqqonlik (AGI): *{char['agility']}*\n"
        f"🛡 Himoya (CON): *{char['constitution']}* | 🧠 Aql (INT): *{char['intelligence']}*\n\n"
        f"🧠 *Ruhiyat (Sanity):* {sanity}% [{sanity_badge}]\n"
        f"🩸 *Zulmat Ahdi:* {pact_display}\n"
        f"🩹 *Faol Travmalar:* \n{wounds_display}\n\n"
        f"🪙 Oltin: *{char['gold']:,}* | 💎 Qimmatbaho javohirlar: *{char['gems']}*\n"
        f"🐴 Tulpor: *{char['horse_name']}* (Bog'lanish: {char['horse_bond']}%)\n"
        f"🏆 Janglar: *{char['wins']}* G'alaba | *{char['losses']}* Mag'lubiyat"
    )

    buttons = []
    buttons.append([InlineKeyboardButton(text="🪪 Vizual Ritsar Kartasi (Banner)", callback_data="menu_card")])
    if wounds_list:
        buttons.append([InlineKeyboardButton(text="🏥 Tabibga Borish (Davolash)", callback_data="tavern_healer_menu")])
    if sanity < 80:
        buttons.append([InlineKeyboardButton(text="🍷 Taverna Sharobi (Sanity +30)", callback_data="tavern_drink_ale")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@start_router.message(F.text.startswith("/card") | F.text.startswith("/banner"))
async def cmd_knight_card(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return

    from services.card_generator import generate_knight_card
    from database.db import get_character_equipment, get_guild_info
    from aiogram.types import BufferedInputFile

    eq = await get_character_equipment(char["id"])
    guild = await get_guild_info(char.get("guild_id", 0)) if char.get("guild_id") else None
    guild_name = guild["name"] if guild else None

    buf = generate_knight_card(char, equipment=eq, guild_name=guild_name)
    photo = BufferedInputFile(buf.getvalue(), filename=f"knight_{user_id}.png")
    caption = (
        f"🪪 *RITSAR RASMIY YORLIG'I: {char['name']}*\n\n"
        f"👑 Qirollik: {char.get('kingdom_id', 'Valoriya')} | Daraja: {char['level']}\n"
        f"⚔️ G'alabalar: {char['wins']} | Mag'lubiyatlar: {char['losses']}\n"
        f"💰 Xazina: {char['gold']:,} 🪙 | {char.get('gems', 0)} 💎"
    )
    buttons = [
        [InlineKeyboardButton(text="⚔️ Arenada Jang", callback_data="menu_arena")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await message.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@start_router.callback_query(F.data == "menu_card")
async def cb_knight_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    from services.card_generator import generate_knight_card
    from database.db import get_character_equipment, get_guild_info
    from aiogram.types import BufferedInputFile

    await callback.answer("🪪 Ritsar kartasi chizilmoqda...", show_alert=False)
    eq = await get_character_equipment(char["id"])
    guild = await get_guild_info(char.get("guild_id", 0)) if char.get("guild_id") else None
    guild_name = guild["name"] if guild else None

    buf = generate_knight_card(char, equipment=eq, guild_name=guild_name)
    photo = BufferedInputFile(buf.getvalue(), filename=f"knight_{user_id}.png")
    caption = (
        f"🪪 *RITSAR RASMIY YORLIG'I: {char['name']}*\n\n"
        f"👑 Qirollik: {char.get('kingdom_id', 'Valoriya')} | Daraja: {char['level']}\n"
        f"⚔️ G'alabalar: {char['wins']} | Mag'lubiyatlar: {char['losses']}\n"
        f"💰 Xazina: {char['gold']:,} 🪙 | {char.get('gems', 0)} 💎"
    )
    buttons = [
        [InlineKeyboardButton(text="⚔️ Arenada Jang", callback_data="menu_arena")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# REFERAL TIZIMI: MENYU VA BUYRUQLAR
# =====================================================================
@start_router.callback_query(F.data == "menu_referral")
async def show_referral_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    stats = await get_referral_stats(user_id)
    bot_me = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_me.username}?start=ref_{user_id}"

    text = (
        "👥 *VALORIYA VIRUSLI REFERAL TIZIMI* 👥\n\n"
        "O'z do'stlaringiz va birodarlaringizni Valoriya qirolligiga taklif qiling va cheksiz boylikka ega bo'ling!\n\n"
        "🎁 *Sizga beriladigan mukofotlar:*\n"
        "• Har bir qo'shilgan do'stingiz uchun: **+500 🪙 Oltin** va **+1 💎 Qimmatbaho Javohir**!\n"
        "• Do'stingiz janglarda yutgan barcha oltinlarning **5% qismi sizga passiv keshbek** bo'lib tushadi!\n\n"
        f"📊 *Sizning statistikangiz:*\n"
        f"• Taklif qilingan ritsarlar: *{stats['count']} ta*\n"
        f"• Ishlab topilgan passiv oltin: *{stats['gold_earned']:,} 🪙*\n\n"
        f"🔗 *Sizning shaxsiy taklif havolangiz:*\n`{ref_link}`\n\n"
        "Havolani nusxalab, do'stlaringiz va guruhlarga yuboring!"
    )
    buttons = [
        [InlineKeyboardButton(text="📢 Do'stlarga Ulashish", url=f"https://t.me/share/url?url={ref_link}&text=Valoriya%20qirolliklar%20urushiga%20qo%27shil%20va%20ritsar%20bo%27l!")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@start_router.message(F.text.regexp(r"^(!|\/)(ref|referal|taklif)"))
async def text_command_referral(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    stats = await get_referral_stats(user_id)
    bot_me = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_me.username}?start=ref_{user_id}"

    text = (
        "👥 *VALORIYA REFERAL HAVOLASI* 👥\n\n"
        f"Har bir taklif uchun: **+500 🪙 Oltin** va **+1 💎 Javohir**!\n"
        f"Taklif qilinganlar: *{stats['count']} ta* | Topilgan oltin: *{stats['gold_earned']:,} 🪙*\n\n"
        f"🔗 *Havolangiz:*\n`{ref_link}`"
    )
    buttons = [
        [InlineKeyboardButton(text="📢 Do'stlarga Ulashish", url=f"https://t.me/share/url?url={ref_link}&text=Valoriya%20qirolliklar%20urushiga%20qo%27shil%20va%20ritsar%20bo%27l!")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await message.reply(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
