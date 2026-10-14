from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, get_current_king, challenge_king

tournament_router = Router()

@tournament_router.callback_query(F.data == "menu_tournament")
async def show_tournament_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    king = await get_current_king()
    king_name = king.get("king_name") or "Bo'sh (Egalanmagan)"
    defense_wins = king.get("defense_wins", 0)

    is_king = king.get("king_character_id") == char["id"]
    status_msg = "\n👑 *Siz hozirgi Valoriya Qirolisiz! Toj sizning boshingizda!*" if is_king else ""

    text = (
        "👑 *VALORIYA OLIY TAXTI VA BUYUK TURNIR* 👑\n\n"
        "Butun qit'aning eng qudratli ritsari ushbu Oltin Tojni kiyadi!\n"
        "Qirol barcha ritsarlarga buyruq berish, shon-sharaf va barcha bozor savdolaridan soliq olish huquqiga ega!\n\n"
        f"👑 *Amaldagi Valoriya Qiroli:* {king_name}\n"
        f"🛡 *Tojni muvaffaqiyatli himoya qilgan:* {defense_wins} marta{status_msg}\n\n"
        "Har qanday 3-darajadan yuqori ritsar qirolga duel e'lon qilib taxtni tortib olishi mumkin!\n"
        "Jur'at qilasizmi?"
    )

    buttons = []
    if not is_king:
        buttons.append([InlineKeyboardButton(text="⚔️ Qirolga Taxt Duellari E'lon Qilish", callback_data="challenge_king_duel")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tournament_router.callback_query(F.data == "challenge_king_duel")
async def process_challenge_king(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    await callback.answer("👑 Saroy qorovullari darvozani ochmoqda...", show_alert=False)
    success, msg = await challenge_king(char["id"])

    buttons = [
        [InlineKeyboardButton(text="👑 Taxt Zaliga Qaytish", callback_data="menu_tournament")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tournament_router.message(F.text.regexp(r"^(!|\/)(turnir|taxt|qirol|tournament)"))
async def command_tournament_text(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    king = await get_current_king()
    king_name = king.get("king_name") or "Bo'sh (Egalanmagan)"

    buttons = [
        [InlineKeyboardButton(text="👑 Taxt Zali & Turnir", callback_data="menu_tournament")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await message.reply(
        f"👑 *VALORIYA OLIY TAXTI:*\nAmaldagi Qirol: *{king_name}*\n\n"
        f"Taxtga da'vogarlik qilish uchun tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
