import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from database.db import (
    get_character_by_user_id, update_character, get_character_equipment,
    get_or_create_daily_quests, get_player_professions, get_runes_inventory,
    get_guild_info, get_all_castles, get_current_king, get_top_knights,
    claim_daily_streak, RUNES_DATA, TRADE_CITIES, DUNGEON_FLOORS, get_dungeon_progress
)
from game.events_engine import EventsEngine
from game.bestiary import BESTIARY_DATA
from game.items_db import ITEMS_CATALOG
from game.lore_db import TAVERN_RUMORS, ANCIENT_SCROLLS
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

# =====================================================================
# 17. ZINDON VA PVE REYDLAR (DUNGEONS)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🗺 Zindon") | (F.text == "/dungeon"))
async def btn_dungeon(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    max_floor = await get_dungeon_progress(char["id"])
    sanity = char.get("sanity", 100)
    sanity_badge, _, _ = DarkEngine.get_sanity_status(sanity)

    text = (
        "🗺 *VALORIYA TAQIQLANGAN ZINDONLARI (10 TA BOSHQICH)* 🗺\n\n"
        "Qadimgi zulmat kuchlari qit'a ostidagi g'orlarni egallab olgan.\n"
        "Har bir qavatda afsonaviy mahluqlar, qadimiy bosslar va xazinalar yashiringan!\n\n"
        f"🧠 Sizning Ruhiyatingiz: *{sanity_badge}* ({sanity}%)\n"
        f"🏆 *Siz yetib borgan eng yuqori qavat:* {max_floor}-Qavat\n\n"
        "⚠️ *Zulmat Qoidasi:* Mag'lubiyat 25% oltinni boy berishga, ruhiyat sinishiga va qurollar darz ketishiga olib keladi!\n"
        "Qaysi qavatga tushishga jur'at qilasiz?"
    )

    buttons = []
    for floor_num, info in DUNGEON_FLOORS.items():
        is_unlocked = floor_num <= max_floor
        lock_icon = "⚔️" if is_unlocked else "🔒"
        status_txt = f"{info['name']} (Boss: {info['boss']})" if is_unlocked else f"{floor_num}-Qavat (Qulflangan)"
        callback_data = f"enter_dungeon_{floor_num}" if is_unlocked else "dungeon_locked"
        buttons.append([InlineKeyboardButton(text=f"{lock_icon} {status_txt}", callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 18. SAHRO VA SARGUZASHT (WILDERNESS EXPLORATION)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("🧭 Sahro") | (F.text == "/explore") | (F.text == "/sahro"))
async def btn_explore(message: Message):
    char = await get_character_by_user_id(message.from_user.id)
    if not char:
        await message.answer("Avval /start orqali qahramon yarating!", reply_markup=class_selection_keyboard())
        return

    if char["stamina"] < 15:
        await message.answer("Charchagansiz (Stamina kamida 15 bo'lishi kerak)! Tavernada ovqatlaning yoki dam oling.")
        return

    # Stamina sarflash
    await update_character(char["id"], stamina=char["stamina"] - 15)
    event = EventsEngine.get_random_event()

    text = (
        f"🧭 *VALORIYA SARHADLARI BO'YLAB SAYOHAT* (-15 Stamina)\n\n"
        f"*{event['title']}*\n\n"
        f"{event['desc']}\n\n"
        f"Qanday qarorga kelasiz?"
    )

    buttons = []
    for choice_key, choice_label in event["options"]:
        buttons.append([
            InlineKeyboardButton(text=choice_label, callback_data=f"expact_{event['id']}_{choice_key}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])

    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data.startswith("expact_"))
async def process_explore_action(callback: CallbackQuery):
    parts = callback.data.split("_")
    # expact_event_shrine_pray -> event_id: event_shrine, choice: pray
    if len(parts) < 4:
        return
    event_id = f"{parts[1]}_{parts[2]}"
    choice = parts[3]

    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    result_text, changes = EventsEngine.resolve_event(event_id, choice, char)

    # Bazadagi o'zgarishlarni qo'llash
    new_gold = max(0, char["gold"] + changes.get("gold", 0))
    new_hp = max(10, min(char["max_hp"], char["hp"] + changes.get("hp", 0)))
    new_sanity = max(0, min(100, char.get("sanity", 100) + changes.get("sanity", 0)))
    new_xp = char.get("xp", 0) + changes.get("xp", 0)

    await update_character(char["id"], gold=new_gold, hp=new_hp, sanity=new_sanity, xp=new_xp)

    buttons = [
        [InlineKeyboardButton(text="🧭 Yana Sahroga Chiqish (-15 Stamina)", callback_data="menu_explore_again")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(result_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data == "menu_explore_again")
async def process_explore_again(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
    if char["stamina"] < 15:
        await callback.answer("Stamina kamida 15 bo'lishi kerak! Tavernaga boring.", show_alert=True)
        return

    await update_character(char["id"], stamina=char["stamina"] - 15)
    event = EventsEngine.get_random_event()

    text = (
        f"🧭 *VALORIYA SARHADLARI BO'YLAB SAYOHAT* (-15 Stamina)\n\n"
        f"*{event['title']}*\n\n"
        f"{event['desc']}\n\n"
        f"Qanday qarorga kelasiz?"
    )

    buttons = []
    for choice_key, choice_label in event["options"]:
        buttons.append([
            InlineKeyboardButton(text=choice_label, callback_data=f"expact_{event['id']}_{choice_key}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 19. ENSIKLOPEDIYA VA LORE (GRAND ARCHIVE OF VALORIA)
# =====================================================================
@menu_buttons_router.message(F.text.startswith("📖 Ensiklopediya") | (F.text == "/lore") | (F.text == "/bestiary") | (F.text == "/ensiklopediya"))
async def btn_lore(message: Message):
    text = (
        "📖 *VALORIYA BUYUK ARXIVI VA ENSIKLOPEDIYASI* 🏛\n\n"
        "Qit'aning ming yillik sirlari, maxluqlar anatomiyasi, afsonaviy relikviyalar "
        "va 12 ta buyuk imperiya qasamyodlari shu yerda saqlanadi.\n\n"
        "Qaysi bo'limdagi ilmlarni o'rganmoqchisiz?"
    )
    buttons = [
        [InlineKeyboardButton(text="👺 Maxluqlar Ensiklopediyasi (Bestiariy)", callback_data="lore_menu_bestiary")],
        [InlineKeyboardButton(text="🗡 100+ Qurollar & Sovutlar Katalogi", callback_data="lore_menu_items")],
        [InlineKeyboardButton(text="📜 Qadimiy Qo'lyozmalar & Mayxona Sirlari", callback_data="lore_menu_scrolls")],
        [InlineKeyboardButton(text="🦁 12 Imperiya Tarixi va Armiyalari", callback_data="lore_menu_kingdoms")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data == "lore_hub")
async def cb_lore_hub(callback: CallbackQuery):
    text = (
        "📖 *VALORIYA BUYUK ARXIVI VA ENSIKLOPEDIYASI* 🏛\n\n"
        "Qit'aning ming yillik sirlari, maxluqlar anatomiyasi, afsonaviy relikviyalar "
        "va 12 ta buyuk imperiya qasamyodlari shu yerda saqlanadi.\n\n"
        "Qaysi bo'limdagi ilmlarni o'rganmoqchisiz?"
    )
    buttons = [
        [InlineKeyboardButton(text="👺 Maxluqlar Ensiklopediyasi (Bestiariy)", callback_data="lore_menu_bestiary")],
        [InlineKeyboardButton(text="🗡 100+ Qurollar & Sovutlar Katalogi", callback_data="lore_menu_items")],
        [InlineKeyboardButton(text="📜 Qadimiy Qo'lyozmalar & Mayxona Sirlari", callback_data="lore_menu_scrolls")],
        [InlineKeyboardButton(text="🦁 12 Imperiya Tarixi va Armiyalari", callback_data="lore_menu_kingdoms")],
        [InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# 19.1 BESTIARY LIST & DETAILS
@menu_buttons_router.callback_query(F.data == "lore_menu_bestiary")
async def cb_lore_bestiary_list(callback: CallbackQuery):
    text = (
        "👺 *VALORIYA MAXLUQOTLAR BESTIARIYSI* 👺\n\n"
        "Valoriya o'rmonlari, zindonlari va tog'larida uchraydigan barcha yirtqichlar, "
        "bosslar va la'natlangan maxluqlar ro'yxati. Ularning zaifliklarini bilish g'alaba kalitidir!\n\n"
        "Batafsil anketasini ko'rish uchun maxluqni tanlang:"
    )
    buttons = []
    for b_id, b_data in BESTIARY_DATA.items():
        buttons.append([
            InlineKeyboardButton(text=f"{b_data['name']} [{b_data['danger']}]", callback_data=f"beast_info_{b_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Ensiklopediya", callback_data="lore_hub")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data.startswith("beast_info_"))
async def cb_lore_beast_details(callback: CallbackQuery):
    b_id = callback.data.replace("beast_info_", "")
    b = BESTIARY_DATA.get(b_id)
    if not b:
        return

    text = (
        f"👺 *MAXLUQ SHAXSIY ANKETASI: {b['name']}*\n\n"
        f"⚠️ Xavflilik darajasi: *{b['danger']}*\n"
        f"🌲 Yashash muhiti: _{b['habitat']}_\n"
        f"❤️ Jon (HP): *{b['hp']}* | ⚔️ Zarba: *{b['atk']}* | 🛡 Himoya: *{b['def']}*\n"
        f"🎯 *Zaifligi:* `{b['weakness']}`\n\n"
        f"📜 *Tavsif va Xatti-harakati:*\n{b['desc']}\n\n"
        f"🎁 *Tushadigan o'ljalar (Loot):*\n{b['loot']}"
    )
    buttons = [
        [InlineKeyboardButton(text="⬅️ Maxluqlar Ro'yxati", callback_data="lore_menu_bestiary")],
        [InlineKeyboardButton(text="🏛 Bosh Arxiv", callback_data="lore_hub")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# 19.2 ITEMS CATALOG
@menu_buttons_router.callback_query(F.data == "lore_menu_items")
async def cb_lore_items_list(callback: CallbackQuery):
    text = (
        "🗡 *100+ ANJOMLAR VA AFSONAVIY RELIKVIYALAR KATALOGI* 🛡\n\n"
        "Valoriya dunyosidagi barcha qurollar, sovutlar, uzuklar va mifik tojlar to'plami.\n\n"
        "Eng kuchli buyumlarni ko'zdan kechiring:"
    )
    buttons = []
    # Eng mashhur 10 ta afsonaviy qurol/zirh
    sample_items = list(ITEMS_CATALOG.items())[:12]
    for i_id, i_data in sample_items:
        buttons.append([
            InlineKeyboardButton(text=f"{i_data['name']} (⚔️{i_data['attack']} | 🛡{i_data['defense']})", callback_data=f"item_info_{i_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Ensiklopediya", callback_data="lore_hub")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data.startswith("item_info_"))
async def cb_lore_item_details(callback: CallbackQuery):
    i_id = callback.data.replace("item_info_", "")
    item = ITEMS_CATALOG.get(i_id)
    if not item:
        return

    rarity_icons = {"common": "⚪️ Oddiy", "rare": "🔵 Noyob", "epic": "🟣 Epik", "legendary": "🟡 Afsonaviy", "mythic": "🔴 Mifik", "divine": "👑 Ilohiy"}
    r_str = rarity_icons.get(item["rarity"], item["rarity"].upper())

    text = (
        f"*{item['name']}*\n\n"
        f"🏷 Qimmatlilik darajasi: *{r_str}* (Tier {item['tier']})\n"
        f"⚔️ Hujum kuchi (ATK): *+{item['attack']}*\n"
        f"🛡 Himoya kuchi (DEF): *+{item['defense']}*\n"
        f"🪙 O'rtacha bozor narxi: *{item['price']:,} 🪙 Oltin*\n\n"
        f"📜 *Tarixi va Afsonasi:*\n_{item['desc']}_"
    )
    buttons = [
        [InlineKeyboardButton(text="⬅️ Buyumlar Katalogi", callback_data="lore_menu_items")],
        [InlineKeyboardButton(text="🏛 Bosh Arxiv", callback_data="lore_hub")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# 19.3 SCROLLS & TAVERN RUMORS
@menu_buttons_router.callback_query(F.data == "lore_menu_scrolls")
async def cb_lore_scrolls_list(callback: CallbackQuery):
    text = (
        "📜 *QADIMIY QO'LYOZMALAR VA MAYXONA AFSONALARI* 📜\n\n"
        "Mayxonalarda aytiladigan sirlar, karvon yo'llari xaritalari va "
        "Valoriya yaratilishi haqidagi qo'lyozmalarni mutolaa qiling:"
    )
    buttons = []
    for s_id, s_data in ANCIENT_SCROLLS.items():
        buttons.append([InlineKeyboardButton(text=f"📜 {s_data['title']}", callback_data=f"scroll_read_{s_id}")])
    buttons.append([InlineKeyboardButton(text="🍻 Mayxona Mish-Mishlari (Tasodifiy)", callback_data="lore_random_rumor")])
    buttons.append([InlineKeyboardButton(text="⬅️ Ensiklopediya", callback_data="lore_hub")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data.startswith("scroll_read_"))
async def cb_lore_scroll_read(callback: CallbackQuery):
    s_id = callback.data.replace("scroll_read_", "")
    sc = ANCIENT_SCROLLS.get(s_id)
    if not sc:
        return

    text = f"*{sc['title']}*\n\n{sc['text']}"
    buttons = [
        [InlineKeyboardButton(text="⬅️ Qo'lyozmalar Ro'yxati", callback_data="lore_menu_scrolls")],
        [InlineKeyboardButton(text="🏛 Bosh Arxiv", callback_data="lore_hub")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data == "lore_random_rumor")
async def cb_lore_random_rumor(callback: CallbackQuery):
    import random
    rumor = random.choice(TAVERN_RUMORS)
    text = (
        f"🍻 *MAYXONA SHIVIR-SHIVIRI: {rumor['title']}*\n\n"
        f"🗣 *Aytuvchi:* _{rumor['author']}_\n\n"
        f"'{rumor['text']}'"
    )
    buttons = [
        [InlineKeyboardButton(text="🎲 Boshqa Mish-Mish Eshitish", callback_data="lore_random_rumor")],
        [InlineKeyboardButton(text="⬅️ Qo'lyozmalar", callback_data="lore_menu_scrolls")],
        [InlineKeyboardButton(text="🏛 Bosh Arxiv", callback_data="lore_hub")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# 19.4 KINGDOMS LORE
@menu_buttons_router.callback_query(F.data == "lore_menu_kingdoms")
async def cb_lore_kingdoms_list(callback: CallbackQuery):
    text = (
        "🦁 *12 BUYUK IMPERIYA SIYOSATI VA HARBIY DOKTRINALARI* 🦁\n\n"
        "Har bir imperiyaning yashirin maqsadlari, elita qo'shinlari va afzalliklari:"
    )
    buttons = []
    for k_id, k_data in KINGDOMS.items():
        buttons.append([InlineKeyboardButton(text=f"{k_data['name']}", callback_data=f"lore_k_view_{k_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Ensiklopediya", callback_data="lore_hub")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@menu_buttons_router.callback_query(F.data.startswith("lore_k_view_"))
async def cb_lore_single_kingdom(callback: CallbackQuery):
    k_id = callback.data.replace("lore_k_view_", "")
    k = KINGDOMS.get(k_id)
    if not k:
        return

    text = (
        f"👑 *{k['name']} TO'LIQ DOSYESI* 👑\n\n"
        f"🏛 *Poytaxti:* {k['capital']}\n"
        f"👤 *Hukmdori:* {k['ruler']}\n"
        f"📜 *Shiori:* _{k['motto']}_\n"
        f"⚔️ *Harbiy ixtisosligi:* {k['specialty']}\n"
        f"💎 *Qirollik Bonusi:* Mudofaa, iqtisod va qonli urushlarda maxsus afzallik beradi.\n"
        f"🎙 *Hukmdor tabiati:* _{k['personality'].upper()} — {k['voice_style']}_\n\n"
        f"Siz ushbu imperiya saroyiga borib, paxta qo'yishingiz yoki xizmatiga kirishingiz mumkin!"
    )
    buttons = [
        [InlineKeyboardButton(text="🍯 Saroyga Borish (Paxta Qo'yish)", callback_data=f"flatter_{k_id}")],
        [InlineKeyboardButton(text="⬅️ Qirolliklar Ro'yxati", callback_data="lore_menu_kingdoms")],
        [InlineKeyboardButton(text="🏛 Bosh Arxiv", callback_data="lore_hub")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

