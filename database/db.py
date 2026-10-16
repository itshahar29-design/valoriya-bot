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
            castle_owned TEXT DEFAULT NULL,
            castle_tax_collected INTEGER DEFAULT 0,
            members_count INTEGER DEFAULT 1,
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

        # 14. Castles Table (Qal'alar & Soliqlar)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS castles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_guild_id INTEGER DEFAULT NULL,
            defense_power INTEGER DEFAULT 500,
            daily_tax INTEGER DEFAULT 1500,
            last_tax_claim TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 15. Tournament & Throne (Oliy Taxt)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tournament_throne (
            id INTEGER PRIMARY KEY DEFAULT 1,
            king_character_id INTEGER DEFAULT NULL,
            crown_title TEXT DEFAULT 'Valoriya Oliy Hukmdori',
            reign_started TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            defense_wins INTEGER DEFAULT 0
        );
        """)

        # 16. P2P Open Market Listings (Jonli O'yinchilar Bozori)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS market_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            seller_name TEXT NOT NULL,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_data_json TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price_per_unit INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 17. Daily Quests (Kundalik Kvestlar)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS daily_quests (
            character_id INTEGER PRIMARY KEY,
            quest_date TEXT NOT NULL,
            arena_wins INTEGER DEFAULT 0,
            mining_count INTEGER DEFAULT 0,
            market_or_tavern INTEGER DEFAULT 0,
            is_claimed INTEGER DEFAULT 0
        );
        """)

        # 18. Achievements (Faxriy Yutuqlar va Medallar)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            title TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(character_id, achievement_id)
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
            ("guild_id", "INTEGER DEFAULT NULL"),
            ("referral_count", "INTEGER DEFAULT 0"),
            ("referral_gold_earned", "INTEGER DEFAULT 0"),
            ("professions_json", "TEXT DEFAULT '{\"mining_level\": 1, \"alchemy_level\": 1, \"iron_ore\": 0, \"gold_ore\": 0, \"mithril_ore\": 0, \"herbs\": 0, \"potions\": {}}'"),
            ("active_buff_potion", "TEXT DEFAULT NULL"),
            ("buff_potion_battles", "INTEGER DEFAULT 0"),
            ("is_king", "INTEGER DEFAULT 0"),
            ("current_city", "TEXT DEFAULT 'samarkand'"),
            ("trade_inventory_json", "TEXT DEFAULT '{}'"),
            ("runes_inventory_json", "TEXT DEFAULT '{\"fire_rune\": 0, \"frost_rune\": 0, \"lightning_rune\": 0}'")
        ]:
            try:
                await db.execute(f"ALTER TABLE characters ADD COLUMN {col_def[0]} {col_def[1]};")
            except Exception:
                pass

        for col_def in [
            ("castle_owned", "TEXT DEFAULT NULL"),
            ("castle_tax_collected", "INTEGER DEFAULT 0"),
            ("members_count", "INTEGER DEFAULT 1")
        ]:
            try:
                await db.execute(f"ALTER TABLE guilds ADD COLUMN {col_def[0]} {col_def[1]};")
            except Exception:
                pass

        # Seed castles if not existing
        for c_id, c_name, c_tax in [
            ("dragonstone", "Ajdaho Qal'asi", 3000),
            ("iron_fortress", "Temir Qo'rg'on", 2000),
            ("frost_keep", "Muzli Arsh", 1500)
        ]:
            await db.execute("""
            INSERT OR IGNORE INTO castles (id, name, daily_tax) VALUES (?, ?, ?);
            """, (c_id, c_name, c_tax))

        await db.execute("""
        INSERT OR IGNORE INTO tournament_throne (id, crown_title) VALUES (1, 'Valoriya Oliy Hukmdori');
        """)

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

# =====================================================================
# 1. GILDIYALAR VA QAL'ALAR (GUILDS & CASTLE SIEGES)
# =====================================================================

async def create_guild(leader_character_id: int, guild_name: str) -> Tuple[bool, str]:
    guild_name = guild_name.strip()
    if len(guild_name) < 3 or len(guild_name) > 30:
        return False, "Gildiya nomi 3 tadan 30 tagacha belgidan iborat bo'lishi kerak!"

    cost = 1000
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT gold, guild_id, name FROM characters WHERE id = ?", (leader_character_id,)) as cur:
            char = dict(await cur.fetchone())

        if char["guild_id"]:
            return False, "Siz allaqachon biror gildiya a'zosisiz! Avval undan chiqing."

        if char["gold"] < cost:
            return False, f"Gildiya tuzish uchun {cost:,} 🪙 Oltin kerak! Sizda: {char['gold']:,} 🪙."

        try:
            cursor = await db.execute("""
            INSERT INTO guilds (name, leader_id, level, treasury, members_count)
            VALUES (?, ?, 1, 200, 1);
            """, (guild_name, leader_character_id))
            guild_id = cursor.lastrowid
            
            await db.execute("UPDATE characters SET gold = gold - ?, guild_id = ? WHERE id = ?", (cost, guild_id, leader_character_id))
            await db.commit()
            return True, f"🏰 *TABRIKLAYMIZ!* '{guild_name}' nomli buyuk ritsarlar gildiyasi tuzildi! Bosh qarorgoh ochildi."
        except Exception as e:
            return False, f"Ushbu nomdagi gildiya allaqachon mavjud! Boshqa nom tanlang."

