import json
import aiosqlite
from typing import Tuple, Dict, List, Any
from pathlib import Path
from config import DB_PATH
from game.constants import KINGDOMS, CLASSES, STARTER_GEAR

def get_connection():
    return aiosqlite.connect(DB_PATH)

async def init_db():
    async with get_connection() as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Characters table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            is_owner INTEGER DEFAULT 0,
            tier INTEGER DEFAULT 1,
            class_id TEXT DEFAULT 'warrior',
            kingdom_id TEXT DEFAULT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            hp INTEGER DEFAULT 120,
            max_hp INTEGER DEFAULT 120,
            stamina INTEGER DEFAULT 100,
            max_stamina INTEGER DEFAULT 100,
            mana INTEGER DEFAULT 50,
            strength INTEGER DEFAULT 15,
            agility INTEGER DEFAULT 12,
            constitution INTEGER DEFAULT 15,
            intelligence INTEGER DEFAULT 10,
            sanity INTEGER DEFAULT 100,
            honor INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 250,
            gems INTEGER DEFAULT 5,
            horse_name TEXT DEFAULT 'Boychibor',
            horse_bond INTEGER DEFAULT 10,
            wounds_json TEXT DEFAULT '[]',
            bloodline_trait TEXT DEFAULT 'noble_blood',
            hide_from_leaderboard INTEGER DEFAULT 0,
            invited_by_user_id INTEGER DEFAULT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            tutorial_done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Equipment table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            slot_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            rarity TEXT DEFAULT 'common',
            attack INTEGER DEFAULT 0,
            defense INTEGER DEFAULT 0,
            durability INTEGER DEFAULT 100,
            max_durability INTEGER DEFAULT 100,
            runes_json TEXT DEFAULT '[]',
            is_equipped INTEGER DEFAULT 0,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
        );
        """)

        # 3. Kingdoms table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS kingdoms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            ruler_name TEXT NOT NULL,
            treasury INTEGER DEFAULT 50000,
            tax_rate REAL DEFAULT 0.05,
            anger INTEGER DEFAULT 20,
            pride INTEGER DEFAULT 60,
            affection INTEGER DEFAULT 30,
            fear INTEGER DEFAULT 10,
            greed INTEGER DEFAULT 40,
            morale INTEGER DEFAULT 80,
            territory_count INTEGER DEFAULT 5
        );
        """)

        # 4. Auction Lots
        await db.execute("""
        CREATE TABLE IF NOT EXISTS auction_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            item_json TEXT NOT NULL,
            start_bid INTEGER NOT NULL,
            buyout_price INTEGER NOT NULL,
            current_bid INTEGER NOT NULL,
            highest_bidder_id INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        """)

        # 5. P2P Trades (Escrow)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS p2p_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            sender_items TEXT DEFAULT '[]',
            receiver_items TEXT DEFAULT '[]',
            sender_gold INTEGER DEFAULT 0,
            receiver_gold INTEGER DEFAULT 0,
            sender_locked INTEGER DEFAULT 0,
            receiver_locked INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending'
        );
        """)

        # 6. Pigeon Mails
        await db.execute("""
        CREATE TABLE IF NOT EXISTS pigeon_mails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            attached_item_json TEXT DEFAULT NULL,
            attached_gold INTEGER DEFAULT 0,
            is_claimed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. Captives (Prison & Ransom)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS captives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captor_id INTEGER NOT NULL,
            prisoner_id INTEGER NOT NULL,
            ransom_price INTEGER DEFAULT 500,
            status TEXT DEFAULT 'imprisoned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 8. Anti-Cheat Logs
        await db.execute("""
        CREATE TABLE IF NOT EXISTS anti_cheat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 9. World Snapshots (Rollback)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS world_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_tag TEXT NOT NULL,
            characters_count INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 10. Active Groups for spontaneous NPC broadcasts
        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_groups (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 11. Game Settings Table (Key-Value)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS game_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)

        # 12. Guilds Table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            leader_id INTEGER,
            level INTEGER DEFAULT 1,
            treasury INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 13. Dungeon Progress
        await db.execute("""
        CREATE TABLE IF NOT EXISTS dungeon_progress (
            character_id INTEGER PRIMARY KEY,
            max_floor INTEGER DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Migrations if needed
        for col_def in [
            ("username", "TEXT DEFAULT NULL"),
            ("is_jailed", "INTEGER DEFAULT 0"),
            ("is_muted", "INTEGER DEFAULT 0"),
            ("buff_multiplier", "REAL DEFAULT 1.0"),
            ("last_daily_claim", "TEXT DEFAULT NULL"),
            ("daily_streak", "INTEGER DEFAULT 0"),
            ("guild_id", "INTEGER DEFAULT NULL")
        ]:
            try:
                await db.execute(f"ALTER TABLE characters ADD COLUMN {col_def[0]} {col_def[1]};")
            except Exception:
                pass

        # Seed kingdoms if not existing
        for k_id, k_data in KINGDOMS.items():
            await db.execute("""
            INSERT OR IGNORE INTO kingdoms (id, name, ruler_name)
            VALUES (?, ?, ?);
            """, (k_id, k_data["name"], k_data["ruler"]))

        await db.commit()

async def register_group(chat_id: int, title: str):
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO active_groups (chat_id, title, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(chat_id) DO UPDATE SET title = excluded.title, updated_at = CURRENT_TIMESTAMP;
        """, (chat_id, title))
        await db.commit()

async def get_active_groups():
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM active_groups") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

# =====================================================================
# CHARACTER OPERATIONS
# =====================================================================

async def get_character_by_user_id(user_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_character_by_identifier(identifier: str | int):
    ident_str = str(identifier).strip().lstrip("@")
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        if ident_str.isdigit():
            async with db.execute("SELECT * FROM characters WHERE user_id = ? OR id = ?", (int(ident_str), int(ident_str))) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        async with db.execute("SELECT * FROM characters WHERE LOWER(username) = ? OR LOWER(name) = ?", (ident_str.lower(), ident_str.lower())) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            async with db.execute("SELECT * FROM characters WHERE LOWER(name) LIKE ? OR LOWER(username) LIKE ?", (f"%{ident_str.lower()}%", f"%{ident_str.lower()}%")) as cursor2:
                row2 = await cursor2.fetchone()
                return dict(row2) if row2 else None

async def give_player_item(character_id: int, item_name: str, slot_type: str = "weapon", attack: int = 150, defense: int = 50, rarity: str = "legendary"):
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
        VALUES (?, ?, ?, ?, ?, ?, 999, 999, 1);
        """, (character_id, slot_type, item_name, rarity, attack, defense))
        await db.commit()
        return True

async def strip_player_equipment(character_id: int):
    async with get_connection() as db:
        await db.execute("DELETE FROM equipment WHERE character_id = ?", (character_id,))
        await db.commit()
        return True

async def reset_player_character(character_id: int):
    async with get_connection() as db:
        await db.execute("""
        UPDATE characters SET
            level = 1, xp = 0, gold = 100, gems = 0,
            hp = 100, max_hp = 100, stamina = 100, max_stamina = 100,
            strength = 15, agility = 10, constitution = 12, intelligence = 10,
            wounds_json = '[]', wins = 0, losses = 0, is_jailed = 0, is_muted = 0
        WHERE id = ?;
        """, (character_id,))
        await db.execute("DELETE FROM equipment WHERE character_id = ?", (character_id,))
        await db.commit()
        return True

async def create_character(user_id: int, name: str, class_id: str = "warrior", invited_by: int = None, is_owner: bool = False):
    class_data = CLASSES.get(class_id, CLASSES["warrior"])
    hide_leaderboard = 1 if is_owner else 0
    owner_flag = 1 if is_owner else 0
    
    async with get_connection() as db:
        cursor = await db.execute("""
        INSERT INTO characters (
            user_id, name, is_owner, class_id, hp, max_hp, strength, agility, 
            constitution, hide_from_leaderboard, invited_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, name, owner_flag, class_id, class_data["base_hp"], class_data["base_hp"],
            class_data["base_atk"], class_data["base_agi"], class_data["base_def"],
            hide_leaderboard, invited_by
        ))
        char_id = cursor.lastrowid
        
        # Starter gear adding
        for gear in STARTER_GEAR:
            await db.execute("""
            INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (char_id, gear["slot_type"], gear["item_name"], gear["rarity"], gear["attack"], gear["defense"], gear["durability"], gear["max_durability"]))
        
        await db.commit()
        return char_id

async def update_character(char_id: int, **fields):
    if not fields:
        return
    set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [char_id]
    
    async with get_connection() as db:
        await db.execute(f"UPDATE characters SET {set_clause} WHERE id = ?", values)
        await db.commit()

# =====================================================================
# EQUIPMENT & QOL OPERATIONS
# =====================================================================

async def get_character_equipment(character_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM equipment WHERE character_id = ?", (character_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def equip_item(character_id: int, item_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        # Get target item slot
        async with db.execute("SELECT * FROM equipment WHERE id = ? AND character_id = ?", (item_id, character_id)) as cur:
            item = await cur.fetchone()
            if not item:
                return False
            slot = item["slot_type"]
        
        # Unequip currently equipped item in this slot
        await db.execute("UPDATE equipment SET is_equipped = 0 WHERE character_id = ? AND slot_type = ?", (character_id, slot))
        # Equip target item
        await db.execute("UPDATE equipment SET is_equipped = 1 WHERE id = ?", (item_id,))
        await db.commit()
        return True

async def auto_equip_best(character_id: int):
    """QoL: Xaltadagi eng kuchli buyumlarni avtomatik kiyib chiqadi."""
    items = await get_character_equipment(character_id)
    if not items:
        return 0
    
    # Slotlar bo'yicha eng yaxshisini tanlash (Atk + Def summasi eng kattasi)
    best_per_slot = {}
    for item in items:
        slot = item["slot_type"]
        power = item["attack"] + item["defense"]
        if slot not in best_per_slot or power > (best_per_slot[slot]["attack"] + best_per_slot[slot]["defense"]):
            best_per_slot[slot] = item
            
    equipped_count = 0
    async with get_connection() as db:
        for slot, item in best_per_slot.items():
            await db.execute("UPDATE equipment SET is_equipped = 0 WHERE character_id = ? AND slot_type = ?", (character_id, slot))
            await db.execute("UPDATE equipment SET is_equipped = 1 WHERE id = ?", (item["id"],))
            equipped_count += 1
        await db.commit()
    return equipped_count

async def repair_all_items(character_id: int, gold_available: int):
    """QoL: Barcha siniq kiyimlarni bir bosishda to'liq ta'mirlaydi."""
    items = await get_character_equipment(character_id)
    repair_cost = 0
    items_to_repair = []
    
    for item in items:
        damage = item["max_durability"] - item["durability"]
        if damage > 0:
            cost = max(1, damage // 2)
            repair_cost += cost
            items_to_repair.append(item["id"])
            
    if repair_cost > gold_available:
        return False, repair_cost, "Oltin yetarli emas!"
    
    if not items_to_repair:
        return True, 0, "Barcha anjomlar to'liq soz holatda!"
        
    async with get_connection() as db:
        await db.execute("UPDATE characters SET gold = gold - ? WHERE id = ?", (repair_cost, character_id))
        for item_id in items_to_repair:
            await db.execute("UPDATE equipment SET durability = max_durability WHERE id = ?", (item_id,))
        await db.commit()
        
    return True, repair_cost, f"Barcha {len(items_to_repair)} ta anjom {repair_cost} oltinga ta'mirlandi!"

async def dismantle_junk(character_id: int):
    """QoL: Egnida bo'lmagan oddiy (common) ortiqcha o'ljalarni eritib oltinga aylantiradi."""
    items = await get_character_equipment(character_id)
    junk = [i for i in items if i["is_equipped"] == 0 and i["rarity"] == "common"]
    
    if not junk:
        return 0, 0
        
    earned_gold = len(junk) * 25
    junk_ids = [i["id"] for i in junk]
    
    async with get_connection() as db:
        await db.execute(f"DELETE FROM equipment WHERE id IN ({','.join(['?']*len(junk_ids))})", junk_ids)
        await db.execute("UPDATE characters SET gold = gold + ? WHERE id = ?", (earned_gold, character_id))
        await db.commit()
        
    return len(junk), earned_gold

# =====================================================================
# LEADERBOARD & GOD-MODE
# =====================================================================

async def get_top_knights(limit: int = 10):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
        SELECT name, level, honor, wins, losses, class_id, kingdom_id 
        FROM characters 
        WHERE hide_from_leaderboard = 0
        ORDER BY honor DESC, level DESC, wins DESC 
        LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

# =====================================================================
# WORLD SNAPSHOTS (ROLLBACK)
# =====================================================================

async def create_world_snapshot(tag: str, description: str = ""):
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) FROM characters") as cur:
            count = (await cur.fetchone())[0]
        await db.execute("""
        INSERT INTO world_snapshots (snapshot_tag, characters_count, description)
        VALUES (?, ?, ?)
        """, (tag, count, description))
        await db.commit()
        return True

async def get_world_telemetry():
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) FROM characters") as c:
            total_chars = (await c.fetchone())[0]
        async with db.execute("SELECT COALESCE(SUM(gold), 0) FROM characters") as c:
            total_player_gold = (await c.fetchone())[0]
        async with db.execute("SELECT COALESCE(SUM(treasury), 0) FROM kingdoms") as c:
            total_kingdom_gold = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM active_groups") as c:
            total_groups = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM equipment") as c:
            total_items = (await c.fetchone())[0]
        return {
            "total_chars": total_chars,
            "total_player_gold": total_player_gold,
            "total_kingdom_gold": total_kingdom_gold,
            "total_groups": total_groups,
            "total_items": total_items
        }

async def give_global_airdrop(amount: int = 500):
    async with get_connection() as db:
        await db.execute("UPDATE characters SET gold = gold + ? WHERE is_owner = 0", (amount,))
        await db.commit()

# =====================================================================
# GAME SETTINGS & MANDATORY CHANNEL
# =====================================================================

async def get_setting(key: str, default: str = "") -> str:
    async with get_connection() as db:
        async with db.execute("SELECT value FROM game_settings WHERE key = ?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default

async def set_setting(key: str, value: str):
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO game_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value;
        """, (key, value))
        await db.commit()

# =====================================================================
# DAILY REWARD STREAK SYSTEM
# =====================================================================

DAILY_REWARDS = {
    1: {"gold": 100, "gems": 0, "xp": 50, "text": "1-Kunlik Qasamyod: +100 🪙 Oltin"},
    2: {"gold": 250, "gems": 1, "xp": 100, "text": "2-Kunlik Sadoqat: +250 🪙 Oltin, +1 💎 Javohir"},
    3: {"gold": 500, "gems": 2, "xp": 200, "text": "3-Kunlik Matonat: +500 🪙 Oltin, +2 💎 Javohir"},
    4: {"gold": 1000, "gems": 3, "xp": 350, "text": "4-Kunlik Jasorat: +1,000 🪙 Oltin, +3 💎 Javohir"},
    5: {"gold": 2000, "gems": 5, "xp": 500, "text": "5-Kunlik Qahramonlik: +2,000 🪙 Oltin, +5 💎 Javohir"},
    6: {"gold": 3500, "gems": 8, "xp": 750, "text": "6-Kunlik Imperator Mukofoti: +3,500 🪙 Oltin, +8 💎 Javohir"},
    7: {"gold": 7777, "gems": 25, "xp": 2000, "text": "🔥 7-KUNLIK AFSUN: +7,777 🪙 Oltin, +25 💎 Javohir va Afsonaviy Sovut!"}
}

async def claim_daily_streak(character_id: int):
    import datetime
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        now = datetime.datetime.utcnow()
        last_claim_str = char.get("last_daily_claim")
        streak = char.get("daily_streak", 0) or 0

        if last_claim_str:
            try:
                last_claim = datetime.datetime.fromisoformat(last_claim_str)
                diff = now - last_claim
                if diff.total_seconds() < 72000: # 20 soatdan kam bo'lsa
                    hours_left = int((72000 - diff.total_seconds()) // 3600)
                    return False, f"⏳ Siz bugungi mukofotni olgansiz! Keyingi sovg'a {hours_left} soatdan so'ng ochiladi.", streak
                elif diff.total_seconds() > 172800: # 48 soatdan o'tib ketgan bo'lsa zanjir uziladi
                    streak = 0
            except Exception:
                streak = 0

        streak = (streak % 7) + 1
        reward = DAILY_REWARDS.get(streak, DAILY_REWARDS[1])

        new_gold = char["gold"] + reward["gold"]
        new_gems = char.get("gems", 0) + reward["gems"]
        new_xp = char["xp"] + reward["xp"]

        await db.execute("""
        UPDATE characters SET
            gold = ?, gems = ?, xp = ?,
            daily_streak = ?, last_daily_claim = ?
        WHERE id = ?;
        """, (new_gold, new_gems, new_xp, streak, now.isoformat(), character_id))

        # 7-kunda maxsus sovg'a
        if streak == 7:
            await db.execute("""
            INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
            VALUES (?, 'armor', '🌟 7-Kunlik Afsonaviy Gambeson', 'legendary', 20, 180, 999, 999, 0);
            """, (character_id,))

        await db.commit()
        return True, f"🎁 *TABRIKLAYMIZ!* Siz {streak}-kunlik sovg'ani oldingiz!\n\n{reward['text']}", streak

# =====================================================================
# BLACKSMITH FORGE (QUROLLARNI +1 ... +10 KUCHAYTIRISH - DARK SOULS EDITION)
# =====================================================================

async def upgrade_equipment(item_id: int, character_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM equipment WHERE id = ? AND character_id = ?", (item_id, character_id)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Anjom topilmadi!"
            item = dict(row)

        async with db.execute("SELECT gold FROM characters WHERE id = ?", (character_id,)) as cur:
            char_gold = (await cur.fetchone())[0]

        # Name format: "Qilich +1"
        name = item["item_name"]
        import re
        m = re.search(r"\+(\d+)$", name)
        current_plus = int(m.group(1)) if m else 0

        if current_plus >= 10:
            return False, "Ushbu anjom maksimal +10 darajaga yetgan!"

        cost = (current_plus + 1) * 200
        if char_gold < cost:
            return False, f"Oltin yetarli emas! Kuchaytirish narxi: {cost} 🪙 Oltin."

        # Hardcore success rate scaling
        if current_plus < 4:
            success_rate = 85 - (current_plus * 10)
        elif current_plus < 7:
            success_rate = 50 - ((current_plus - 4) * 8)
        else:
            success_rate = 32

        import random
        roll = random.randint(1, 100)

        # 1. G'ALABA: Muvaffaqiyatli kuchaytirish
        if roll <= success_rate:
            new_plus = current_plus + 1
            clean_name = re.sub(r"\s*\+\d+$", "", name)
            new_name = f"{clean_name} +{new_plus}"
            new_atk = item["attack"] + 15
            new_def = item["defense"] + 10

            await db.execute("UPDATE characters SET gold = gold - ? WHERE id = ?", (cost, character_id))
            await db.execute("""
            UPDATE equipment SET item_name = ?, attack = ?, defense = ? WHERE id = ?;
            """, (new_name, new_atk, new_def, item_id))
            await db.commit()
            return True, f"✨ *TEMIRCHI MO'JIZASI!* Anjom muvaffaqiyatli kuchaytirildi: *{new_name}* (+15 Zarba, +10 Himoya)!"

        # 2. MAG'LUBIYAT (ZULMAT TIZIMI XATARI)
        await db.execute("UPDATE characters SET gold = gold - ? WHERE id = ?", (cost, character_id))
        
        # +7 va undan yuqori: 15% ehtimol bilan qurol darz ketishi (durability 0, +0 ga tushish)
        if current_plus >= 7:
            break_roll = random.randint(1, 100)
            if break_roll <= 18:
                clean_name = re.sub(r"\s*\+\d+$", "", name)
                shattered_name = f"{clean_name} (Siniq)"
                base_atk = max(5, item["attack"] - (current_plus * 15))
                base_def = max(3, item["defense"] - (current_plus * 10))
                await db.execute("""
                UPDATE equipment SET item_name = ?, attack = ?, defense = ?, durability = 0 WHERE id = ?;
                """, (shattered_name, base_atk, base_def, item_id))
                await db.commit()
                return False, f"⚡️ *DAHSHAT! QUROL SINDI VA MAYDALANDI!* 💥\n\nTemirchi bolg'asi ostida anjom haddan tashqari qizib darz ketdi! *{name}* sinib, chidamliligi 0 ga tushdi!"
            
            # Aks holda 45% daraja pasayishi (-1)
            elif break_roll <= 65 and current_plus > 0:
                new_plus = current_plus - 1
                clean_name = re.sub(r"\s*\+\d+$", "", name)
                new_name = f"{clean_name} +{new_plus}" if new_plus > 0 else clean_name
                new_atk = max(5, item["attack"] - 15)
                new_def = max(3, item["defense"] - 10)
                await db.execute("""
                UPDATE equipment SET item_name = ?, attack = ?, defense = ? WHERE id = ?;
                """, (new_name, new_atk, new_def, item_id))
                await db.commit()
                return False, f"📉 *QUROL DARZ KETDI!* ({cost} 🪙 ketdi)\n\nKuchaytirish xato ketdi va anjom darajasi pasaydi: *{new_name}* (-15 Zarba)!"

        # +4 dan +6 gacha: 25% ehtimol bilan daraja pasayishi (-1)
        elif current_plus >= 4:
            if random.randint(1, 100) <= 25:
                new_plus = current_plus - 1
                clean_name = re.sub(r"\s*\+\d+$", "", name)
                new_name = f"{clean_name} +{new_plus}" if new_plus > 0 else clean_name
                new_atk = max(5, item["attack"] - 15)
                new_def = max(3, item["defense"] - 10)
                await db.execute("""
                UPDATE equipment SET item_name = ?, attack = ?, defense = ? WHERE id = ?;
                """, (new_name, new_atk, new_def, item_id))
                await db.commit()
                return False, f"📉 *TEMIRCHI XATOSI!* Ruda erib ketmadi va anjom darajasi pasaydi: *{new_name}*!"

        await db.commit()
        return False, f"💨 *OMAD KELMADI!* Temirchi bolg'asi ostida ruda birlashmadi. ({cost} Oltin sarflandi, anjom buzilmadi)."

# =====================================================================
# PVE DUNGEON PROGRESS (5 BOSQICHLI ZINDONLAR)
# =====================================================================

DUNGEON_FLOORS = {
    1: {"name": "Zulmat G'ori (Goblinlar)", "boss": "Goblinlar Sardori Grik", "hp": 180, "atk": 25, "loot_gold": 250, "loot_xp": 150},
    2: {"name": "Qora Botqoqlik (Zaharlar)", "boss": "Zaharli Botqoq Iloni", "hp": 300, "atk": 40, "loot_gold": 600, "loot_xp": 300},
    3: {"name": "Tashlandiq Qasr (Sharpalar)", "boss": "Qora Ritsar sharpasi", "hp": 550, "atk": 65, "loot_gold": 1200, "loot_xp": 600},
    4: {"name": "Ajdaho Qoyasi (Olovli Mag'ora)", "boss": "Qizil Ajdaho Bolasi", "hp": 900, "atk": 95, "loot_gold": 2500, "loot_xp": 1200},
    5: {"name": "Valoriya Taqiqlangan Labirinti", "boss": "Lord Malakor — Qorong'ulik Hukmdori", "hp": 1500, "atk": 140, "loot_gold": 5000, "loot_xp": 3000}
}

async def get_dungeon_progress(character_id: int):
    async with get_connection() as db:
        async with db.execute("SELECT max_floor FROM dungeon_progress WHERE character_id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 1

async def advance_dungeon_floor(character_id: int, current_floor: int):
    async with get_connection() as db:
        await db.execute("""
        INSERT INTO dungeon_progress (character_id, max_floor) VALUES (?, ?)
        ON CONFLICT(character_id) DO UPDATE SET max_floor = MAX(max_floor, excluded.max_floor);
        """, (character_id, current_floor + 1))
        await db.commit()

# =====================================================================
# DARK ENGINE DATABASE INTEGRATION (ZULMAT VA TRAVMA TIZIMI)
# =====================================================================

async def apply_defeat_penalty(character_id: int, is_dungeon: bool = False) -> dict:
    """
    Mag'lubiyat oqibatlari:
    - Oltin yo'qotish (15% Arena, 25% Zindon)
    - Sanity (Aql) pasayishi (-15 Arena, -25 Zindon)
    - Kiyimdagi barcha qurol/sovutlar chidamliligi (Durability) -15..-25 ga tushishi
    - Og'ir travma (Wound) orttirish
    """
    from game.dark_engine import WOUND_TYPES
    import random

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        # 1. Oltin yo'qotish
        loss_pct = 0.25 if is_dungeon else 0.15
        gold_drop = int(char["gold"] * loss_pct)
        if char["gold"] > 0 and gold_drop == 0:
            gold_drop = min(char["gold"], 20)
        new_gold = max(0, char["gold"] - gold_drop)

        # 2. Sanity pasayishi
        sanity_drop = 25 if is_dungeon else 15
        new_sanity = max(0, char.get("sanity", 100) - sanity_drop)

        # 3. Travma (Wound) orttirish
        wounds_list = []
        try:
            w_raw = char.get("wounds_json", "[]")
            wounds_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
        except Exception:
            wounds_list = []

        wound_chance = 0.85 if is_dungeon else 0.60
        new_wound_inflicted = None
        available_wounds = [w for w in WOUND_TYPES.keys() if w not in wounds_list]

        if random.random() <= wound_chance and available_wounds:
            new_wound_key = random.choice(available_wounds)
            wounds_list.append(new_wound_key)
            new_wound_inflicted = WOUND_TYPES[new_wound_key]

        # 4. Qurollarning eskirishi / darz ketishi (Durability loss)
        durability_drop = random.randint(15, 25)
        await db.execute("""
        UPDATE equipment 
        SET durability = MAX(0, durability - ?)
        WHERE character_id = ? AND is_equipped = 1;
        """, (durability_drop, character_id))

        # 5. O'yinchi holatini yangilash (Jon max_hp ning 25% qismida qoladi)
        res_hp = max(1, char["max_hp"] // 4)
        await db.execute("""
        UPDATE characters SET
            gold = ?,
            sanity = ?,
            hp = ?,
            losses = losses + 1,
            wounds_json = ?
        WHERE id = ?;
        """, (new_gold, new_sanity, res_hp, json.dumps(wounds_list), character_id))
        await db.commit()

        return {
            "gold_lost": gold_drop,
            "sanity_lost": sanity_drop,
            "current_sanity": new_sanity,
            "durability_lost": durability_drop,
            "new_wound": new_wound_inflicted,
            "total_wounds": len(wounds_list),
            "res_hp": res_hp
        }

async def cure_wound(character_id: int, wound_id: str) -> Tuple[bool, str]:
    from game.dark_engine import WOUND_TYPES
    wound_info = WOUND_TYPES.get(wound_id)
    if not wound_info:
        return False, "Noma'lum jarohat turi!"

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT gold, wounds_json FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Qahramon topilmadi!"
            char = dict(row)

        cost = wound_info["cure_cost"]
        if char["gold"] < cost:
            return False, f"Oltin yetarli emas! Davolash narxi: {cost} 🪙 Oltin."

        wounds = []
        try:
            wounds = json.loads(char["wounds_json"])
        except Exception:
            wounds = []

        if wound_id not in wounds:
            return False, "Sizda bunday jarohat yo'q!"

        wounds.remove(wound_id)
        await db.execute("""
        UPDATE characters SET gold = gold - ?, wounds_json = ? WHERE id = ?;
        """, (cost, json.dumps(wounds), character_id))
        await db.commit()
        return True, f"✨ *JAROHAT DAVOLANDI!* Tabib malham surtib *{wound_info['name']}* jarohatini davoladi! ({cost} 🪙 to'landi)"

async def cure_all_wounds(character_id: int) -> Tuple[bool, str]:
    from game.dark_engine import WOUND_TYPES
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT gold, wounds_json FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Qahramon topilmadi!"
            char = dict(row)

        wounds = []
        try:
            wounds = json.loads(char["wounds_json"])
        except Exception:
            wounds = []

        if not wounds:
            return True, "Sizda hech qanday davolanmagan jarohat yo'q, tanangiz sog'lom!"

        total_cost = sum(WOUND_TYPES.get(w, {}).get("cure_cost", 150) for w in wounds)
        if char["gold"] < total_cost:
            return False, f"Barcha jarohatlarni davolash uchun {total_cost} 🪙 kerak! Hamyoningizda: {char['gold']} 🪙."

        await db.execute("""
        UPDATE characters SET gold = gold - ?, wounds_json = '[]' WHERE id = ?;
        """, (total_cost, character_id))
        await db.commit()
        return True, f"✨ *BOSH TABIB MO'JIZASI!* Barcha {len(wounds)} ta og'ir jarohatlar to'liq davolandi! ({total_cost} 🪙 sarflandi)"

async def restore_sanity(character_id: int, amount: int, cost: int) -> Tuple[bool, str]:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT gold, sanity FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Qahramon topilmadi!"
            char = dict(row)

        if char["gold"] < cost:
            return False, f"Oltin yetarli emas! Narxi: {cost} 🪙."

        current_sanity = char.get("sanity", 100)
        if current_sanity >= 100:
            return False, "Ruhingiz va aqlingiz allaqachon 100% to'la va sokin!"

        new_sanity = min(100, current_sanity + amount)
        await db.execute("""
        UPDATE characters SET gold = gold - ?, sanity = ? WHERE id = ?;
        """, (cost, new_sanity, character_id))
        await db.commit()
        return True, f"🍷 *AQIL VA RUH TIKLANDI!* Sizning Sanity ko'rsatkichingiz: *{new_sanity}%* ga ko'tarildi! ({cost} 🪙 sarflandi)"

async def sign_blood_pact(character_id: int) -> Tuple[bool, str]:
    """
    Qonli Ahd: Iblis Morvath bilan shartnoma.
    +45 Dark ATK, 20% Lifesteal evaziga -25 Max HP va Sanity yo'qotish.
    """
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if char.get("bloodline_trait") == "demon_pact":
            return False, "Siz allaqachon Qonli Ahd imzolagansiz! Ruhingiz Zulmatga tegishli."

        new_max_hp = max(50, char["max_hp"] - 25)
        new_hp = min(char["hp"], new_max_hp)
        new_sanity = max(10, char.get("sanity", 100) - 30)

        await db.execute("""
        UPDATE characters SET
            bloodline_trait = 'demon_pact',
            max_hp = ?,
            hp = ?,
            sanity = ?
        WHERE id = ?;
        """, (new_max_hp, new_hp, new_sanity, character_id))
        await db.commit()
        return True, (
            "🩸 *QONLI AHD IMZOLANDI! (IBLIS MORVATH)* 🩸\n\n"
            "Qora qon tomirlaringizga oqib kirdi!\n"
            "⚡️ *In'om:* +45 Dark ATK va Janglarda 20% Qon So'rish (Lifesteal)!\n"
            "💀 *To'lov:* Maksimal joningiz -25 ga kamaydi va Sanity 30% yo'qotildi!\n"
            "Shahardagi tabib va savdogarlar sizdan nafrat bilan chetlanadi."
        )

async def cleanse_blood_pact(character_id: int) -> Tuple[bool, str]:
    cost = 1500
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if char.get("bloodline_trait") != "demon_pact":
            return False, "Sizda hech qanday Zulmat Ahdi yo'q, ruhingiz ozod!"

        if char["gold"] < cost:
            return False, f"Ibodatxonada tavba qilish va ahdni buzish uchun {cost} 🪙 Oltin kerak!"

        new_max_hp = char["max_hp"] + 25
        await db.execute("""
        UPDATE characters SET
            gold = gold - ?,
            bloodline_trait = 'noble_blood',
            max_hp = ?,
            sanity = 100
        WHERE id = ?;
        """, (cost, new_max_hp, character_id))
        await db.commit()
        return True, (
            "🕯 *MUQADDAS POKLANISH MO'JIZASI!* 🕯\n\n"
            "Ibodatxona ruhoniylari qadimgi duolar bilan tanangizdagi zulmat qonini tozaladi!\n"
            "Maksimal joningiz qaytarildi (+25 Max HP) va Sanity 100% tiklandi."
        )


