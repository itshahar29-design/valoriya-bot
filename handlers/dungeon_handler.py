import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, update_character,
    get_dungeon_progress, advance_dungeon_floor, DUNGEON_FLOORS,
    apply_defeat_penalty
)
from game.battle_engine import BattleEngine
from game.dark_engine import DarkEngine

dungeon_router = Router()

@dungeon_router.callback_query(F.data == "menu_dungeon")
async def show_dungeon_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    max_floor = await get_dungeon_progress(char["id"])
    sanity = char.get("sanity", 100)
    sanity_badge, _, _ = DarkEngine.get_sanity_status(sanity)
    
    text = (
        "🗺 *VALORIYA TAQIQLANGAN ZINDONLARI (PVE REYDLAR)* 🗺\n\n"
        "Qadimgi zulmat kuchlari qit'a ostidagi g'orlarni egallab olgan.\n"
        "Har bir qavatda afsonaviy mahluqlar va qaroqchilar xazinalari yashiringan!\n\n"
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
        buttons.append([InlineKeyboardButton(text=f"{lock_icon} {floor_num}. {status_txt}", callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dungeon_router.callback_query(F.data == "dungeon_locked")
async def process_locked_dungeon(callback: CallbackQuery):
    await callback.answer("🔒 Ushbu qavat qulflangan! Avvalgi qavat bossini mag'lub etishingiz kerak.", show_alert=True)

@dungeon_router.callback_query(F.data.startswith("enter_dungeon_"))
async def process_enter_dungeon(callback: CallbackQuery):
    floor = int(callback.data.replace("enter_dungeon_", ""))
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    floor_info = DUNGEON_FLOORS.get(floor)
    if not floor_info:
        return

    # Aql va jarohatlar hisobi
    eff_stats = DarkEngine.calculate_effective_stats(char)
    
    # Chuqur qavatlar (3+) tumanidan Sanity yo'qotish
    if floor >= 3:
        current_san = char.get("sanity", 100)
        await update_character(char["id"], sanity=max(0, current_san - 5))

    attacker = {
        "name": char["name"],
        "hp": min(char["hp"], eff_stats["eff_max_hp"]),
        "max_hp": eff_stats["eff_max_hp"],
        "strength": char["strength"],
        "agility": eff_stats["eff_agi"],
        "constitution": char["constitution"],
        "stamina": char["stamina"],
        "weapon_attack": 25,
        "armor_defense": 15,
        "sanity": char.get("sanity", 100),
        "bloodline_trait": char.get("bloodline_trait", "noble_blood"),
        "stamina_drain_round": eff_stats["stamina_drain_round"],
        "is_defending": False
    }

    boss_hp = floor_info["hp"]
    defender = {
        "name": floor_info["boss"],
        "hp": boss_hp,
        "max_hp": boss_hp,
        "constitution": 18 + floor * 4,
        "agility": 12 + floor * 2,
        "stamina": 100,
        "strength": 16 + floor * 4,
        "armor_defense": 10 + floor * 3,
        "is_defending": False
    }

    # 3-raundlik qonli zindon to'qnashuvi
    combat_logs = []
    player_survived = True

    for r_num in range(1, 4):
        # O'yinchi hujumi
        dmg_p, log_p, _ = BattleEngine.calculate_round(attacker, defender, "torso", "heavy_strike" if r_num == 1 else "skill")
        combat_logs.extend(log_p)

        if defender["hp"] <= 0:
            break

        # Bossning qattiq javob zarbasi
        dmg_b, log_b, _ = BattleEngine.calculate_round(defender, attacker, "neck", "heavy_strike")
        combat_logs.extend(log_b)

        if attacker["hp"] <= 0:
            player_survived = False
            break

    # G'alaba yoki Qaqshatqich Mag'lubiyat
    if defender["hp"] <= 0 and player_survived:
        await advance_dungeon_floor(char["id"], floor)
        await update_character(char["id"], gold=char["gold"] + floor_info["loot_gold"], xp=char["xp"] + floor_info["loot_xp"])
        
        res_text = (
            f"🎉 *ZINDON BOSSI QONGA BELANDI VA YENGILDI!* 🏆\n\n"
            f"Siz *{floor}-Qavat* dahshatli xo'jayini **{floor_info['boss']}** ni maydalab tashladingiz!\n\n"
            f"📜 *Jang Tafsilotlari:*\n" + "\n".join(combat_logs[:4]) + "\n\n"
            f"💰 *Qo'lga Kiritilgan Xazina:* +{floor_info['loot_gold']:,} 🪙 Oltin | +{floor_info['loot_xp']} XP!\n"
            f"Keyingi qavat darvozalari ochildi!"
        )
        buttons = [
            [InlineKeyboardButton(text="🗺 Zindonlar Ro'yxati", callback_data="menu_dungeon")],
            [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
        ]
    else:
        # Zulmat jazolari
        penalty = await apply_defeat_penalty(char["id"], is_dungeon=True)
        wound_txt = f"\n🩸 *ZINDONDA OLINGAN TRAVMA:* {penalty['new_wound']['name']}!\n_{penalty['new_wound']['desc']}_" if penalty["new_wound"] else ""

        res_text = (
            f"🩸 *ZINDONDA QAQSHATQICH MAG'LUBIYAT!* 💀\n\n"
            f"**{floor_info['boss']}** o'zining dahshatli zulmat kuchi bilan sizni chil-parchin qildi!\n\n"
            f"📜 *Oxirgi daqiqalar:*\n" + "\n".join(combat_logs[-3:]) + "\n\n"
            f"💸 *Zindonda Yo'qotilgan Oltin:* -{penalty['gold_lost']:,} 🪙\n"
            f"🧠 *Aql/Sanity Zarari:* -{penalty['sanity_lost']}% (Hozirgi Sanity: {penalty['current_sanity']}%)\n"
            f"🛡 *Anjomlar Talafoti:* Qurol va sovutlar -{penalty['durability_lost']} chidamlilik yo'qotdi!{wound_txt}\n\n"
            f"Ser Artur sizning qonga belangan vujudingizni zindondan zo'rg'a olib chiqdi."
        )
        buttons = [
            [InlineKeyboardButton(text="🏥 Tabibxonaga Borish", callback_data="tavern_healer_menu")],
            [InlineKeyboardButton(text="🔨 Temirchida Qurollarni Tuzatish", callback_data="menu_forge")],
            [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
        ]

    await callback.message.edit_text(res_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

