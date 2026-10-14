import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character

tavern_router = Router()

@tavern_router.callback_query(F.data == "menu_tavern")
async def show_tavern_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    text = (
        "🍻 *SHAHAR TAVERNA VA MAYXONASI* 🍻\n\n"
        "Mayxona qizigan! Ritsarlar sharob ichib, suyak tashlab qimor o'ynamoqda. "
        "Keksa askarlar esa burchakda mish-mishlarni muhokama qilishmoqda.\n\n"
        f"🪙 Cho'ntagingizdagi Oltin: *{char['gold']}*\n"
        f"❤️ Joningiz: *{char['hp']}/{char['max_hp']}*"
    )
    
    buttons = [
        [InlineKeyboardButton(text="🎲 Suyak Tashlash Qimor (Tikish: 50 🪙)", callback_data="tavern_dice")],
        [InlineKeyboardButton(text="🍗 Qovurilgan Bug'u Go'shti (Jon Tiklash - 30 🪙)", callback_data="tavern_eat")],
        [InlineKeyboardButton(text="🤫 Mayxona Mish-Mishlari", callback_data="tavern_rumors")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "tavern_dice")
async def play_tavern_dice(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    if char["gold"] < 50:
        await callback.answer("Oltiningiz yetarli emas (kamida 50 oltin kerak)!", show_alert=True)
        return
        
    player_roll = random.randint(1, 6) + random.randint(1, 6)
    opponent_roll = random.randint(1, 6) + random.randint(1, 6)
    
    if player_roll > opponent_roll:
        await update_character(char["id"], gold=char["gold"] + 50)
        msg = f"🎉 *SIZ YUTDINGIZ!* ({player_roll} vs {opponent_roll})\n\nSiz raqibingizdan 50 Oltin yutib oldingiz!"
    elif player_roll < opponent_roll:
        await update_character(char["id"], gold=char["gold"] - 50)
        msg = f"💀 *RAQIB YUTDI!* ({player_roll} vs {opponent_roll})\n\n50 Oltin boy berildi."
    else:
        msg = f"🤝 *DURRANG!* ({player_roll} vs {opponent_roll})\n\nOltinlar o'z joyida qoldi."
        
    buttons = [
        [InlineKeyboardButton(text="🎲 Yana Suyak Tashlash", callback_data="tavern_dice")],
        [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "tavern_eat")
async def eat_tavern_meal(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    if char["gold"] < 30:
        await callback.answer("Oltiningiz yetarli emas (30 oltin kerak)!", show_alert=True)
        return
        
    await update_character(char["id"], gold=char["gold"] - 30, hp=char["max_hp"], stamina=100)
    await callback.answer("🍗 Qorin to'ydi! Joningiz va Staminangiz 100% tiklandi!", show_alert=True)
    await show_tavern_menu(callback)

@tavern_router.callback_query(F.data == "tavern_rumors")
async def show_rumors(callback: CallbackQuery):
    rumors = [
        "Keksa ritsar pichirladi: 'Eshitishimcha, Qonxo'r Ragnar yaqinda Oltin Sher chegarasiga 200 askar bilan bostirib bormoqchi...'",
        "Mast savdogar aytdi: 'Sharqdan kelayotgan ipak karvoni yo'lda tuman ichida qolib ketibdi, qo'riqchilari kam ekan...'",
        "Sayyoh aytdi: 'Oltin Tarozi bankirlari yaqinda qarzini to'lamagan bitta lordning saroyini yashirincha yoqib yuborishibdi!'"
    ]
    await callback.answer(random.choice(rumors), show_alert=True)
