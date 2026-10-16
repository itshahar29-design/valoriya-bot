import json
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_active_market_listings, get_player_market_listings,
    create_market_listing, cancel_market_listing, buy_market_listing,
    get_player_professions, get_runes_inventory, get_trade_inventory,
    get_character_equipment, RUNES_DATA, TRADE_CITIES
)
from keyboards.inline_menus import main_menu_keyboard

router = Router()

def get_market_hub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗡 Qurol & Sovutlar", callback_data="market_cat_equipment"),
            InlineKeyboardButton(text="⛏ Rudalar & O'tlar", callback_data="market_cat_ore")
        ],
        [
            InlineKeyboardButton(text="🧪 Sehrli Damlamalar", callback_data="market_cat_potion"),
            InlineKeyboardButton(text="🔮 Elementar Runalar", callback_data="market_cat_rune")
        ],
        [
            InlineKeyboardButton(text="🐫 Karvon Tovarlari", callback_data="market_cat_trade_good"),
            InlineKeyboardButton(text="📦 Mening E'lonlarim", callback_data="market_my_listings")
        ],
        [
            InlineKeyboardButton(text="➕ Bozorga Mahsulot Qo'yish", callback_data="market_sell_menu")
        ],
        [
            InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
        ]
    ])

@router.message(F.text.startswith("/market") | F.text.startswith("/bozor"))
async def cmd_market(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!")
        return
    text = (
        "🛒 *VALORIYA OCHIQ P2P SAVDO BOZORI* ⚖️\n\n"
        "Qirollikning markaziy savdo maydoniga xush kelibsiz! Bu yerda o'yinchilar o'zaro to'g'ridan-to'g'ri "
        "har qanday buyumni sotishlari yoki sotib olishlari mumkin.\n\n"
        f"💰 *Sizning hamyoningiz:* {char['gold']:,} 🪙 Oltin | {char.get('gems', 0)} 💎 Javohir\n"
        "🏛 *Qirollik Solig'i:* Har bir xariddan 3% bozor to'lovi ushlab qolinadi.\n\n"
        "Qaysi bo'limdagi tovarlarni ko'rmoqchisiz?"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_market_hub_keyboard())

@router.callback_query(F.data == "menu_market")
async def cb_market_hub(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return
    text = (
        "🛒 *VALORIYA OCHIQ P2P SAVDO BOZORI* ⚖️\n\n"
        "Qirollikning markaziy savdo maydoniga xush kelibsiz! Bu yerda o'yinchilar o'zaro to'g'ridan-to'g'ri "
        "har qanday buyumni sotishlari yoki sotib olishlari mumkin.\n\n"
        f"💰 *Sizning hamyoningiz:* {char['gold']:,} 🪙 Oltin | {char.get('gems', 0)} 💎 Javohir\n"
        "🏛 *Qirollik Solig'i:* Har bir xariddan 3% bozor to'lovi ushlab qolinadi.\n\n"
        "Qaysi bo'limdagi tovarlarni ko'rmoqchisiz?"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_market_hub_keyboard())
    await callback.answer()

# =====================================================================
# KATEGORIYALAR BO'YICHA MAHSULOTLARNI KO'RISH
# =====================================================================

CAT_NAMES = {
    "equipment": "🗡 Qurol & Sovutlar",
    "ore": "⛏ Rudalar & O'tlar",
    "potion": "🧪 Sehrli Damlamalar",
    "rune": "🔮 Elementar Runalar",
    "trade_good": "🐫 Karvon Tovarlari"
}

@router.callback_query(F.data.startswith("market_cat_"))
async def cb_market_cat(callback: CallbackQuery):
    cat = callback.data.replace("market_cat_", "")
    cat_title = CAT_NAMES.get(cat, "Bozor")
    listings = await get_active_market_listings(cat)

    if not listings:
        buttons = [
            [InlineKeyboardButton(text="➕ Ushbu bo'limga tovar qo'yish", callback_data="market_sell_menu")],
            [InlineKeyboardButton(text="⬅️ Bozorga qaytish", callback_data="menu_market")]
        ]
        text = f"🛒 *{cat_title.upper()} BO'LIMI*\n\nHozircha ushbu bo'limda faol e'lonlar yo'q. Birinchi bo'lib o'z tovaringizni soting!"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.answer()
        return

    text = f"🛒 *{cat_title.upper()} SAVDO RASTASI*\n\nSotib olish uchun mahsulot tugmasini bosing:\n\n"
    buttons = []
    for l in listings[:10]:
        total_p = l["price_per_unit"] * l["quantity"]
        seller_label = l["seller_name"][:12]
        btn_text = f"🛍 {l['item_name']} ({l['quantity']}x) - {total_p:,}🪙 [{seller_label}]"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"market_buy_{l['id']}")])

    buttons.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"market_cat_{cat}"),
        InlineKeyboardButton(text="⬅️ Bozorga qaytish", callback_data="menu_market")
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# =====================================================================
# SOTIB OLISH (1-CLICK BUY) VA SOTUVCHIGA TELEGRAM XABARNOMA
# =====================================================================