async def join_guild(character_id: int, guild_name: str) -> Tuple[bool, str]:
    guild_name = guild_name.strip()
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM guilds WHERE LOWER(name) = ?", (guild_name.lower(),)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, f"'{guild_name}' nomli gildiya topilmadi!"
            guild = dict(row)

        async with db.execute("SELECT guild_id, name FROM characters WHERE id = ?", (character_id,)) as cur2:
            char = dict(await cur2.fetchone())

        if char["guild_id"]:
            return False, "Siz allaqachon boshqa gildiya a'zosisiz!"

        await db.execute("UPDATE characters SET guild_id = ? WHERE id = ?", (guild["id"], character_id))
        await db.execute("UPDATE guilds SET members_count = members_count + 1 WHERE id = ?", (guild["id"],))
        await db.commit()
        return True, f"🛡 *QASAMYOD QABUL QILINDI!* Siz '{guild['name']}' gildiyasiga rasman qabul qilindingiz!"

async def deposit_guild_treasury(character_id: int, amount: int) -> Tuple[bool, str]:
    if amount <= 0:
        return False, "Miqdor musbat bo'lishi kerak!"

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT gold, guild_id FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if not char["guild_id"]:
            return False, "Siz biror gildiyaga a'zo emassiz!"

        if char["gold"] < amount:
            return False, f"Sizda yetarli oltin yo'q! Balans: {char['gold']:,} 🪙."

        await db.execute("UPDATE characters SET gold = gold - ? WHERE id = ?", (amount, character_id))
        await db.execute("UPDATE guilds SET treasury = treasury + ? WHERE id = ?", (amount, char["guild_id"]))
        await db.commit()
        return True, f"💰 *Gildiya xazinasiga +{amount:,} 🪙 Oltin qo'shildi!*"

async def get_guild_info(guild_id: int) -> dict | None:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM guilds WHERE id = ?", (guild_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            guild = dict(row)
        
        async with db.execute("SELECT id, name, level, wins FROM characters WHERE guild_id = ?", (guild_id,)) as cur2:
            members = [dict(r) for r in await cur2.fetchall()]
            guild["members"] = members
            return guild

async def get_all_castles() -> list:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
        SELECT c.*, g.name as owner_guild_name 
        FROM castles c
        LEFT JOIN guilds g ON c.owner_guild_id = g.id;
        """) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def siege_castle(character_id: int, castle_id: str) -> Tuple[bool, str]:
    import random
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if not char["guild_id"]:
            return False, "Qal'ani qamal qilish uchun biror gildiya a'zosi bo'lishingiz shart!"

        async with db.execute("SELECT * FROM castles WHERE id = ?", (castle_id,)) as cur2:
            row = await cur2.fetchone()
            if not row:
                return False, "Bunday qal'a mavjud emas!"
            castle = dict(row)

        if castle["owner_guild_id"] == char["guild_id"]:
            return False, "Bu qal'a allaqachon sizning gildiyangizga tegishli!"

        async with db.execute("SELECT * FROM guilds WHERE id = ?", (char["guild_id"],)) as cur3:
            guild = dict(await cur3.fetchone())

        # Qamal jangi: 50% g'alaba ehtimoli (darajaga bog'liq)
        if random.random() < 0.55:
            # G'alaba: Qal'a egallandi!
            await db.execute("UPDATE castles SET owner_guild_id = ? WHERE id = ?", (guild["id"], castle_id))
            await db.execute("UPDATE guilds SET castle_owned = ? WHERE id = ?", (castle["name"], guild["id"]))
            loot = castle["daily_tax"] // 2
            await db.execute("UPDATE guilds SET treasury = treasury + ? WHERE id = ?", (loot, guild["id"]))
            await db.commit()
            return True, (
                f"🏰 *QAL'A QAMALI G'ALABASI!* 🏆\n\n"
                f"'{guild['name']}' jangchilari devorlarni yorib o'tib, **{castle['name']}** ni zabt etdi!\n"
                f"Qal'a xazinasidan +{loot:,} 🪙 o'lja gildiyaga qo'shildi!\n"
                f"Endi har kuni {castle['daily_tax']:,} 🪙 passiv soliq gildiyangizga tushadi!"
            )
        else:
            loss_hp = max(10, char["hp"] // 2)
            await db.execute("UPDATE characters SET hp = ? WHERE id = ?", (loss_hp, character_id))
            await db.commit()
            return False, f"🩸 *QAMAL QAYTARILDI!* Qal'a kamonchilari va soqchilari hujumingizni to'xtatdi! Siz og'ir yaralandingiz."

# =====================================================================
# 2. VIRUSLI REFERAL TIZIMI (REFERRALS & PASSIVE CASHBACK)
# =====================================================================

async def handle_referral_signup(new_user_id: int, referrer_user_id: int) -> Tuple[bool, str, int]:
    if new_user_id == referrer_user_id:
        return False, "O'zingizni referal qila olmaysiz!", 0

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, name, gold, gems FROM characters WHERE user_id = ?", (referrer_user_id,)) as cur:
            referrer = await cur.fetchone()
            if not referrer:
                return False, "Taklif qiluvchi topilmadi!", 0
            ref_dict = dict(referrer)

        # Referrerga +500 Oltin va +1 Gem
        bonus_gold = 500
        await db.execute("""
        UPDATE characters SET
            gold = gold + ?,
            gems = gems + 1,
            referral_count = COALESCE(referral_count, 0) + 1,
            referral_gold_earned = COALESCE(referral_gold_earned, 0) + ?
        WHERE id = ?;
        """, (bonus_gold, bonus_gold, ref_dict["id"]))
        await db.commit()
        return True, ref_dict["name"], bonus_gold

async def award_referral_cashback(earner_character_id: int, earned_gold: int):
    """O'yinchi jangda oltin yutsa, uni chaqirgan ritsarga 5% keshbek tushadi."""
    if earned_gold <= 0:
        return
    cashback = max(1, int(earned_gold * 0.05))

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT invited_by_user_id FROM characters WHERE id = ?", (earner_character_id,)) as cur:
            row = await cur.fetchone()
            if not row or not row[0]:
                return
            referrer_user_id = row[0]

        await db.execute("""
        UPDATE characters SET
            gold = gold + ?,
            referral_gold_earned = COALESCE(referral_gold_earned, 0) + ?
        WHERE user_id = ?;
        """, (cashback, cashback, referrer_user_id))
        await db.commit()

