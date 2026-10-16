from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_or_create_daily_quests, claim_daily_quest_reward,
    get_player_achievements
)
from keyboards.inline_menus import main_menu_keyboard

router = Router()

ALL_ACHIEVEMENTS = {
    "king_throne": {"name": "👑 Valoriya Oliy Qiroli", "desc": "Markaziy Taxtni egallab butun qit'aga hukmronlik qilish."},
    "arena_champion": {"name": "⚔️ Arena Chempioni", "desc": "Arenada 10 ta g'alabaga erishish."},
    "mining_master": {"name": "⛏ Mohir Konchi", "desc": "Shaxtada kamida 5 marta qazish ishlarini bajarish."},
    "alchemy_master": {"name": "🧪 Mohir Alximik", "desc": "Qozonda sehrli jangovar damlama tayyorlash."},
    "market_trader": {"name": "🛒 Savdo Magnati", "desc": "Ochiq P2P bozorda tovar sotish yoki sotib olish."},
    "demon_pact": {"name": "🩸 Zulmat Qurboni", "desc": "Zulmat ibodatxonasida qonli ahd tuzish."},
    "castle_conqueror": {"name": "🏰 Qal'a Fotihi", "desc": "Gildiya bilan birga qadimiy qal'ani qamal qilish."}
}

def get_progress_bar(current: int, total: int) -> str:
    current = min(current, total)
    filled = int((current / total) * 5)
    return "🟩" * filled + "⬜️" * (5 - filled) + f" [{current}/{total}]"

@router.message(F.text.startswith("/quests") | F.text.startswith("/kvest"))
async def cmd_quests(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return

    q = await get_or_create_daily_quests(char["id"])
    text, markup = render_quests_ui(q)
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "menu_quests")
async def cb_quests(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    q = await get_or_create_daily_quests(char["id"])
    text, markup = render_quests_ui(q)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

def render_quests_ui(q: dict):
    p_arena = get_progress_bar(q["arena_wins"], 2)
    p_mine = get_progress_bar(q["mining_count"], 2)
    p_market = get_progress_bar(q["market_or_tavern"], 1)

    is_all_done = (q["arena_wins"] >= 2 and q["mining_count"] >= 2 and q["market_or_tavern"] >= 1)
    is_claimed = (q.get("is_claimed", 0) == 1)

    text = (
        "📜 *KUNDALIK RITSARLIK KVESTLARI* 🏆\n\n"
        f"📅 Sana: `{q['quest_date']}`\n\n"
        f"1. ⚔️ *Arenada 2 ta g'alaba:*\n{p_arena}\n\n"
        f"2. ⛏ *Shaxtada 2 marta ruda qazish:*\n{p_mine}\n\n"
        f"3. 🛒 *Bozor yoki Tavernada 1 marta savdo/dam olish:*\n{p_market}\n\n"
        "🎁 *To'liq bajarilgandagi mukofot:* +1,500 🪙 Oltin | +2 💎 Javohir | +300 XP\n\n"
    )

    buttons = []
    if is_claimed:
        text += "✅ *Bugungi mukofot to'liq olindi! Yangi vazifalar ertaga soat 00:00 da beriladi.*"
    elif is_all_done:
        text += "🔥 *Barcha 3 ta kvest bajarildi! Mukofotingizni oling!*"
        buttons.append([InlineKeyboardButton(text="🎁 Mukofotni Olish (+1,500🪙 +2💎)", callback_data="claim_daily_quest")])
    else:
        text += "⏳ *Kvestlarni bajaring va kunlik xazinani qo'lga kiriting!*"

    buttons.append([InlineKeyboardButton(text="🏆 Faxriy Yutuqlar (Badges)", callback_data="menu_achievements")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    return text, InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "claim_daily_quest")
async def cb_claim_quest(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    ok, msg = await claim_daily_quest_reward(char["id"])
    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Mukofot berildi!", show_alert=False)
    q = await get_or_create_daily_quests(char["id"])
    text, markup = render_quests_ui(q)
    await callback.message.edit_text(f"{msg}\n\n{text}", parse_mode="Markdown", reply_markup=markup)

# =====================================================================
# YUTUQLAR (ACHIEVEMENTS)
# =====================================================================

@router.message(F.text.startswith("/achievements") | F.text.startswith("/yutuqlar"))
async def cmd_achievements(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return
    text, markup = await render_achievements_ui(char["id"])
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "menu_achievements")
async def cb_achievements(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return
    text, markup = await render_achievements_ui(char["id"])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

async def render_achievements_ui(character_id: int):
    unlocked = await get_player_achievements(character_id)
    unlocked_ids = {a["achievement_id"] for a in unlocked}

    text = (
        "🏆 *FAXRIY RITSARLIK YUTUQLARI (ACHIEVEMENTS)* 🎖\n\n"
        f"Ochilgan yutuqlar: *{len(unlocked_ids)} / {len(ALL_ACHIEVEMENTS)}*\n\n"
    )

    for ach_id, data in ALL_ACHIEVEMENTS.items():
        if ach_id in unlocked_ids:
            text += f"✅ *{data['name']}* (Qo'lga kiritildi!)\n_{data['desc']}_\n\n"
        else:
            text += f"🔒 *{data['name']}* (Qulflangan)\n_{data['desc']}_\n\n"

    buttons = [
        [InlineKeyboardButton(text="📜 Kundalik Kvestlar", callback_data="menu_quests")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    return text, InlineKeyboardMarkup(inline_keyboard=buttons)
