from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from database.db import get_character_by_user_id, create_character, get_character_equipment, update_character
from config import OWNER_ID, OWNER_USERNAME
from game.constants import CLASSES
from game.retention_engine import RetentionEngine
from keyboards.inline_menus import main_menu_keyboard, class_selection_keyboard

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
        if target_owner and not character.get("is_owner", 0):
            await update_character(character["id"], is_owner=1, hide_from_leaderboard=1)
            character["is_owner"] = 1
            character["hide_from_leaderboard"] = 1
        is_owner = bool(character.get("is_owner", 0))
        await message.answer(
            f"👑 *Qaytganingiz bilan, {character['name']}!*\n\n"
            f"🏰 Daraja: *{character['level']}* | 🪙 Oltin: *{character['gold']}*\n"
            f"⚔️ Kasb: *{character['class_id'].upper()}* | ❤️ Jon: *{character['hp']}/{character['max_hp']}*\n\n"
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
        f"🪙 Oltin: *{char['gold']}* | 💎 Qimmatbaho javohirlar: *{char['gems']}*\n"
        f"🐴 Tulpor: *{char['horse_name']}* (Bog'lanish: {char['horse_bond']}%)\n"
        f"🏆 Janglar: *{char['wins']}* G'alaba | *{char['losses']}* Mag'lubiyat"
    )
    buttons = [[InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