async def get_referral_stats(user_id: int) -> dict:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT referral_count, referral_gold_earned FROM characters WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return {"count": 0, "gold_earned": 0}
            return {
                "count": row["referral_count"] or 0,
                "gold_earned": row["referral_gold_earned"] or 0
            }

# =====================================================================
# 3. SHAXTA VA ALXIMIYA (MINING & CRAFTING)
# =====================================================================

async def get_player_professions(character_id: int) -> dict:
    async with get_connection() as db:
        async with db.execute("SELECT professions_json FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            raw = row[0] if row and row[0] else "{}"
            try:
                data = json.loads(raw)
            except Exception:
                data = {}
            default = {
                "mining_level": 1, "alchemy_level": 1,
                "iron_ore": 0, "gold_ore": 0, "mithril_ore": 0,
                "herbs": 0, "potions": {"rage": 0, "healing": 0, "void_poison": 0}
            }
            default.update(data)
            return default

async def mine_resources(character_id: int) -> Tuple[bool, str, dict]:
    import random
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT stamina, gold FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if char["stamina"] < 20:
            return False, "Charchagansiz (Stamina kamida 20 bo'lishi kerak)! Tavernada ovqatlaning.", {}

        profs = await get_player_professions(character_id)
        
        # 10% g'or qulashi xavfi (Dark System)
        if random.random() < 0.12:
            await db.execute("UPDATE characters SET stamina = stamina - 20, hp = MAX(10, hp - 20) WHERE id = ?", (character_id,))
            await db.commit()
            return False, "⚠️ *G'ORDA QULASH!* Shaxta shiftidan tosh qulab sizni jarohatladi (-20 HP). Ruda olinmadi!", {}

        iron_found = random.randint(1, 4)
        gold_found = 1 if random.random() < 0.35 else 0
        mithril_found = 1 if random.random() < 0.15 else 0
        herbs_found = random.randint(1, 2)

        profs["iron_ore"] = profs.get("iron_ore", 0) + iron_found
        profs["gold_ore"] = profs.get("gold_ore", 0) + gold_found
        profs["mithril_ore"] = profs.get("mithril_ore", 0) + mithril_found
        profs["herbs"] = profs.get("herbs", 0) + herbs_found

        # 12% qadimiy runa topish ehtimoli
        rune_found_msg = ""
        if random.random() < 0.12:
            r_types = ["fire_rune", "frost_rune", "lightning_rune"]
            r_choice = random.choice(r_types)
            runes = await get_runes_inventory(character_id)
            runes[r_choice] = runes.get(r_choice, 0) + 1
            await db.execute("UPDATE characters SET runes_inventory_json = ? WHERE id = ?", (json.dumps(runes), character_id))
            rune_found_msg = f"\n• 🔮 *QADIMIY RUNA:* {RUNES_DATA[r_choice]['name']} topildi!"

        await db.execute("""
        UPDATE characters SET
            stamina = stamina - 20,
            professions_json = ?
        WHERE id = ?;
        """, (json.dumps(profs), character_id))
        await db.commit()

        # Kundalik kvest va yutuqlar
        await increment_quest_progress(character_id, "mining_count", 1)
        await unlock_achievement(character_id, "mining_master", "⛏ Mohir Konchi")

        msg = f"⛏ *SHAXTADA RUDA QAZIB OLINDI!* (-20 Stamina)\n"
        msg += f"• 🔩 Temir rudasi: +{iron_found}\n"
        if gold_found:
            msg += f"• 🪙 Oltin rudasi: +{gold_found}\n"
        if mithril_found:
            msg += f"• ✨ Sehrli Mithril: +{mithril_found}\n"
        msg += f"• 🌿 Shifobaxsh O'tlar: +{herbs_found}{rune_found_msg}"

        return True, msg, profs

async def brew_potion(character_id: int, potion_type: str) -> Tuple[bool, str]:
    profs = await get_player_professions(character_id)
    potions = profs.get("potions", {"rage": 0, "healing": 0, "void_poison": 0})

    if potion_type == "rage":
        # 2 Temir + 1 O't
        if profs.get("iron_ore", 0) < 2 or profs.get("herbs", 0) < 1:
            return False, "Resurs yetarli emas! Kerak: 2 ta Temir rudasi va 1 ta O't."
        profs["iron_ore"] -= 2
        profs["herbs"] -= 1
        potions["rage"] = potions.get("rage", 0) + 1
        name = "🧪 G'azab Damlamasi (+30% Zarba)"
    elif potion_type == "healing":
        # 3 O't + 1 Oltin ruda
        if profs.get("herbs", 0) < 3 or profs.get("gold_ore", 0) < 1:
            return False, "Resurs yetarli emas! Kerak: 3 ta O't va 1 ta Oltin rudasi."
        profs["herbs"] -= 3
        profs["gold_ore"] -= 1
        potions["healing"] = potions.get("healing", 0) + 1
        name = "🧪 Hayot Eliksiri (Jonni 100% tiklash)"
    elif potion_type == "void_poison":
        # 1 Mithril + 2 O't
        if profs.get("mithril_ore", 0) < 1 or profs.get("herbs", 0) < 2:
            return False, "Resurs yetarli emas! Kerak: 1 ta Mithril va 2 ta O't."
        profs["mithril_ore"] -= 1
        profs["herbs"] -= 2
        potions["void_poison"] = potions.get("void_poison", 0) + 1
        name = "🧪 Zulmat Zaxari (+40 Qo'shimcha Zahar Zarbasi)"
    else:
        return False, "Noma'lum damlama turi!"

    await unlock_achievement(character_id, "alchemy_master", "🧪 Mohir Alximik")

    profs["potions"] = potions
    async with get_connection() as db:
        await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), character_id))
        await db.commit()

    return True, f"✨ *ALXIMIYA MUVOFAQIShI!* Siz *{name}* damlamasini tayyorladingiz!"

