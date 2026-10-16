from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_character_equipment, upgrade_equipment,
    get_runes_inventory, socket_rune_to_equipment, RUNES_DATA
)

forge_router = Router()

@forge_router.callback_query(F.data == "menu_forge")
async def show_forge_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    items = await get_character_equipment(char["id"])
    equipped = [i for i in items if i["is_equipped"] == 1]
    
    buttons = []
    text = (
        "🔨 *VALORIYA QIROVUL TEMIRCHISI (FORGE - DARK SOULS EDITION)* 🔨\n\n"
        "Bu yerda qurol va sovutlaringizni sehrli ruda yordamida **+1 dan +10 gacha** kuchaytirishingiz mumkin!\n"
        "Har bir kuchaytirish qurolga **+15 Zarba**, sovutga **+10 Himoya** beradi.\n\n"
        "⚠️ *ZULMATNING TEMIRCHI QOIDALARI:*\n"
        "• **+1 .. +3:** Xavfsiz (faqat oltin sarflanadi)\n"
        "• **+4 .. +6:** Xavfli (omadsizlikda daraja -1 pasayishi mumkin)\n"
        "• **+7 .. +10:** O'ta Xatarli (qurol maydalanib sinishi mumkin!)\n\n"
        f"🪙 Hamyoningizdagi oltin: *{char['gold']:,} 🪙*\n\n"
        "Qaysi anjomingizni bolg'a ostiga qo'yasiz?"
    )

    for item in equipped:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔨 {item['item_name']} (⚔️{item['attack']} | 🛡{item['defense']})",
                callback_data=f"forge_upgrade_{item['id']}"
            )
        ])
        
    buttons.append([InlineKeyboardButton(text="🔮 Qurolga Runa O'rnatish (Socket)", callback_data="menu_forge_runes")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@forge_router.callback_query(F.data.startswith("forge_upgrade_"))
async def process_forge_upgrade(callback: CallbackQuery):
    item_id = int(callback.data.replace("forge_upgrade_", ""))
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await upgrade_equipment(item_id, char["id"])
    if not success and "yetarli emas" in msg:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("💥 Temirchi bolg'a urmoqda...", show_alert=False)
    
    buttons = [
        [InlineKeyboardButton(text="🔨 Yana Kuchaytirish", callback_data=f"forge_upgrade_{item_id}")],
        [InlineKeyboardButton(text="🔮 Runa O'rnatish", callback_data="menu_forge_runes")],
        [InlineKeyboardButton(text="⬅️ Temirchiga Qaytish", callback_data="menu_forge")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(
        f"{msg}\n\n"
        f"Keyingi qadamni tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# =====================================================================
# RUNALAR O'RNATISH (RUNE SOCKETING)
# =====================================================================

@forge_router.callback_query(F.data == "menu_forge_runes")
async def show_runes_forge_menu(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    runes = await get_runes_inventory(char["id"])
    items = await get_character_equipment(char["id"])
    equipped = [i for i in items if i["is_equipped"] == 1]

    buttons = []
    for item in equipped:
        buttons.append([
            InlineKeyboardButton(
                text=f"✨ {item['item_name']} ga runa qo'yish",
                callback_data=f"forge_pick_rune_item_{item['id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="🛒 Bozorga Borish (Runa sotib olish)", callback_data="market_cat_rune")])
    buttons.append([InlineKeyboardButton(text="⬅️ Temirchiga Qaytish", callback_data="menu_forge")])

    text = (
        "🔮 *TEMIRCHI RUNA USTAXONASI (RUNE SOCKETING)* ✨\n\n"
        "Qadimiy elementar runalarni qurol va sovutlaringizga o'rnatib, jangda mutlaq ustunlikka erishing!\n\n"
        f"📦 *Sizning Runalaringiz:*\n"
        f"• 🔥 Olov Runasi: {runes.get('fire_rune', 0)} dona\n"
        f"• ❄️ Muz Runasi: {runes.get('frost_rune', 0)} dona\n"
        f"• ⚡️ Momaqaldiroq Runasi: {runes.get('lightning_rune', 0)} dona\n\n"
        "_(Har bir anjomga maksimal 2 ta elementar runa joylashtirish mumkin)_\n\n"
        "Qaysi anjomga runa o'rnatmoqchisiz?"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@forge_router.callback_query(F.data.startswith("forge_pick_rune_item_"))
async def pick_rune_for_item(callback: CallbackQuery):
    item_id = int(callback.data.replace("forge_pick_rune_item_", ""))
    char = await get_character_by_user_id(callback.from_user.id)
    runes = await get_runes_inventory(char["id"])

    buttons = []
    if runes.get("fire_rune", 0) > 0:
        buttons.append([InlineKeyboardButton(text="🔥 Olov Runasini O'rnatish (+25 Burn DMG)", callback_data=f"forge_socket_{item_id}_fire_rune")])
    if runes.get("frost_rune", 0) > 0:
        buttons.append([InlineKeyboardButton(text="❄️ Muz Runasini O'rnatish (Dushman qocholmaydi)", callback_data=f"forge_socket_{item_id}_frost_rune")])
    if runes.get("lightning_rune", 0) > 0:
        buttons.append([InlineKeyboardButton(text="⚡️ Momaqaldiroq Runasini O'rnatish (Qalqon teshar)", callback_data=f"forge_socket_{item_id}_lightning_rune")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_forge_runes")])

    if not any(runes.values()):
        text = "⚠️ Sizda hozir hech qanday runa yo'q! Bozordan yoki shaxtaning chuqur qatlamlaridan toping."
    else:
        text = "🔮 O'rnatmoqchi bo'lgan runangizni tanlang:"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@forge_router.callback_query(F.data.startswith("forge_socket_"))
async def process_socket_rune(callback: CallbackQuery):
    # forge_socket_{item_id}_{rune_type}
    parts = callback.data.split("_")
    item_id = int(parts[2])
    rune_type = f"{parts[3]}_{parts[4]}"

    char = await get_character_by_user_id(callback.from_user.id)
    ok, msg = await socket_rune_to_equipment(char["id"], item_id, rune_type)

    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Runa muvaffaqiyatli o'rnatildi!", show_alert=False)
    buttons = [
        [InlineKeyboardButton(text="🔮 Yana Runa O'rnatish", callback_data="menu_forge_runes")],
        [InlineKeyboardButton(text="⚔️ Arenada Sinab Ko'rish", callback_data="menu_arena")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(f"{msg}\n\nJangovar qurolingiz endi elementar afsun bilan yonmoqda!", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

