import json
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, update_character, get_character_by_identifier,
    restore_sanity, cure_wound, cure_all_wounds, sign_blood_pact, cleanse_blood_pact
)
from game.dark_engine import DarkEngine, WOUND_TYPES
from config import is_owner

tavern_router = Router()

SLOT_SYMBOLS = ["⚔️", "🪙", "💎", "👑", "💀", "🛡"]

@tavern_router.callback_query(F.data == "menu_tavern")
async def show_tavern_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    from database.db import increment_quest_progress
    await increment_quest_progress(char["id"], "market_or_tavern", 1)

    sanity = char.get("sanity", 100)
    sanity_badge, _, _ = DarkEngine.get_sanity_status(sanity)

    wounds_list = []
    try:
        w_raw = char.get("wounds_json", "[]")
        wounds_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
    except Exception:
        wounds_list = []

    has_pact = char.get("bloodline_trait") == "demon_pact"
    pact_status = "\n🩸 *Zulmat Ahdi:* Iblis Morvath bilan ahd faol (+45 ATK)!" if has_pact else ""
    wounds_status = f"\n🩹 *Jarohatlar:* {len(wounds_list)} ta bitmagan travma mavjud!" if wounds_list else "\n🟢 *Tanangiz:* Sog'lom va baquvvat."

    text = (
        "🍻 *SHAHAR TAVERNA VA QIMORXONASI* 🍻\n\n"
        "Mayxona qizigan! Ritsarlar sharob ichib, suyak tashlab qimor o'ynamoqda. "
        "Burchakda esa xalq tabibi va qora qonli iblis sehrgari o'tiribdi.\n\n"
        f"🪙 Cho'ntagingizdagi Oltin: *{char['gold']:,} 🪙*\n"
        f"❤️ Joningiz: *{char['hp']}/{char['max_hp']}* | 🧠 Aql (Sanity): *{sanity_badge}* ({sanity}%){wounds_status}{pact_status}"
    )
    
    buttons = [
        [
            InlineKeyboardButton(text="🍷 Qadimgi Sharob (Sanity +30 - 50 🪙)", callback_data="tavern_drink_ale"),
            InlineKeyboardButton(text=f"🏥 Tabibxona ({len(wounds_list)} Travma)", callback_data="tavern_healer_menu")
        ],
        [
            InlineKeyboardButton(text="🎲 Suyak Tashlash (50 🪙)", callback_data="tavern_dice"),
            InlineKeyboardButton(text="🎰 Oltin Baraban (100 🪙)", callback_data="tavern_slots")
        ],
        [
            InlineKeyboardButton(text="🎡 Omad G'ildiragi (Har 8 soatda BEPUL!)", callback_data="tavern_lucky_wheel")
        ],
        [
            InlineKeyboardButton(text="🍗 Shohona Ziyofat (Jon 100% - 30 🪙)", callback_data="tavern_eat"),
            InlineKeyboardButton(text="🤫 Mayxona Mish-Mishlari", callback_data="tavern_rumors")
        ],
        [
            InlineKeyboardButton(text="🩸 Zulmat Qurbongohi (Qonli Ahd)", callback_data="tavern_pact_menu"),
            InlineKeyboardButton(text="🕯 Muqaddas Ibodatxona", callback_data="tavern_cleanse_menu")
        ],
        [
            InlineKeyboardButton(text="🎯 Xufyona Cho'ntakkesarlik (O'g'rilik)", callback_data="tavern_steal_info")
        ],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "tavern_lucky_wheel")
