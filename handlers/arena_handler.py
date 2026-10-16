from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_character_by_user_id, update_character, apply_defeat_penalty, award_referral_cashback
from game.battle_engine import BattleEngine
from game.npc_engine import NPCEngine
from game.retention_engine import RetentionEngine
from keyboards.inline_menus import battle_actions_keyboard, hit_zones_keyboard, main_menu_keyboard
from config import is_owner

arena_router = Router()

# Faol janglar xotirasi (Active battle sessions in-memory)
ACTIVE_BATTLES = {}

@arena_router.callback_query(F.data == "menu_arena")
async def start_arena_duel(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval ro'yxatdan o'ting!", show_alert=True)
        return

    # Instant NPC Matchmaking
    bot_opponent = NPCEngine.generate_bot_knight(target_level=char["level"])
    
    # Zulmat Tizimi: Haqiqiy statlar va travmalar hisobi
    from game.dark_engine import DarkEngine
    import json
    from database.db import get_character_equipment, increment_quest_progress, unlock_achievement
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

    # Jang sessiyasi
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

    battle = ACTIVE_BATTLES[user_id]
    
    sanity_badge, _, sanity_desc = DarkEngine.get_sanity_status(char.get("sanity", 100))
    wound_warn = f"\n⚠️ *Jarohatlar:* {eff_stats['wounds_count']} ta og'ir travma mavjud!" if eff_stats["wounds_count"] > 0 else ""
    pact_warn = "\n🩸 *Zulmat Ahdi faol (+45 Dark ATK, 20% Lifesteal)!*" if eff_stats["has_blood_pact"] else ""
    runes_warn = f"\n🔮 *Qurol Runalari:* {' '.join(['🔥' if r=='fire_rune' else ('❄️' if r=='frost_rune' else '⚡️') for r in player_runes])}" if player_runes else ""

    await callback.message.edit_text(
        f"⚔️ *ARENA: 1v1 SHON-SHARAF DUELI (1-Raund)* ⚔️\n\n"
        f"👤 *Siz:* ❤️ {battle['player']['hp']}/{battle['player']['max_hp']} HP | ⚡️ {battle['player']['stamina']} Stamina\n"
        f"🧠 Ruh holati: *{sanity_badge}* ({battle['player']['sanity']}%){wound_warn}{pact_warn}{runes_warn}\n"
        f"🆚\n"
        f"🤖 *Raqib:* {bot_opponent['name']} (Lvl {bot_opponent['level']})\n"
        f"❤️ {bot_opponent['hp']}/{bot_opponent['max_hp']} HP | Xarakter: *{bot_opponent['persona'].upper()}*\n\n"
        f"🎯 Tanlangan nishon zonasi: *{battle['selected_zone'].upper()}*\n"
        f"Qanday jangovar harakat qilasiz?",
        parse_mode="Markdown",
        reply_markup=battle_actions_keyboard()
    )

@arena_router.callback_query(F.data.in_(["battle_strike", "battle_heavy_strike", "battle_defend", "battle_skill"]))
async def process_battle_turn(callback: CallbackQuery):
    user_id = callback.from_user.id
    battle = ACTIVE_BATTLES.get(user_id)
    
    if not battle:
        await callback.answer("Jang sessiyasi tugagan!", show_alert=True)
        return
        
    action_type = callback.data.replace("battle_", "")
    
    # 1. O'yinchining zarbasi
    p = battle["player"]
    opp = battle["opponent"]
    zone = battle["selected_zone"]
    
    if action_type == "defend":
        p["is_defending"] = True
        p_log = [f"🛡 Siz qalqoningizni ko'tarib himoyaga o'tdingiz."]
    else:
        p["is_defending"] = False
        _, p_log, _ = BattleEngine.calculate_round(p, opp, target_zone=zone, action=action_type)
        
    # G'alaba tekshiruvi
    if opp["hp"] <= 0:
        del ACTIVE_BATTLES[user_id]
        char = await get_character_by_user_id(user_id)
        loot_gold = opp["loot_gold"]
        loot_xp = opp["loot_xp"]
        
        await update_character(
            char["id"], 
            gold=char["gold"] + loot_gold, 
            xp=char["xp"] + loot_xp,
            wins=char["wins"] + 1,
            honor=char["honor"] + 25
        )
        await award_referral_cashback(char["id"], loot_gold)

        # Kundalik kvest va yutuqlar
        await increment_quest_progress(char["id"], "arena_wins", 1)
        if (char["wins"] + 1) >= 10:
            await unlock_achievement(char["id"], "arena_champion", "⚔️ Arena Chempioni")
        
        # Tasodifiy Dervish sovg'asi (Dopamin qopqoni)
        has_dervish, gift, dervish_msg = RetentionEngine.check_random_dervish_encounter()
        bonus_text = f"\n\n{dervish_msg}" if has_dervish else ""
        
        await callback.message.edit_text(
            f"🏆 *BUYUK G'ALABA! RAQIB MAG'LUB ETILDI!* 🏆\n\n"
            f"Siz {opp['name']} ustidan qonli g'alabaga erishdingiz!\n\n"
            f"💰 *O'lja:* +{loot_gold} Oltin\n"
            f"✨ *Tajriba:* +{loot_xp} XP\n"
            f"🎖 *Shon-sharaf:* +25 Honor\n"
            f"📜 *Kundalik Kvest:* Arenadagi g'alaba hisobga olindi!{bonus_text}",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(is_owner(user_id=user_id, username=callback.from_user.username))
        )
        return
        
    # 2. Dushmanning javob zarbasi
    opp_action, opp_zone, opp_note = NPCEngine.choose_bot_action(opp, (p["hp"] / p["max_hp"]) * 100)
    
    if opp_action == "surrender":
        del ACTIVE_BATTLES[user_id]
        char = await get_character_by_user_id(user_id)
        loot_gold = opp["loot_gold"]
        await update_character(char["id"], gold=char["gold"] + loot_gold, wins=char["wins"] + 1)
        await increment_quest_progress(char["id"], "arena_wins", 1)
        if (char["wins"] + 1) >= 10:
            await unlock_achievement(char["id"], "arena_champion", "⚔️ Arena Chempioni")
        await callback.message.edit_text(
            f"🏳️ *DUSHMAN TASLIM BO'LDI!* 🏳️\n\n"
            f"{opp['name']} qo'rquvdan tiz cho'kib jonini saqlab qolish uchun {loot_gold} oltin to'ladi!\n"
            f"📜 *Kundalik Kvest:* Arenadagi g'alaba hisobga olindi!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(is_owner(user_id=user_id, username=callback.from_user.username))
        )
        return
        
    if opp_action == "defend":
        opp_log = [f"🛡 {opp['name']} mudofaaga o'tdi."]
    else:
        _, opp_log, _ = BattleEngine.calculate_round(opp, p, target_zone=opp_zone, action=opp_action)
        
    # Mag'lubiyat tekshiruvi (Zulmat Tizimi oqibatlari)
    if p["hp"] <= 0:
        del ACTIVE_BATTLES[user_id]
        char = await get_character_by_user_id(user_id)
        penalty = await apply_defeat_penalty(char["id"], is_dungeon=False)
        
        wound_txt = f"\n🩸 *ORTTIRILGAN OG'IR TRAVMA:* {penalty['new_wound']['name']}!\n_{penalty['new_wound']['desc']}_" if penalty["new_wound"] else "\n🩹 Baxtingizga suyaklaringiz darz ketmadi."
        
        defeat_msg = (
            f"💀 *SHAVQATSIZ MAG'LUBIYAT! JANGDA QULADINGIZ!* 💀\n\n"
            f"**{opp['name']}** qilichi bilan qalqoningizni yorib, sizni hushsiz qulatdi!\n\n"
            f"💸 *Yo'qotilgan Oltin:* -{penalty['gold_lost']:,} 🪙 (Talonchilar shilib ketdi)\n"
            f"🧠 *Aql/Sanity Zarari:* -{penalty['sanity_lost']}% (Hozirgi Sanity: {penalty['current_sanity']}%)\n"
            f"🛡 *Anjomlar Eskirishi:* Egnidagi barcha anjomlar -{penalty['durability_lost']} chidamlilik yo'qotdi!{wound_txt}\n\n"
            f"Tavernaga borib tabibga ko'rining yoki sharob bilan ruhingizni tinchlantiring!"
        )
        buttons = [
            [InlineKeyboardButton(text="🏥 Tabibga Borish (Davolash)", callback_data="tavern_healer_menu")],
            [InlineKeyboardButton(text="🍻 Taverna Sharobi (Sanity)", callback_data="menu_tavern")],
            [InlineKeyboardButton(text="🔨 Qurollarni Tuzatish", callback_data="menu_forge")],
            [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
        ]
        await callback.message.edit_text(
            defeat_msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return
        
    battle["round"] += 1
    all_logs = "\n".join(p_log + opp_log)
    
    await callback.message.edit_text(
        f"⚔️ *ARENA ({battle['round']}-Raund)* ⚔️\n\n"
        f"👤 *Siz:* ❤️ {p['hp']}/{p['max_hp']} HP | ⚡️ {p['stamina']} Stamina\n"
        f"🤖 *Raqib:* {opp['name']}\n"
        f"❤️ {opp['hp']}/{opp['max_hp']} HP\n\n"
        f"📜 *Jang Jurnali:*\n{all_logs}\n\n"
        f"🎯 Tanlangan zona: *{zone.upper()}*",
        parse_mode="Markdown",
        reply_markup=battle_actions_keyboard()
    )

@arena_router.callback_query(F.data == "battle_choose_zone")
async def choose_hit_zone_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎯 *ZARBA BERISH UCHUN TANA QISMINI TANLANG:*\n\n"
        "• *Bosh / Miya:* 2.2x zarar, yuqori krit\n"
        "• *Bo'yin:* 2.5x zarar, qon ketish chaqiradi\n"
        "• *Ko'krak:* Ishonchli, qovurg'a sindirish\n"
        "• *Qorin:* Ichki organlar jarohati\n"
        "• *Qo'llar & Oyoqlar:* Qurol yoki qochishni pasaytirish",
        parse_mode="Markdown",
        reply_markup=hit_zones_keyboard()
    )

@arena_router.callback_query(F.data.startswith("zone_"))
async def set_hit_zone(callback: CallbackQuery):
    user_id = callback.from_user.id
    zone = callback.data.replace("zone_", "")
    
    if user_id in ACTIVE_BATTLES:
        ACTIVE_BATTLES[user_id]["selected_zone"] = zone
        
    await callback.answer(f"Nishon: {zone.upper()} etib belgilandi!")
    battle = ACTIVE_BATTLES.get(user_id)
    if battle:
        await callback.message.edit_text(
            f"⚔️ *ARENA ({battle['round']}-Raund)* ⚔️\n\n"
            f"👤 *Siz:* ❤️ {battle['player']['hp']} HP\n"
            f"🤖 *Raqib:* ❤️ {battle['opponent']['hp']} HP\n\n"
            f"🎯 Yangi nishon: *{zone.upper()}*",
            parse_mode="Markdown",
            reply_markup=battle_actions_keyboard()
        )
