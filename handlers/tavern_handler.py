import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character, get_character_by_identifier

tavern_router = Router()

SLOT_SYMBOLS = ["⚔️", "🪙", "💎", "👑", "💀", "🛡"]

@tavern_router.callback_query(F.data == "menu_tavern")
async def show_tavern_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    text = (
        "🍻 *SHAHAR TAVERNA VA QIMORXONASI* 🍻\n\n"
        "Mayxona qizigan! Ritsarlar sharob ichib, suyak tashlab qimor o'ynamoqda. "
        "Burchakda esa xufyona o'g'rilar va sirli qimorbozlar o'tiribdi.\n\n"
        f"🪙 Cho'ntagingizdagi Oltin: *{char['gold']:,} 🪙*\n"
        f"❤️ Joningiz: *{char['hp']}/{char['max_hp']}*"
    )
    
    buttons = [
        [
            InlineKeyboardButton(text="🎲 Suyak Tashlash (50 🪙)", callback_data="tavern_dice"),
            InlineKeyboardButton(text="🎰 Oltin Baraban (100 🪙)", callback_data="tavern_slots")
        ],
        [
            InlineKeyboardButton(text="🍗 Shohona Ziyofat (Jon 100% - 30 🪙)", callback_data="tavern_eat"),
            InlineKeyboardButton(text="🤫 Mayxona Mish-Mishlari", callback_data="tavern_rumors")
        ],
        [
            InlineKeyboardButton(text="🎯 Xufyona Cho'ntakkesarlik (O'g'rilik)", callback_data="tavern_steal_info")
        ],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "tavern_slots")
async def play_tavern_slots(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    if char["gold"] < 100:
        await callback.answer("Kamida 100 oltin kerak!", show_alert=True)
        return

    s1 = random.choice(SLOT_SYMBOLS)
    s2 = random.choice(SLOT_SYMBOLS)
    s3 = random.choice(SLOT_SYMBOLS)

    if s1 == s2 == s3:
        if s1 == "👑":
            multiplier = 15
        elif s1 == "💎":
            multiplier = 10
        elif s1 == "🪙":
            multiplier = 5
        elif s1 == "💀":
            multiplier = 0
        else:
            multiplier = 4
        won_gold = 100 * multiplier
        new_gold = char["gold"] - 100 + won_gold
        await update_character(char["id"], gold=new_gold)
        msg = (
            f"🎰 *JEKPOT! KATTA G'ALABA!* 🎰\n\n"
            f"[ {s1} | {s2} | {s3} ]\n\n"
            f"🎉 3 ta bir xil tushdi! Siz **+{won_gold:,} 🪙 Oltin** yutib oldingiz!\n"
            f"Hozirgi hisobingiz: {new_gold:,} 🪙"
        )
    elif s1 == s2 or s2 == s3 or s1 == s3:
        new_gold = char["gold"] - 100 + 150
        await update_character(char["id"], gold=new_gold)
        msg = (
            f"🎰 *KICHIK YUTUQ!* 🎰\n\n"
            f"[ {s1} | {s2} | {s3} ]\n\n"
            f"✨ 2 ta bir xil belgi! Siz **+150 🪙 Oltin** oldingiz!"
        )
    else:
        new_gold = char["gold"] - 100
        await update_character(char["id"], gold=new_gold)
        msg = (
            f"🎰 *OMAD KELMADI!* 🎰\n\n"
            f"[ {s1} | {s2} | {s3} ]\n\n"
            f"💨 100 Oltin mayxona xazinasiga ketdi. Yana urinib ko'ring!"
        )

    buttons = [
        [InlineKeyboardButton(text="🎰 Yana Aylantirish (100 🪙)", callback_data="tavern_slots")],
        [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

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
        msg = f"🎉 *SIZ YUTDINGIZ!* ({player_roll} vs {opponent_roll})\n\nSiz raqibingizdan +50 Oltin yutib oldingiz!"
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
        "Sayyoh aytdi: 'Temirchi ustaxonada qurollarni +10 gacha sehrlay olar ekan, lekin ehtiyot bo'lish kerak!'",
        "Darvesh aytdi: 'Har kuni 7 kun ketma-ket qasamyod qilgan ritsarga imperator xazinasi ochilar emish!'"
    ]
    await callback.answer(random.choice(rumors), show_alert=True)

@tavern_router.callback_query(F.data == "tavern_steal_info")
async def show_steal_info(callback: CallbackQuery):
    text = (
        "🎯 *XUFYONA CHO'NTAKKESARLIK (O'G'RILIK) TIZIMI* 🎯\n\n"
        "Siz istalgan ritsarning hamyoniga yashirincha qo'l solishingiz mumkin!\n\n"
        "📜 *Foydalanish:*\n"
        "`/steal @username` yoki `!ogirla @username` *(yoki guruhda xabariga reply qilib: `!ogirla`)*\n\n"
        "⚡️ **Ehtimollik:**\n"
        "• **50% Omad:** Qurbonning 5% dan 10% gacha oltinini sezdirmay o'g'irlaysiz!\n"
        "• **50% Xavf:** Shahar soqchilari ushlab olib, sizni Qirollik Zindoniga tashlaydi!"
    )
    buttons = [[InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# CHO'NTAKKESARLIK (STEAL COMMAND)
@tavern_router.message(F.text.regexp(r"^(!|\/)(steal|ogirla)"))
async def process_pickpocket(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char or target_char["id"] == char["id"]:
        await message.reply("❌ O'g'rilik uchun boshqa ritsarni nishonga oling! Misol: `/steal @username`")
        return

    # Owner immunity check
    if target_char.get("is_owner", 0):
        await message.reply("⚡️ *Chaqmoq urdi!* Oliy Yaratuvchiga qo'l uzatishga jur'at qilganingiz uchun qo'lingiz kuydi!")
        return

    if target_char["gold"] < 50:
        await message.reply(f"💨 *{target_char['name']}* ning cho'ntagi bo'm-bo'sh ekan, o'g'irlaydigan hech narsa yo'q!")
        return

    # 50% chance
    if random.random() < 0.5:
        stolen_gold = max(10, int(target_char["gold"] * random.uniform(0.05, 0.12)))
        await update_character(char["id"], gold=char["gold"] + stolen_gold)
        await update_character(target_char["id"], gold=target_char["gold"] - stolen_gold)
        await message.reply(
            f"🎯 *OMADLI O'G'RILIK!* 🤫\n\n"
            f"Siz *{target_char['name']}* ning belidagi xaltasini sezdirmay kesib, **+{stolen_gold:,} 🪙 Oltin** o'g'irladingiz!\n"
            f"U hali nima bo'lganini ham sezmadi!",
            parse_mode="Markdown"
        )
    else:
        await update_character(char["id"], is_jailed=1)
        await message.reply(
            f"🚨 *QO'LGA TUSHINGIZ!* 👮‍♂️\n\n"
            f"*{target_char['name']}* o'z vaqtida qo'lingizdan ushlab oldi va soqchilarni chaqirdi!\n"
            f"Sizni hibsga olishdi va **Qirollik Zindoniga** tashlashdi!",
            parse_mode="Markdown"
        )
