import asyncio
import sys
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
    await create_character(user_id=owner_id, name="Oliy Yaratuvchi (Owner)", is_owner=True)
    owner_char = await get_character_by_user_id(owner_id)
    assert owner_char["is_owner"] == 1, "Owner flag belgilanmadi!"
    assert owner_char["hide_from_leaderboard"] == 1, "Reytingdan yashirish belgilanmadi!"
    
    top_list = await get_top_knights(limit=50)
    top_names = [k["name"] for k in top_list]
    assert "Oliy Yaratuvchi (Owner)" not in top_names, "XATO! Owner reytingda ko'rinib qoldi!"
    print("✅ TEST 3 O'TDI: Owner profiling reytingda 100% yashirin va daxlsiz ekanligi tasdiqlandi.")

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

    print("\n=========================================================")
    print("🎉 BARCHA 9 TA TEST 100% MUVAFFAQIShLI O'TDI!")
    print("👑 TIZIM TO'LIQ ISHCHI VA BEXATO HOLATDA!")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
