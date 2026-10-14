from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database.db import get_character_by_user_id, create_character, get_character_equipment
from game.constants import CLASSES
from game.retention_engine import RetentionEngine
from keyboards.inline_menus import main_menu_keyboard, class_selection_keyboard

start_router = Router()

@start_router.message(CommandStart())
async def handle_start(message: Message):
    user_id = message.from_user.id
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
    
    if character:
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
    user_name = callback.from_user.first_name or "Jasur Ritsar"
    
    char_id = await create_character(user_id=user_id, name=user_name, class_id=class_id)
    
    class_name = CLASSES.get(class_id, {}).get("name", class_id)
    await callback.message.edit_text(
        f"🎉 *TABRIKLAYMIZ! QASAMYOD QABUL QILINDI!* 🎉\n\n"
        f"Siz *{class_name}* sifatida Valoriya qit'asiga qadam qo'ydingiz!\n\n"
        f"🛡 Sizga dastlabki zangori po'lat qilich, paxtali gambeson va ritsarlik qalqoni berildi.\n"
        f"Endi Arenada jang qilish, auksionda savdo qilish yoki 12 ta AI Qirollikdan biriga xizmatga kirishingiz mumkin!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_owner=False)
    )
