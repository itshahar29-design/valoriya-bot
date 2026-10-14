import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character, register_group

horse_race_router = Router()

ACTIVE_RACES = {}

@horse_race_router.message(F.text.regexp(r"^(!|\/)(poyga|race)"))
async def command_start_race(message: Message):
    if message.chat.type == "private":
        await message.reply("🏇 Tulporlar poygasi faqat guruhlarda o'tkaziladi! Botni guruhingizga qo'shing.")
        return

    chat_id = message.chat.id
    await register_group(chat_id, message.chat.title or "Guruh")

    if chat_id in ACTIVE_RACES:
        await message.reply("🏇 Ushbu guruhda allaqachon poyga ro'yxatga olinmoqda!")
        return

    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval botga /start bosing!")
        return

    bet = 100
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        bet = max(50, min(5000, int(args[1])))

    if char["gold"] < bet:
        await message.reply(f"Sizda poyga garovi uchun yetarli oltin yo'q ({bet} 🪙 kerak)!")
        return

    ACTIVE_RACES[chat_id] = {
        "bet": bet,
        "racers": {user_id: char}, # user_id -> char
        "host_id": user_id
    }

    text = (
        f"🏇 *QIROLLIK TULPORLARI DERBISI (POYGA)* 🏇\n\n"
        f"Ser *{char['name']}* o'zining '{char['horse_name']}' tulpuri bilan poyga e'lon qildi!\n\n"
        f"🪙 *Garov miqdori:* {bet:,} 🪙 Oltin\n"
        f"👥 *Ishtirokchilar (1/4):*\n• 🐎 {char['name']} ({char['horse_name']})\n\n"
        f"Poygaga qo'shilish uchun pastdagi tugmani bosing:"
    )

    buttons = [
        [InlineKeyboardButton(text=f"🏇 Poygaga Kirish ({bet} 🪙)", callback_data="race_join")],
        [InlineKeyboardButton(text="🏁 Poygani Boshlash (Start)", callback_data="race_start")]
    ]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@horse_race_router.callback_query(F.data == "race_join")
async def process_race_join(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    race = ACTIVE_RACES.get(chat_id)
    if not race:
        await callback.answer("Poyga topilmadi yoki tugagan!", show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id in race["racers"]:
        await callback.answer("Siz allaqachon poyga safigasiz!", show_alert=True)
        return

    if len(race["racers"]) >= 4:
        await callback.answer("Poygada maksimal 4 ta ritsar qatnasha oladi!", show_alert=True)
        return

    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval botga /start bosing!", show_alert=True)
        return

    if char["gold"] < race["bet"]:
        await callback.answer(f"Garov uchun oltin yetarli emas ({race['bet']} 🪙 kerak)!", show_alert=True)
        return

    race["racers"][user_id] = char
    await callback.answer(f"Siz '{char['horse_name']}' tulpuringiz bilan poygaga kirdingiz!", show_alert=False)

    racers_list = "\n".join([f"• 🐎 {c['name']} ({c['horse_name']})" for c in race["racers"].values()])
    text = (
        f"🏇 *QIROLLIK TULPORLARI DERBISI (POYGA)* 🏇\n\n"
        f"🪙 *Garov miqdori:* {race['bet']:,} 🪙 Oltin\n"
        f"👥 *Ishtirokchilar ({len(race['racers'])}/4):*\n{racers_list}\n\n"
        f"Boshlash uchun '🏁 Poygani Boshlash' tugmasini bosing:"
    )
    buttons = [
        [InlineKeyboardButton(text=f"🏇 Poygaga Kirish ({race['bet']} 🪙)", callback_data="race_join")],
        [InlineKeyboardButton(text="🏁 Poygani Boshlash (Start)", callback_data="race_start")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@horse_race_router.callback_query(F.data == "race_start")
async def process_race_start(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    race = ACTIVE_RACES.get(chat_id)
    if not race:
        return

    if len(race["racers"]) < 2:
        await callback.answer("Poygani boshlash uchun kamida 2 ta ritsar kerak!", show_alert=True)
        return

    # Delete race from active so others can't interfere
    del ACTIVE_RACES[chat_id]
    racers = list(race["racers"].values())
    bet = race["bet"]
    total_prize = bet * len(racers)

    # Deduct bets
    for r in racers:
        await update_character(r["id"], gold=r["gold"] - bet)

    await callback.message.edit_text("🏁 *POYGA BOSHLANDI! TULPORLAR SHIDDAT BILAN CHOPMOQDA!* 🐎💨", parse_mode="Markdown")
    await asyncio.sleep(2)

    # Animation Frame 1
    frame1 = "🏇 *1-BURILISH:* Tulporlar chang-to'zon ko'tarib quvib o'tmoqda!\n\n"
    for r in racers:
        prog = random.randint(2, 5)
        bar = "=" * prog + ">" + "-" * (8 - prog)
        frame1 += f"🐎 *{r['name']}* [{bar}]\n"
    await callback.message.edit_text(frame1, parse_mode="Markdown")
    await asyncio.sleep(2)

    # Animation Frame 2
    frame2 = "🔥 *OXIRGI TO'G'RI CHIZIQ:* Ritsarlar qamchi bosmoqda!\n\n"
    scores = {}
    for r in racers:
        bond_bonus = r.get("horse_bond", 10) // 10
        score = random.randint(10, 30) + bond_bonus
        scores[r["id"]] = score
        prog = min(8, max(4, score // 4))
        bar = "=" * prog + ">" + "-" * (8 - prog)
        frame2 += f"🐎 *{r['name']}* [{bar}]\n"
    await callback.message.edit_text(frame2, parse_mode="Markdown")
    await asyncio.sleep(2)

    # Winner determination
    winner = max(racers, key=lambda r: scores[r["id"]])
    await update_character(winner["id"], gold=winner["gold"] - bet + total_prize, wins=winner["wins"] + 1)

    result_text = (
        f"🏆 *POYGA MARRASIGA BIRINCHI BO'LIB YETIB KELDI!* 🏆\n\n"
        f"🥇 *G'olib:* Ser *{winner['name']}* o'zining sodiq *'{winner['horse_name']}'* tulpuri bilan marraga birinchi sakrab o'tdi!\n\n"
        f"💰 *Yutib Olingan Jami Mukofot:* **+{total_prize:,} 🪙 Oltin**!\n"
        f"Barcha garov pullari g'olib xazinasiga o'tkazildi."
    )
    await callback.message.edit_text(result_text, parse_mode="Markdown")
