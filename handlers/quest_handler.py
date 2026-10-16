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

    buttons.append([InlineKeyboardButton(text="🎟 1-Mavsum Jang Chiptasi (Battle Pass)", callback_data="menu_battle_pass")])
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

# =====================================================================
# BATTLE PASS (MAVSUM CHIPTASI)
# =====================================================================
@router.message(F.text.startswith("/battlepass") | F.text.startswith("/pass"))
async def cmd_battle_pass(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return
    text, markup = await render_battle_pass_ui(char["id"])
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "menu_battle_pass")
async def cb_battle_pass(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        return
    text, markup = await render_battle_pass_ui(char["id"])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)

async def render_battle_pass_ui(character_id: int):
    import json
    from database.db import get_or_create_battle_pass
    from game.battle_pass import SEASON_INFO, BATTLE_PASS_TIERS, calculate_bp_tier, DAILY_SEASON_CHALLENGES

    bp = await get_or_create_battle_pass(character_id)
    cur_tier = calculate_bp_tier(bp["total_exp"])
    claimed_free = set(json.loads(bp.get("claimed_free_json") or "[]"))
    has_royal = bp.get("has_royal") == 1

    text = (
        f"🎟 *{SEASON_INFO['title']}* 🎟\n\n"
        f"⏳ Mavsum tugashiga: *{SEASON_INFO['days_left']} kun* qoldi.\n"
        f"🌟 Sizning Tieringiz: *Tier {cur_tier} / {SEASON_INFO['max_tier']}*\n"
        f"⚡️ Mavsum Tajribasi (EXP): *{bp['total_exp']} EXP*\n"
        f"👑 Qirollik Pass: *{'Faol 🟢' if has_royal else 'Faol emas ⚪️'}*\n\n"
        f"🎁 *Yaqin Olish Mumkin Bo'lgan Sovrinlar:*\n"
    )

    buttons = []
    # Show current tier and next 3 tiers
    for t in range(max(1, cur_tier - 1), min(51, cur_tier + 4)):
        tier_data = BATTLE_PASS_TIERS[t]
        free_claimed = t in claimed_free
        can_claim = (cur_tier >= t and not free_claimed)

        status_icon = "✅" if free_claimed else ("🎁 [Olish]" if can_claim else "🔒")
        text += f"• *Tier {t}:* {tier_data['free']['name']} — {status_icon}\n"

        if can_claim:
            buttons.append([
                InlineKeyboardButton(text=f"🎁 Tier {t} Sovg'asini Olish ({tier_data['free']['name']})", callback_data=f"bp_claim_{t}_free")
            ])

    text += "\n📌 *Mavsumiy Kunlik Vazifalar (EXP Olish uchun):*\n"
    for ch in DAILY_SEASON_CHALLENGES[:4]:
        text += f"• {ch['desc']} (+{ch['exp']} EXP)\n"

    buttons.append([InlineKeyboardButton(text="📜 Kundalik Kvestlarga Qaytish", callback_data="menu_quests")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    return text, InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data.startswith("bp_claim_"))
async def cb_claim_bp(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        return

    parts = callback.data.split("_")
    tier = int(parts[2])
    track = parts[3]

    from database.db import claim_bp_reward
    success, msg = await claim_bp_reward(char["id"], tier, track)
    await callback.answer(msg, show_alert=True)
    text, markup = await render_battle_pass_ui(char["id"])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
