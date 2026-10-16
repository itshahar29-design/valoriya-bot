import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from database.db import (
    get_character_by_user_id, update_character, get_character_equipment,
    get_or_create_daily_quests, get_player_professions, get_runes_inventory,
    get_guild_info, get_all_castles, get_current_king, get_top_knights,
    claim_daily_streak, RUNES_DATA, TRADE_CITIES
)
from keyboards.inline_menus import (
    main_menu_keyboard, battle_actions_keyboard,
    inventory_qol_keyboard, owner_god_mode_keyboard, class_selection_keyboard
)
from keyboards.reply_keyboards import main_reply_keyboard
from game.constants import KINGDOMS, EQUIPMENT_SLOTS
from game.dark_engine import DarkEngine, WOUND_TYPES
from game.npc_engine import NPCEngine
from services.card_generator import generate_knight_card
from handlers.arena_handler import ACTIVE_BATTLES
from handlers.market_handler import get_market_hub_keyboard
from handlers.quest_handler import render_quests_ui
from handlers.trade_travel_handler import render_trade_ui
from config import OWNER_ID, OWNER_USERNAME

menu_buttons_router = Router()

def is_owner_user(user_id: int, username: str | None, char: dict | None) -> bool:
    if char and char.get("is_owner", 0):
        return True
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return False

