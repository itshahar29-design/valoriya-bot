from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_trade_inventory, buy_trade_good, sell_trade_good,
    travel_to_city, TRADE_CITIES
)
from keyboards.inline_menus import main_menu_keyboard

router = Router()

def get_trade_market_keyboard(char: dict, trade_inv: dict):
    city_key = char.get("current_city") or "samarkand"
    city = TRADE_CITIES.get(city_key, TRADE_CITIES["samarkand"])
    goods = city["goods"]

    buttons = []
    # Xarid qilish qatori
    buttons.append([
        InlineKeyboardButton(text=f"🛒 Olish: Ipak ({goods['silk']['buy']}🪙)", callback_data="trade_buy_silk"),
        InlineKeyboardButton(text=f"🛒 Ziravor ({goods['spices']['buy']}🪙)", callback_data="trade_buy_spices"),
    ])
    buttons.append([
        InlineKeyboardButton(text=f"🛒 Olish: Mo'yna ({goods['fur']['buy']}🪙)", callback_data="trade_buy_fur")
    ])

    # Sotish qatori
    buttons.append([
        InlineKeyboardButton(text=f"💰 Sotish: Ipak ({goods['silk']['sell']}🪙)", callback_data="trade_sell_silk"),
        InlineKeyboardButton(text=f"💰 Ziravor ({goods['spices']['sell']}🪙)", callback_data="trade_sell_spices"),
    ])
    buttons.append([
        InlineKeyboardButton(text=f"💰 Sotish: Mo'yna ({goods['fur']['sell']}🪙)", callback_data="trade_sell_fur")
    ])

    # Sayohat va Bosh menyu
    buttons.append([
        InlineKeyboardButton(text="🐫 Boshqa Shaharga Sayohat (-25 Stamina)", callback_data="trade_travel_menu")
    ])
    buttons.append([
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text.startswith("/trade") | F.text.startswith("/tijorat") | F.text.startswith("/karvon"))
async def cmd_trade(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return

    text, markup = await render_trade_ui(char)
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "menu_trade")
async def cb_trade_hub(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    text, markup = await render_trade_ui(char)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

async def render_trade_ui(char: dict):
    city_key = char.get("current_city") or "samarkand"
    city = TRADE_CITIES.get(city_key, TRADE_CITIES["samarkand"])
    trade_inv = await get_trade_inventory(char["id"])

    goods = city["goods"]
    text = (
        f"🐫 *SHAHARLARARO KARVON TIJORATI (ARBITRAJLIK)* ⚖️\n\n"
        f"📍 *Hozirgi Shahar:* {city['name']}\n"
        f"💰 *Mablag':* {char['gold']:,} 🪙 Oltin | ⚡️ *Stamina:* {char['stamina']}/100\n\n"
        f"📦 *Mahalliy Bozor Narxlari:*\n"
        f"• 🧶 Ipak Mato: Olish {goods['silk']['buy']}🪙 | Sotish {goods['silk']['sell']}🪙 (Sizda: {trade_inv.get('silk', 0)} dona)\n"
        f"• 🌶 Ziravorlar: Olish {goods['spices']['buy']}🪙 | Sotish {goods['spices']['sell']}🪙 (Sizda: {trade_inv.get('spices', 0)} dona)\n"
        f"• 🦊 Qimmat Mo'yna: Olish {goods['fur']['buy']}🪙 | Sotish {goods['fur']['sell']}🪙 (Sizda: {trade_inv.get('fur', 0)} dona)\n\n"
        "💡 *Savdogar Sirlari:* Mahsulotni arzon shahardan sotib olib, qimmat shaharga karvonda olib borib soting va katta boylik orttiring!\n"
    )
    markup = get_trade_market_keyboard(char, trade_inv)
    return text, markup

@router.callback_query(F.data.startswith("trade_buy_"))
async def cb_trade_buy(callback: CallbackQuery):
    good_key = callback.data.replace("trade_buy_", "")
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    ok, msg = await buy_trade_good(char["id"], good_key, 1)
    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Tovar xarid qilindi!", show_alert=False)
    # Yangilangan holat
    char = await get_character_by_user_id(callback.from_user.id)
    text, markup = await render_trade_ui(char)
    await callback.message.edit_text(f"{msg}\n\n{text}", parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data.startswith("trade_sell_"))
async def cb_trade_sell(callback: CallbackQuery):
    good_key = callback.data.replace("trade_sell_", "")
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    ok, msg = await sell_trade_good(char["id"], good_key, 1)
    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Tovar sotildi!", show_alert=False)
    # Yangilangan holat
    char = await get_character_by_user_id(callback.from_user.id)
    text, markup = await render_trade_ui(char)
    await callback.message.edit_text(f"{msg}\n\n{text}", parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "trade_travel_menu")
async def cb_travel_menu(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    current_city = char.get("current_city") or "samarkand"

    buttons = []
    for c_key, c_val in TRADE_CITIES.items():
        if c_key != current_city:
            buttons.append([InlineKeyboardButton(text=f"🐫 {c_val['name']} (-25 Stamina)", callback_data=f"trade_go_{c_key}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Bozorda Qolish", callback_data="menu_trade")])

    text = (
        "🐫 *KARVONDA SHAHARLARARO SAYOHAT* 🗺\n\n"
        "Qaysi shaharga yo'l olmoqchisiz?\n"
        "⚠️ *Ogohlantirish:* Sayohat 25 Stamina talab qiladi va yo'lda sahro qaroqchilari pistirmasiga duch kelish xavfi (20%) bor!"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("trade_go_"))
async def cb_travel_go(callback: CallbackQuery):
    target_city = callback.data.replace("trade_go_", "")
    char = await get_character_by_user_id(callback.from_user.id)

    ok, msg = await travel_to_city(char["id"], target_city)
    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Manzilga yetdingiz!", show_alert=False)
    char = await get_character_by_user_id(callback.from_user.id)
    text, markup = await render_trade_ui(char)
    await callback.message.edit_text(f"{msg}\n\n{text}", parse_mode="Markdown", reply_markup=markup)
