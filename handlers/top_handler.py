from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_top_knights, get_character_by_user_id
from keyboards.inline_menus import main_menu_keyboard

top_router = Router()

@top_router.callback_query(F.data == "menu_top")
async def show_leaderboard(callback: CallbackQuery):
    top_knights = await get_top_knights(limit=10)
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    is_owner = bool(char.get("is_owner", 0)) if char else False
    
    if not top_knights:
        text = "🏆 *VALORIYA SHON-SHARAF ZALI* 🏆\n\nHali janglar endi boshlanmoqda! Birinchi bo'lib maydonga chiqing."
    else:
        lines = []
        for rank, k in enumerate(top_knights, start=1):
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            badge = medals.get(rank, f"{rank}.")
            k_id = k["kingdom_id"] or "Darbadar"
            lines.append(f"{badge} *{k['name']}* — Lvl {k['level']} | 🎖 {k['honor']} Honor ({k['wins']}W / {k['losses']}L)")
            
        text = "🏆 *VALORIYA SHON-SHARAF ZALI (TOP-10)* 🏆\n\n" + "\n".join(lines)
        
    buttons = [[InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