async def cb_lucky_wheel_view(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    import time
    from game.tavern_games import WHEEL_COOLDOWN_SECONDS

    now = int(time.time())
    last_spin = int(char.get("last_wheel_spin") or 0)
    time_passed = now - last_spin
    is_free = time_passed >= WHEEL_COOLDOWN_SECONDS

    if is_free:
        status_str = "🟢 *Hozir BEPUL aylantirish mumkin!*"
    else:
        left_mins = (WHEEL_COOLDOWN_SECONDS - time_passed) // 60
        status_str = f"⏳ Bepul aylantirishga: *{left_mins} daqiqa* qoldi. (Pullik: 100 🪙 yoki 1 💎)"

    text = (
        "🎡 *VALORIYA OMAD G'ILDIRAGI (LUCKY WHEEL)* 🎡\n\n"
        "Har 8 soatda kelib bepul aylantiring va shohona sovrinlarni yutib oling!\n\n"
        f"👑 *Bosh Sovrin (Jackpot):* `10,000 🪙 Oltin + 50 💎 Javohir`\n"
        f"🥚 Hamroh Tuxumi | 🗡 Afsonaviy Qurollar | ⚡️ Runalar\n\n"
        f"{status_str}\n\n"
        f"Sizda mavjud: *{char['gold']:,} 🪙* | *{char['gems']} 💎*"
    )

    buttons = [
        [InlineKeyboardButton(text="🎡 G'ildirakni Aylantirish!", callback_data="tavern_wheel_spin_action")],
        [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "tavern_wheel_spin_action")
async def cb_lucky_wheel_spin(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    from database.db import spin_lucky_wheel
    success, msg, slot = await spin_lucky_wheel(char["id"])
    if not success:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer(f"Yutuq: {slot['name']}!", show_alert=True)
    await cb_lucky_wheel_view(callback)

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
    if is_owner(user_id=target_char.get("user_id"), username=target_char.get("username")) or target_char.get("is_owner", 0):
        await message.reply("⚡️ *Chaqmoq urdi!* Oliy Yaratuvchiga (@NAKAMA_02) qo'l uzatishga jur'at qilganingiz uchun qo'lingiz kuydi!")
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

# =====================================================================
# ZULMAT TIZIMI: AQL VA SANITY TIKLASH (SHAROB & MED)
# =====================================================================
@tavern_router.callback_query(F.data == "tavern_drink_ale")
async def process_drink_ale(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await restore_sanity(char["id"], amount=30, cost=50)
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_tavern_menu(callback)

# =====================================================================
# ZULMAT TIZIMI: SHAHAR TABIBXONASI (TRAVMA VA JAROHATLAR)
# =====================================================================
@tavern_router.callback_query(F.data == "tavern_healer_menu")
async def show_healer_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    wounds_list = []
    try:
        w_raw = char.get("wounds_json", "[]")
        wounds_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
    except Exception:
        wounds_list = []

    text = (
        "🏥 *VALORIYA SHAHAR TABIBXONASI* 🏥\n\n"
        "Keksa xalq tabibi qadimiy o'tlar, ilon zahri va sehrli malhamlar bilan ishlaydi.\n"
        "Jangda olingan har qanday jarohat va singan suyaklarni shu yerda davolashingiz mumkin!\n\n"
        f"🪙 Hamyoningiz: *{char['gold']:,} 🪙*\n"
    )

    buttons = []
    if not wounds_list:
        text += "\n✅ *Sizda hech qanday davolanmagan travma yo'q! Taningiz sog'lom va bardam.*"
    else:
        text += f"\n🩸 *Sizdagi faol og'ir jarohatlar ({len(wounds_list)} ta):*\n"
        total_cost = 0
        for w_id in wounds_list:
            w_info = WOUND_TYPES.get(w_id, {"name": w_id, "desc": "Og'ir yara", "cure_cost": 150})
            total_cost += w_info["cure_cost"]
            text += f"• *{w_info['name']}:* {w_info['desc']} _(Davolash: {w_info['cure_cost']} 🪙)_\n"
            buttons.append([
                InlineKeyboardButton(
                    text=f"🩹 {w_info['name']} ({w_info['cure_cost']} 🪙)",
                    callback_data=f"cure_wound_{w_id}"
                )
            ])

        if len(wounds_list) > 1:
            buttons.append([
                InlineKeyboardButton(
                    text=f"✨ Barcha Jarohatlarni Davolash ({total_cost} 🪙)",
                    callback_data="cure_all_wounds"
                )
            ])

    buttons.append([InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")])
    buttons.append([InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data.startswith("cure_wound_"))
async def process_cure_single_wound(callback: CallbackQuery):
    wound_id = callback.data.replace("cure_wound_", "")
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await cure_wound(char["id"], wound_id)
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_healer_menu(callback)

@tavern_router.callback_query(F.data == "cure_all_wounds")
async def process_cure_all_wounds(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await cure_all_wounds(char["id"])
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await show_healer_menu(callback)

# =====================================================================
# ZULMAT TIZIMI: QONLI AHD (BLOOD PACT - IBLIS MORVATH)
# =====================================================================
@tavern_router.callback_query(F.data == "tavern_pact_menu")
async def show_blood_pact_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    has_pact = char.get("bloodline_trait") == "demon_pact"
    if has_pact:
        text = (
            "🩸 *QONLI AHD QURBONGOHI (FAOL)* 🩸\n\n"
            "Siz allaqachon Iblis Morvath bilan qonli ahd tuzgansiz!\n"
            "Tomirlaringizda qora olov oqmoqda.\n\n"
            "⚡️ *Zulmat Quvvati:* +45 Dark ATK va Janglarda 20% Lifesteal!\n"
            "💀 *Jazo:* -25 Max HP doimiy cheklov.\n\n"
            "Ushbu ahddan qutulish faqat **Muqaddas Ibodatxonada** mumkin."
        )
        buttons = [
            [InlineKeyboardButton(text="🕯 Muqaddas Ibodatxonaga Borish", callback_data="tavern_cleanse_menu")],
            [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")]
        ]
    else:
        text = (
            "🩸 *ZULMATNING QONLI QURBONGOHI (TAQIQLANGAN)* 🩸\n\n"
            "Qorong'u burchakda qora plash kiygan kultist pichirlamoqda:\n"
            "_\"Iblis Morvath o'z kuchini senga berishga tayyor, ritsar... Lekin har bir qudratning qonli to'lovi bor!\"_\n\n"
            "⚡️ *SIZGA BERILADIGAN QUVVAT:*\n"
            "• **+45 Dark Attack** (Barcha janglarda ulkan qora zarba)\n"
            "• **20% Lifesteal** (Zarba berganingizda dushman jonini o'zingizga so'rib olasiz)\n\n"
            "💀 *SHAVQATSIZ TO'LOV:*\n"
            "• **-25 Doimiy Max HP** (Vujudingiz yemirilib boradi)\n"
            "• **-30 Sanity** (Zulmat sharpalari vasvasasi)\n"
            "• Qirollik ritsarlari sizga la'natlangan qotil deb qaraydi!\n\n"
            "Ushbu qonli ahdni imzolashga tayyormisiz?"
        )
        buttons = [
            [InlineKeyboardButton(text="🩸 Qonli Ahdni Imzolash (Tavakkal!)", callback_data="confirm_sign_pact")],
            [InlineKeyboardButton(text="⬅️ Mayxonaga Qaytish", callback_data="menu_tavern")]
        ]

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "confirm_sign_pact")
async def confirm_sign_pact_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await sign_blood_pact(char["id"])
    await callback.answer("🩸 Qora qon tomirlaringizga kirdi!", show_alert=True)
    buttons = [
        [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# ZULMAT TIZIMI: MUQADDAS IBODATXONA (POKLANISH)
# =====================================================================
@tavern_router.callback_query(F.data == "tavern_cleanse_menu")
async def show_cleanse_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    has_pact = char.get("bloodline_trait") == "demon_pact"
    text = (
        "🕯 *VALORIYA MUQADDAS IBODATXONASI* 🕯\n\n"
        "Shahar markazidagi oq toshli ibodatxonada shamlar yonib turibdi. "
        "Bu yerda ritsarlar o'z ruhiyatini tozalaydi va qora afsunlarni yechadi.\n\n"
        f"🪙 Sizdagi oltin: *{char['gold']:,} 🪙*\n"
    )

    buttons = []
    if has_pact:
        text += (
            "🩸 *SIZNING RUHINGIZDA IBLIS LA'NATI MAVJUD!* 💀\n"
            "Ruhoniylar 1,500 Oltin evaziga maxsus marosim o'tkazib, qonli ahdni parchalashi mumkin.\n"
            "Bu sizning asl joningizni (+25 Max HP) va Sanityni 100% tiklaydi."
        )
        buttons.append([InlineKeyboardButton(text="🕯 Qonli Ahdni Bekor Qilish (1,500 🪙)", callback_data="confirm_cleanse_pact")])
    else:
        text += "\n✨ Ruhingiz toza, iblis ahdlari mavjud emas!"

    buttons.append([InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")])
    buttons.append([InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")] )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@tavern_router.callback_query(F.data == "confirm_cleanse_pact")
async def confirm_cleanse_pact_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    success, msg = await cleanse_blood_pact(char["id"])
    if not success:
        await callback.answer(msg, show_alert=True)
        return

    await callback.answer("🕯 Ruhingiz poklandi!", show_alert=True)
    buttons = [
        [InlineKeyboardButton(text="⬅️ Taverna", callback_data="menu_tavern")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# CHAT VA BUYRUQLAR (TEXT TRIGGERS: /pact, /tabib, /wounds, /sanity)
# =====================================================================
@tavern_router.message(F.text.regexp(r"^(!|\/)(pact|ahd|zulmat)"))
async def text_command_pact(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    has_pact = char.get("bloodline_trait") == "demon_pact"
    if has_pact:
        await message.reply(
            "🩸 *QONLI AHD STATUS:* Siz Iblis Morvath bilan shartnoma tuzgansiz!\n"
            "Quvvat: +45 Dark ATK, 20% Lifesteal.\nBekor qilish uchun: `/cleanse` yoki Ibodatxonaga boring.",
            parse_mode="Markdown"
        )
    else:
        buttons = [
            [InlineKeyboardButton(text="🩸 Qonli Ahd Menyusi", callback_data="tavern_pact_menu")],
            [InlineKeyboardButton(text="🍻 Taverna", callback_data="menu_tavern")]
        ]
        await message.reply(
            "🩸 *IBLIS MORVATHNING QONLI AHDI:* Kuch va o'lim shartnomasi!\n"
            "Tafsilotlarni ko'rish va imzolash uchun quyidagi tugmani bosing:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

@tavern_router.message(F.text.regexp(r"^(!|\/)(cleanse|poklanish)"))
async def text_command_cleanse(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    buttons = [[InlineKeyboardButton(text="🕯 Ibodatxonaga O'tish", callback_data="tavern_cleanse_menu")]]
    await message.reply(
        "🕯 *VALORIYA MUQADDAS IBODATXONASI:*\nRuhingizni poklash uchun ibodatxonaga tashrif buyuring:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@tavern_router.message(F.text.regexp(r"^(!|\/)(tabib|wounds|yaralar|davolan)"))
async def text_command_healer(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    buttons = [[InlineKeyboardButton(text="🏥 Tabibxonaga Kirish", callback_data="tavern_healer_menu")]]
    await message.reply(
        "🏥 *SHAHAR TABIBXONASI:*\nSingan suyaklar va og'ir travmalarni davolash uchun tabibxonaga kiring:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@tavern_router.message(F.text.regexp(r"^(!|\/)(sanity|aql|ruhiyat)"))
async def text_command_sanity(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.reply("Avval /start bosing!")
        return

    sanity = char.get("sanity", 100)
    badge, mood, desc = DarkEngine.get_sanity_status(sanity)
    buttons = [[InlineKeyboardButton(text="🍷 Taverna Sharobi (Sanity +30)", callback_data="tavern_drink_ale")]]
    await message.reply(
        f"🧠 *AQL VA RUHIYAT (SANITY) HOLATI:*\n\n"
        f"Ko'rsatkich: *{sanity}%* [{badge}]\n"
        f"Holat: {mood}\n\n"
        f"📜 {desc}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

