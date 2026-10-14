from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character

auction_router = Router()

@auction_router.callback_query(F.data == "menu_auction")
async def show_auction_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    text = (
        "🏛 *VALORIYA GLOBAL OCHIQ AUKSIONI VA BOZORI* 🏛\n\n"
        "Bu yerda barcha 12 imperiya ritsarlari o'z o'ljalarini kimoshdi savdosiga qo'yadilar.\n\n"
        "• *Jonli Lotlar:* 14 ta afsonaviy qurol savdoda\n"
        "• *Xavfsizlik:* Firibgarlikka qarshi Escrow tizimi yoqilgan\n\n"
        f"🪙 Cho'ntagingizdagi Oltin: *{char['gold']}*"
    )
    
    buttons = [
        [InlineKeyboardButton(text="🗡 Lotlar Ro'yxatini Ko'rish", callback_data="auction_view_lots")],
        [InlineKeyboardButton(text="🏦 Garovxona (Pawn Shop - Naqd Oltin)", callback_data="auction_pawn_shop")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@auction_router.callback_query(F.data == "auction_view_lots")
async def view_lots(callback: CallbackQuery):
    sample_lots = (
        "📜 *FAOL AUKSION LOTLARI:*\n\n"
        "1. ⚔️ *Alanga Po'lat Qilichi* (Epik)\n"
        "   • Hozirgi narx: 420 🪙 | Sotib olish: 650 🪙\n"
        "   • Sotuvchi: Lord_Roland (Lvl 5)\n\n"
        "2. 🛡 *Zanjirli Qirollik Sovuti* (Kamyob)\n"
        "   • Hozirgi narx: 280 🪙 | Sotib olish: 400 🪙\n"
        "   • Sotuvchi: Ser_Galahad (Lvl 4)\n\n"
        "3. 🧪 *Buyuk Hayot Eliksiri (x3)*\n"
        "   • Hozirgi narx: 90 🪙 | Sotib olish: 150 🪙"
    )
    buttons = [
        [InlineKeyboardButton(text="💰 Taklif Berish (Bid)", callback_data="auction_bid_mock")],
        [InlineKeyboardButton(text="⬅️ Bozorga Qaytish", callback_data="menu_auction")]
    ]
    await callback.message.edit_text(sample_lots, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@auction_router.callback_query(F.data == "auction_bid_mock")
async def handle_mock_bid(callback: CallbackQuery):
    await callback.answer("✅ Sizning taklifingiz auksionga qabul qilindi!", show_alert=True)

@auction_router.callback_query(F.data == "auction_pawn_shop")
async def handle_pawn_shop(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    await callback.answer("🏦 Garovxona: Sizga zudlik bilan 200 Oltin garov krediti berildi!", show_alert=True)
    await update_character(char["id"], gold=char["gold"] + 200)
    await show_auction_menu(callback)

@auction_router.callback_query(F.data == "menu_pigeon")
async def show_pigeon_menu(callback: CallbackQuery):
    text = (
        "🕊 *QIROLLIK KAPTAR VA POSILKA POCHTASI* 🕊\n\n"
        "Kaptarlar orqali do'stlaringiz yoki vassallaringizga uzoq masofadan xat, "
        "oltin yoki qimmatbaho qurol jo'natishingiz mumkin!\n\n"
        "📥 *Yangi xatlar:* Yo'q (Pochtachilar tinch)\n"
        "📤 *Do'stga yuborish:* O'yinchining Telegram @username yoki ID sini yozib posilka jo'nating."
    )
    buttons = [[InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