# =====================================================================
# 1. ARENA (1v1 DUEL)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("⚔️ Arena") | (F.text == "/arena"))
async def btn_arena(message: Message):
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.answer("Avval /start orqali qahramoningizni tanlang!", reply_markup=class_selection_keyboard())
        return

    bot_opponent = NPCEngine.generate_bot_knight(target_level=char["level"])
    eff_stats = DarkEngine.calculate_effective_stats(char)

    eq_items = await get_character_equipment(char["id"])
    weapon = next((i for i in eq_items if i.get("slot_type") == "weapon" and i.get("is_equipped") == 1), None)
    armor = next((i for i in eq_items if i.get("slot_type") == "armor" and i.get("is_equipped") == 1), None)

    player_runes = []
    if weapon and weapon.get("runes_json"):
        try:
            player_runes.extend(json.loads(weapon["runes_json"]))
        except Exception:
            pass
    w_atk = weapon["attack"] if weapon else 12
    a_def = armor["defense"] if armor else 8

    ACTIVE_BATTLES[user_id] = {
        "player": {
            "name": char["name"],
            "hp": min(char["hp"], eff_stats["eff_max_hp"]),
            "max_hp": eff_stats["eff_max_hp"],
            "stamina": 100,
            "strength": char["strength"],
            "constitution": char["constitution"],
            "agility": eff_stats["eff_agi"],
            "weapon_attack": w_atk,
            "armor_defense": a_def,
            "sanity": char.get("sanity", 100),
            "bloodline_trait": char.get("bloodline_trait", "noble_blood"),
            "stamina_drain_round": eff_stats["stamina_drain_round"],
            "runes": player_runes,
            "is_defending": False
        },
        "opponent": bot_opponent,
        "selected_zone": "torso",
        "round": 1
    }

    sanity_badge, _, _ = DarkEngine.get_sanity_status(char.get("sanity", 100))
    wound_warn = f"\n⚠️ *Jarohatlar:* {eff_stats['wounds_count']} ta og'ir travma mavjud!" if eff_stats["wounds_count"] > 0 else ""
    pact_warn = "\n🩸 *Zulmat Ahdi faol (+45 Dark ATK, 20% Lifesteal)!*" if eff_stats["has_blood_pact"] else ""
    runes_warn = f"\n🔮 *Qurol Runalari:* {' '.join(['🔥' if r=='fire_rune' else ('❄️' if r=='frost_rune' else '⚡️') for r in player_runes])}" if player_runes else ""

    text = (
        f"⚔️ *ARENA: 1v1 SHON-SHARAF DUELI (1-Raund)* ⚔️\n\n"
        f"👤 *Siz:* {char['name']} (Lvl {char['level']}) | ❤️ {char['hp']}/{eff_stats['eff_max_hp']} HP | ⚡️ 100 Stamina{runes_warn}{pact_warn}\n"
        f"🧠 Aql: {sanity_badge} ({char.get('sanity', 100)}%){wound_warn}\n\n"
        f"💀 *Raqib:* {bot_opponent['name']} (Lvl {bot_opponent['level']})\n"
        f"❤️ Raqib Joni: {bot_opponent['hp']} HP | 🎭 Persona: {bot_opponent['persona'].upper()}\n"
        f"💰 O'lja: {bot_opponent['loot_gold']} 🪙\n\n"
        f"🎯 Nizonli zona: *Gavda / Ko'krak (Torso)*\n"
        f"Harakatni tanlang:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=battle_actions_keyboard())

# =====================================================================
# 2. 12 QIROLLIK
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🏰 12 Qirollik") | (F.text == "/kingdoms") | (F.text == "/qirollik"))
async def btn_kingdoms(message: Message):
    buttons = []
    for k_id, k_data in KINGDOMS.items():
        buttons.append([InlineKeyboardButton(text=f"{k_data['name']}", callback_data=f"view_k_{k_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    await message.answer(
        "🏰 *VALORIYA QIT'ASINING 12 BUYUK AI IMPERIYASI* 🏰\n\n"
        "Har bir imperiya o'z mustaqil aqli, armiyasi, boyligi va hukmdoriga ega. "
        "Birini tanlab, uning saroyiga tashrif buyuring:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# =====================================================================
# 3. INVENTAR (8 SLOT & QOL)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🎒 Inventar") | (F.text == "/inventory") | (F.text == "/bag"))
async def btn_inventory(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    items = await get_character_equipment(char["id"])
    equipped = {i["slot_type"]: i for i in items if i["is_equipped"] == 1}

    slots_text = []
    for slot_key, slot_name in EQUIPMENT_SLOTS:
        item = equipped.get(slot_key)
        if item:
            durability_str = f"({item['durability']}/{item['max_durability']}🛡)"
            if item["durability"] <= 0:
                durability_str = "(💥 SINIQ - 0🛡)"
            slots_text.append(f"• *{slot_name}:* {item['item_name']} {durability_str}")
        else:
            slots_text.append(f"• *{slot_name}:* _Bo'sh_")

    sanity = char.get("sanity", 100)
    badge, _, _ = DarkEngine.get_sanity_status(sanity)

    wounds_count = 0
    try:
        w_raw = char.get("wounds_json", "[]")
        w_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
        wounds_count = len(w_list)
    except Exception:
        pass

    wound_alert = f" | 🩸 *Travmalar:* {wounds_count} ta" if wounds_count > 0 else ""

    text = (
        f"🎒 *{char['name']} NING 8-SLOTLI ANJOMLARI* 🎒\n\n"
        f"🪙 Oltin: *{char['gold']:,}* | 💎 Yoqut: *{char.get('gems', 0)}*\n"
        f"❤️ HP: *{char['hp']}/{char['max_hp']}* | ⚡️ Stamina: *{char['stamina']}/100*\n"
        f"🧠 Sanity: *{sanity}%* [{badge}]{wound_alert}\n"
        f"🐎 Ot: *{char['horse_name']}* ({char['horse_bond']}% bog'lanish)\n\n"
        + "\n".join(slots_text) + "\n\n"
        "⚡️ *Tezkor Qulayliklar (QoL):*"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=inventory_qol_keyboard())

# =====================================================================
# 4. TEMIRCHI VA RUNALAR (FORGE)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🔨 Temirchi") | (F.text == "/forge"))
async def btn_forge(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    items = await get_character_equipment(char["id"])
    equipped = [i for i in items if i["is_equipped"] == 1]

    buttons = []
    text = (
        "🔨 *VALORIYA QIROVUL TEMIRCHISI (FORGE - DARK SOULS EDITION)* 🔨\n\n"
        "Bu yerda qurol va sovutlaringizni sehrli ruda yordamida **+1 dan +10 gacha** kuchaytirishingiz mumkin!\n"
        "Har bir kuchaytirish qurolga **+15 Zarba**, sovutga **+10 Himoya** beradi.\n\n"
        "⚠️ *ZULMATNING TEMIRCHI QOIDALARI:*\n"
        "• **+1 .. +3:** Xavfsiz (faqat oltin sarflanadi)\n"
        "• **+4 .. +6:** Xavfli (omadsizlikda daraja -1 pasayishi mumkin)\n"
        "• **+7 .. +10:** O'ta Xatarli (qurol maydalanib sinishi mumkin!)\n\n"
        f"🪙 Hamyoningizdagi oltin: *{char['gold']:,} 🪙*\n\n"
        "Qaysi anjomingizni bolg'a ostiga qo'yasiz?"
    )

    for item in equipped:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔨 {item['item_name']} (⚔️{item['attack']} | 🛡{item['defense']})",
                callback_data=f"forge_upgrade_{item['id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="🔮 Qurolga Runa O'rnatish (Socket)", callback_data="menu_forge_runes")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 5. JONLI BOZOR (P2P MARKET)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🛒") | (F.text == "/market") | (F.text == "/bozor"))
async def btn_market(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
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

# =====================================================================
# 6. KVESTLAR VA YUTUQLAR (QUESTS & ACHIEVEMENTS)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("📜") | (F.text == "/quests") | (F.text == "/kvest"))
async def btn_quests(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    q = await get_or_create_daily_quests(char["id"])
    text, markup = render_quests_ui(q)
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

# =====================================================================
# 7. SHAXTA VA ALXIMIYA (MINING & ALCHEMY)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("⛏ Shaxta") | (F.text == "/mine") | (F.text == "/alximiya"))
async def btn_professions(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    profs = await get_player_professions(char["id"])
    potions = profs.get("potions", {})

    active_buff = ""
    if char.get("active_buff_potion"):
        active_buff = f"\n⚡️ *Faol Damlama:* {char['active_buff_potion'].upper()} ({char.get('buff_potion_battles', 0)} ta jang qoldi!)"

    text = (
        "⛏ *VALORIYA SHAXTASI VA ALXIMIYA USTAXONASI* 🧪\n\n"
        "Bu yerda ritsarlar qoyalardan qimmatbaho rudalar qazib oladi va "
        "qadimiy qozonlarda jangovar damlamalar (potions) tayyorlaydi!\n\n"
        f"⚡️ Chidamlilik (Stamina): *{char['stamina']}/100*\n"
        f"📦 *Yig'ilgan Resurslaringiz:*\n"
        f"• 🔩 Temir rudasi: *{profs.get('iron_ore', 0)} ta*\n"
        f"• 🪙 Oltin rudasi: *{profs.get('gold_ore', 0)} ta*\n"
        f"• ✨ Sehrli Mithril: *{profs.get('mithril_ore', 0)} ta*\n"
        f"• 🌿 Shifobaxsh O'tlar: *{profs.get('herbs', 0)} ta*\n\n"
        f"🧪 *Tayyor Damlamalaringiz:*\n"
        f"• 🔥 G'azab (+30% ATK): *{potions.get('rage', 0)} ta*\n"
        f"• ❤️ Hayot Eliksiri (Jon 100%): *{potions.get('healing', 0)} ta*\n"
        f"• 💀 Zulmat Zaxari (+40 Zaharlash): *{potions.get('void_poison', 0)} ta*{active_buff}\n\n"
        "Qanday harakat qilasiz?"
    )

    buttons = [
        [InlineKeyboardButton(text="⛏ Shaxtada Qazish (-20 Stamina)", callback_data="action_mine_ore")],
        [
            InlineKeyboardButton(text="🧪 G'azab Damlamasi (2 Temir + 1 O't)", callback_data="brew_potion_rage"),
            InlineKeyboardButton(text="❤️ Hayot Eliksiri (3 O't + 1 Oltin)", callback_data="brew_potion_healing")
        ],
        [InlineKeyboardButton(text="💀 Zulmat Zaxari (1 Mithril + 2 O't)", callback_data="brew_potion_void_poison")],
        [
            InlineKeyboardButton(text="🔥 G'azabni Ichish", callback_data="use_potion_rage"),
            InlineKeyboardButton(text="❤️ Jonni Tiklash", callback_data="use_potion_healing"),
            InlineKeyboardButton(text="💀 Zaxarni Surtish", callback_data="use_potion_void_poison")
        ],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 8. SHAHARLARARO KARVON SAVDOSI (TRADE ARBITRAGE)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🐫 Karvon") | (F.text == "/trade") | (F.text == "/karvon"))
async def btn_trade(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    text, markup = await render_trade_ui(char)
    await message.answer(text, parse_mode="Markdown", reply_markup=markup)

# =====================================================================
# 9. GILDIYA VA QAL'ALAR (GUILDS & CASTLES)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🏰 Gildiya") | (F.text == "/guild") | (F.text == "/klan"))
async def btn_guild(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
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
    else:
        guild = await get_guild_info(guild_id)
        castle_txt = f"🏰 Egallangan Qal'a: *{guild.get('castle_owned')}*" if guild and guild.get("castle_owned") else "🏰 Egallangan Qal'a: _Hozircha yo'q_"
        members_list = "\n".join([f"• ⚔️ {m['name']} (Lvl {m['level']}) — {m['wins']} G'alaba" for m in guild.get("members", [])[:5]]) if guild else ""
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
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 10. OLIY TAXT VA TURNIR (THRONE)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("👑 Oliy Taxt") | (F.text == "/throne") | (F.text == "/taxt"))
async def btn_throne(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    king = await get_current_king()
    king_name = king.get("king_name") or "Bo'sh (Egalanmagan)"
    defense_wins = king.get("defense_wins", 0)
    is_king = king.get("king_character_id") == char["id"]
    status_msg = "\n👑 *Siz hozirgi Valoriya Qirolisiz! Toj sizning boshingizda!*" if is_king else ""
    text = (
        "👑 *VALORIYA OLIY TAXTI VA BUYUK TURNIR* 👑\n\n"
        "Butun qit'aning eng qudratli ritsari ushbu Oltin Tojni kiyadi!\n"
        "Qirol barcha ritsarlarga buyruq berish, shon-sharaf va barcha bozor savdolaridan soliq olish huquqiga ega!\n\n"
        f"👑 *Amaldagi Valoriya Qiroli:* {king_name}\n"
        f"🛡 *Tojni muvaffaqiyatli himoya qilgan:* {defense_wins} marta{status_msg}\n\n"
        "Har qanday 3-darajadan yuqori ritsar qirolga duel e'lon qilib taxtni tortib olishi mumkin!\n"
        "Jur'at qilasizmi?"
    )
    buttons = []
    if not is_king:
        buttons.append([InlineKeyboardButton(text="⚔️ Qirolga Taxt Duellari E'lon Qilish", callback_data="challenge_king_duel")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 11. TAVERNA VA QIMOR (TAVERN)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🍻 Taverna") | (F.text == "/tavern"))
async def btn_tavern(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
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
            InlineKeyboardButton(text="🍗 Shohona Ziyofat (Jon 100% - 30 🪙)", callback_data="tavern_eat"),
            InlineKeyboardButton(text="🤫 Mayxona Mish-Mishlari", callback_data="tavern_rumors")
        ],
        [
            InlineKeyboardButton(text="🩸 Morvath Qonli Ahdi (Qora Sehr)", callback_data="tavern_blood_pact_menu"),
            InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
        ]
    ]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 12. KUNDALIK SOVG'A (DAILY REWARDS)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🎁") | (F.text == "/daily"))
async def btn_daily(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    streak = char.get("daily_streak", 0) or 0
    streak_bar = ""
    for day in range(1, 8):
        icon = "✅" if day <= streak else "🔒"
        streak_bar += f"{icon} {day}-Kun | "
    streak_bar = streak_bar.rstrip(" | ")

    text = (
        "🎁 *QIROLLIK KUNDALIK MARHAMATI (7-KUNLIK STREAK)* 🎁\n\n"
        "Har kuni o'yinga kiring va tobora qimmatbaho xazinalarni qo'lga kiriting!\n"
        "Agar bir kun o'tkazib yuborsangiz, zanjir 1-kundan qayta boshlanadi.\n\n"
        f"📊 *Sizning joriy zanjiringiz:* {streak} kun ketma-ket\n"
        f"[{streak_bar}]\n\n"
        "👑 *7-Kunda:* 7,777 Oltin, 25 Javohir va Afsonaviy Mifik Gambeson!"
    )
    buttons = [
        [InlineKeyboardButton(text="💎 Bugungi Sovg'ani Olish", callback_data="claim_daily_action")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 13. REYTING (TOP LEADERBOARD)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🏆") | (F.text == "/top") | (F.text == "/leaderboard"))
async def btn_top(message: Message):
    top_knights = await get_top_knights(limit=10)
    if not top_knights:
        text = "🏆 *VALORIYA SHON-SHARAF ZALI* 🏆\n\nHali janglar endi boshlanmoqda! Birinchi bo'lib maydonga chiqing."
    else:
        lines = []
        for rank, k in enumerate(top_knights, start=1):
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            badge = medals.get(rank, f"{rank}.")
            lines.append(f"{badge} *{k['name']}* — Lvl {k['level']} | 🎖 {k['honor']} Honor ({k['wins']}W / {k['losses']}L)")
        text = "🏆 *VALORIYA SHON-SHARAF ZALI (TOP-10)* 🏆\n\n" + "\n".join(lines)
    buttons = [[InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 14. PROFIL VA KARTA (PROFILE & VISUAL CARD)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("👤") | (F.text == "/profile") | (F.text == "/card"))
async def btn_profile(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    eq = await get_character_equipment(char["id"])
    guild = await get_guild_info(char.get("guild_id", 0)) if char.get("guild_id") else None
    guild_name = guild["name"] if guild else None

    # Visual Pillow Knight Card
    buf = generate_knight_card(char, equipment=eq, guild_name=guild_name)
    photo = BufferedInputFile(buf.getvalue(), filename=f"knight_{user_id}.png")

    is_owner = is_owner_user(user_id, username, char)
    status_str = "👑 *Valoriya Yaratuvchisi (Owner - God-Mode)*" if is_owner else "🛡 *Qasamyod qilgan Ritsar*"
    sanity = char.get("sanity", 100)
    sanity_badge, _, _ = DarkEngine.get_sanity_status(sanity)

    wounds_list = []
    try:
        w_raw = char.get("wounds_json", "[]")
        wounds_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
    except Exception:
        wounds_list = []

    has_pact = char.get("bloodline_trait") == "demon_pact"
    pact_display = "🩸 *Iblis Ahdi (+45 ATK)*" if has_pact else "🌟 *Ozod Ruh*"

    caption = (
        f"👤 *RITSAR SHAXSIY HUJJATI & VIZUAL KARTASI* 🪪\n\n"
        f"Ism: *{char['name']}*\n"
        f"Maqom: {status_str}\n"
        f"Kasb: *{char['class_id'].upper()}* | Daraja: *{char['level']}*\n"
        f"❤️ Jon: *{char['hp']}/{char['max_hp']}* | ⚡️ Stamina: *{char['stamina']}/100*\n"
        f"🧠 Sanity: *{sanity}%* [{sanity_badge}] | {pact_display}\n"
        f"🩹 Jarohatlar: *{len(wounds_list)} ta*\n"
        f"🪙 Oltin: *{char['gold']:,}* | 💎 Javohir: *{char.get('gems', 0)}*\n"
        f"🏆 Janglar: *{char['wins']}* G'alaba | *{char['losses']}* Mag'lubiyat"
    )
    buttons = [
        [InlineKeyboardButton(text="⚔️ Arenada Jang", callback_data="menu_arena")],
        [InlineKeyboardButton(text="🎒 Inventar (8 Slot)", callback_data="menu_inventory")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await message.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 15. GOD-MODE (OWNER OLIY BOSHQARUVI)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("👑 OLIY") | F.text.startswith("👑 GOD") | (F.text == "/owner") | (F.text == "/god"))
async def btn_owner_god(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)

    is_owner = is_owner_user(user_id, username, char)
    if not is_owner:
        await message.answer("⛔️ Bu bo'lim faqat Oliy Yaratuvchi (Owner) uchun himoyalangan!")
        return

    text = (
        "⚡️ *VALORIYA YARATUVCHISI (GOD-MODE) [1-SAHIFA]* ⚡️\n\n"
        "👑 *Shaxsiy Qudrat va Xudo Darajasidagi Buyumlar:*\n"
        "• Cheksiz oltin, javohirlar, elementar runalar va eliksirlar\n"
        "• God-Stats: 99,999 HP / 999 ATK va 999 DEF\n"
        "• Bir zumda Valoriya Taxtini egallash (Qirol bo'lish)\n"
        "• Afsonaviy Pegas va Iblis Ahdini yoqish/o'chirish."
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=owner_god_mode_keyboard(page=1))

# =====================================================================
# 16. BOSH MENYU REFRESH
# =====================================================================
@menu_buttons_router.message(F.text.in_(["/menu", "🏠 Bosh Menyu", "Bosh Menyu", "menyu", "Menyu"]))
async def btn_menu(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    is_owner = is_owner_user(user_id, username, char)
    await message.answer(
        f"👑 *Qaytganingiz bilan, {char['name']}!*\n\n"
        f"🏰 Daraja: *{char['level']}* | 🪙 Oltin: *{char['gold']:,}*\n"
        f"⚔️ Kasb: *{char['class_id'].upper()}* | ❤️ Jon: *{char['hp']}/{char['max_hp']}*\n\n"
        f"Harbiy harakatlar uchun pastki menyu tugmalaridan yoki quyidagi bo'limlardan foydalaning:",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard(is_owner)
    )
    await message.answer(
        "🏰 *Valoriya Oliy Harbiy Shtabi:*",
        reply_markup=main_menu_keyboard(is_owner)
    )