@router.callback_query(F.data.startswith("market_buy_"))
async def cb_market_buy(callback: CallbackQuery, bot: Bot):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    listing_id = int(callback.data.replace("market_buy_", ""))
    ok, msg, seller_user_id, net_gold, item_name = await buy_market_listing(char["id"], listing_id)

    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("Xarid muvaffaqiyatli!", show_alert=False)

    # Sotuvchiga jonli Telegram xabarnoma jo'natish
    if seller_user_id and seller_user_id != callback.from_user.id:
        try:
            seller_text = (
                f"🔔 *BOZORDA MAHSULOTINGIZ SOTILDI!* 💰\n\n"
                f"Siz sotuvga qo'ygan *{item_name}* o'yinchi *{char['name']}* tomonidan sotib olindi!\n"
                f"Sof daromad: +{net_gold:,} 🪙 Oltin hisobingizga o'tkazildi (3% qirollik solig'i ushlandi)."
            )
            await bot.send_message(seller_user_id, seller_text, parse_mode="Markdown")
        except Exception:
            pass

    # Xaridorga yangilangan menyuni ko'rsatish
    buttons = [
        [InlineKeyboardButton(text="🛒 Bozorga Qaytish", callback_data="menu_market")],
        [InlineKeyboardButton(text="🎒 Inventarni Ko'rish", callback_data="menu_inventory")]
    ]
    await callback.message.edit_text(f"{msg}\n\n🏛 *Qirollik 3% Bozor Solig'i davlat xazinasiga kiritildi.*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# MENING E'LONLARIM VA BEKOR QILISH (MY LISTINGS)
# =====================================================================

@router.callback_query(F.data == "market_my_listings")
async def cb_my_listings(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    listings = await get_player_market_listings(char["id"])
    if not listings:
        buttons = [
            [InlineKeyboardButton(text="➕ Yangi E'lon Qo'yish", callback_data="market_sell_menu")],
            [InlineKeyboardButton(text="⬅️ Bozorga qaytish", callback_data="menu_market")]
        ]
        text = "📦 *SIZNING E'LONLARINGIZ*\n\nSiz hozircha bozorga hech qanday tovar qo'ymagansiz."
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.answer()
        return

    text = "📦 *SIZNING FAOL E'LONLARINGIZ*\n\nMahsulotni qaytarib inventarga olish uchun '❌ Bekor qilish' tugmasini bosing:\n\n"
    buttons = []
    for l in listings:
        total_p = l["price_per_unit"] * l["quantity"]
        btn_txt = f"❌ Bekor qilish: {l['item_name']} ({l['quantity']}x) - {total_p:,}🪙"
        buttons.append([InlineKeyboardButton(text=btn_txt, callback_data=f"market_cancel_{l['id']}")])

    buttons.append([
        InlineKeyboardButton(text="➕ Yana tovar qo'yish", callback_data="market_sell_menu"),
        InlineKeyboardButton(text="⬅️ Bozorga qaytish", callback_data="menu_market")
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("market_cancel_"))
async def cb_market_cancel(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    listing_id = int(callback.data.replace("market_cancel_", ""))
    ok, msg = await cancel_market_listing(char["id"], listing_id)
    await callback.answer(msg, show_alert=True)
    # Qayta mening e'lonlarim sahifasini ko'rsatish
    await cb_my_listings(callback)

# =====================================================================
# MAHSULOT SOTISH MENYUSI (SELL MENU)
# =====================================================================

@router.callback_query(F.data == "market_sell_menu")
async def cb_sell_menu(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    if not char:
        await callback.answer("Qahramon topilmadi!", show_alert=True)
        return

    buttons = [
        [
            InlineKeyboardButton(text="⛏ Rudalarni Sotish", callback_data="market_sell_cat_ore"),
            InlineKeyboardButton(text="🧪 Damlamalarni Sotish", callback_data="market_sell_cat_potion")
        ],
        [
            InlineKeyboardButton(text="🔮 Runalarni Sotish", callback_data="market_sell_cat_rune"),
            InlineKeyboardButton(text="🐫 Karvon Tovarini Sotish", callback_data="market_sell_cat_good")
        ],
        [
            InlineKeyboardButton(text="🗡 Qurol / Zirhni Sotish", callback_data="market_sell_cat_equip")
        ],
        [
            InlineKeyboardButton(text="⬅️ Bozorga Qaytish", callback_data="menu_market")
        ]
    ]
    text = (
        "➕ *BOZORGA TOVAR SOTUVGA CHIQARISH* ⚖️\n\n"
        "Qaysi turdagi zaxirangizni bozorga qo'ymoqchisiz?\n"
        "Bozorga qo'yilgan tovar boshqa ritsarlar tomonidan darhol sotib olinishi mumkin!"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 1. Rudalar sotish
@router.callback_query(F.data == "market_sell_cat_ore")
async def cb_sell_ore(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    profs = await get_player_professions(char["id"])

    iron = profs.get("iron_ore", 0)
    gold = profs.get("gold_ore", 0)
    mithril = profs.get("mithril_ore", 0)
    herbs = profs.get("herbs", 0)

    buttons = []
    if iron >= 2:
        buttons.append([InlineKeyboardButton(text=f"🔩 2x Temir Rudasi (150🪙)", callback_data="market_post_ore_iron_2_150")])
    if gold >= 1:
        buttons.append([InlineKeyboardButton(text=f"🪙 1x Oltin Rudasi (300🪙)", callback_data="market_post_ore_gold_1_300")])
    if mithril >= 1:
        buttons.append([InlineKeyboardButton(text=f"✨ 1x Sehrli Mithril (700🪙)", callback_data="market_post_ore_mithril_1_700")])
    if herbs >= 2:
        buttons.append([InlineKeyboardButton(text=f"🌿 2x Shifobaxsh O't (120🪙)", callback_data="market_post_ore_herbs_2_120")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="market_sell_menu")])

    text = (
        f"⛏ *RUDALAR VA O'TLAR ZAXIRANGIZ:*\n\n"
        f"• 🔩 Temir: {iron} dona\n"
        f"• 🪙 Oltin ruda: {gold} dona\n"
        f"• ✨ Mithril: {mithril} dona\n"
        f"• 🌿 O'tlar: {herbs} dona\n\n"
        "Tezkor sotuvga chiqarish uchun quyidagi to'plamlardan birini bosing:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 2. Damlamalar sotish
@router.callback_query(F.data == "market_sell_cat_potion")
async def cb_sell_potion(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    profs = await get_player_professions(char["id"])
    pots = profs.get("potions", {})

    rage = pots.get("rage", 0)
    heal = pots.get("healing", 0)
    void_p = pots.get("void_poison", 0)

    buttons = []
    if rage >= 1:
        buttons.append([InlineKeyboardButton(text=f"🧪 1x G'azab Damlamasi (350🪙)", callback_data="market_post_pot_rage_1_350")])
    if heal >= 1:
        buttons.append([InlineKeyboardButton(text=f"🧪 1x Hayot Eliksiri (500🪙)", callback_data="market_post_pot_healing_1_500")])
    if void_p >= 1:
        buttons.append([InlineKeyboardButton(text=f"🧪 1x Zulmat Zahri (750🪙)", callback_data="market_post_pot_void_1_750")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="market_sell_menu")])

    text = (
        f"🧪 *ALXIMIYA DAMLAMALARI ZAXIRANGIZ:*\n\n"
        f"• 🧪 G'azab Damlamasi: {rage} dona\n"
        f"• 🧪 Hayot Eliksiri: {heal} dona\n"
        f"• 🧪 Zulmat Zahri: {void_p} dona\n\n"
        "Bozorga chiqarish uchun damlamani tanlang:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 3. Runalar sotish
@router.callback_query(F.data == "market_sell_cat_rune")
async def cb_sell_rune(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    runes = await get_runes_inventory(char["id"])

    fire = runes.get("fire_rune", 0)
    frost = runes.get("frost_rune", 0)
    lightning = runes.get("lightning_rune", 0)

    buttons = []
    if fire >= 1:
        buttons.append([InlineKeyboardButton(text=f"🔥 1x Olov Runasi (450🪙)", callback_data="market_post_rune_fire_1_450")])
    if frost >= 1:
        buttons.append([InlineKeyboardButton(text=f"❄️ 1x Muz Runasi (500🪙)", callback_data="market_post_rune_frost_1_500")])
    if lightning >= 1:
        buttons.append([InlineKeyboardButton(text=f"⚡️ 1x Momaqaldiroq Runasi (550🪙)", callback_data="market_post_rune_lightning_1_550")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="market_sell_menu")])

    text = (
        f"🔮 *ELEMENTAR RUNALAR ZAXIRANGIZ:*\n\n"
        f"• 🔥 Olov Runasi: {fire} dona\n"
        f"• ❄️ Muz Runasi: {frost} dona\n"
        f"• ⚡️ Momaqaldiroq Runasi: {lightning} dona\n\n"
        "Bozorga chiqarish uchun runani tanlang:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 4. Karvon tovarlari sotish
@router.callback_query(F.data == "market_sell_cat_good")
async def cb_sell_good(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    trade_inv = await get_trade_inventory(char["id"])

    silk = trade_inv.get("silk", 0)
    spices = trade_inv.get("spices", 0)
    fur = trade_inv.get("fur", 0)

    buttons = []
    if silk >= 1:
        buttons.append([InlineKeyboardButton(text=f"🧶 1x Ipak Mato (250🪙)", callback_data="market_post_good_silk_1_250")])
    if spices >= 1:
        buttons.append([InlineKeyboardButton(text=f"🌶 1x Sharq Ziravorlari (180🪙)", callback_data="market_post_good_spices_1_180")])
    if fur >= 1:
        buttons.append([InlineKeyboardButton(text=f"🦊 1x Mo'yna (280🪙)", callback_data="market_post_good_fur_1_280")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="market_sell_menu")])

    text = (
        f"🐫 *KARVON TOVARLARI ZAXIRANGIZ:*\n\n"
        f"• 🧶 Ipak: {silk} dona\n"
        f"• 🌶 Sharq Ziravorlari: {spices} dona\n"
        f"• 🦊 Qimmatbaho Mo'yna: {fur} dona\n\n"
        "Bozorga chiqarish uchun tovar tanlang:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 5. Qurol va sovutlarni sotish
@router.callback_query(F.data == "market_sell_cat_equip")
async def cb_sell_equip(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    gear = await get_character_equipment(char["id"])
    unequipped = [g for g in gear if g.get("is_equipped", 0) == 0]

    buttons = []
    for item in unequipped[:6]:
        price = 200 + item.get("attack", 0) * 15 + item.get("defense", 0) * 15
        buttons.append([InlineKeyboardButton(text=f"🗡 {item['item_name']} ({price:,}🪙)", callback_data=f"market_post_eq_{item['id']}_{price}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="market_sell_menu")])

    if not unequipped:
        text = "🗡 *EGNIDAGI EMAS ANJOMLAR:* Sizda hozir bo'sh (kiyilmagan) anjom yo'q!"
    else:
        text = "🗡 *EGNIDAGI EMAS ANJOMLAR:*\n\nBozorga chiqarish uchun anjomni bosing:"
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# =====================================================================
# SOTUVGA CHIQARISH AMALLARI (POSTING ACTIONS)
# =====================================================================

@router.callback_query(F.data.startswith("market_post_ore_"))
async def cb_post_ore(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    # market_post_ore_iron_2_150
    parts = callback.data.split("_")
    ore_type = parts[3]
    qty = int(parts[4])
    price = int(parts[5])

    profs = await get_player_professions(char["id"])
    key = "iron_ore" if ore_type == "iron" else ("gold_ore" if ore_type == "gold" else ("mithril_ore" if ore_type == "mithril" else "herbs"))
    name = "Temir Rudasi" if ore_type == "iron" else ("Oltin Rudasi" if ore_type == "gold" else ("Sehrli Mithril" if ore_type == "mithril" else "Shifobaxsh O't"))

    if profs.get(key, 0) < qty:
        await callback.answer("Zaxirangizda ushbu ruda yetarli emas!", show_alert=True)
        return

    profs[key] -= qty
    from database.db import get_connection
    async with get_connection() as db:
        await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), char["id"]))
        await db.commit()

    ok, msg = await create_market_listing(
        seller_character_id=char["id"],
        category="ore",
        item_name=name,
        quantity=qty,
        price_per_unit=price // qty,
        item_data={"key": key}
    )
    await callback.answer("Bozorga qo'yildi!", show_alert=False)
    await callback.message.edit_text(f"{msg}\n\nO'yinchilar sizning taklifingizni qabul qilishlari mumkin!", parse_mode="Markdown", reply_markup=get_market_hub_keyboard())

@router.callback_query(F.data.startswith("market_post_pot_"))
async def cb_post_pot(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    # market_post_pot_rage_1_350
    parts = callback.data.split("_")
    pot_type = parts[3]
    qty = int(parts[4])
    price = int(parts[5])

    key = "rage" if pot_type == "rage" else ("healing" if pot_type == "healing" else "void_poison")
    name = "G'azab Damlamasi" if pot_type == "rage" else ("Hayot Eliksiri" if pot_type == "healing" else "Zulmat Zahri")

    profs = await get_player_professions(char["id"])
    pots = profs.get("potions", {})
    if pots.get(key, 0) < qty:
        await callback.answer("Sizda bu damlama yo'q!", show_alert=True)
        return

    pots[key] -= qty
    profs["potions"] = pots
    from database.db import get_connection
    async with get_connection() as db:
        await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), char["id"]))
        await db.commit()

    ok, msg = await create_market_listing(
        seller_character_id=char["id"],
        category="potion",
        item_name=name,
        quantity=qty,
        price_per_unit=price // qty,
        item_data={"key": key}
    )
    await callback.answer("Bozorga qo'yildi!", show_alert=False)
    await callback.message.edit_text(f"{msg}", parse_mode="Markdown", reply_markup=get_market_hub_keyboard())

@router.callback_query(F.data.startswith("market_post_rune_"))
async def cb_post_rune(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    # market_post_rune_fire_1_450
    parts = callback.data.split("_")
    r_type = f"{parts[3]}_rune"
    qty = int(parts[4])
    price = int(parts[5])

    runes = await get_runes_inventory(char["id"])
    if runes.get(r_type, 0) < qty:
        await callback.answer("Sizda bu runa yo'q!", show_alert=True)
        return

    runes[r_type] -= qty
    from database.db import get_connection
    async with get_connection() as db:
        await db.execute("UPDATE characters SET runes_inventory_json = ? WHERE id = ?", (json.dumps(runes), char["id"]))
        await db.commit()

    ok, msg = await create_market_listing(
        seller_character_id=char["id"],
        category="rune",
        item_name=RUNES_DATA[r_type]["name"],
        quantity=qty,
        price_per_unit=price // qty,
        item_data={"key": r_type}
    )
    await callback.answer("Runa bozorga qo'yildi!", show_alert=False)
    await callback.message.edit_text(f"{msg}", parse_mode="Markdown", reply_markup=get_market_hub_keyboard())

@router.callback_query(F.data.startswith("market_post_good_"))
async def cb_post_good(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    # market_post_good_silk_1_250
    parts = callback.data.split("_")
    g_key = parts[3]
    qty = int(parts[4])
    price = int(parts[5])

    trade_inv = await get_trade_inventory(char["id"])
    if trade_inv.get(g_key, 0) < qty:
        await callback.answer("Sizda bu tovar yetarli emas!", show_alert=True)
        return

    trade_inv[g_key] -= qty
    name = "Ipak Mato" if g_key == "silk" else ("Sharq Ziravorlari" if g_key == "spices" else "Qimmatbaho Mo'yna")

    from database.db import get_connection
    async with get_connection() as db:
        await db.execute("UPDATE characters SET trade_inventory_json = ? WHERE id = ?", (json.dumps(trade_inv), char["id"]))
        await db.commit()

    ok, msg = await create_market_listing(
        seller_character_id=char["id"],
        category="trade_good",
        item_name=name,
        quantity=qty,
        price_per_unit=price // qty,
        item_data={"key": g_key}
    )
    await callback.answer("Tovar bozorga qo'yildi!", show_alert=False)
    await callback.message.edit_text(f"{msg}", parse_mode="Markdown", reply_markup=get_market_hub_keyboard())

@router.callback_query(F.data.startswith("market_post_eq_"))
async def cb_post_eq(callback: CallbackQuery):
    char = await get_character_by_user_id(callback.from_user.id)
    # market_post_eq_{item_id}_{price}
    parts = callback.data.split("_")
    item_id = int(parts[3])
    price = int(parts[4])

    from database.db import get_connection
    import aiosqlite
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM equipment WHERE id = ? AND character_id = ? AND is_equipped = 0", (item_id, char["id"])) as cur:
            row = await cur.fetchone()
            if not row:
                await callback.answer("Anjom topilmadi yoki egnida!", show_alert=True)
                return
            eq_item = dict(row)

        await db.execute("DELETE FROM equipment WHERE id = ?", (item_id,))
        await db.commit()

    ok, msg = await create_market_listing(
        seller_character_id=char["id"],
        category="equipment",
        item_name=eq_item["item_name"],
        quantity=1,
        price_per_unit=price,
        item_data=eq_item
    )
    await callback.answer("Anjom bozorga qo'yildi!", show_alert=False)
    await callback.message.edit_text(f"{msg}", parse_mode="Markdown", reply_markup=get_market_hub_keyboard())
