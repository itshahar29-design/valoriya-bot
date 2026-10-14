import json
import aiosqlite
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

        # Migrations if needed
        try:
            await db.execute("ALTER TABLE characters ADD COLUMN username TEXT DEFAULT NULL;")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE characters ADD COLUMN is_jailed INTEGER DEFAULT 0;")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE characters ADD COLUMN is_muted INTEGER DEFAULT 0;")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE characters ADD COLUMN buff_multiplier REAL DEFAULT 1.0;")
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

