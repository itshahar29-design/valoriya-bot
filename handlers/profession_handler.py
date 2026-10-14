from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_player_professions,
    mine_resources, brew_potion, use_potion
)

profession_router = Router()

@profession_router.callback_query(F.data == "menu_professions")
async def show_professions_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    profs = await get_player_professions(char["id"])
    potions = profs.get("potions", {})

    active_buff = ""
    if char.get("active_buff_potion"):
        active_buff = f"\n⚡️ *Faol Damlama:* {char['active_buff_potion'].upper()} ({char.get('buff_potion_battles', 0)} ta jang qoldi!)"

    text = (
        "⛏ *VALORIYA SHAXTASI VA ALXIMIYA USTAXONASI* 🧪\n\n"
        "Bu yerda ritsarlar qoyalardan qimmatbaho rudalar qazib oladi va "
        "qadimiy qozonlarda jangovar damlamalar (potions) tayyorlaydi!\n\n"
        f"⚡️ Chidamlilik (Stamina): *{char['stamina']}/100*\n"
        f"📦 *Yig'ilgan Resurslaringiz:*\n"
        f"• 🔩 Temir rudasi: *{profs.get('iron_ore', 0)} ta*\n"
        f"• 🪙 Oltin rudasi: *{profs.get('gold_ore', 0)} ta*\n"
        f"• ✨ Sehrli Mithril: *{profs.get('mithril_ore', 0)} ta*\n"
        f"• 🌿 Shifobaxsh O'tlar: *{profs.get('herbs', 0)} ta*\n\n"
        f"🧪 *Tayyor Damlamalaringiz:*\n"
        f"• 🔥 G'azab (+30% ATK): *{potions.get('rage', 0)} ta*\n"
        f"• ❤️ Hayot Eliksiri (Jon 100%): *{potions.get('healing', 0)} ta*\n"
        f"• 💀 Zulmat Zaxari (+40 Zaharlash): *{potions.get('void_poison', 0)} ta*{active_buff}\n\n"
        "Qanday harakat qilasiz?"
    )

    buttons = [
        [
            InlineKeyboardButton(text="⛏ Shaxtada Qazish (-20 Stamina)", callback_data="action_mine_ore")
        ],
        [
            InlineKeyboardButton(text="🧪 G'azab Damlamasi (2 Temir + 1 O't)", callback_data="brew_potion_rage"),
            InlineKeyboardButton(text="❤️ Hayot Eliksiri (3 O't + 1 Oltin)", callback_data="brew_potion_healing")
        ],
        [
            InlineKeyboardButton(text="💀 Zulmat Zaxari (1 Mithril + 2 O't)", callback_data="brew_potion_void_poison")
        ],
        [
            InlineKeyboardButton(text="🔥 G'azabni Ichish", callback_data="use_potion_rage"),
            InlineKeyboardButton(text="❤️ Jonni Tiklash", callback_data="use_potion_healing"),
            InlineKeyboardButton(text="💀 Zaxarni Surtish", callback_data="use_potion_void_poison")
        ],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@profession_router.callback_query(F.data == "action_mine_ore")
async def process_mining(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg, _ = await mine_resources(char["id"])
    await callback.answer("⛏ Cho'kich bilan qoya urilmoqda...", show_alert=False)
    
    buttons = [
        [InlineKeyboardButton(text="⛏ Yana Qazish (-20 Stamina)", callback_data="action_mine_ore")],
        [InlineKeyboardButton(text="⬅️ Ustaxona", callback_data="menu_professions")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@profession_router.callback_query(F.data.startswith("brew_potion_"))
async def process_brew(callback: CallbackQuery):
    potion_type = callback.data.replace("brew_potion_", "")
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await brew_potion(char["id"], potion_type)
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_professions_menu(callback)

@profession_router.callback_query(F.data.startswith("use_potion_"))
async def process_use(callback: CallbackQuery):
    potion_type = callback.data.replace("use_potion_", "")
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await use_potion(char["id"], potion_type)
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_professions_menu(callback)