async def use_potion(character_id: int, potion_type: str) -> Tuple[bool, str]:
    profs = await get_player_professions(character_id)
    potions = profs.get("potions", {})

    if potions.get(potion_type, 0) <= 0:
        return False, "Sizda ushbu damlamadan mavjud emas! Avval alximiyada tayyorlang."

    potions[potion_type] -= 1
    profs["potions"] = potions

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if potion_type == "healing":
            await db.execute("UPDATE characters SET hp = max_hp, stamina = 100, professions_json = ? WHERE id = ?", (json.dumps(profs), character_id))
            await db.commit()
            return True, "🧪 *HAYOT ELIKSIRI ICHILDI!* Jon va Stamina to'liq 100% tiklandi!"
        elif potion_type == "rage":
            await db.execute("""
            UPDATE characters SET
                active_buff_potion = 'rage',
                buff_potion_battles = 3,
                professions_json = ?
            WHERE id = ?;
            """, (json.dumps(profs), character_id))
            await db.commit()
            return True, "🔥 *G'AZAB DAMLAMASI ICHILDI!* Keyingi 3 ta jangda zarbangizga +30% quvvat qo'shiladi!"
        elif potion_type == "void_poison":
            await db.execute("""
            UPDATE characters SET
                active_buff_potion = 'void_poison',
                buff_potion_battles = 3,
                professions_json = ?
            WHERE id = ?;
            """, (json.dumps(profs), character_id))
            await db.commit()
            return True, "💀 *ZULMAT ZAXARI QUROLGA SURTILDI!* Keyingi 3 ta jangda zarbalaringiz dushmanga zahar yetkazadi!"

    return False, "Damlama qo'llanilmadi."

# =====================================================================
# 4. VALORIYA OLIY TAXTI VA TURNIR (THRONE & TOURNAMENT)
# =====================================================================

