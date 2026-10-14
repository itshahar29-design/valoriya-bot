from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, create_guild, join_guild,
    deposit_guild_treasury, get_guild_info, get_all_castles, siege_castle
)

guild_router = Router()

@guild_router.callback_query(F.data == "menu_guild")
async def show_guild_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    guild_id = char.get("guild_id")
    if not guild_id:
        text = (
            "🏰 *VALORIYA RITSARLAR GILDIYALARI (KLANLAR)* 🏰\n\n"
            "Yolg'iz ritsarni bo'rilar yeydi! Valoriya dunyosida o'z gildiyangizni tuzing "
            "yoki qudratli birodarlik safiga qo'shiling!\n\n"
            "👑 *Gildiya afzalliklari:*\n"
            "• Qal'a qamallari (Castle Sieges) va passiv soliq daromadi!\n"
            "• Umumiy klan xazinasi va yordam!\n"
            "• Guruhlardagi ulkan obro'!\n\n"
            "Gildiya tuzish narxi: **1,000 🪙 Oltin**."
        )
        buttons = [
            [InlineKeyboardButton(text="➕ Yangi Gildiya Tuzish (1,000 🪙)", callback_data="guild_create_prompt")],
            [InlineKeyboardButton(text="🏰 Valoriya Qal'alari (Ro'yxat)", callback_data="menu_castles")],
            [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
        ]
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        return

    guild = await get_guild_info(guild_id)
    if not guild:
        await callback.answer("Gildiya ma'lumotlari topilmadi!", show_alert=True)
        return

    castle_txt = f"🏰 Egallangan Qal'a: *{guild['castle_owned']}*" if guild.get("castle_owned") else "🏰 Egallangan Qal'a: _Hozircha yo'q_"
    members_list = "\n".join([f"• ⚔️ {m['name']} (Lvl {m['level']}) — {m['wins']} G'alaba" for m in guild.get("members", [])[:5]])

    text = (
        f"🏰 *'{guild['name'].upper()}' GILDIYASI BOSHQARUVI* 🏰\n\n"
        f"👑 Daraja: *{guild['level']}* | 👥 A'zolar: *{len(guild.get('members', []))} ta*\n"
        f"💰 Umumiy Xazina: *{guild['treasury']:,} 🪙 Oltin*\n"
        f"{castle_txt}\n\n"
        f"📜 *Safdoshlar:*\n{members_list}\n\n"
        "Qanday buyruq berasiz?"
    )
    buttons = [
        [
            InlineKeyboardButton(text="💰 Xazinaga Oltin Qo'shish (500 🪙)", callback_data="guild_deposit_500"),
            InlineKeyboardButton(text="⚔️ Qal'a Qamaliga Chiqish", callback_data="menu_castles")
        ],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@guild_router.callback_query(F.data == "guild_create_prompt")
async def guild_create_prompt_handler(callback: CallbackQuery):
    await callback.answer()
    text = (
        "➕ *YANGI GILDIYA TUZISH:*\n\n"
        "Gildiya tuzish uchun quyidagi buyruqni yuboring:\n"
        "`/create_guild Nom` yoki `!klan_tuz Nom`\n\n"
        "Misol: `/create_guild Temur_Vorislari`\n"
        "Narxi: 1,000 🪙 Oltin."
    )
    buttons = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_guild")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@guild_router.message(F.text.regexp(r"^(!|\/)(create_guild|klan_tuz|gildiya_tuz)"))
async def text_create_guild(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Gildiya nomini ham yozing!\nMisol: `/create_guild Oltin_Bo'rilar`", parse_mode="Markdown")
        return

    name = parts[1].strip()
    success, msg = await create_guild(char["id"], name)
    await message.reply(msg, parse_mode="Markdown")

@guild_router.message(F.text.regexp(r"^(!|\/)(join_guild|klanga_kir|gildiyaga_kir)"))
async def text_join_guild(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Gildiya nomini ham yozing!\nMisol: `/join_guild Oltin_Bo'rilar`", parse_mode="Markdown")
        return

    name = parts[1].strip()
    success, msg = await join_guild(char["id"], name)
    await message.reply(msg, parse_mode="Markdown")

@guild_router.callback_query(F.data == "guild_deposit_500")
async def process_guild_deposit(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await deposit_guild_treasury(char["id"], 500)
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_guild_menu(callback)

# =====================================================================
# QAL'A QAMALLARI VA SOLIQLAR (CASTLE SIEGES)
# =====================================================================
@guild_router.callback_query(F.data == "menu_castles")
async def show_castles_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    castles = await get_all_castles()
    text = (
        "🏰 *VALORIYA BUYUK QAL'ALARI (QAMAL VA SOLIQLAR)* 🏰\n\n"
        "Ushbu afsonaviy qal'alarni faqat kuchli gildiyalar qamal qilib egallashi mumkin! "
        "Qal'a egasi bo'lgan klan har kuni yirik passiv soliq oladi!\n\n"
    )

    buttons = []
    for c in castles:
        owner = c["owner_guild_name"] or "Egasi yo'q (Qirollik soqchilari)"
        text += f"🏰 *{c['name']}*\n• Egasi: *{owner}*\n• Kundalik Soliq: *{c['daily_tax']:,} 🪙*\n\n"
        buttons.append([InlineKeyboardButton(text=f"⚔️ {c['name']} Qamal Qilish", callback_data=f"siege_castle_{c['id']}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Gildiya Menyusi", callback_data="menu_guild")])
    buttons.append([InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@guild_router.callback_query(F.data.startswith("siege_castle_"))
async def process_siege_castle(callback: CallbackQuery):
    castle_id = callback.data.replace("siege_castle_", "")
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    await callback.answer("⚔️ Qamal manjaniqlari o't ochmoqda...", show_alert=False)
    success, msg = await siege_castle(char["id"], castle_id)
    
    buttons = [
        [InlineKeyboardButton(text="🏰 Qal'alar Ro'yxati", callback_data="menu_castles")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
