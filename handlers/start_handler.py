import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from database.db import get_character_by_user_id, create_character, get_character_equipment, update_character
from config import OWNER_ID, OWNER_USERNAME
from game.constants import CLASSES
from game.retention_engine import RetentionEngine
from game.dark_engine import DarkEngine, WOUND_TYPES
from keyboards.inline_menus import main_menu_keyboard, class_selection_keyboard
from services.channel_sub import is_subscribed_to_channel

start_router = Router()

def is_user_owner(user_id: int, username: str | None) -> bool:
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return False

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
        except ValueError:
            pass

    character = await get_character_by_user_id(user_id)
    target_owner = is_user_owner(user_id, username)
    
    if character:
        clean_user = (username or "").lower().lstrip("@")
        if character.get("username") != clean_user:
            await update_character(character["id"], username=clean_user)
            
        if target_owner and not character.get("is_owner", 0):
            await update_character(character["id"], is_owner=1, hide_from_leaderboard=1)
            character["is_owner"] = 1
            character["hide_from_leaderboard"] = 1
            
        is_owner = bool(character.get("is_owner", 0))
        
        jail_notice = ""
        if character.get("is_jailed", 0):
            jail_notice = "\n\n⛓ *DIQQAT: Siz Qirollik Zindoniga tashlangansiz!* Yaratuvchi ozod etmagunicha harakatlaringiz cheklangan."
        await message.answer(
            f"👑 *Qaytganingiz bilan, {character['name']}!*\n\n"
            f"🏰 Daraja: *{character['level']}* | 🪙 Oltin: *{character['gold']}*\n"
            f"⚔️ Kasb: *{character['class_id'].upper()}* | ❤️ Jon: *{character['hp']}/{character['max_hp']}*{jail_notice}\n\n"
            f"Valoriya qit'asida qanday harbiy buyruq berasiz?",
            parse_mode="Markdown",
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
        is_owner = bool(character.get("is_owner", 0)) or is_user_owner(user_id, username)
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
    char_id = await create_character(user_id=user_id, name=user_name, class_id=class_id, is_owner=is_owner)
    
    class_name = CLASSES.get(class_id, {}).get("name", class_id)
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
        
    is_owner = bool(char.get("is_owner", 0)) or is_user_owner(user_id, username)
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
    if wounds_list:
        buttons.append([InlineKeyboardButton(text="🏥 Tabibga Borish (Davolash)", callback_data="tavern_healer_menu")])
    if sanity < 80:
        buttons.append([InlineKeyboardButton(text="🍷 Taverna Sharobi (Sanity +30)", callback_data="tavern_drink_ale")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
