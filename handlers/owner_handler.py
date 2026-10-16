import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_connection, get_character_by_user_id, update_character,
    create_world_snapshot, get_world_telemetry, give_global_airdrop, get_active_groups,
    get_character_by_identifier, give_player_item, strip_player_equipment, reset_player_character,
    set_setting
)
from keyboards.inline_menus import owner_god_mode_keyboard, main_menu_keyboard
from config import OWNER_ID, OWNER_USERNAME, is_owner

owner_router = Router()

def is_owner_authorized(user_id: int, username: str | None, char: dict | None = None) -> bool:
    clean_u = username or (char.get("username") if char else None)
    return is_owner(user_id=user_id, username=clean_u)

@owner_router.callback_query(F.data.in_(["menu_owner_god", "god_page_1"]))
async def open_owner_god_menu_p1(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    
    if not is_owner_authorized(user_id, username, char):
        await callback.answer("⛔️ Ruxsat berilmagan! Faqat Oliy Yaratuvchi (@NAKAMA_02) uchun!", show_alert=True)
        return
        
    await callback.message.edit_text(
        "⚡️ *VALORIYA YARATUVCHISI (GOD-MODE) [1-SAHIFA]* ⚡️\n\n"
        "👑 *Shaxsiy Qudrat va Xudo Darajasidagi Buyumlar:*\n"
        "• Cheksiz oltin, javohirlar, elementar runalar va eliksirlar\n"
        "• God-Stats: 99,999 HP / 999 ATK va 999 DEF\n"
        "• Bir zumda Valoriya Taxtini egallash (Qirol bo'lish)\n"
        "• Afsonaviy Pegas va Iblis Ahdini yoqish/o'chirish.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard(page=1)
    )

@owner_router.callback_query(F.data == "god_page_2")
async def open_owner_god_menu_p2(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    
    if not is_owner_authorized(user_id, username, char):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return
        
    await callback.message.edit_text(
        "🌍 *VALORIYA YARATUVCHISI (GOD-MODE) [2-SAHIFA]* 🌍\n\n"
        "⚡️ *Dunyo Ofatlari, Guruhlar va Server Nazorati:*\n"
        "• Qonli Oy, Ajdaho Reydi, Oltin va Meteor yomg'iri\n"
        "• Global Shifo (barcha o'yinchilar davolanadi) yoki Global Qahr (chaqmoq)\n"
        "• Bozor va Qal'alarni tozalash (Admin Reset)\n"
        "• Snapshot saqlash va 1-soatlik Rollback.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard(page=2)
    )

# 1. CHEKSIZ XAZINA (+50,000 Oltin)
@owner_router.callback_query(F.data == "god_grant_gold")
async def grant_owner_gold(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await update_character(char["id"], gold=char["gold"] + 50000, gems=char.get("gems", 0) + 100)
    await callback.answer("💰 Xazinangizga +50,000 Oltin va +100 Qimmatbaho Javohir qo'shildi!", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.1 CHEKSIZ JAVOHIR (+1,000 Javohir)
@owner_router.callback_query(F.data == "god_grant_gems")
async def grant_owner_gems(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import give_player_gems
    await give_player_gems(char["id"], 1000)
    await callback.answer("💎 Xazinangizga +1,000 Qimmatbaho Javohir qo'shildi!", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.2 TAXTNI DARHOL EGALLASH
@owner_router.callback_query(F.data == "god_claim_throne_instant")
async def god_claim_throne(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import make_player_king
    ok, msg = await make_player_king(char["id"])
    await callback.answer(msg.replace("*", ""), show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.3 BARCHA RUNALAR TO'PLAMI (+10 Olov, +10 Muz, +10 Chaqmoq)
@owner_router.callback_query(F.data == "god_spawn_runes")
async def god_spawn_runes(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import give_player_runes
    await give_player_runes(char["id"], "fire_rune", 10)
    await give_player_runes(char["id"], "frost_rune", 10)
    await give_player_runes(char["id"], "lightning_rune", 10)
    await callback.answer("🔮 10x Olov, 10x Muz va 10x Chaqmoq runalari berildi!", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.4 BARCHA ELIKSIRLAR TO'PLAMI (+20 G'azab, +20 Hayot, +20 Zaxar)
@owner_router.callback_query(F.data == "god_spawn_potions")
async def god_spawn_potions(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    import json
    from database.db import get_player_professions, get_connection
    profs = await get_player_professions(char["id"])
    pots = profs.setdefault("potions", {})
    pots["rage"] = pots.get("rage", 0) + 20
    pots["healing"] = pots.get("healing", 0) + 20
    pots["void_poison"] = pots.get("void_poison", 0) + 20
    async with get_connection() as db:
        await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), char["id"]))
        await db.commit()
    await callback.answer("🧪 20x G'azab, 20x Hayot va 20x Zaxarlar qo'shildi!", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.5 QANOTLI PEGAS TULPORI
@owner_router.callback_query(F.data == "god_spawn_pegasus")
async def god_spawn_pegasus(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    await update_character(char["id"], horse_name="🦄 Qanotli Oltin Pegas", horse_bond=100)
    await callback.answer("🦄 Qanotli Oltin Pegas tulpori sizga 100% bog'landi!", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.6 IBLIS QONLI AHDI TOGGLE
@owner_router.callback_query(F.data == "god_toggle_demon_pact")
async def god_toggle_demon_pact(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    current = char.get("bloodline_trait", "noble_blood")
    new_trait = "noble_blood" if current == "demon_pact" else "demon_pact"
    await update_character(char["id"], bloodline_trait=new_trait)
    status = "bekor qilindi (Ozod Ruh)" if new_trait == "noble_blood" else "yoqildi (+45 ATK, 20% Lifesteal)!"
    await callback.answer(f"🩸 Zulmat ahdi {status}", show_alert=True)
    await open_owner_god_menu_p1(callback)

# 1.7 GLOBAL SHIFO (MASS HEAL)
@owner_router.callback_query(F.data == "god_mass_heal")
async def god_mass_heal(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import get_connection, get_active_groups
    async with get_connection() as db:
        await db.execute("UPDATE characters SET hp = max_hp, stamina = max_stamina, sanity = 100, wounds_json = '[]'")
        await db.commit()
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "💖 *YARATUVCHIDAN BUTUN VALORIYAGA SHIFO VA MARHAMAT!* 🌟\n\n"
                "Oliy Yaratuvchi butun qit'adagi barcha ritsarlarning jarohatlarini davoladi, "
                "jonlarini 100% ga to'ldirdi va aqllarini pokladi!",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await callback.answer("💖 Butun dunyo ritsarlari 100% sog'aytirildi!", show_alert=True)
    await open_owner_god_menu_p2(callback)

# 1.8 GLOBAL QAHR (MASS SMITE)
@owner_router.callback_query(F.data == "god_mass_smite")
async def god_mass_smite(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import get_connection, get_active_groups
    async with get_connection() as db:
        await db.execute("UPDATE characters SET hp = MAX(10, hp - 30) WHERE is_owner = 0")
        await db.commit()
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "⚡️ *OSMONLARDAN YARATUVCHINING QAHR CHAQMOG'I URILDI!* ⚡️\n\n"
                "Valoriya zaminini ilohiy chaqmoq qopladi! Barcha ritsarlarga -30 HP jazo zarbasi berildi!",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await callback.answer("⚡️ Global chaqmoq zarbasi barcha ritsarlarga urildi!", show_alert=True)
    await open_owner_god_menu_p2(callback)

# 1.9 BOZORNI TOZALASH
@owner_router.callback_query(F.data == "god_clear_market")
async def god_clear_market(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import clear_market_listings_admin
    count = await clear_market_listings_admin()
    await callback.answer(f"🛒 Bozordagi barcha {count} ta faol listinglar bekor qilindi!", show_alert=True)
    await open_owner_god_menu_p2(callback)

# 1.10 QAL'ALARNI NEYTRAL QILISH
@owner_router.callback_query(F.data == "god_reset_castles")
async def god_reset_castles(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
    from database.db import get_connection
    async with get_connection() as db:
        await db.execute("UPDATE castles SET owner_guild_id = NULL")
        await db.commit()
    await callback.answer("🏰 Barcha 3 ta qadimiy qal'a neytral holatga qaytarildi!", show_alert=True)
    await open_owner_god_menu_p2(callback)

# 2. GOD-STATS (99,999 HP / 999 STR)
@owner_router.callback_query(F.data == "god_max_stats")
async def set_owner_god_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await update_character(
        char["id"],
        hp=99999, max_hp=99999,
        stamina=9999, max_stamina=9999,
        strength=999, agility=999, constitution=999, intelligence=999
    )
    await callback.answer("⚡️ OLIY YARATUVCHI QUDRATI YOQILDI!\nHP: 99,999 | Kuch: 999 | Himoya: 999", show_alert=True)
    await open_owner_god_menu(callback)

# 3. AFSONAVIY YARATUVCHI QILICHI (+999 ATK)
@owner_router.callback_query(F.data == "god_spawn_sword")
async def spawn_god_sword(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
        VALUES (?, 'weapon', '👑 Valoriya Yaratuvchisining Qonli Qilichi', 'mythic', 999, 150, 9999, 9999, 1);
        """, (char["id"],))
        await db.commit()
        
    await callback.answer("🗡 'Yaratuvchining Qonli Qilichi' (+999 Zarba) yaratildi va qo'lingizga berildi!", show_alert=True)

# 4. DAXLSIZLIK QALQONI (+999 DEF)
@owner_router.callback_query(F.data == "god_spawn_shield")
async def spawn_god_shield(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
        VALUES (?, 'shield', '🛡 Valoriya Daxlsizlik Qalqoni', 'mythic', 50, 999, 9999, 9999, 1);
        """, (char["id"],))
        await db.commit()
        
    await callback.answer("🛡 'Valoriya Daxlsizlik Qalqoni' (+999 Himoya) yaratildi va taqildi!", show_alert=True)

# 5. QONLI OY (BLOOD MOON)
@owner_router.callback_query(F.data == "god_blood_moon")
async def trigger_blood_moon(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_blood_moon", "Qonli oy hodisasi boshlanishidan oldingi snapshot")
    
    # Barcha guruhlarga xabar
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🩸 *DIQQAT! VALORIYA OSMONIDA QONLI OY YOQILDI!* 🩸\n\n"
                "Osmon qip-qizil tusga kirdi! Barcha Berserklarning zarbasi 2 barobar oshirildi! Qabrlardan sharpalar uyg'onmoqda!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🩸 Qonli Oy butun dunyoda yoqildi va guruhlarga e'lon qilindi!", show_alert=True)

# 6. AJDAHO REYDI
@owner_router.callback_query(F.data == "god_dragon_raid")
async def trigger_dragon_raid(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_dragon_raid", "Ajdaho reydi chaqirilishidan oldingi snapshot")
    
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🐉 *AFSONAVIY ZANGORI AJDAHO IGNIS OSMONDAN TUSHDI!* 🐉\n\n"
                "Oliy Yaratuvchi farmoni bilan ulkan reyd boshlandi! Jang qilish uchun `!boss` deb yozing!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🐉 Ajdaho reydi butun qit'ada faollashtirildi!", show_alert=True)

# 7. OLTIN YOMG'IRI (2x LOOT)
@owner_router.callback_query(F.data == "god_golden_rain")
async def trigger_golden_rain(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🌧 *OLTIN YOMG'IRI HODISASI BOSHLANDI!* 🪙\n\n"
                "Osmonlardan oltin tangalar yog'moqda! Bugun barcha janglarda o'ljalar 2 barobar ko'p beriladi!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🌧 Oltin yomg'iri hodisasi barcha guruhlarda yoqildi!", show_alert=True)

# 8. METEOR BO'RONI (OFAT)
@owner_router.callback_query(F.data == "god_meteor_storm")
async def trigger_meteor_storm(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("pre_meteor_storm", "Meteor bo'roni oldingi snapshot")
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "☄️ *OSMONDAN ALANGALI METEORITLAR QULAMOQDA!* ☄️\n\n"
                "Valoriya zaminini osmon toshlari larzaga keltirdi! Qal'alar titramoqda, qalqonlaringizni mahkam tuting!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("☄️ Meteor bo'roni dunyoga yo'naltirildi!", show_alert=True)

# 9. BARCHA RITSARLARGA AIRDROP (+500 Oltin)
@owner_router.callback_query(F.data == "god_airdrop_all")
async def trigger_global_airdrop(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await give_global_airdrop(500)
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "🎁 *YARATUVCHIDAN BUTUN VALORIYAGA GLOBAL AIRDROP!* 🎁\n\n"
                "Oliy Yaratuvchi @NAKAMA_02 saxovati bilan barcha ritsarlarning xazinasiga **+500 Tillo Tanga** hadya etildi!\n"
                "Valoriya taxti nomidan qasamyodingiz mustahkam bo'lsin!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("🎁 Barcha o'yinchilarga +500 Oltin tarqatildi va e'lon qilindi!", show_alert=True)

# 10. BARCHA GURUHLARGA YARATUVCHI E'LONI
@owner_router.callback_query(F.data == "god_broadcast_all")
async def trigger_god_broadcast(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    groups = await get_active_groups()
    for g in groups:
        try:
            await callback.bot.send_message(
                g["chat_id"],
                "📢 *VALORIYA YARATUVCHISI @NAKAMA_02 OLAMSHUMUL FARMONI!* 👑\n\n"
                "\"Ey 12 ta imperiya hukmdorlari va qit'aning barcha ritsarlari!\n"
                "Qilichlaringizni ko'taring, chunki shon-sharaf faqat jang maydonida qon to'kkanlarga nasib qiladi!\n"
                "Valoriya qonunlari mening irodam bilan mustahkamdir!\"",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer("📢 Oliy Yaratuvchi e'loni barcha guruhlarga yuborildi!", show_alert=True)

# 11. DUNYO TELEMETRIYASI
@owner_router.callback_query(F.data == "god_inspect")
async def inspect_world_telemetry(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    telem = await get_world_telemetry()
    text = (
        "📊 *VALORIYA BUTUN DUNYO TELEMETRIYASI* 📊\n\n"
        f"👥 Jami Ro'yxatdan O'tgan Ritsarlar: *{telem['total_chars']} ta*\n"
        f"🏰 Faol Ulangan Guruhlar: *{telem['total_groups']} ta*\n"
        f"⚔️ Yaratilgan Qurol va Sovutlar: *{telem['total_items']} ta*\n\n"
        f"💰 O'yinchilar Qo'lidagi Jami Oltin: *{telem['total_player_gold']:,} 🪙*\n"
        f"🏛 12 Imperiya Xazinasidagi Jami Oltin: *{telem['total_kingdom_gold']:,} 🪙*\n\n"
        "🛡 Barcha relyatsion jadvallar va server parametrlari 100% barqaror ishlamoqda."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=owner_god_mode_keyboard())

# 12. YANGI SNAPSHOT SAQLASH
@owner_router.callback_query(F.data == "god_save_snapshot")
async def manual_save_snapshot(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await create_world_snapshot("manual_owner_backup", "Owner tomonidan olingan to'liq xavfsiz zaxira nusxasi")
    await callback.answer("💾 Dunyo holati va barcha o'yinchilar ma'lumoti to'liq arxivlandi!", show_alert=True)

# 13. ROLLBACK QILISH
@owner_router.callback_query(F.data == "god_rollback")
async def trigger_rollback(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    await callback.answer("⏪ Dunyo xavfsiz snapshotga qaytarildi!", show_alert=True)
    await callback.message.edit_text(
        "✅ *ROLLBACK MUVAFFAQIYATLI BAJARILDI!* ✅\n\n"
        "Dunyodagi barcha parametrlar va iqtisodiy oqimlar oxirgi barqaror holatga qaytarildi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

# =====================================================================
# 14. O'YINCHILARNI BOSHQARISH YO'RIQNOMASI
# =====================================================================
@owner_router.callback_query(F.data == "god_player_mgmt_guide")
async def show_player_mgmt_guide(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return
        
    text = (
        "👤 *O'YINCHILARNI BOSHQARISH VA QAZO (ADMIN) VOSITALARI* 👑\n\n"
        "Siz istalgan guruhda yoki shaxsiy chatda o'yinchining xabariga **Reply** qilib yoki uning `@username`ini yozib boshqarishingiz mumkin:\n\n"
        "💰 *Pul Berish:*\n"
        "`/give_gold @username 5000` *(yoki reply qilib: `/give_gold 5000`)*\n\n"
        "💸 *Pul Olish (Tortib olish):*\n"
        "`/take_gold @username 2000`\n\n"
        "🗡 *Afsonaviy Qurol Berish:*\n"
        "`/give_item @username Afsonaviy Zangori Qilich`\n\n"
        "👑 *Daraja Berish / O'zgartirish:*\n"
        "`/set_level @username 15`\n\n"
        "⛓ *Zindonga Tashlash (Muzlatish):*\n"
        "`/jail @username`\n\n"
        "🕊 *Zindondan Ozod Qilish:*\n"
        "`/unjail @username`"
    )
    buttons = [[InlineKeyboardButton(text="⬅️ God-Mode Panel", callback_data="menu_owner_god")]]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================================
# 15. ADMIN KOMANDALARI: PUL VA BUYUM BOSHQARUVI
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_gold|ber_oltin|pul_ber)"))
async def admin_give_gold(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    amount = 1000
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_ident = args[1]
        amount = int(args[2])
        target_char = await get_character_by_identifier(target_ident)
    elif len(args) == 2 and args[1].isdigit():
        target_char = char
        amount = int(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/give_gold @username 5000` yoki reply qilib `/give_gold 5000`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], gold=target_char["gold"] + amount)
    await message.reply(
        f"💰 *OLTIN IN'OM ETILDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* xazinasiga **+{amount:,} Oltin** berildi!\n"
        f"Hozirgi balansi: *{target_char['gold'] + amount:,} 🪙*",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(take_gold|ol_oltin|pul_ol)"))
async def admin_take_gold(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    amount = 500
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_ident = args[1]
        amount = int(args[2])
        target_char = await get_character_by_identifier(target_ident)
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/take_gold @username 2000`", parse_mode="Markdown")
        return
        
    new_gold = max(0, target_char["gold"] - amount)
    await update_character(target_char["id"], gold=new_gold)
    await message.reply(
        f"💸 *OLTIN TORTIB OLINDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* xazinasidan **-{amount:,} Oltin** musodara qilindi!\n"
        f"Qolgan balansi: *{new_gold:,} 🪙*",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(give_item|ber_qurol|buyum)"))
async def admin_give_item(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    item_name = "Afsonaviy Olovli Qilich"
    args = message.text.split(maxsplit=2)
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1:
            item_name = " ".join(args[1:])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        item_name = args[2]
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/give_item @username Afsonaviy Qilich`", parse_mode="Markdown")
        return
        
    await give_player_item(target_char["id"], item_name=item_name, slot_type="weapon", attack=180, defense=40, rarity="mythic")
    await message.reply(
        f"🗡 *AFSONAVIY BUYUM SOVG'A QILINDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* ga yangi qurol berildi:\n"
        f"✨ *'{item_name}'* (Mifik daraja, +180 Zarba)!\n"
        f"Buyum uning anjomlar ro'yxatiga qo'shildi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(set_level|daraja)"))
async def admin_set_level(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    lvl = 10
    args = message.text.split()
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1 and args[1].isdigit():
            lvl = int(args[1])
    elif len(args) >= 3 and args[2].isdigit():
        target_char = await get_character_by_identifier(args[1])
        lvl = int(args[2])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/set_level @username 15`", parse_mode="Markdown")
        return
        
    await update_character(
        target_char["id"],
        level=lvl,
        hp=100 + (lvl * 25), max_hp=100 + (lvl * 25),
        strength=15 + (lvl * 5), constitution=10 + (lvl * 4)
    )
    await message.reply(
        f"👑 *RITSAR DARAJA KO'TARILDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* darajasi to'g'ridan-to'g'ri *{lvl}-Daraja*ga o'rnatildi!\n"
        f"Uning joni va kuch parametrlari yangilandi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(jail|zindonga)"))
async def admin_jail_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/jail @username`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], is_jailed=1)
    await message.reply(
        f"⛓ *RITSAR ZINDONGA TASHLANDI!* ⛓\n\n"
        f"Ritsar *{target_char['name']}* Oliy Yaratuvchi g'azabiga uchradi va Qirollik Zindoniga zanjirband qilindi!\n"
        f"U Yaratuvchi kechirmagunicha harakat qila olmaydi.",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(unjail|ozod)"))
async def admin_unjail_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish:\n`/unjail @username`", parse_mode="Markdown")
        return
        
    await update_character(target_char["id"], is_jailed=0)
    await message.reply(
        f"🕊 *RITSAR ZINDONDAN OZOD QILINDI!* 🕊\n\n"
        f"Ritsar *{target_char['name']}* Yaratuvchining saxovati va marhamati bilan zindondan ozod etildi!",
        parse_mode="Markdown"
    )

# =====================================================================
# MAJBURIY KANAL SOZLAMASI (/set_channel, /remove_channel)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(set_channel|kanal_quying)"))
async def admin_set_channel(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Kanal ko'rsatilmadi! Foydalanish:\n`/set_channel @kanal_usernami`", parse_mode="Markdown")
        return
        
    channel = args[1].strip()
    await set_setting("required_channel", channel)
    await message.reply(
        f"📢 *MAJBURIY KANAL O'RNATILDI!* 👑\n\n"
        f"Endi botdan foydalanish uchun barcha o'yinchilar *{channel}* kanaliga a'zo bo'lishi shart qilib belgilandi!\n\n"
        f"⚠️ *Muhim Eslatma:* Bot ushbu kanalda **Administrator** bo'lishi shart (a'zolikni tekshira olishi uchun).",
        parse_mode="Markdown"
    )

@owner_router.message(F.text.regexp(r"^(!|\/)(remove_channel|kanalni_ochir)"))
async def admin_remove_channel(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    await set_setting("required_channel", "")
    await message.reply("📢 *Majburiy kanal a'zoligi talabi o'chirildi!* Endi hamma erkin kira oladi.", parse_mode="Markdown")


# =====================================================================
# 16. CHAQMOQ VA JAZO: SMITE (/kill, !chaqmoq, !ur)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(kill|chaqmoq|ur)"))
async def admin_smite_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/kill @username` yoki reply qilib `/kill`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], hp=1, stamina=0)
    await message.reply(
        f"⚡️ *OSMON CHAQMOG'I URILDI!* ⚡️\n\n"
        f"Oliy Yaratuvchi barmog'ini silkitishi bilan osmondan moviy chaqmoq tushdi!\n"
        f"Ritsar *{target_char['name']}* hushidan ketib yerga quladi! (Jon: 1/1 HP)",
        parse_mode="Markdown"
    )

# =====================================================================
# 17. TO'LIQ DAVOLASH: HEAL (/heal, !jon, !tuzat)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(heal|jon|tuzat)"))
async def admin_heal_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
    else:
        target_char = char
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/heal @username`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], hp=target_char["max_hp"], stamina=target_char["max_stamina"], wounds_json="[]")
    await message.reply(
        f"✨ *ILOHIY DAVOLASH MO''JIZASI!* ✨\n\n"
        f"Ritsar *{target_char['name']}* ustiga ilohiy nur yog'ildi!\n"
        f"Barcha jarohatlar bitdi, jon va charchoq 100% to'liq tiklandi! (❤️ {target_char['max_hp']}/{target_char['max_hp']} HP)",
        parse_mode="Markdown"
    )

# =====================================================================
# 18. QUROLSIZLANTIRISH / SOVUTLARNI YECHISH (/strip, !yech)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(strip|yech)"))
async def admin_strip_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/strip @username`", parse_mode="Markdown")
        return

    await strip_player_equipment(target_char["id"])
    await message.reply(
        f"🪓 *RITSAR QUROLSIZLANTIRILDI!* 🪓\n\n"
        f"Ritsar *{target_char['name']}* ning barcha qurollari, sovutlari va qalqonlari tortib olindi!\n"
        f"U maydonda yalangoyoq holda qoldi.",
        parse_mode="Markdown"
    )

# =====================================================================
# 19. ISM O'ZGARTIRISH / TROLL NOM BERISH (/rename, !nom, !laqab)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(rename|nom|laqab)"))
async def admin_rename_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    new_name = "Eshakboqar Ritsar"
    args = message.text.split(maxsplit=2)
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1:
            new_name = " ".join(args[1:])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        new_name = args[2]
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/rename @username Yangi Ism`", parse_mode="Markdown")
        return

    old_name = target_char["name"]
    await update_character(target_char["id"], name=new_name)
    await message.reply(
        f"🏷 *RITSAR ISMI O'ZGARTIRILDI!* 👑\n\n"
        f"Oldingi ism: *{old_name}*\n"
        f"Yangi qirollik ismi: *{new_name}* deb rasman e'lon qilindi!",
        parse_mode="Markdown"
    )

# =====================================================================
# 20. AFSONAVIY TULPOR SOVG'A QILISH (/give_horse, !tulpor)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_horse|tulpor)"))
async def admin_give_horse(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    horse_name = "Qanotli Pegas"
    args = message.text.split(maxsplit=2)
    
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
        if len(args) > 1:
            horse_name = " ".join(args[1:])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        horse_name = args[2]
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/give_horse @username Qanotli Bo'ron`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], horse_name=horse_name, horse_bond=100)
    await message.reply(
        f"🐴 *SHOHONA TULPOR SOVG'A QILINDI!* 👑\n\n"
        f"Ritsar *{target_char['name']}* ga afsonaviy *'{horse_name}'* (Sadoqat: 100%) sovg'a qilindi!",
        parse_mode="Markdown"
    )

# =====================================================================
# 21. ILOHIY BARAKA (2X STAT BUFF) (/bless, !baraka)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(bless|baraka)"))
async def admin_bless_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/bless @username`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], buff_multiplier=2.0)
    await message.reply(
        f"🌟 *ILOHIY BARAKA IN'OM ETILDI!* 🌟\n\n"
        f"Ritsar *{target_char['name']}* ga Yaratuvchi barakasi berildi: Barcha janglarda **2x Zarba va Himoya** kuchiga ega bo'ldi!",
        parse_mode="Markdown"
    )

# =====================================================================
# 22. QORA LA'NAT (0.5X STAT DEBUFF) (/curse, !lanat)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(curse|lanat)"))
async def admin_curse_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/curse @username`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], buff_multiplier=0.5)
    await message.reply(
        f"💀 *QORA LA'NAT YOG'ILDI!* 💀\n\n"
        f"Ritsar *{target_char['name']}* qora sehr bilan la'natlandi: Uning qudrati 50% ga zaiflashtirildi!",
        parse_mode="Markdown"
    )

# =====================================================================
# 23. SUKUT SAQLASH / CHATDAN TO'SIQ (/mute, !jim, /unmute, !gapir)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(mute|jim)"))
async def admin_mute_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/mute @username`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], is_muted=1)
    await message.reply(f"🔇 *Ritsar {target_char['name']} ga sukut saqlash amri berildi!* Bot uning xabarlariga javob bermaydi.", parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(unmute|gapir_ber)"))
async def admin_unmute_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/unmute @username`", parse_mode="Markdown")
        return

    await update_character(target_char["id"], is_muted=0)
    await message.reply(f"🔊 *Ritsar {target_char['name']} ga yana so'zlash huquqi berildi!*", parse_mode="Markdown")

# =====================================================================
# 24. PROFILNI TO'LIQ NOLGA TUSHIRISH (/wipe_user, !reset, !nolga)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(wipe_user|reset|nolga)"))
async def admin_wipe_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    target_char = None
    args = message.text.split()
    if message.reply_to_message:
        target_uid = message.reply_to_message.from_user.id
        target_char = await get_character_by_user_id(target_uid)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        
    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `/wipe_user @username`", parse_mode="Markdown")
        return

    await reset_player_character(target_char["id"])
    await message.reply(
        f"💥 *PROFIL TO'LIQ NOLGA TUSHIRILDI!* 💥\n\n"
        f"Ritsar *{target_char['name']}* ning barcha darajasi, qurollari va xazinasi tozalab tashlandi (1-Daraja, 100 Oltin).",
        parse_mode="Markdown"
    )

# =====================================================================
# 25. GLOBAL QIROLLIKLAR URUSHI BOSHLASH (/start_war, !urush)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(start_war|urush)"))
async def admin_start_kingdom_war(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    groups = await get_active_groups()
    for g in groups:
        try:
            await message.bot.send_message(
                g["chat_id"],
                "⚔️ *QIT'ADA BUYUK QIROLLIKLAR URUSHI BOSHLANDI!* ⚔️\n\n"
                "🏰 Imperator Valter V va Sulton Arslonxon o'rtasida qonli to'qnashuv boshlandi!\n"
                "Barcha ritsarlar o'z imperiyasi uchun qon to'kishga chaqiriladi! `!duel` deb yozing!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await message.reply("⚔️ Barcha guruhlarda Buyuk Urush e'lon qilindi!", parse_mode="Markdown")

# =====================================================================
# 26. GLOBAL QIROLLIK YARMARKASI (/start_fair, !yarmarka)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(start_fair|yarmarka)"))
async def admin_start_fair(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    groups = await get_active_groups()
    for g in groups:
        try:
            await message.bot.send_message(
                g["chat_id"],
                "🎪 *VALORIYA BUYUK QIROLLIK YARMARKASI BOSHLANDI!* 🎪\n\n"
                "Barcha tavernalarda ichimliklar va taomlar bepul, auksion soliqlari 0% ga tushirildi!\n"
                "Bayram sharafiga har bir mehmonga xushxabar!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await message.reply("🎪 Buyuk Yarmarka festivali butun qit'ada yoqildi!", parse_mode="Markdown")

# =====================================================================
# 27. JAVOHIR BERISH VA OLISH (!give_gems, !take_gems, !ber_javohir, !ol_javohir)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_gems|ber_javohir)"))
async def admin_give_gems(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    amount = 10
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        if len(args) >= 2 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        if args[2].isdigit():
            amount = int(args[2])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `!give_gems @username 20`", parse_mode="Markdown")
        return

    from database.db import give_player_gems
    new_gems = await give_player_gems(target_char["id"], amount)
    await message.reply(f"💎 *JAVOHIR HADYA ETILDI!* Ritsar *{target_char['name']}* ga +{amount} 💎 Javohir berildi! (Jami: {new_gems} 💎)", parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(take_gems|ol_javohir)"))
async def admin_take_gems(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    amount = 10
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        if len(args) >= 2 and args[1].isdigit():
            amount = int(args[1])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        if args[2].isdigit():
            amount = int(args[2])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `!take_gems @username 10`", parse_mode="Markdown")
        return

    from database.db import give_player_gems
    new_gems = await give_player_gems(target_char["id"], -amount)
    await message.reply(f"💎 *JAVOHIR MUSODARA QILINDI!* Ritsar *{target_char['name']}* dan -{amount} 💎 olindi! (Qoldiq: {new_gems} 💎)", parse_mode="Markdown")

# =====================================================================
# 28. ELEMENTAR RUNA BERISH (!give_rune, !ber_runa)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_rune|ber_runa)"))
async def admin_give_rune(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    rune_type = "fire_rune"
    qty = 1

    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        if len(args) >= 2:
            r = args[1].lower()
            rune_type = "fire_rune" if "olov" in r or "fire" in r else ("frost_rune" if "muz" in r or "frost" in r else "lightning_rune")
        if len(args) >= 3 and args[2].isdigit():
            qty = int(args[2])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        r = args[2].lower()
        rune_type = "fire_rune" if "olov" in r or "fire" in r else ("frost_rune" if "muz" in r or "frost" in r else "lightning_rune")
        if len(args) >= 4 and args[3].isdigit():
            qty = int(args[3])

    if not target_char:
        await message.reply("❌ Foydalanish: `!give_rune @username [fire|frost|lightning] [soni]`", parse_mode="Markdown")
        return

    from database.db import give_player_runes, RUNES_DATA
    await give_player_runes(target_char["id"], rune_type, qty)
    await message.reply(f"🔮 *RUNA BERILDI!* Ritsar *{target_char['name']}* ga +{qty}x {RUNES_DATA[rune_type]['name']} hadya qilindi!", parse_mode="Markdown")

# =====================================================================
# 29. QIROLLIK TAXTINI TOPSHIRISH VA AG'DARISH (!make_king, !dethrone, !qirol_qil, !taxtdan_ur)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(make_king|qirol_qil)"))
async def admin_make_king(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `!make_king @username`", parse_mode="Markdown")
        return

    from database.db import make_player_king, get_active_groups
    ok, msg = await make_player_king(target_char["id"])
    groups = await get_active_groups()
    for g in groups:
        try:
            await message.bot.send_message(
                g["chat_id"],
                f"👑 *YANGI QIROLIY FARMON!* 👑\n\n"
                f"Oliy Yaratuvchi irodasi bilan ritsar *{target_char['name']}* Valoriya Qiroli deb e'lon qilindi! Oltin Toj uning boshiga kiydirildi!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await message.reply(msg, parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(dethrone|taxtdan_ur|taxtdan_ol)"))
async def admin_dethrone(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    from database.db import dethrone_current_king
    ok, msg = await dethrone_current_king()
    await message.reply(msg, parse_mode="Markdown")

# =====================================================================
# 30. JAROHAT BERISH VA TO'LIQ DAVOLASH (!wound, !cure_all, !jarohatla)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(wound|jarohatla)"))
async def admin_wound_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    wound = "broken_ribs"
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        if len(args) >= 2:
            wound = args[1]
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])
        if len(args) >= 3:
            wound = args[2]

    if not target_char:
        await message.reply("❌ Foydalanish: `!wound @username [broken_ribs|deep_gash|concussion]`", parse_mode="Markdown")
        return

    from database.db import give_player_wound
    from game.dark_engine import WOUND_TYPES
    w_name = WOUND_TYPES.get(wound, {}).get("name", wound)
    await give_player_wound(target_char["id"], wound)
    await message.reply(f"🩸 *OG'IR TRAVMA YETKAZILDI!* Ritsar *{target_char['name']}* ga [{w_name}] jarohati yuklandi!", parse_mode="Markdown")

# =====================================================================
# 31. AQL VA TELBALIK BOSHQARUVI (!sanity, !aql, !telba_qil)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(telba_qil)"))
async def admin_insane_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi!", parse_mode="Markdown")
        return

    from database.db import set_player_sanity
    await set_player_sanity(target_char["id"], 0)
    await message.reply(f"🧠💀 *MUTLAQ TELBALIK!* Ritsar *{target_char['name']}* ning Sanity ko'rsatkichi 0% ga tushirildi! U janglarda vasvasaga tushadi!", parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(sanity|aql)"))
async def admin_set_sanity(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    val = 100
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        if len(args) >= 2 and args[1].isdigit():
            val = int(args[1])
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        if args[2].isdigit():
            val = int(args[2])

    if not target_char:
        await message.reply("❌ Foydalanish: `!sanity @username 100`", parse_mode="Markdown")
        return

    from database.db import set_player_sanity
    await set_player_sanity(target_char["id"], val)
    await message.reply(f"🧠 Ritsar *{target_char['name']}* ning Sanity ko'rsatkichi {val}% qilib belgilandi!", parse_mode="Markdown")

# =====================================================================
# 32. IBLIS AHDINI MAJBURLASH YOKI TOZALASH (!give_pact, !cleanse_pact)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(give_pact|ahd_ber)"))
async def admin_give_pact(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi!", parse_mode="Markdown")
        return

    await update_character(target_char["id"], bloodline_trait="demon_pact")
    await message.reply(f"🩸 *ZULMAT AHDIGA BOG'LANDI!* Ritsar *{target_char['name']}* ga Morvath Iblis Ahdi yuklandi (+45 ATK, 20% Lifesteal)!", parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(cleanse_pact|ahdni_bekor_qil)"))
async def admin_cleanse_pact(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi!", parse_mode="Markdown")
        return

    await update_character(target_char["id"], bloodline_trait="noble_blood")
    await message.reply(f"🌟 *ZULMATDAN POKLANDI!* Ritsar *{target_char['name']}* iblis ahdidan to'liq ozod qilindi!", parse_mode="Markdown")

# =====================================================================
# 33. GILDIYA VA QAL'ALARNI BOSHQARISH (!disband_guild, !give_guild_gold, !set_castle)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(disband_guild|gildiyani_yop)"))
async def admin_disband_guild(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ Foydalanish: `!disband_guild [Gildiya Nomi]`", parse_mode="Markdown")
        return

    from database.db import disband_guild_by_name
    ok, msg = await disband_guild_by_name(args[1])
    await message.reply(msg, parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(give_guild_gold|gildiyaga_oltin)"))
async def admin_give_guild_gold(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply("❌ Foydalanish: `!give_guild_gold [Gildiya_Nomi] [oltin]`", parse_mode="Markdown")
        return

    g_name = args[1]
    amount = int(args[2]) if args[2].isdigit() else 5000
    from database.db import give_guild_gold_by_name
    ok, msg = await give_guild_gold_by_name(g_name, amount)
    await message.reply(msg, parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(set_castle|qala_egasi)"))
async def admin_set_castle(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("❌ Foydalanish: `!set_castle [black_stone|iron_fort|golden_rock] [Gildiya Nomi|none]`", parse_mode="Markdown")
        return

    castle_id = args[1]
    guild_name = args[2]
    from database.db import assign_castle_owner_by_id
    ok, msg = await assign_castle_owner_by_id(castle_id, guild_name)
    await message.reply(msg, parse_mode="Markdown")

# =====================================================================
# 34. KVESTLAR VA YUTUQLARNI AVTO-OCHISH (!finish_quests, !unlock_achievements)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(finish_quests|kvestni_bajar)"))
async def admin_finish_quests(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        target_char = char

    from database.db import complete_all_daily_quests_admin
    await complete_all_daily_quests_admin(target_char["id"])
    await message.reply(f"📜 *KVESTLAR TO'LIQ BAJARILDI!* Ritsar *{target_char['name']}* bugungi barcha kvestlarni 100% bajardi deb belgilandi!", parse_mode="Markdown")

@owner_router.message(F.text.regexp(r"^(!|\/)(unlock_achievements|yutuqlarni_och)"))
async def admin_unlock_all_achievements(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        target_char = char

    from database.db import unlock_all_player_achievements
    count = await unlock_all_player_achievements(target_char["id"])
    await message.reply(f"🏆 *BARCHA {count} TA YUTUQLAR BERILDI!* Ritsar *{target_char['name']}* barcha medallarga sazovor bo'ldi!", parse_mode="Markdown")

# =====================================================================
# 35. RENTGEN VA KUZATUV (!spy, !kuzat, !rentgen)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(spy|kuzat|rentgen)"))
async def admin_spy_player(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split()
    target_char = None
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
    elif len(args) >= 2:
        target_char = await get_character_by_identifier(args[1])

    if not target_char:
        await message.reply("❌ O'yinchi topilmadi! Foydalanish: `!spy @username`", parse_mode="Markdown")
        return

    from database.db import get_character_equipment, get_runes_inventory, get_trade_inventory
    eq = await get_character_equipment(target_char["id"])
    runes = await get_runes_inventory(target_char["id"])
    trade = await get_trade_inventory(target_char["id"])

    gear_str = ", ".join([e["item_name"] for e in eq if e.get("is_equipped") == 1]) or "Hech narsa yo'q"
    runes_str = f"🔥{runes.get('fire_rune',0)} ❄️{runes.get('frost_rune',0)} ⚡️{runes.get('lightning_rune',0)}"

    text = (
        f"🕵️‍♂️ *RENTGEN MA'LUMOTNOMASI: {target_char['name']}* 🔍\n\n"
        f"🆔 ID: `{target_char['id']}` | Telegram ID: `{target_char['user_id']}`\n"
        f"👑 Daraja: {target_char['level']} | Kasb: {target_char['class_id'].upper()}\n"
        f"❤️ HP: {target_char['hp']}/{target_char['max_hp']} | ⚡️ Stamina: {target_char['stamina']}/100\n"
        f"🧠 Sanity: {target_char.get('sanity', 100)}% | Zulmat Ahdi: {target_char.get('bloodline_trait', 'noble_blood')}\n"
        f"💰 Xazina: {target_char['gold']:,} 🪙 | 💎 {target_char.get('gems', 0)}\n"
        f"⚔️ Duel: {target_char['wins']}G' / {target_char['losses']}M | 🎖 Shon: {target_char.get('honor', 0)}\n"
        f"🛡 Kiyingan anjomlar: {gear_str}\n"
        f"🔮 Runalar: {runes_str}\n"
        f"🐫 Karvon mollari: Ipak: {trade.get('silk',0)}, Ziravor: {trade.get('spices',0)}, Mo'yna: {trade.get('fur',0)}\n"
        f"🐴 Tulpor: {target_char.get('horse_name')} ({target_char.get('horse_bond')}%)"
    )
    await message.reply(text, parse_mode="Markdown")

# =====================================================================
# 36. BOT NOMIDAN SHAXSIY XABAR (DIRECT PM) (!pm, !lichka)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(pm|lichka)"))
async def admin_send_pm(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    args = message.text.split(maxsplit=2)
    target_char = None
    pm_text = ""
    if message.reply_to_message:
        target_char = await get_character_by_user_id(message.reply_to_message.from_user.id)
        pm_text = message.text.replace("!pm", "").replace("/pm", "").strip()
    elif len(args) >= 3:
        target_char = await get_character_by_identifier(args[1])
        pm_text = args[2]

    if not target_char or not pm_text:
        await message.reply("❌ Foydalanish: `!pm @username [xabar matni]`", parse_mode="Markdown")
        return

    try:
        await message.bot.send_message(
            target_char["user_id"],
            f"👑 *VALORIYA OLIY YARATUVCHISIDAN SHAXSIY FARMON:* ⚡️\n\n{pm_text}",
            parse_mode="Markdown"
        )
        await message.reply(f"📨 Xabar *{target_char['name']}* ning shaxsiy chatiga yetkazildi!", parse_mode="Markdown")
    except Exception as e:
        await message.reply(f"⚠️ Xabarni yuborib bo'lmadi (ehtimol botni bloklagan): {e}")

# =====================================================================
# 37. BOZORNI TOZALASH BUYRUG'I (!clear_market, !bozorni_tozala)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(clear_market|bozorni_tozala)"))
async def admin_cmd_clear_market(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    from database.db import clear_market_listings_admin
    count = await clear_market_listings_admin()
    await message.reply(f"🛒 Bozordagi barcha {count} ta listing bekor qilindi va tozalandi!", parse_mode="Markdown")

# =====================================================================
# 38. MASTER GOD-MODE YO'RIQNOMASI (/god_help, !god_help)
# =====================================================================
@owner_router.message(F.text.regexp(r"^(!|\/)(god_help|owner_help)"))
async def admin_master_help(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    char = await get_character_by_user_id(user_id)
    if not is_owner_authorized(user_id, username, char):
        return

    text = (
        "👑 *VALORIYA YARATUVCHISI (GOD-MODE) MASTER BUYRUQLAR KITOBI* 👑\n\n"
        "*(Har qanday buyruqni @username bilan yoki o'yinchining xabariga Reply qilib ishlatishingiz mumkin)*\n\n"
        "💰 **MOLIYAVIY VA IQTISODIY BOSHQARUV:**\n"
        "• `!give_gold @username [miqdor]` — Oltin berish\n"
        "• `!take_gold @username [miqdor]` — Oltin musodara qilish\n"
        "• `!give_gems @username [miqdor]` — Qimmatbaho javohir berish\n"
        "• `!take_gems @username [miqdor]` — Javohirni tortib olish\n"
        "• `!give_rune @username [fire|frost|lightning] [soni]` — Elementar runalar berish\n"
        "• `!clear_market` — Bozordagi barcha listinglarni tozalash\n\n"
        "👑 **TAXTI RAVON VA HUKUMRONLIK:**\n"
        "• `!make_king @username` — To'g'ridan-to'g'ri Valoriya Qiroli etib tayinlash!\n"
        "• `!dethrone` — Amaldagi qirolni taxtdan ag'darish\n"
        "• `!finish_quests @username` — Kundalik kvestlarni 100% bajarilgan qilish\n"
        "• `!unlock_achievements @username` — Barcha yutuq va medallarni berish\n\n"
        "🏰 **GILDIYA VA QAL'ALAR NAZORATI:**\n"
        "• `!disband_guild [Nomi]` — Gildiyani butunlay tarqatib yo'q qilish\n"
        "• `!give_guild_gold [Nomi] [miqdor]` — Gildiya xazinasiga oltin to'kish\n"
        "• `!set_castle [qal'a_id] [Gildiya|none]` — Qal'a egaligini o'zgartirish\n\n"
        "🗡 **QUROL VA SOVUTLAR:**\n"
        "• `!give_item @username [qurol]` — Afsonaviy/Mifik qurol yaratib berish\n"
        "• `!strip @username` — Barcha kiygan qurol/sovutlarini yechib olish\n"
        "• `!give_horse @username [nomi]` — 100% sadoqatli jangovar tulpor berish\n\n"
        "🩸 **ZULMAT TIZIMI VA TRAVMALAR:**\n"
        "• `!wound @username [broken_ribs|deep_gash]` — Og'ir travma yuklash\n"
        "• `!heal @username` — Jon va staminani to'ldirish, travmalarni davolash\n"
        "• `!sanity @username [0..100]` — Aql-hush ko'rsatkichini o'zgartirish\n"
        "• `!telba_qil @username` — Sanity 0% qilib telbaga aylantirish!\n"
        "• `!give_pact @username` — Morvath Iblis Ahdini majburlash\n"
        "• `!cleanse_pact @username` — Qonli ahd va la'natlardan poklash\n\n"
        "⚡️ **JAZO, HUJJAT VA KUZATUV:**\n"
        "• `!spy @username` — O'yinchining to'liq rentgen tahlili (X-Ray)\n"
        "• `!pm @username [matn]` — O'yinchining lichkasiga bot nomidan farmon yozish!\n"
        "• `!kill @username` — Chaqmoq bilan urib joni 1 HP qilish\n"
        "• `!bless @username` / `!curse @username` — Baraka yoki La'nat\n"
        "• `!jail @username [daqiqa]` / `!unjail @username` — Zindonga qamash/ozod qilish\n"
        "• `!mute @username` / `!unmute @username` — Chatda gapirishni bloklash\n"
        "• `!wipe_user @username` — Profilni to'liq 1-darajaga reset qilish\n\n"
        "🌍 **DUNYO HODISALARI:**\n"
        "• `!start_war` — Imperiyalar urushini boshlash\n"
        "• `!start_fair` — Butun qit'ada bepul yarmarka e'lon qilish"
    )
    await message.reply(text, parse_mode="Markdown")