async def get_current_king() -> dict:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
        SELECT t.*, c.name as king_name, c.level, c.wins, c.user_id as king_user_id
        FROM tournament_throne t
        LEFT JOIN characters c ON t.king_character_id = c.id
        WHERE t.id = 1;
        """) as cur:
            row = await cur.fetchone()
            return dict(row) if row else {}

async def challenge_king(challenger_character_id: int) -> Tuple[bool, str]:
    import random
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        king_info = await get_current_king()
        king_char_id = king_info.get("king_character_id")

        async with db.execute("SELECT * FROM characters WHERE id = ?", (challenger_character_id,)) as cur:
            challenger = dict(await cur.fetchone())

        if challenger["level"] < 3:
            return False, "Taxtga da'vogarlik qilish uchun kamida 3-daraja bo'lishingiz kerak!"

        if king_char_id == challenger_character_id:
            return False, "Siz allaqachon Valoriya Qirolisiz! Taxt sizning qo'lingizda."

        if not king_char_id:
            # Taxt bo'sh, darhol egallash
            await db.execute("UPDATE tournament_throne SET king_character_id = ?, reign_started = CURRENT_TIMESTAMP WHERE id = 1", (challenger_character_id,))
            await db.execute("UPDATE characters SET is_king = 1 WHERE id = ?", (challenger_character_id,))
            await db.commit()
            return True, f"👑 *BO'SH TAXT EGALLANDI!* Siz Valoriya Qiroli deb e'lon qilindingiz!"

        # Taxt egasi bilan duel
        if random.random() < 0.50:
            # G'alaba: Yangi qirol!
            await db.execute("UPDATE characters SET is_king = 0 WHERE id = ?", (king_char_id,))
            await db.execute("UPDATE characters SET is_king = 1 WHERE id = ?", (challenger_character_id,))
            await db.execute("UPDATE tournament_throne SET king_character_id = ?, reign_started = CURRENT_TIMESTAMP, defense_wins = 0 WHERE id = 1", (challenger_character_id,))
            await db.commit()
            return True, (
                f"👑 *YANGI VALORIYA QIROLI TUG'ILDI!* ⚔️\n\n"
                f"Siz sobiq qirol ustidan qonli g'alaba qozonib, Oltin Tojni boshiga kiydingiz!\n"
                f"Butun qirolliklar sizning oldingizda tiz cho'kmoqda!"
            )
        else:
            await db.execute("UPDATE tournament_throne SET defense_wins = defense_wins + 1 WHERE id = 1")
            await db.execute("UPDATE characters SET hp = MAX(10, hp / 2) WHERE id = ?", (challenger_character_id,))
            await db.commit()
            return False, f"🩸 *DUELDA MAG'LUBIYAT!* Amaldagi qirol o'zining afsonaviy zarbasi bilan da'vongizni chippakka chiqardi!"

# =====================================================================
# 5. JONLI P2P OCHIQ BOZOR (LIVE PLAYER MARKETPLACE)
# =====================================================================

async def create_market_listing(seller_character_id: int, category: str, item_name: str, quantity: int, price_per_unit: int, item_data: dict) -> Tuple[bool, str]:
    if quantity <= 0 or price_per_unit <= 0:
        return False, "Miqdor va narx musbat bo'lishi shart!"

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT name FROM characters WHERE id = ?", (seller_character_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Qahramon topilmadi!"
            seller_name = row["name"]

        await db.execute("""
        INSERT INTO market_listings (seller_id, seller_name, category, item_name, item_data_json, quantity, price_per_unit, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active');
        """, (seller_character_id, seller_name, category, item_name, json.dumps(item_data), quantity, price_per_unit))
        await db.commit()
        return True, f"📦 *BOZORGA QO'YILDI!* {quantity}x *{item_name}* donasi {price_per_unit:,} 🪙 dan sotuvga chiqarildi!"

async def get_active_market_listings(category: str = None) -> list:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        if category:
            query = "SELECT * FROM market_listings WHERE status = 'active' AND category = ? ORDER BY created_at DESC LIMIT 25"
            params = (category,)
        else:
            query = "SELECT * FROM market_listings WHERE status = 'active' ORDER BY created_at DESC LIMIT 25"
            params = ()
        async with db.execute(query, params) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def get_player_market_listings(seller_character_id: int) -> list:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE seller_id = ? AND status = 'active' ORDER BY created_at DESC", (seller_character_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]

async def cancel_market_listing(seller_character_id: int, listing_id: int) -> Tuple[bool, str]:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE id = ? AND seller_id = ? AND status = 'active'", (listing_id, seller_character_id)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "E'lon topilmadi yoki allaqachon bekor qilingan!"
            listing = dict(row)

        await db.execute("UPDATE market_listings SET status = 'cancelled' WHERE id = ?", (listing_id,))
        
        # Mahsulotni egasiga qaytarish
        cat = listing["category"]
        qty = listing["quantity"]
        item_data = json.loads(listing["item_data_json"])
        
        if cat in ["ore", "potion"]:
            profs = await get_player_professions(seller_character_id)
            if cat == "ore":
                ore_key = item_data.get("key", "iron_ore")
                profs[ore_key] = profs.get(ore_key, 0) + qty
            elif cat == "potion":
                pot_key = item_data.get("key", "rage")
                profs.setdefault("potions", {})[pot_key] = profs.setdefault("potions", {}).get(pot_key, 0) + qty
            await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), seller_character_id))
        elif cat == "rune":
            runes = await get_runes_inventory(seller_character_id)
            r_key = item_data.get("key", "fire_rune")
            runes[r_key] = runes.get(r_key, 0) + qty
            await db.execute("UPDATE characters SET runes_inventory_json = ? WHERE id = ?", (json.dumps(runes), seller_character_id))
        elif cat == "trade_good":
            t_inv = await get_trade_inventory(seller_character_id)
            g_key = item_data.get("key", "silk")
            t_inv[g_key] = t_inv.get(g_key, 0) + qty
            await db.execute("UPDATE characters SET trade_inventory_json = ? WHERE id = ?", (json.dumps(t_inv), seller_character_id))
        elif cat == "equipment":
            eq = item_data
            await db.execute("""
            INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0);
            """, (seller_character_id, eq.get("slot_type", "weapon"), eq.get("item_name", "Qilich"), eq.get("rarity", "common"), eq.get("attack", 10), eq.get("defense", 5), eq.get("durability", 100), eq.get("max_durability", 100)))

        await db.commit()
        return True, f"↩️ *E'LON BEKOR QILINDI!* {listing['item_name']} inventaringizga qaytarildi."

async def buy_market_listing(buyer_character_id: int, listing_id: int) -> Tuple[bool, str, int, int, str]:
    """
    Mahsulot sotib olish.
    Returns: (success, msg, seller_user_id, net_gold_for_seller, item_name)
    """
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE id = ? AND status = 'active'", (listing_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Mahsulot allaqachon sotib olingan yoki sotuvdan olingan!", 0, 0, ""
            listing = dict(row)

        if listing["seller_id"] == buyer_character_id:
            return False, "O'zingizning mahsulotingizni sotib ololmaysiz!", 0, 0, ""

        async with db.execute("SELECT * FROM characters WHERE id = ?", (buyer_character_id,)) as cur2:
            buyer = dict(await cur2.fetchone())

        total_price = listing["price_per_unit"] * listing["quantity"]
        if buyer["gold"] < total_price:
            return False, f"Oltin yetarli emas! Narxi: {total_price:,} 🪙. Sizda: {buyer['gold']:,} 🪙.", 0, 0, ""

        # 3% Qirollik / Bozor solig'i
        tax = max(1, int(total_price * 0.03))
        net_gold = total_price - tax

        # Sotuvchining telegram user_id sini olish
        seller_user_id = 0
        async with db.execute("SELECT user_id FROM characters WHERE id = ?", (listing["seller_id"],)) as cur_s:
            s_row = await cur_s.fetchone()
            if s_row:
                seller_user_id = s_row[0]

        # Mablag'larni yangilash
        await db.execute("UPDATE characters SET gold = gold - ? WHERE id = ?", (total_price, buyer_character_id))
        await db.execute("UPDATE characters SET gold = gold + ? WHERE id = ?", (net_gold, listing["seller_id"]))
        await db.execute("UPDATE market_listings SET status = 'sold' WHERE id = ?", (listing_id,))

        # Mahsulotni xaridorga topshirish
        cat = listing["category"]
        qty = listing["quantity"]
        item_data = json.loads(listing["item_data_json"])

        if cat in ["ore", "potion"]:
            profs = await get_player_professions(buyer_character_id)
            if cat == "ore":
                ore_key = item_data.get("key", "iron_ore")
                profs[ore_key] = profs.get(ore_key, 0) + qty
            elif cat == "potion":
                pot_key = item_data.get("key", "rage")
                profs.setdefault("potions", {})[pot_key] = profs.setdefault("potions", {}).get(pot_key, 0) + qty
            await db.execute("UPDATE characters SET professions_json = ? WHERE id = ?", (json.dumps(profs), buyer_character_id))
        elif cat == "rune":
            runes = await get_runes_inventory(buyer_character_id)
            r_key = item_data.get("key", "fire_rune")
            runes[r_key] = runes.get(r_key, 0) + qty
            await db.execute("UPDATE characters SET runes_inventory_json = ? WHERE id = ?", (json.dumps(runes), buyer_character_id))
        elif cat == "trade_good":
            t_inv = await get_trade_inventory(buyer_character_id)
            g_key = item_data.get("key", "silk")
            t_inv[g_key] = t_inv.get(g_key, 0) + qty
            await db.execute("UPDATE characters SET trade_inventory_json = ? WHERE id = ?", (json.dumps(t_inv), buyer_character_id))
        elif cat == "equipment":
            eq = item_data
            await db.execute("""
            INSERT INTO equipment (character_id, slot_type, item_name, rarity, attack, defense, durability, max_durability, is_equipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0);
            """, (buyer_character_id, eq.get("slot_type", "weapon"), eq.get("item_name", "Qilich"), eq.get("rarity", "common"), eq.get("attack", 10), eq.get("defense", 5), eq.get("durability", 100), eq.get("max_durability", 100)))

        await db.commit()

        # Kundalik kvest va yutuqlar
        await increment_quest_progress(buyer_character_id, "market_or_tavern", 1)
        await unlock_achievement(buyer_character_id, "market_trader", "🛒 Savdo Magnati")
        await unlock_achievement(listing["seller_id"], "market_trader", "🛒 Savdo Magnati")

        return True, f"🎉 *XARID MUVAFFAQIYATLI!* Siz {listing['item_name']} ni {total_price:,} 🪙 evaziga sotib oldingiz!", seller_user_id, net_gold, listing["item_name"]

# =====================================================================
# 6. KUNDALIK KVESTLAR VA FAXRIY YUTUQLAR (DAILY QUESTS & ACHIEVEMENTS)
# =====================================================================

async def get_or_create_daily_quests(character_id: int) -> dict:
    import datetime
    today_str = datetime.date.today().isoformat()
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM daily_quests WHERE character_id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            if row:
                q = dict(row)
                if q["quest_date"] == today_str:
                    return q
                # Yangi kun kvestlari
                await db.execute("""
                UPDATE daily_quests SET
                    quest_date = ?, arena_wins = 0, mining_count = 0,
                    market_or_tavern = 0, is_claimed = 0
                WHERE character_id = ?;
                """, (today_str, character_id))
                await db.commit()
                q.update({"quest_date": today_str, "arena_wins": 0, "mining_count": 0, "market_or_tavern": 0, "is_claimed": 0})
                return q

        # Birinchi marta yaratish
        await db.execute("""
        INSERT INTO daily_quests (character_id, quest_date, arena_wins, mining_count, market_or_tavern, is_claimed)
        VALUES (?, ?, 0, 0, 0, 0);
        """, (character_id, today_str))
        await db.commit()
        return {
            "character_id": character_id,
            "quest_date": today_str,
            "arena_wins": 0,
            "mining_count": 0,
            "market_or_tavern": 0,
            "is_claimed": 0
        }

async def increment_quest_progress(character_id: int, quest_key: str, amount: int = 1):
    valid_keys = ["arena_wins", "mining_count", "market_or_tavern"]
    if quest_key not in valid_keys:
        return
    await get_or_create_daily_quests(character_id)
    async with get_connection() as db:
        await db.execute(f"UPDATE daily_quests SET {quest_key} = {quest_key} + ? WHERE character_id = ?", (amount, character_id))
        await db.commit()

async def claim_daily_quest_reward(character_id: int) -> Tuple[bool, str]:
    q = await get_or_create_daily_quests(character_id)
    if q["is_claimed"] == 1:
        return False, "Siz bugungi barcha kvest mukofotlarini allaqachon olgansiz!"

    # Tekshiruv: 2 arena, 2 shaxta, 1 taverna/bozor
    is_done = (q["arena_wins"] >= 2 and q["mining_count"] >= 2 and q["market_or_tavern"] >= 1)
    if not is_done:
        return False, "Hali barcha 3 ta kvest bajarilmadi! Vazifalar jurnalini ko'ring."

    bonus_gold = 1500
    bonus_gems = 2
    bonus_xp = 300

    async with get_connection() as db:
        await db.execute("""
        UPDATE characters SET
            gold = gold + ?,
            gems = gems + ?,
            xp = xp + ?
        WHERE id = ?;
        """, (bonus_gold, bonus_gems, bonus_xp, character_id))
        await db.execute("UPDATE daily_quests SET is_claimed = 1 WHERE character_id = ?", (character_id,))
        await db.commit()

    return True, (
        f"🎁 *KUNDALIK KVESTLAR TO'LIQ BAJARILDI!* 🏆\n\n"
        f"Siz jasorat bilan kunlik vazifalarni yakunladingiz!\n\n"
        f"💰 *Mukofot:* +{bonus_gold:,} 🪙 Oltin | +{bonus_gems} 💎 Qimmatbaho Javohir | +{bonus_xp} XP!\n"
        f"Ertaga yangi vazifalar sizni kutadi."
    )

async def unlock_achievement(character_id: int, achievement_id: str, title: str) -> bool:
    async with get_connection() as db:
        try:
            await db.execute("""
            INSERT OR IGNORE INTO achievements (character_id, achievement_id, title)
            VALUES (?, ?, ?);
            """, (character_id, achievement_id, title))
            await db.commit()
            return True
        except Exception:
            return False

async def get_player_achievements(character_id: int) -> list:
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM achievements WHERE character_id = ? ORDER BY unlocked_at DESC", (character_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]

# =====================================================================
# 7. QUROLLARGA RUNALAR O'RNATISH (RUNE SOCKETING)
# =====================================================================

RUNES_DATA = {
    "fire_rune": {"name": "🔥 Olov Runasi", "desc": "Kuydirish: Jangda har raund +25 olov zarari!", "cost": 400},
    "frost_rune": {"name": "❄️ Muz Runasi", "desc": "Muzlatish: Dushmanning zarbadan qochish imkonini 0 qiladi!", "cost": 450},
    "lightning_rune": {"name": "⚡️ Momaqaldiroq Runasi", "desc": "Yorish: Qalqonni 100% teshib o'tadi va dushman staminasini 0 qiladi!", "cost": 500}
}

async def get_runes_inventory(character_id: int) -> dict:
    async with get_connection() as db:
        async with db.execute("SELECT runes_inventory_json FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            raw = row[0] if row and row[0] else "{}"
            try:
                data = json.loads(raw)
            except Exception:
                data = {}
            default = {"fire_rune": 0, "frost_rune": 0, "lightning_rune": 0}
            default.update(data)
            return default

async def socket_rune_to_equipment(character_id: int, item_id: int, rune_type: str) -> Tuple[bool, str]:
    if rune_type not in RUNES_DATA:
        return False, "Noma'lum runa turi!"

    runes = await get_runes_inventory(character_id)
    if runes.get(rune_type, 0) <= 0:
        return False, f"Sizda {RUNES_DATA[rune_type]['name']} yo'q! Bozordan yoki shaxtadan toping."

    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM equipment WHERE id = ? AND character_id = ?", (item_id, character_id)) as cur:
            row = await cur.fetchone()
            if not row:
                return False, "Anjom topilmadi!"
            item = dict(row)

        current_runes = []
        try:
            current_runes = json.loads(item.get("runes_json", "[]"))
        except Exception:
            current_runes = []

        if len(current_runes) >= 2:
            return False, "Ushbu anjomda maksimal 2 ta runa o'rni to'lgan!"

        current_runes.append(rune_type)
        runes[rune_type] -= 1

        # Runa belgisi nomiga qo'shiladi
        rune_icon = "🔥" if rune_type == "fire_rune" else ("❄️" if rune_type == "frost_rune" else "⚡️")
        new_name = f"{item['item_name']} [{rune_icon}]"

        await db.execute("""
        UPDATE equipment SET item_name = ?, runes_json = ? WHERE id = ?;
        """, (new_name, json.dumps(current_runes), item_id))
        await db.execute("UPDATE characters SET runes_inventory_json = ? WHERE id = ?", (json.dumps(runes), character_id))
        await db.commit()

        return True, f"✨ *RUNA O'RNATILDI!* {RUNES_DATA[rune_type]['name']} anjomga muvaffaqiyatli singdirildi: *{new_name}*!"

# =====================================================================
# 8. SHAHARLARARO TIJORAT VA SAYOHAT (MERCHANT ARBITRAGE)
# =====================================================================

TRADE_CITIES = {
    "samarkand": {
        "name": "Samarqand Poytaxti",
        "goods": {
            "silk": {"name": "Ipak Mato", "buy": 100, "sell": 90},
            "spices": {"name": "Sharq Ziravorlari", "buy": 150, "sell": 135},
            "fur": {"name": "Qimmatbaho Mo'yna", "buy": 320, "sell": 300}
        }
    },
    "frost_peak": {
        "name": "Muzli Cho'qqi (Qonxo'r Ragnar)",
        "goods": {
            "silk": {"name": "Ipak Mato", "buy": 380, "sell": 350}, # Judayam qimmat!
            "spices": {"name": "Sharq Ziravorlari", "buy": 260, "sell": 240},
            "fur": {"name": "Qimmatbaho Mo'yna", "buy": 80, "sell": 70}   # Judayam arzon!
        }
    },
    "lionguard": {
        "name": "Oltin Sher Qirolligi",
        "goods": {
            "silk": {"name": "Ipak Mato", "buy": 220, "sell": 200},
            "spices": {"name": "Sharq Ziravorlari", "buy": 110, "sell": 95}, # Arzon!
            "fur": {"name": "Qimmatbaho Mo'yna", "buy": 240, "sell": 220}
        }
    }
}

async def travel_to_city(character_id: int, target_city: str) -> Tuple[bool, str]:
    if target_city not in TRADE_CITIES:
        return False, "Noma'lum shahar manzili!"

    import random
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT current_city, stamina, gold FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        if char.get("current_city") == target_city:
            return False, f"Siz allaqachon *{TRADE_CITIES[target_city]['name']}* shahridamisiz!"

        if char["stamina"] < 25:
            return False, "Karvonda sayohat qilish uchun kamida 25 Stamina kerak!"

        # 20% qaroqchilar hujumi xavfi
        ambush_txt = ""
        if random.random() < 0.20:
            lost_gold = min(char["gold"], 150)
            await db.execute("UPDATE characters SET gold = gold - ?, hp = MAX(10, hp - 15) WHERE id = ?", (lost_gold, character_id))
            ambush_txt = f"\n⚠️ *QAROQCHILAR PISTIRMASI:* Yo'lda sahro qaroqchilari karvonga hujum qildi! -{lost_gold} 🪙 yo'qotildi va -15 HP jarohatlandingiz!"

        await db.execute("""
        UPDATE characters SET current_city = ?, stamina = stamina - 25 WHERE id = ?;
        """, (target_city, character_id))
        await db.commit()

        return True, f"🐫 *KARVON MANZILGA YETDI!* Siz *{TRADE_CITIES[target_city]['name']}* shahriga qadam qo'ydingiz! (-25 Stamina){ambush_txt}"

async def get_trade_inventory(character_id: int) -> dict:
    async with get_connection() as db:
        async with db.execute("SELECT trade_inventory_json FROM characters WHERE id = ?", (character_id,)) as cur:
            row = await cur.fetchone()
            raw = row[0] if row and row[0] else "{}"
            try:
                data = json.loads(raw)
            except Exception:
                data = {}
            default = {"silk": 0, "spices": 0, "fur": 0}
            default.update(data)
            return default

async def buy_trade_good(character_id: int, good_key: str, amount: int = 1) -> Tuple[bool, str]:
    if amount <= 0:
        return False, "Miqdor musbat bo'lishi kerak!"
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        city_key = char.get("current_city") or "samarkand"
        city = TRADE_CITIES.get(city_key, TRADE_CITIES["samarkand"])
        if good_key not in city["goods"]:
            return False, "Ushbu shaharda bu tovar sotilmaydi!"

        good = city["goods"][good_key]
        total_cost = good["buy"] * amount
        if char["gold"] < total_cost:
            return False, f"Oltin yetarli emas! Kerak: {total_cost:,} 🪙. Sizda: {char['gold']:,} 🪙."

        trade_inv = await get_trade_inventory(character_id)
        trade_inv[good_key] = trade_inv.get(good_key, 0) + amount

        await db.execute("""
        UPDATE characters SET
            gold = gold - ?,
            trade_inventory_json = ?
        WHERE id = ?;
        """, (total_cost, json.dumps(trade_inv), character_id))
        await db.commit()

        await increment_quest_progress(character_id, "market_or_tavern", 1)
        return True, f"📦 *XARID QILINDI!* {amount}x {good['name']} jami {total_cost:,} 🪙 ga sotib olindi!"

async def sell_trade_good(character_id: int, good_key: str, amount: int = 1) -> Tuple[bool, str]:
    if amount <= 0:
        return False, "Miqdor musbat bo'lishi kerak!"
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) as cur:
            char = dict(await cur.fetchone())

        city_key = char.get("current_city") or "samarkand"
        city = TRADE_CITIES.get(city_key, TRADE_CITIES["samarkand"])
        if good_key not in city["goods"]:
            return False, "Ushbu shaharda bu tovar qabul qilinmaydi!"

        trade_inv = await get_trade_inventory(character_id)
        if trade_inv.get(good_key, 0) < amount:
            return False, f"Sizda yetarli {good_key} yo'q! Sizda: {trade_inv.get(good_key, 0)} dona."

        good = city["goods"][good_key]
        total_revenue = good["sell"] * amount
        trade_inv[good_key] -= amount

        await db.execute("""
        UPDATE characters SET
            gold = gold + ?,
            trade_inventory_json = ?
        WHERE id = ?;
        """, (total_revenue, json.dumps(trade_inv), character_id))
        await db.commit()

        await increment_quest_progress(character_id, "market_or_tavern", 1)
        await unlock_achievement(character_id, "market_trader", "🛒 Savdo Magnati")
        return True, f"💰 *SOTILDI!* {amount}x {good['name']} jami {total_revenue:,} 🪙 ga sotildi!"





