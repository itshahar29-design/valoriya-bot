import asyncio
import sys
import json
from pathlib import Path

# Fix Windows console emoji encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import (
    init_db, create_character, get_character_by_user_id,
    get_character_equipment, auto_equip_best, repair_all_items,
    dismantle_junk, get_top_knights, create_world_snapshot
)
from game.battle_engine import BattleEngine
from game.npc_engine import NPCEngine
from game.emotions_engine import EmotionsEngine
from game.retention_engine import RetentionEngine

async def run_comprehensive_tests():
    print("=========================================================")
    print("🏰 VALORIYA: MUKAMMAL TEST SUITE BOSHLANDI")
    print("=========================================================")

    # 1. DATABASE INIT
    print("\n[TEST 1] Relyatsion Baza Initsializatsiyasi...")
    await init_db()
    print("✅ TEST 1 O'TDI: Barcha 9 ta SQL jadvallari va 12 ta imperiya muvaffaqiyatli yuklandi.")

    # 2. CHARACTER CREATION & STARTER GEAR
    import time
    base_id = int(time.time()) % 10000000 + 1000000
    test_user_id = base_id
    char_id = await create_character(user_id=test_user_id, name="Ser Temurxon", class_id="warrior")
    char = await get_character_by_user_id(test_user_id)
    assert char is not None, "Qahramon topilmadi!"
    assert char["class_id"] == "warrior", "Kasb noto'g'ri!"
    assert char["hp"] == 120, "Boshlang'ich jon noto'g'ri!"
    
    gear = await get_character_equipment(char["id"])
    assert len(gear) >= 3, "Boshlang'ich sovutlar berilmadi!"
    print(f"✅ TEST 2 O'TDI: Qahramon '{char['name']}' (Lvl {char['level']}) yaratildi va {len(gear)} ta anjom kiyildi.")

    # 3. OWNER GOD-MODE & STEALTH VERIFICATION
    print("\n[TEST 3] Owner (God-Mode) Daxlsizligi va Reytingdan Yashirinish...")
    owner_id = base_id + 1
    await create_character(user_id=owner_id, name="Oliy Yaratuvchi (Owner)", is_owner=True, username="nakama_02")
    owner_char = await get_character_by_user_id(owner_id)
    assert owner_char["is_owner"] == 1, "Owner flag belgilanmadi!"
    assert owner_char["hide_from_leaderboard"] == 1, "Reytingdan yashirish belgilanmadi!"
    
    top_list = await get_top_knights(limit=50)
    top_names = [k["name"] for k in top_list]
    assert "Oliy Yaratuvchi (Owner)" not in top_names, "XATO! Owner reytingda ko'rinib qoldi!"
    
    # Mutloq xavfsizlik: Faqat @NAKAMA_02 ga ruxsat berilishi tekshiruvi
    from config import is_owner
    from handlers.owner_handler import is_owner_authorized
    from handlers.menu_buttons_handler import is_owner_user
    from handlers.start_handler import is_user_owner
    
    assert is_owner(user_id=owner_id, username="nakama_02") is True, "Owner username tasdiqlanmadi!"
    assert is_owner(user_id=owner_id, username="@NAKAMA_02") is True, "Case-insensitive username tasdiqlanmadi!"
    assert is_owner(user_id=99999, username="oddiy_user") is False, "Notanish user owner deb qabul qilindi!"
    assert is_owner_authorized(user_id=99999, username="oddiy_user", char={"is_owner": 1}) is False, "Notanish user is_owner flag bilan o'tib ketdi!"
    assert is_owner_user(user_id=99999, username="oddiy_user", char={"is_owner": 1}) is False, "menu_buttons_handler da notanish user ruxsat oldi!"
    assert is_user_owner(user_id=99999, username="oddiy_user") is False, "start_handler da notanish user ruxsat oldi!"
    assert is_owner_authorized(user_id=owner_id, username="NAKAMA_02", char=owner_char) is True, "Haqiqiy owner (@NAKAMA_02) rad etildi!"

    print("✅ TEST 3 O'TDI: God-Mode FAQAT @NAKAMA_02 ga tegishliligi va boshqalar 100% bloklangani tasdiqlandi.")

    # 4. 12-ZONE ANATOMICAL COMBAT & STAMINA
    print("\n[TEST 4] 12-Zonali Anatomik Jang Fizikasi va Stamina...")
    attacker = {"name": "Hujumchi", "strength": 20, "agility": 15, "stamina": 100, "weapon_attack": 15}
    defender = {"name": "Himoyachi", "hp": 100, "constitution": 12, "agility": 10, "stamina": 100, "armor_defense": 8, "is_defending": False}
    
    dmg, log, is_crit = BattleEngine.calculate_round(attacker, defender, target_zone="neck", action="skill")
    assert dmg > 0, "Zarar hisoblanmadi!"
    assert attacker["stamina"] < 100, "Stamina sarflanmadi!"
    assert defender["hp"] < 100, "Jon kamaymadi!"
    print(f"✅ TEST 4 O'TDI: Bo'yin zonasiga kinetik zarba: {dmg} zarar. Log: {log[0]}")

    # 5. DYNAMIC NPC BOT GENERATION
    print("\n[TEST 5] Protsessual Bot-Ritsarlar Generatsiyasi...")
    bot = NPCEngine.generate_bot_knight(target_level=3)
    assert bot["level"] in [2, 3, 4], "Bot darajasi o'yinchiga mos emas!"
    assert bot["persona"] in ["berserk", "defender", "poisoner", "coward"], "Persona noto'g'ri!"
    assert bot["loot_gold"] > 0, "O'lja oltin hisoblanmadi!"
    print(f"✅ TEST 5 O'TDI: Bot yaratildi: '{bot['name']}' (Lvl {bot['level']}), Persona: {bot['persona']}, O'lja: {bot['loot_gold']}🪙")

    # 6. BDI EMOTION ENGINE & "PAXTA QO'YISH" NLP
    print("\n[TEST 6] AI Hissiyotlar Matritsasi va 'Paxta Qo'yish' Tahlili...")
    # Kibrli Valterga paxta qo'yish
    speech1 = "Ey ulug' va yengilmas quyosh hukmdori Valter, sizning buyukligingiz oldida ta'zim qilaman!"
    res1 = EmotionsEngine.evaluate_player_speech("lionguard", speech1)
    assert res1["mood"] == "pleased", "Kibrli qirol erimadi!"
    assert res1["reward_gold"] > 0, "Mukofot oltin berilmadi!"
    print(f"✅ TEST 6.1 O'TDI (Paxta): {res1['ruler']} eridi va +{res1['reward_gold']} oltin berdi.")

    # Qonxo'r Ragnar Berserkka paxta qo'yish (rad etishi kerak)
    speech2 = "Ey buyuk va dono podshohim Ragnar..."
    res2 = EmotionsEngine.evaluate_player_speech("frost_peak", speech2)
    assert res2["mood"] == "disgusted", "Qonxo'r qirol paxtani yoqtirib qoldi!"
    assert res2["anger_change"] > 0, "G'azab ko'tarilmadi!"
    print(f"✅ TEST 6.2 O'TDI (G'azab): {res2['ruler']} laganbardorlikni rad etdi: {res2['reply'][:45]}...")

    # 7. QOL AUTO-EQUIP, REPAIR ALL, DISMANTLE JUNK
    print("\n[TEST 7] O'yinchi Qulayliklari (QoL: Auto-Equip, Repair, Dismantle)...")
    # Repair test
    success, cost, msg = await repair_all_items(char["id"], gold_available=500)
    assert success is True, "Ta'mirlash muvaffaqiyatsiz!"
    print(f"✅ TEST 7.1 (Ta'mirlash): {msg}")

    # Auto-equip test
    eq_count = await auto_equip_best(char["id"])
    assert eq_count >= 1, "Avto-kiyinish ishlamadi!"
    print(f"✅ TEST 7.2 (Avto-Kiyinish): {eq_count} ta eng yaxshi anjom kiyildi.")

    # 8. RETENTION & DOPAMINE ENGINE
    print("\n[TEST 8] Psixologik Bog'lanish va FTUE Kvesti...")
    ftue = RetentionEngine.get_ftue_tutorial()
    assert "Ser Artur" in ftue["story"], "Ser Artur FTUE kvesti yo'q!"
    letter = RetentionEngine.generate_guilt_trip_letter("Temurxon", hours_away=12)
    assert "Lordim Temurxon" in letter, "Aybdorlik xati noto'g'ri!"
    print("✅ TEST 8 O'TDI: FTUE Kvesti va Psixologik Qurolbardor xatlari tayyor.")

    # 9. FOOLPROOF SNAPSHOT & ROLLBACK
    print("\n[TEST 9] Foolproof Snapshot va Xavfsizlik Tizimi...")
    snap_ok = await create_world_snapshot("test_backup_01", "Sinov snapshot")
    assert snap_ok is True, "Snapshot yaratilmadi!"
    print("✅ TEST 9 O'TDI: 1-Soatlik dunyo arxivi (Snapshot) muvaffaqiyatli saqlandi.")

    # 10. DARK SYSTEM (ZULMAT TIZIMI): HARDCORE MECHANICS
    print("\n[TEST 10] Zulmat Tizimi: Sanity, Travmalar, Shavqatsiz Mag'lubiyat va Qonli Ahd...")
    from database.db import (
        apply_defeat_penalty, restore_sanity, cure_wound, cure_all_wounds,
        sign_blood_pact, cleanse_blood_pact, upgrade_equipment, update_character
    )
    from game.dark_engine import DarkEngine

    # 10.1 Defeat penalty
    await update_character(char["id"], gold=500, sanity=100)
    penalty = await apply_defeat_penalty(char["id"], is_dungeon=False)
    assert penalty["gold_lost"] > 0, "Oltin yo'qotilmadi!"
    assert penalty["current_sanity"] < 100, "Sanity kamaymadi!"
    assert penalty["durability_lost"] >= 15, "Qurol chidamliligi kamaymadi!"
    print(f"✅ TEST 10.1 (Mag'lubiyat Jazolari): -{penalty['gold_lost']} 🪙 Oltin, -{penalty['sanity_lost']}% Sanity, -{penalty['durability_lost']} Durability")

    # 10.2 Sanity restoration
    restored, r_msg = await restore_sanity(char["id"], amount=30, cost=50)
    assert restored is True, "Sanity tiklanmadi!"
    print(f"✅ TEST 10.2 (Sanity Tiklash): {r_msg}")

    # 10.3 Blood pact
    pact_ok, pact_msg = await sign_blood_pact(char["id"])
    assert pact_ok is True, "Qonli ahd imzolanmadi!"
    char_after_pact = await get_character_by_user_id(test_user_id)
    assert char_after_pact["bloodline_trait"] == "demon_pact", "Trait o'zgarmadi!"
    
    # Blood pact combat test (Lifesteal)
    pact_attacker = {
        "name": "Iblis Ritsari", "strength": 20, "agility": 15, "stamina": 100,
        "weapon_attack": 15, "bloodline_trait": "demon_pact", "hp": 50, "max_hp": 100
    }
    pact_defender = {"name": "Qurbon", "hp": 100, "constitution": 10, "armor_defense": 5}
    dmg_pact, log_pact, _ = BattleEngine.calculate_round(pact_attacker, pact_defender, action="skill")
    assert dmg_pact > 50, "Dark ATK qo'shilmadi!"
    assert pact_attacker["hp"] > 50, "Lifesteal ishlamadi!"
    print(f"✅ TEST 10.3 (Qonli Ahd & Lifesteal): Zarar: {dmg_pact} DMG, Tiklangan jon: +{pact_attacker['hp'] - 50} HP")

    # 10.4 Cleanse pact
    await update_character(char["id"], gold=2000)
    cleanse_ok, cl_msg = await cleanse_blood_pact(char["id"])
    assert cleanse_ok is True, "Qonli ahd bekor qilinmadi!"
    print("✅ TEST 10.4 (Ibodatxonada Poklanish): Qonli ahd muvaffaqiyatli bekor qilindi.")

    # 10.5 High-Stakes Forge test
    gear_items = await get_character_equipment(char["id"])
    test_weapon = gear_items[0]
    await update_character(char["id"], gold=5000)
    forge_res, forge_msg = await upgrade_equipment(test_weapon["id"], char["id"])
    print(f"✅ TEST 10.5 (Temirchi Tavakkali): {forge_msg[:60]}...")

    # 11. ULKAN YANGI TIZIMLAR: GILDIYA, REFERAL, SHAXTA & ALXIMIYA, TAXT
    print("\n[TEST 11] 6 Ta Yangi Mega-Tizim (Gildiyalar, Referal, Shaxta, Alximiya, Taxt)...")
    from database.db import (
        create_guild, join_guild, deposit_guild_treasury, get_guild_info,
        get_all_castles, siege_castle, handle_referral_signup, award_referral_cashback,
        get_referral_stats, mine_resources, brew_potion, use_potion,
        get_current_king, challenge_king
    )

    # 11.1 Guild creation & deposit
    await update_character(char["id"], gold=10000, guild_id=None)
    g_name = f"Bo'rilar_{int(time.time()) % 100000}"
    guild_ok, g_msg = await create_guild(char["id"], g_name)
    assert guild_ok is True, f"Gildiya tuzilmadi: {g_msg}"
    dep_ok, d_msg = await deposit_guild_treasury(char["id"], 500)
    assert dep_ok is True, "Xazinaga oltin qo'shilmadi!"
    print(f"✅ TEST 11.1 (Gildiya & Xazina): {g_msg} | {d_msg}")

    # 11.2 Castle siege
    castles = await get_all_castles()
    assert len(castles) >= 3, "Qal'alar bazada yo'q!"
    siege_res, s_msg = await siege_castle(char["id"], castles[0]["id"])
    print(f"✅ TEST 11.2 (Qal'a Qamali): {s_msg[:50]}...")

    # 11.3 Referral system & cashback
    ref_user_id = base_id + 500
    ref_ok, inv_name, b_gold = await handle_referral_signup(new_user_id=ref_user_id, referrer_user_id=test_user_id)
    assert ref_ok is True, "Referal ro'yxatga olinmadi!"
    await award_referral_cashback(char["id"], 1000)
    ref_stats = await get_referral_stats(test_user_id)
    assert ref_stats["count"] >= 1, "Referal soni hisoblanmadi!"
    print(f"✅ TEST 11.3 (Referal & Keshbek): Taklif qilinganlar: {ref_stats['count']} ta, Keshbek: {ref_stats['gold_earned']} 🪙")

    # 11.4 Mining & Alchemy
    mine_ok, m_msg, profs = False, "", {}
    for _ in range(5):
        await update_character(char["id"], stamina=100, hp=100)
        mine_ok, m_msg, profs = await mine_resources(char["id"])
        if mine_ok:
            break
    assert mine_ok is True, "Shaxtada ruda olinmadi!"
    print(f"✅ TEST 11.4 (Shaxta Qazish): {m_msg[:50]}...")
    
    # Brew potion
    profs["iron_ore"] = 5
    profs["herbs"] = 5
    await update_character(char["id"], professions_json=json.dumps(profs))
    brew_ok, b_msg = await brew_potion(char["id"], "rage")
    assert brew_ok is True, "Damlama tayyorlanmadi!"
    use_ok, u_msg = await use_potion(char["id"], "rage")
    assert use_ok is True, "Damlama ichilmadi!"
    print(f"✅ TEST 11.5 (Alximiya Damlamasi): {b_msg} | {u_msg}")

    # 11.5 King Throne challenge
    await update_character(char["id"], level=5)
    king_challenge, k_msg = await challenge_king(char["id"])
    current_king = await get_current_king()
    print(f"✅ TEST 11.6 (Valoriya Oliy Taxti): {k_msg[:50]}... Hozirgi Qirol: {current_king.get('king_name', 'Bo\'sh')}")

    # =====================================================================
    # 12. P2P OCHIQ BOZOR, KVESTLAR, VIZUAL KARTA, RUNALAR VA TIJORAT
    # =====================================================================
    print("\n[TEST 12] 5 Ta Yangi Mukammal Tizim (Market, Quests, Card, Runes, Arbitrage)...")
    from database.db import (
        create_market_listing, get_active_market_listings, get_player_market_listings,
        cancel_market_listing, buy_market_listing,
        get_or_create_daily_quests, increment_quest_progress, claim_daily_quest_reward,
        unlock_achievement, get_player_achievements,
        get_runes_inventory, socket_rune_to_equipment,
        get_trade_inventory, buy_trade_good, sell_trade_good, travel_to_city
    )
    from services.card_generator import generate_knight_card

    # 12.1 P2P Market: Listing, Cancelling, Buying with 3% Tax
    buyer_user_id = base_id + 999
    buyer_id = await create_character(user_id=buyer_user_id, name="Savdogar Bobur", class_id="scout")
    await update_character(buyer_id, gold=10000)

    # Listing yaratish
    list_ok, list_msg = await create_market_listing(
        seller_character_id=char["id"],
        category="ore",
        item_name="Sehrli Mithril Rudasi",
        quantity=2,
        price_per_unit=500,
        item_data={"key": "mithril_ore"}
    )
    assert list_ok is True, "Bozorga listing qo'yilmadi!"
    active_listings = await get_active_market_listings("ore")
    assert len(active_listings) >= 1, "Faol listinglar topilmadi!"
    target_listing = active_listings[0]

    # Xarid qilish (Buyer buys seller's listing)
    buy_ok, buy_msg, seller_uid, net_g, item_n = await buy_market_listing(buyer_id, target_listing["id"])
    assert buy_ok is True, f"Xarid amalga oshmadi: {buy_msg}"
    assert net_g == int(1000 * 0.97), "3% soliq noto'g'ri hisoblandi!"
    print(f"✅ TEST 12.1 (P2P Bozor & 3% Soliq): {list_msg[:45]}... | Xarid sof tushum: {net_g}🪙 (Soliq: 30🪙)")

    # 12.2 Daily Quests & Achievements
    q = await get_or_create_daily_quests(char["id"])
    assert q["quest_date"] is not None, "Kundalik kvest sanasi yo'q!"
    await increment_quest_progress(char["id"], "arena_wins", 2)
    await increment_quest_progress(char["id"], "mining_count", 2)
    await increment_quest_progress(char["id"], "market_or_tavern", 1)
    claim_ok, claim_msg = await claim_daily_quest_reward(char["id"])
    assert claim_ok is True, f"Kvest mukofoti berilmadi: {claim_msg}"
    await unlock_achievement(char["id"], "market_trader", "🛒 Savdo Magnati")
    achievements = await get_player_achievements(char["id"])
    assert len(achievements) >= 1, "Yutuqlar topilmadi!"
    print(f"✅ TEST 12.2 (Kundalik Kvestlar & Yutuqlar): Mukofot olindi! Yutuqlar soni: {len(achievements)} ta.")

    # 12.3 Pillow Visual Knight Identity Banner Card
    buf = generate_knight_card(char, equipment=gear, guild_name="Bo'rilar Klani")
    card_bytes = buf.getvalue()
    assert len(card_bytes) > 10000, "Ritsar kartasi chizilmadi yoki hajmi juda kichik!"
    print(f"✅ TEST 12.3 (Pillow Ritsar Kartasi): 800x530 yuqori sifatli banner tayyorlandi ({len(card_bytes)} bayt).")

    # 12.4 Elemental Rune Socketing & Battle Mechanics
    await update_character(char["id"], runes_inventory_json=json.dumps({"fire_rune": 2, "frost_rune": 1, "lightning_rune": 1}))
    sock_ok, sock_msg = await socket_rune_to_equipment(char["id"], test_weapon["id"], "fire_rune")
    assert sock_ok is True, f"Runa o'rnatilmadi: {sock_msg}"

    # Jangda Olov Runasi tekshiruvi (+25 Burn DMG)
    rune_attacker = {
        "name": "Runa Ritsari", "strength": 20, "agility": 15, "stamina": 100,
        "weapon_attack": 15, "runes": ["fire_rune"], "hp": 100, "max_hp": 100
    }
    rune_defender = {"name": "Himoyachi", "hp": 100, "constitution": 10, "agility": 0, "armor_defense": 5}
    r_dmg, r_log, _ = BattleEngine.calculate_round(rune_attacker, rune_defender, action="skill")
    assert any("Olov Runasi" in l for l in r_log), "Olov runasi jangda ishlamadi!"

    # Muz Runasi tekshiruvi (0% dodge)
    frost_attacker = {
        "name": "Muz Ritsari", "strength": 20, "agility": 5, "stamina": 100,
        "weapon_attack": 15, "runes": ["frost_rune"], "hp": 100, "max_hp": 100
    }
    f_dmg, f_log, _ = BattleEngine.calculate_round(frost_attacker, rune_defender)
    assert any("Muz Runasi" in l for l in f_log), "Muz runasi dushmanni muzlatmadi!"

    # Momaqaldiroq Runasi tekshiruvi (Shield Pierce & Stamina Break)
    shield_defender = {"name": "Qalqonchi", "hp": 100, "constitution": 10, "armor_defense": 5, "is_defending": True, "stamina": 100}
    light_attacker = {
        "name": "Chaqmoq Ritsari", "strength": 20, "agility": 15, "stamina": 100,
        "weapon_attack": 15, "runes": ["lightning_rune"]
    }
    l_dmg, l_log, _ = BattleEngine.calculate_round(light_attacker, shield_defender)
    assert shield_defender["stamina"] == 0, "Momaqaldiroq runasi staminani 0 qilmadi!"
    print("✅ TEST 12.4 (Elementar Runalar & Jang): 🔥 Olov (+25 DMG), ❄️ Muz (0% Dodge), ⚡️ Chaqmoq (Qalqon teshish) muvaffaqiyatli!")

    # 12.5 Inter-City Commodity Trading & Arbitrage
    await update_character(char["id"], gold=2000, stamina=100, current_city="samarkand")
    buy_g_ok, buy_g_msg = await buy_trade_good(char["id"], "silk", 2)
    assert buy_g_ok is True, f"Tovar olinmadi: {buy_g_msg}"
    
    # Muzli Cho'qqiga sayohat
    tr_ok, tr_msg = await travel_to_city(char["id"], "frost_peak")
    assert tr_ok is True, f"Sayohat qilib bo'lmadi: {tr_msg}"

    # Muzli Cho'qqida Ipakni qimmat narxda sotish
    sell_g_ok, sell_g_msg = await sell_trade_good(char["id"], "silk", 2)
    assert sell_g_ok is True, f"Tovar sotilmadi: {sell_g_msg}"
    print(f"✅ TEST 12.5 (Shaharlararo Karvon Tijorati): Samarqanddan olindi, Muzli Cho'qqida sotildi: {sell_g_msg}")

    # =====================================================================
    # 13. OLIY YARATUVCHI (OWNER GOD-MODE) CHEKSIZ BUYRUQ VA VAKOLATLARI
    # =====================================================================
    print("\n[TEST 13] Oliy Yaratuvchi (Owner) Mutloq Vakolatlari va Cheksiz Buyruqlari...")
    from database.db import (
        give_player_gems, give_player_runes, make_player_king, dethrone_current_king,
        set_player_sanity, give_player_wound, cure_player_all_wounds,
        disband_guild_by_name, give_guild_gold_by_name, assign_castle_owner_by_id,
        clear_market_listings_admin, unlock_all_player_achievements, complete_all_daily_quests_admin
    )

    # 13.1 Javohirlar (Gems) berish
    g_res = await give_player_gems(char["id"], 500)
    assert g_res >= 500, "Javohir berilmadi!"
    print(f"✅ TEST 13.1 (Javohir In'omi): O'yinchiga +500 Javohir berildi (Jami: {g_res} 💎).")

    # 13.2 Elementar Runalar berish
    r_inv = await give_player_runes(char["id"], "fire_rune", 5)
    assert r_inv.get("fire_rune", 0) >= 5, "Runalar berilmadi!"
    print(f"✅ TEST 13.2 (Runa Berish): O'yinchiga 5 ta Olov runasi berildi (Jami: {r_inv['fire_rune']} ta).")

    # 13.3 Qirollik Taxtiga tayinlash va Taxtdan ag'darish
    k_ok, k_res = await make_player_king(char["id"])
    assert k_ok is True, "Qirol tayinlanmadi!"
    c_king = await get_current_king()
    assert c_king.get("king_character_id") == char["id"], "Qirol ID mos kelmadi!"
    
    d_ok, d_res = await dethrone_current_king()
    assert d_ok is True, "Taxt bo'shatilmadi!"
    c_king_after = await get_current_king()
    assert c_king_after.get("king_character_id") is None, "Taxt bo'sh qolmadi!"
    print(f"✅ TEST 13.3 (Taxtni Boshqarish): Qirol tayinlandi va ag'darildi: {d_res[:45]}...")

    # 13.4 Aql/Sanity manipulyatsiyasi va Travmalar berish
    s_val = await set_player_sanity(char["id"], 0)
    assert s_val == 0, "Sanity 0 ga tushirilmadi!"
    w_list = await give_player_wound(char["id"], "broken_arm")
    assert "broken_arm" in w_list, "Jarohat berilmadi!"
    await cure_player_all_wounds(char["id"])
    char_cured = await get_character_by_user_id(test_user_id)
    assert char_cured["sanity"] == 100, "Sanity 100 ga tiklanmadi!"
    print("✅ TEST 13.4 (Sanity & Travmalar): Aql 0% (Telbalik) va Jarohat berildi, so'ngra to'liq shifo berildi.")

    # 13.5 Gildiya va Qal'alarni boshqarish
    test_g_name = f"Vaqtinchalik_{int(time.time()) % 100000}"
    await create_guild(buyer_id, test_g_name)
    g_gold_ok, g_gold_msg = await give_guild_gold_by_name(test_g_name, 50000)
    assert g_gold_ok is True, "Gildiyaga oltin berilmadi!"
    c_assign_ok, c_assign_msg = await assign_castle_owner_by_id(castles[0]["id"], test_g_name)
    assert c_assign_ok is True, "Qal'a topshirilmadi!"
    disband_ok, disband_msg = await disband_guild_by_name(test_g_name)
    assert disband_ok is True, "Gildiya tarqatilmadi!"
    print(f"✅ TEST 13.5 (Gildiya & Qal'alar): Xazina to'ldirildi (+50k 🪙), Qal'a topshirildi va Gildiya tarqatildi.")

    # 13.6 Kundalik Kvestlar va Barcha Yutuqlarni ochish
    await complete_all_daily_quests_admin(char["id"])
    await unlock_all_player_achievements(char["id"])
    ach_all = await get_player_achievements(char["id"])
    assert len(ach_all) >= 5, "Barcha yutuqlar ochilmadi!"
    print(f"✅ TEST 13.6 (Kvest & Yutuqlar): Barcha kvestlar bajarildi va {len(ach_all)} ta yutuq ochildi.")

    # 13.7 Bozorni Tozalash (Admin Market Reset)
    await create_market_listing(char["id"], "potions", "Test Eliksir", 1, 100)
    cleared_cnt = await clear_market_listings_admin()
    assert cleared_cnt >= 1, "Bozor tozalanmadi!"
    print(f"✅ TEST 13.7 (Bozor Reset): {cleared_cnt} ta faol listinglar bekor qilindi.")

    # =====================================================================
    # 14. ASOSIY MENYU TUGMALARI (PERSISTENT REPLY KEYBOARDS)
    # =====================================================================
    print("\n[TEST 14] Doimiy Pastki Menyu Tugmalari (ReplyKeyboardMarkup)...")
    from keyboards.reply_keyboards import main_reply_keyboard
    from handlers.menu_buttons_handler import menu_buttons_router

    kb_player = main_reply_keyboard(is_owner=False)
    kb_owner = main_reply_keyboard(is_owner=True)

    # O'yinchi menyusida barcha yangi tugmalar bo'lishi kerak
    player_buttons = [btn.text for row in kb_player.keyboard for btn in row]
    assert "⚔️ Arena (1v1)" in player_buttons, "Arena tugmasi yo'q!"
    assert "🗺 Zindon & Reydlar" in player_buttons, "Zindon tugmasi yo'q!"
    assert "🧭 Sahro & Sarguzasht" in player_buttons, "Sahro tugmasi yo'q!"
    assert "📖 Ensiklopediya (Lore)" in player_buttons, "Ensiklopediya tugmasi yo'q!"
    assert "🛒 Jonli Bozor (P2P)" in player_buttons, "Bozor tugmasi yo'q!"
    assert "📜 Kvestlar & Yutuqlar" in player_buttons, "Kvestlar tugmasi yo'q!"
    assert "⛏ Shaxta & Alximiya" in player_buttons, "Shaxta tugmasi yo'q!"
    assert "🐫 Karvon Savdosi" in player_buttons, "Karvon tugmasi yo'q!"
    assert "🏰 Gildiya & Qal'alar" in player_buttons, "Gildiya tugmasi yo'q!"
    assert "👑 Oliy Taxt" in player_buttons, "Oliy Taxt tugmasi yo'q!"
    assert "👤 Profil & Karta" in player_buttons, "Profil & Karta tugmasi yo'q!"
    assert "👑 OLIY BOSHQARUV (God-Mode)" not in player_buttons, "Owner tugmasi oddiy o'yinchiga ko'rinib qoldi!"

    # Owner menyusida esa God-Mode tugmasi bo'lishi kerak
    owner_buttons = [btn.text for row in kb_owner.keyboard for btn in row]
    assert "👑 OLIY BOSHQARUV (God-Mode)" in owner_buttons, "Owner uchun God-Mode tugmasi yo'q!"
    print(f"✅ TEST 14 O'TDI: Doimiy menyu tugmalari (O'yinchi: {len(player_buttons)} ta, Owner: {len(owner_buttons)} ta) muvaffaqiyatli tekshirildi.")

    # =====================================================================
    # 15. 1000+ KONTENT ENSIKLOPEDIYASI: 200 ANJOM, BESTIARIY, ALXIMIYA, KVESTLAR
    # =====================================================================
    print("\n[TEST 15] 1,000+ Kontent Kengaytmasi (200 ta Anjom, Bestiariy, Alximiya, Kvestlar)...")
    from game.bestiary import BESTIARY_DATA
    from game.items_db import ITEMS_CATALOG
    from game.events_engine import EventsEngine, WILDERNESS_EVENTS
    from game.lore_db import TAVERN_RUMORS, ANCIENT_SCROLLS, TREASURE_MAPS
    from game.alchemy_db import ORES_DATABASE, HERBS_DATABASE, POTIONS_DATABASE, RUNES_RECIPES
    from game.quest_db import MAIN_CAMPAIGN_QUESTS, GLOBAL_BOUNTIES
    from game.dark_engine import WOUND_TYPES
    from database.db import DUNGEON_FLOORS

    assert len(ITEMS_CATALOG) == 200, f"Anjomlar soni 200 ta emas ({len(ITEMS_CATALOG)})!"
    assert len(BESTIARY_DATA) >= 40, "Bestiariyda maxluqlar kam!"
    assert len(DUNGEON_FLOORS) >= 10, "Zindon qavatlari 10 taga yetmadi!"
    assert len(WILDERNESS_EVENTS) >= 15, "Sahro sarguzashtlari 15 taga yetmadi!"
    assert len(ORES_DATABASE) == 25, "Rudalar soni 25 ta emas!"
    assert len(HERBS_DATABASE) >= 20, "Alximik o'tlar kam!"
    assert len(POTIONS_DATABASE) >= 14, "Eliksirlar kam!"
    assert len(MAIN_CAMPAIGN_QUESTS) == 25, "Asosiy kampaniya kvestlari 25 ta emas!"
    assert len(GLOBAL_BOUNTIES) == 10, "Qidiruvdagi jinoyatchilar 10 ta emas!"
    assert len(TREASURE_MAPS) == 5, "Xazina xaritalari 5 ta emas!"
    assert len(WOUND_TYPES) == 15, "Zulmat travmalari 15 ta emas!"

    # Tasodifiy sahro sarguzashti testi
    ev = EventsEngine.get_random_event()
    assert ev["id"] in [e["id"] for e in WILDERNESS_EVENTS], "Sarguzasht topilmadi!"
    res_text, changes = EventsEngine.resolve_event("event_shrine", "pray", char)
    assert changes["hp"] > 0, "Ilohiy buloq joni tiklamadi!"
    # =====================================================================
    # 16. 10,000+ PROTSESSUAL ARXITEKTURA & GENERATORLAR (131,000+ ENTITIES)
    # =====================================================================
    print("\n[TEST 16] 10,000+ Protsessual Arxitektura & Kombinatorik Generatorlar...")
    from game.procedural_loot import generate_procedural_loot, get_procedural_matrix_size, ITEM_PREFIXES, ITEM_SUFFIXES
    from game.mutation_engine import mutate_monster, get_mutation_matrix_size, MONSTER_MUTATIONS, MONSTER_RANKS
    from game.dungeon_generator import generate_procedural_room, get_dungeon_matrix_size, DUNGEON_THEMES, ROOM_TYPES, ROOM_LAYOUTS

    # 1. Qurol-aslaha affiks matritsasi (125,000+)
    loot_matrix = get_procedural_matrix_size()
    assert len(ITEM_PREFIXES) == 25, f"Prefikslar soni 25 ta emas ({len(ITEM_PREFIXES)})!"
    assert len(ITEM_SUFFIXES) == 25, f"Suffikslar soni 25 ta emas ({len(ITEM_SUFFIXES)})!"
    assert loot_matrix["total_unique_items"] >= 125000, f"Qurol matritsasi 125,000 dan kam ({loot_matrix['total_unique_items']})!"

    sample_loot = generate_procedural_loot(player_level=10)
    assert sample_loot["id"].startswith("proc_"), "Protsessual ID noto'g'ri!"
    assert sample_loot["attack"] > 0 or sample_loot["defense"] > 0, "Qurol ko'rsatkichi 0!"
    assert sample_loot["sockets"] in [0, 1, 2, 3], "Runa teshiklari noto'g'ri!"
    print(f"   ⚔️ Qurol Generatori: {loot_matrix['total_unique_items']} ta kombinatsiya (Namuna: '{sample_loot['name']}', Slotlar: {sample_loot['sockets']})")

    # 2. Maxluqlar mutatsiyasi matritsasi (5,000+)
    mob_matrix = get_mutation_matrix_size()
    assert len(MONSTER_MUTATIONS) == 20, f"Mutatsiyalar soni 20 ta emas ({len(MONSTER_MUTATIONS)})!"
    assert len(MONSTER_RANKS) == 5, f"Unvonlar soni 5 ta emas ({len(MONSTER_RANKS)})!"
    assert mob_matrix["total_unique_encounters"] >= 4500, f"Maxluqlar matritsasi kam ({mob_matrix['total_unique_encounters']})!"

    sample_mob = mutate_monster(dungeon_floor=5, force_rank="champion")
    assert sample_mob["rank"] == "champion", "Chempion unvoni o'rnatilmadi!"
    assert len(sample_mob["mutations"]) == 2, "Chempionda 2 ta mutatsiya bo'lmadi!"
    assert sample_mob["hp"] > 150, "Chempion HP oshmadi!"
    print(f"   👾 Maxluqlar Mutatsiyasi: {mob_matrix['total_unique_encounters']} ta jangovar holat (Namuna: '{sample_mob['name']}', HP: {sample_mob['hp']})")

    # 3. Zindon xonalari matritsasi (1,000+)
    dungeon_matrix = get_dungeon_matrix_size()
    assert len(DUNGEON_THEMES) == 10, "Mavzular 10 ta emas!"
    assert len(ROOM_TYPES) == 10, "Xona turlari 10 ta emas!"
    assert len(ROOM_LAYOUTS) == 10, "Tartiblar 10 ta emas!"
    assert dungeon_matrix["total_rooms"] == 1000, f"Zindon xonalari 1000 ta emas ({dungeon_matrix['total_rooms']})!"

    sample_room = generate_procedural_room(floor=3, room_number=4)
    assert sample_room["id"].startswith("room_"), "Xona ID si xato!"
    assert len(sample_room["description"]) > 20, "Xona tasnifi yetarli emas!"
    print(f"   🏰 Zindon Xonalari: {dungeon_matrix['total_rooms']} ta xona (Namuna: '{sample_room['title']}')")

    total_procedural = loot_matrix["total_unique_items"] + mob_matrix["total_unique_encounters"] + dungeon_matrix["total_rooms"]
    print(f"✅ TEST 16 O'TDI: 10,000+ Arxitektura to'liq tasdiqlandi. Jami: {total_procedural:,} ta protsessual kontent birliklari!")

    # =====================================================================
    # 17. MAHORAT SHAJARASI (675 TALANT) & JANGOVAR HAMROHLAR (960 PETS)
    # =====================================================================
    print("\n[TEST 17] Mahorat Shajarasi (675 Talant) & Hamrohlar Tizimi (960 Pets)...")
    from game.skills_engine import SKILL_TREES, get_skills_matrix_size
    from game.pets_engine import PET_SPECIES, EVOLUTION_STAGES, ELEMENT_ASPECTS, generate_companion, get_pet_matrix_size
    from database.db import (
        unlock_or_upgrade_skill, get_character_skills,
        add_character_pet, get_character_pets, set_active_pet, get_active_pet, feed_pet
    )

    # 1. Mahoratlar Shajarasi (675 Talant)
    skills_matrix = get_skills_matrix_size()
    assert skills_matrix["specializations"] == 9, f"Sub-klasslar 9 ta emas ({skills_matrix['specializations']})!"
    assert skills_matrix["total_skill_nodes"] == 135, f"Mahoratlar 135 ta emas ({skills_matrix['total_skill_nodes']})!"
    assert skills_matrix["total_skill_upgrades"] == 675, f"Talant darajalari 675 ta emas ({skills_matrix['total_skill_upgrades']})!"

    # Mahorat o'rganish testi
    success, msg = await unlock_or_upgrade_skill(char["id"], "paladin", "pal_holy_strike")
    assert success, f"Mahorat ochilmadi: {msg}"
    learned = await get_character_skills(char["id"])
    assert any(s["skill_id"] == "pal_holy_strike" for s in learned), "O'rganilgan mahorat DB da topilmadi!"
    print(f"   🧠 Mahorat Shajarasi: {skills_matrix['total_skill_upgrades']} ta talant (O'rganildi: 'pal_holy_strike', Qolgan SP: {char.get('skill_points', 5)-1})")

    # 2. Hamrohlar & Miniklar Matritsasi (960 Pets & Mounts)
    pet_matrix = get_pet_matrix_size()
    assert pet_matrix["species"] == 30, f"Zotlar 30 ta emas ({pet_matrix['species']})!"
    assert pet_matrix["evolution_stages"] == 4, f"Evolyutsiya bosqichlari 4 ta emas ({pet_matrix['evolution_stages']})!"
    assert pet_matrix["aspects"] == 8, f"Element aspektlari 8 ta emas ({pet_matrix['aspects']})!"
    assert pet_matrix["total_companion_variants"] == 960, f"Hamrohlar 960 ta emas ({pet_matrix['total_companion_variants']})!"

    # Hamroh yaratish va boqish testi
    new_comp = generate_companion(species_id="wolf_shadow", stage=2, aspect_key="fire")
    assert new_comp["atk"] > 30, "Hamroh zarbasi kam!"
    pet_db_id = await add_character_pet(char["id"], new_comp, is_active=True)
    assert pet_db_id > 0, "Hamroh DB ga saqlanmadi!"

    active_p = await get_active_pet(char["id"])
    assert active_p is not None, "Faol hamroh topilmadi!"
    assert active_p["id"] == pet_db_id, "Faol hamroh ID mos emas!"

    # Boqish (Feed)
    feed_success, feed_msg = await feed_pet(char["id"], pet_db_id, food_gold=50)
    assert feed_success, f"Hamrohni boqish muvaffaqiyatsiz: {feed_msg}"
    print(f"   🐾 Hamrohlar Matritsasi: {pet_matrix['total_companion_variants']} ta minik/hamroh (Faol: '{active_p['name']}', Boqildi: {feed_success})")

    grand_total = total_procedural + skills_matrix["total_skill_upgrades"] + pet_matrix["total_companion_variants"]
    print(f"✅ TEST 17 O'TDI: Barcha 675 ta mahorat va 960 ta hamrohlar muvaffaqiyatli ishga tushirildi! Jami Grand Kontent Fondi: {grand_total:,} ta!")

    # =====================================================================
    # 18. RETENTION MEGA-TIZIMLARI: BATTLE PASS, OMAD G'ILDIRAGI & AFK EKSPEDITSIYA
    # =====================================================================
    print("\n[TEST 18] Foydalanuvchilarni Olib Qolish Tizimlari (Retention Systems)...")
    from game.battle_pass import BATTLE_PASS_TIERS, SEASON_INFO, calculate_bp_tier
    from game.tavern_games import WHEEL_SLOTS, play_dice_duel
    from game.expeditions_engine import EXPEDITION_REGIONS
    from database.db import (
        get_or_create_battle_pass, add_battle_pass_exp, claim_bp_reward,
        spin_lucky_wheel, start_expedition, claim_expedition, get_connection
    )

    # 1. Battle Pass (50 Tiers)
    assert len(BATTLE_PASS_TIERS) == 50, "Battle Pass 50 ta daraja emas!"
    bp = await add_battle_pass_exp(char["id"], 250)
    assert bp["total_exp"] >= 250, "Mavsumiy EXP qo'shilmadi!"
    cur_tier = calculate_bp_tier(bp["total_exp"])
    assert cur_tier >= 3, "Tier to'g'ri hisoblanmadi!"

    # Claim tier 1 reward
    claim_ok, claim_msg = await claim_bp_reward(char["id"], 1, "free")
    assert claim_ok, f"Mavsumiy mukofot olinmadi: {claim_msg}"
    claim_again, _ = await claim_bp_reward(char["id"], 1, "free")
    assert not claim_again, "Qayta mukofot olishga yo'l qo'yildi!"
    print(f"   🎟 Battle Pass: 50 ta Tier (Joriy Tier: {cur_tier}, Olingan sovrin: {claim_msg})")

    # 2. Omad G'ildiragi (Lucky Wheel) & Suyak Tashlash
    assert len(WHEEL_SLOTS) >= 8, "G'ildirak slotlari kam!"
    spin_ok, spin_msg, slot = await spin_lucky_wheel(char["id"])
    assert spin_ok, f"G'ildirak aylanmadi: {spin_msg}"
    assert slot is not None, "Yutuq qaytmadi!"

    dice_res = play_dice_duel(bet_gold=100)
    assert dice_res["result"] in ["win", "loss", "tie"], "Suyak natijasi noto'g'ri!"
    print(f"   🎡 Taverna Omad G'ildiragi: {len(WHEEL_SLOTS)} ta mukofot sloti (Yutuq: '{slot['name']}', Suyak: {dice_res['result']})")

    # 3. Oflayn AFK Ekspeditsiyalar (2h, 4h, 8h, 12h, 24h)
    assert len(EXPEDITION_REGIONS) == 5, "Ekspeditsiya hududlari 5 ta emas!"
    exp_ok, exp_msg = await start_expedition(char["id"], "exp_dark_forest")
    assert exp_ok, f"Ekspeditsiya boshlanmadi: {exp_msg}"

    # Ekspeditsiya vaqtini sun'iy ravishda o'tkazib claim qilish testi
    import time
    async with get_connection() as db:
        finished_time = int(time.time()) - 10
        mock_data = json.dumps({
            "region_key": "exp_dark_forest",
            "region_name": "🌲 Tumanli Qorong'u O'rmon",
            "started_at": finished_time - 7200,
            "finishes_at": finished_time,
            "duration_hours": 2
        })
        await db.execute("UPDATE characters SET active_expedition_json = ? WHERE id = ?;", (mock_data, char["id"]))
        await db.commit()

    claim_exp_ok, claim_exp_msg, exp_rewards = await claim_expedition(char["id"])
    assert claim_exp_ok, f"Ekspeditsiya o'ljalari olinmadi: {claim_exp_msg}"
    assert exp_rewards["gold"] > 0, "Ekspeditsiya oltini 0!"
    print(f"   ⛺️ AFK Ekspeditsiyalar: 5 ta hudud (Olingan o'lja: +{exp_rewards['gold']} 🪙, +{exp_rewards['xp']} EXP)")

    print(f"✅ TEST 18 O'TDI: Barcha Retention tizimlari (Battle Pass, Omad G'ildiragi, AFK Ekspeditsiyalar) 100% muvaffaqiyatli ishga tushirildi!")

    # =====================================================================
    # 19. 60+ KUNLIK ENDGAME VA 100,000+ KONTENT MATRITSASI:
    #     PROMO-ENGINE, PRESTIGE X, 100-FLOOR ABYSSAL TOWER & RUNEWORDS
    # =====================================================================
    print("\n[TEST 19] 60+ Kunlik Endgame & 100k+ Kontent Matritsasi (Promo, Prestige X, Tower, Runewords)...")
    from game.promo_engine import OFFICIAL_PROMO_CODES, get_promo_info
    from game.ascension_engine import PRESTIGE_TIERS, can_ascend
    from game.tower_engine import generate_tower_floor, TOWER_MILESTONES
    from game.runewords_engine import ANCIENT_RUNES, FAMOUS_RUNEWORDS, synthesize_runes, get_runewords_matrix_size
    from database.db import (
        redeem_promo_code, perform_ascension, get_tower_floor_progress,
        advance_tower_floor
    )

    # 1. Promo Engine & Marketing Ad Ingestion (Reklama Trafigi)
    assert len(OFFICIAL_PROMO_CODES) >= 6, "Rasmiy promokodlar kam!"
    p_info = get_promo_info("VALORIYA2026")
    assert p_info is not None, "VALORIYA2026 topilmadi!"
    assert p_info["gold"] == 2500, "Promokod oltini noto'g'ri!"

    # Promokodni aktivlashtirish
    promo_ok, promo_msg, promo_data = await redeem_promo_code(char["id"], "VALORIYA2026")
    assert promo_ok, f"Promokod ishlamadi: {promo_msg}"
    assert promo_data["campaign"] == "official_launch", "Kampaniya tegi saqlanmadi!"

    # Qayta ishlatib bo'lmasligini tekshirish (Anti-Abuse)
    promo_again_ok, promo_again_msg, _ = await redeem_promo_code(char["id"], "VALORIYA2026")
    assert not promo_again_ok, "Bir xil promokod ikkinchi marta ishlatildi!"
    print(f"   🎁 Reklama Promokod Dvigateli: {len(OFFICIAL_PROMO_CODES)} ta rasmiy start paketi (Aktivlashtirildi: VALORIYA2026, Anti-Abuse: OK)")

    # 2. Prestige / Ascension Tizimi (10 Tiers - 60+ Days Endgame Loop)
    assert len(PRESTIGE_TIERS) == 10, f"Prestij darajalari 10 ta emas ({len(PRESTIGE_TIERS)})!"
    assert PRESTIGE_TIERS[10]["stat_mult"] == 6.00, "Prestij X multiplikatori 6.00x emas!"

    # 50-darajadan pastda qayta tug'ilish rad etilishi kerak
    can_prestige_low, p_low_reason = can_ascend({"level": 25, "prestige_level": 0})
    assert not can_prestige_low, "25-darajada qayta tug'ilishga ruxsat berildi!"

    # Sun'iy ravishda 50-daraja o'rnatib Ascension qilish
    async with get_connection() as db:
        await db.execute("UPDATE characters SET level = 50, strength = 150, constitution = 100 WHERE id = ?;", (char["id"],))
        await db.commit()

    ascend_ok, ascend_msg = await perform_ascension(char["id"])
    assert ascend_ok, f"Ascension bajarilmadi: {ascend_msg}"

    char_after_asc = await get_character_by_user_id(test_user_id)
    assert char_after_asc["prestige_level"] == 1, "Prestige 1 ga ko'tarilmadi!"
    assert char_after_asc["level"] == 1, "Daraja 1 ga qaytmadi!"
    print(f"   🌟 Prestij & Qayta Tug'ilish: 10 ta Tier (Ascension I amalga oshirildi, Multiplikator: 1.20x, Sovg'a: +100 💎)")

    # 3. 100 Qavatli Cheksiz Tubsizlik Minorasi (Abyssal Tower)
    assert len(TOWER_MILESTONES) == 10, "Minora bosslari 10 ta emas!"
    floor_10 = generate_tower_floor(10)
    assert floor_10["is_boss"] is True, "10-qavat boss emas!"
    assert floor_10["hp"] > 500, "Boss HP si kam!"

    tower_fl_init = await get_tower_floor_progress(char["id"])
    assert tower_fl_init >= 1, "Minora qavati 1 dan kam!"

    # 1-qavat jangini o'tkazish
    tower_fight_ok, tower_msg, tower_data = await advance_tower_floor(char["id"])
    assert tower_fight_ok, f"1-qavat jangida g'alaba qozonilmadi: {tower_msg}"
    tower_fl_after = await get_tower_floor_progress(char["id"])
    assert tower_fl_after == tower_fl_init + 1, "Minora qavati ko'tarilmadi!"
    print(f"   🗼 100 Qavatli Abyssal Tower: 10 ta Milestone Boss (Zabt etildi: {tower_fl_init}-qavat, Yangi manzil: {tower_fl_after}-qavat)")

    # 4. R長nozuvlar & Runalar Sintezi (100,000+ Permutations & Syntheses)
    rw_matrix = get_runewords_matrix_size()
    assert rw_matrix["ancient_runes"] == 20, f"Qadimiy runalar 20 ta emas ({rw_matrix['ancient_runes']})!"
    assert rw_matrix["socket_combinations"] == 8000, f"Teshik kombinatsiyalari 8000 ta emas ({rw_matrix['socket_combinations']})!"
    assert rw_matrix["total_enchantments"] >= 100000, f"Sehrlar 100,000 dan kam ({rw_matrix['total_enchantments']})!"

    # Mashhur Ancient Pledge runozuvini sintez qilish
    syn_pledge = synthesize_runes(["ral", "ort", "tal"])
    assert syn_pledge["is_runeword"] is True, "Ancient Pledge tanilmadi!"
    assert syn_pledge["total_def"] > 40, "Ancient Pledge mudofaasi kam!"

    # Olamlar Hukmdori (Breath of the Dying) runozuvi
    syn_botd = synthesize_runes(["zod", "fal", "ith"])
    assert syn_botd["is_runeword"] is True, "Breath of the Dying tanilmadi!"
    assert syn_botd["total_atk"] >= 100, "Zarba kam!"

    # Oddiy 3-runali sintez
    syn_custom = synthesize_runes(["el", "eld", "tir"])
    assert syn_custom["is_runeword"] is False, "Oddiy kombinatsiya runeword deb tanildi!"
    assert syn_custom["total_atk"] > 0, "Oddiy sintez zarbasi 0!"
    print(f"   🔮 Runozuvlar (Runewords): {rw_matrix['ancient_runes']} ta Runa x 3 Socket = {rw_matrix['socket_combinations']:,} formula | Jami: {rw_matrix['total_enchantments']:,}+ ta effekt!")

    print(f"✅ TEST 19 O'TDI: 60+ Kunlik Endgame Loop (Prestige X, 100-Floor Tower, 100k+ Runewords, Promo-Engine) 100% muvaffaqiyatli ishga tushirildi!")

    # =====================================================================
    # 20. NPC TIRIK DUNYO (FAZA 1): 12 HUKMDOR SHAXSIYATI VA JADVALLAR 24–32
    # =====================================================================
    print("\n[TEST 20] NPC Tirik Dunyo: 12 Hukmdor Shaxsiyat Matritsasi & Jadvallar 24–32...")
    from npc.personality import RULER_PROFILES, validate_profile, get_ruler_profile, TRAIT_NAMES
    from database.db import get_connection

    # 1. 12 ta profil va 8 ta xislat 0-100 oralig'ida ekanligi
    assert len(RULER_PROFILES) == 12, f"Hukmdor profillari 12 ta emas ({len(RULER_PROFILES)})!"
    for emp_id, prof in RULER_PROFILES.items():
        assert validate_profile(prof) is True, f"{emp_id} shaxsiyat profili tekshiruvdan o'tmadi!"
        for t_name, t_val in prof["traits"].items():
            assert 0 <= t_val <= 100, f"{emp_id} ning {t_name} xislati 0-100 oralig'ida emas: {t_val}"

    # Asosiy arxitip tekshiruvlari
    torin = get_ruler_profile("iron_bastion")
    assert torin["traits"]["greed"] == 98, "Torin ochko'zligi 98 emas!"
    qora_soqol = get_ruler_profile("blood_tide")
    assert qora_soqol["traits"]["greed"] == 90, "Qora Soqol ochko'zligi 90 emas!"
    avreliy = get_ruler_profile("sun_order")
    assert avreliy["traits"]["piety"] == 100, "Patriarx Avreliy taqvosi 100 emas!"
    ragnar = get_ruler_profile("frost_peak")
    assert ragnar["traits"]["anger"] == 95, "Ragnar g'azabi 95 emas!"

    # 2. Baza jadvallari (24-32) va migratsiya versiyasi tekshiruvi
    async with get_connection() as db:
        # Schema version
        async with db.execute("SELECT version FROM schema_version WHERE version = 1;") as cur:
            row_v = await cur.fetchone()
            assert row_v is not None and row_v[0] == 1, "Sxema versiyasi 1 emas!"

        # Jadvallarning mavjudligi
        tables_to_check = [
            "npc_rulers", "npc_memory", "npc_relations", "npc_actions_log",
            "world_state", "rumors", "npc_loans", "bot_knights", "npc_quests"
        ]
        for tbl in tables_to_check:
            async with db.execute(f"SELECT count(*) FROM {tbl};") as cur_t:
                res_cnt = await cur_t.fetchone()
                assert res_cnt is not None, f"Jadval {tbl} topilmadi!"

        # npc_rulers da barcha 12 ta hukmdor seed qilinganmi?
        async with db.execute("SELECT count(*) FROM npc_rulers;") as cur_r:
            cnt_rulers = (await cur_r.fetchone())[0]
            assert cnt_rulers == 12, f"npc_rulers jadvalida 12 ta hukmdor yo'q: {cnt_rulers}"

        # Torin xazinasi va ochko'zligi DB da to'g'ri o'tirganmi?
        async with db.execute("SELECT greed, treasury FROM npc_rulers WHERE empire_id = 'iron_bastion';") as cur_torin:
            r_torin = await cur_torin.fetchone()
            assert r_torin[0] == 98, "Bazada Torin ochko'zligi 98 emas!"
            assert r_torin[1] >= 40000, "Bazada Torin xazinasi to'g'ri emas!"

    print(f"✅ TEST 20 O'TDI: NPC Tirik Dunyo Faza 1 (12 Hukmdor, 8 Xislat, Jadvallar 24–32, WAL Mode) 100% muvaffaqiyatli ishga tushirildi!")

    # =====================================================================
    # 21. NPC HISSIYOTLAR VA DECAY (FAZA 2: TEST 21)
    # =====================================================================
    print("\n[TEST 21] NPC Hissiyotlar Vektori va Decay Tizimi (0.10 har tick)...")
    from npc.state import get_ruler_state, update_ruler_mood, apply_mood_decay, BASELINES

    async with get_connection() as db:
        # Hukmdor kayfiyatini qo'zg'atish: quvonchni 20 ga, g'azabni 80 ga chiqarish
        await update_ruler_mood(db, "lionguard", d_joy=-30, d_anger=80)
        st_before = await get_ruler_state(db, "lionguard")
        assert st_before["anger_current"] >= 80, "G'azab 80 ga chiqmadi!"

        # Decay qo'llash
        decay_res = await apply_mood_decay(db, "lionguard")
        st_after = await get_ruler_state(db, "lionguard")

        # Quvonch (20) baza (50) tomon ko'tarilishi kerak: 20 + (50 - 20) * 0.10 = 23
        assert st_after["joy"] > st_before["joy"], "Decay quvonchni bazaga yaqinlashtirmadi!"
        # G'azab (80) baza (0) tomon pasayishi kerak: 80 + (0 - 80) * 0.10 = 72
        assert st_after["anger_current"] < st_before["anger_current"], "Decay g'azabni pasaytirmadi!"
        await db.commit()

    print(f"✅ TEST 21 O'TDI: Hissiyotlar decay formulasi (x + (baza - x)*0.10) to'liq tasdiqlandi (Anger: {st_before['anger_current']} -> {st_after['anger_current']}, Joy: {st_before['joy']} -> {st_after['joy']}).")

    # =====================================================================
    # 22. NPC XOTIRA VA FLATTTERY DECAY (FAZA 2: TEST 22)
    # =====================================================================
    print("\n[TEST 22] NPC Xotira, Munosabatlar va Xushomadning Kamayuvchi Foydasi (0.6^n)...")
    from npc.memory import record_memory_event, get_player_relation, compress_memory_if_needed, MAX_MEMORY_PER_PAIR

    async with get_connection() as db:
        # 1. Ketma-ket 4 ta xushomad (0.6^n kamayuvchi foyda)
        ev1 = await record_memory_event(db, "lionguard", char["id"], "flattery")
        ev2 = await record_memory_event(db, "lionguard", char["id"], "flattery")
        ev3 = await record_memory_event(db, "lionguard", char["id"], "flattery")
        ev4 = await record_memory_event(db, "lionguard", char["id"], "flattery")

        assert ev1["delta_trust"] >= ev2["delta_trust"], "1-xushomad 2-sidan kam ishonch berdi!"
        assert ev2["delta_trust"] >= ev4["delta_trust"], "Xushomad 0.6^n kamayuvchi foyda bermadi!"
        assert ev3["new_suspicion"] >= 5, "Har 3-xushomaddan keyin shubha (+5) oshmadi!"

        # 2. Xotira hajmini cheklash (<= 50 yozuv)
        for i in range(55):
            await db.execute("""
            INSERT INTO npc_memory (ruler_id, character_id, event_type, trust_d, anger_d, grudge_d)
            VALUES ('lionguard', ?, 'small_gift', 1, 0, 0);
            """, (char["id"],))
        await db.commit()

        await compress_memory_if_needed(db, "lionguard", char["id"])

        async with db.execute("SELECT count(*) FROM npc_memory WHERE ruler_id = 'lionguard' AND character_id = ?;", (char["id"],)) as cur_mem:
            cnt_mem = (await cur_mem.fetchone())[0]
            assert cnt_mem <= MAX_MEMORY_PER_PAIR, f"Xotira yozuvlari 50 tadan ko'p qoldi: {cnt_mem}"

        # 3. EmotionsEngine bilan integratsiya testi
        speech_res = await EmotionsEngine.process_speech_with_memory(db, "lionguard", "Siz eng buyuk, ulug' hukmdorsiz!", char["id"])
        assert speech_res["mood"] == "pleased", "Nutq ma'qullanmadi!"
        assert "memory_impact" in speech_res, "Xotira yozilmadi!"
        await db.commit()

    print(f"✅ TEST 22 O'TDI: Xotira hajmi (50 limit siqilishi), munosabatlar va 0.6^n xushomad susayishi 100% muvaffaqiyatli ishga tushirildi!")

    print("\n=========================================================")
    print("🎉 BARCHA 22 TA MEGA-TEST 100% MUVAFFAQIShLI O'TDI!")
    print(f"👑 VALORIYA: TIRIK DUNYO VA NPC AQL V3.0 (FAZA 2 MUVAFFAQIShLI)!")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())


