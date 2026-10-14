from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, claim_daily_streak, DAILY_REWARDS

daily_router = Router()

@daily_router.callback_query(F.data == "menu_daily")
async def show_daily_reward_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    streak = char.get("daily_streak", 0) or 0
    
    # 7-Kunlik zanjir ko'rinishi
    streak_bar = ""
    for day in range(1, 8):
        icon = "✅" if day <= streak else "🔒"
        streak_bar += f"{icon} {day}-Kun | "
    streak_bar = streak_bar.rstrip(" | ")

    text = (
        "🎁 *QIROLLIK KUNDALIK MARHAMATI (7-KUNLIK STREAK)* 🎁\n\n"
        "Har kuni o'yinga kiring va tobora qimmatbaho xazinalarni qo'lga kiriting!\n"
        "Agar bir kun o'tkazib yuborsangiz, zanjir 1-kundan qayta boshlanadi.\n\n"
        f"📊 *Sizning joriy zanjiringiz:* {streak} kun ketma-ket\n"
        f"[{streak_bar}]\n\n"
        "👑 *7-Kunda:* 7,777 Oltin, 25 Javohir va Afsonaviy Mifik Gambeson!"
    )

    buttons = [
        [InlineKeyboardButton(text="💎 Bugungi Sovg'ani Olish", callback_data="claim_daily_action")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@daily_router.callback_query(F.data == "claim_daily_action")
async def process_claim_daily(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg, new_streak = await claim_daily_streak(char["id"])
    if not success:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("🎉 Mukofot qabul qilindi!", show_alert=False)
    
    buttons = [[InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]]
    await callback.message.edit_text(
        f"{msg}\n\n"
        f"🔥 *Joriy Zanjiringiz:* {new_streak}/7 kun!\n"
        f"Ertaga yana kiring, mukofot yanada kattaroq bo'ladi!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
