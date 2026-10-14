from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, get_character_equipment, upgrade_equipment

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
        "🔨 *VALORIYA QIROVUL TEMIRCHISI (FORGE)* 🔨\n\n"
        "Bu yerda qurol va sovutlaringizni sehrli ruda yordamida **+1 dan +10 gacha** kuchaytirishingiz mumkin!\n"
        "Har bir kuchaytirish qurolga **+15 Zarba**, sovutga **+10 Himoya** beradi.\n\n"
        f"🪙 Hamyoningizdagi oltin: *{char['gold']:,} 🪙*\n\n"
        "Qaysi anjomingizni ustaxonaga qo'yasiz?"
    )

    for item in equipped:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔨 {item['item_name']} (⚔️{item['attack']} | 🛡{item['defense']})",
                callback_data=f"forge_upgrade_{item['id']}"
            )
        ])
        
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
        [InlineKeyboardButton(text="⬅️ Temirchiga Qaytish", callback_data="menu_forge")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(
        f"{msg}\n\n"
        f"Keyingi qadamni tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
