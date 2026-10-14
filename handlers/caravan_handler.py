import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character, register_group

caravan_router = Router()

# Active caravans in groups: chat_id -> data
ACTIVE_CARAVANS = {}

@caravan_router.message(F.text.regexp(r"^(!|\/)(karvon|caravan)"))
async def command_start_caravan(message: Message):
    if message.chat.type == "private":
        await message.reply("🐫 Shohona Karvon hodisasi faqat guruhlarda o'tkaziladi! Botni guruhingizga qo'shing.")
        return

    chat_id = message.chat.id
    await register_group(chat_id, message.chat.title or "Guruh")

    if chat_id in ACTIVE_CARAVANS:
        await message.reply("🐫 Ushbu guruhda allaqachon Shohona Karvon harakatlanmoqda!")
        return

    caravan_gold = random.randint(5000, 10000)
    ACTIVE_CARAVANS[chat_id] = {
        "gold": caravan_gold,
        "escorts": {}, # user_id -> char
        "raiders": {}, # user_id -> char
        "started": False
    }

    text = (
        f"🐫 *SHOHONA OLTIN KARVONI YO'LGA CHIQDI!* 🐫\n\n"
        f"Samarqanddan Oltin Sher poytaxtiga **{caravan_gold:,} 🪙 Oltin** ortilgan shohona savdo karvoni yaqinlashmoqda!\n\n"
        f"🛡 *Qo'riqchilar:* Karvonni manzilga yetkazib, xazinani bo'lib oladi.\n"
        f"🪓 *Qaroqchilar:* Karvonga bosqin qilib, barcha boylikni talon-toroj qiladi!\n\n"
        f"⏱ *To'qnashuvga 45 soniya qoldi!* O'z tarafingizni tanlang:"
    )

    buttons = [
        [
            InlineKeyboardButton(text="🛡 Qo'riqlash (Escort)", callback_data="caravan_join_escort"),
            InlineKeyboardButton(text="🪓 Bosqin Qilish (Raid)", callback_data="caravan_join_raid")
        ]
    ]

    sent_msg = await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    
    # 35 soniya kutish
    await asyncio.sleep(35)
    await resolve_caravan(chat_id, sent_msg)

@caravan_router.callback_query(F.data.in_(["caravan_join_escort", "caravan_join_raid"]))
async def process_caravan_join(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    caravan = ACTIVE_CARAVANS.get(chat_id)
    if not caravan:
        await callback.answer("Karvon allaqachon o'tib ketgan!", show_alert=True)
        return

    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval botga /start bosing!", show_alert=True)
        return

    choice = "escorts" if callback.data == "caravan_join_escort" else "raiders"
    other = "raiders" if choice == "escorts" else "escorts"

    # Agar boshqa tarafda bo'lsa, o'chiramiz
    caravan[other].pop(user_id, None)
    caravan[choice][user_id] = char

    side_name = "🛡 Qo'riqchilar" if choice == "escorts" else "🪓 Qaroqchilar"
    await callback.answer(f"Siz {side_name} safiga qo'shildingiz!", show_alert=False)

async def resolve_caravan(chat_id: int, message: Message):
    caravan = ACTIVE_CARAVANS.pop(chat_id, None)
    if not caravan:
        return

    escorts = list(caravan["escorts"].values())
    raiders = list(caravan["raiders"].values())
    gold = caravan["gold"]

    if not escorts and not raiders:
        await message.edit_text(
            f"🐫 *Shohona Karvon bexatar o'tib ketdi!* Hech kim unga tegishga botina olmadi.",
            parse_mode="Markdown"
        )
        return

    escort_power = sum(c["strength"] + c["level"] * 5 for c in escorts) + random.randint(10, 40)
    raid_power = sum(c["strength"] + c["level"] * 5 for c in raiders) + random.randint(10, 40)

    if escort_power >= raid_power:
        winner_side = "🛡 QO'RIQCHILAR"
        winners = escorts
        losers = raiders
        outcome_desc = "Soqchilar qaroqchilarning qonli hujumini qaytarib, karvonni shahar darvozasiga yetkazdi!"
    else:
        winner_side = "🪓 QAROQCHILAR"
        winners = raiders
        losers = escorts
        outcome_desc = "Qaroqchilar karvon qo'riqchilarini yanchib tashlab, xazinani talon-toroj qildi!"

    if winners:
        share = max(100, gold // len(winners))
        for w in winners:
            await update_character(w["id"], gold=w["gold"] + share, wins=w["wins"] + 1)
        winners_names = ", ".join([f"*{w['name']}*" for w in winners])
        prize_txt = f"\n💰 *G'oliblarga taqsimlangan o'lja:* Har biriga **+{share:,} 🪙 Oltin**!\n👥 *G'oliblar:* {winners_names}"
    else:
        prize_txt = ""

    result_text = (
        f"⚔️ *SHOHONA KARVON UCHUN JANG YAKUNLANDI!* ⚔️\n\n"
        f"🏆 *G'alaba:* **{winner_side}**!\n"
        f"📜 {outcome_desc}\n"
        f"{prize_txt}\n\n"
        f"📊 *Kuchlar nisbati:* Qo'riqchilar: {escort_power} vs Qaroqchilar: {raid_power}"
    )

    try:
        await message.edit_text(result_text, parse_mode="Markdown")
    except Exception:
        await message.answer(result_text, parse_mode="Markdown")
