import logging
from npc.personality import seed_npc_rulers

# =====================================================================
# VALORIYA NPC MIGRATSIYASI (JADVALLAR 24–32 & SCHEMA VERSIONING)
# =====================================================================
# Ushbu modul idempotent tarzda ishlaydi: har qanday holatda ham xatoliksiz
# jadvallarni yaratadi, SQLite WAL rejimini yoqadi va versiyani belgilaydi.
# =====================================================================

TARGET_SCHEMA_VERSION = 1

async def apply_npc_migrations(db):
    """
    NPC Aql tizimi uchun zarur 24–32 jadvallarni va ustunlarni yaratadi.
    """
    # 0. SQLite WAL va sinxronlik rejimini yoqish (katta oqimlar uchun)
    try:
        await db.execute("PRAGMA journal_mode = WAL;")
        await db.execute("PRAGMA synchronous = NORMAL;")
    except Exception as e:
        logging.warning(f"WAL rejimini yoqishda ogohlantirish: {e}")

    # 1. Sxema versiyasini kuzatuvchi jadval
    await db.execute("""
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 24. NPC Hukmdorlar holati va shaxsiyati
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_rulers (
        empire_id TEXT PRIMARY KEY,
        ruler_name TEXT NOT NULL,
        persona TEXT NOT NULL,
        greed INTEGER DEFAULT 50,
        pride INTEGER DEFAULT 50,
        anger INTEGER DEFAULT 50,
        cunning INTEGER DEFAULT 50,
        loyalty INTEGER DEFAULT 50,
        caution INTEGER DEFAULT 50,
        piety INTEGER DEFAULT 50,
        ambition INTEGER DEFAULT 50,
        joy INTEGER DEFAULT 50,
        anger_current INTEGER DEFAULT 0,
        fear INTEGER DEFAULT 0,
        boredom INTEGER DEFAULT 0,
        unrest INTEGER DEFAULT 0,
        treasury INTEGER DEFAULT 20000,
        army INTEGER DEFAULT 1000,
        last_tick_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 25. NPC Xotira voqealari (Har juftlik uchun hodisalar jurnali)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruler_id TEXT NOT NULL,
        character_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        trust_d INTEGER DEFAULT 0,
        anger_d INTEGER DEFAULT 0,
        grudge_d INTEGER DEFAULT 0,
        details_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 26. NPC va O'yinchi munosabatlari matritsasi
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_relations (
        ruler_id TEXT NOT NULL,
        character_id INTEGER NOT NULL,
        trust INTEGER DEFAULT 0,
        suspicion INTEGER DEFAULT 0,
        respect INTEGER DEFAULT 0,
        grudge INTEGER DEFAULT 0,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ruler_id, character_id)
    );
    """)

    # 27. NPC Harakatlari jurnali (Tarix va tahlil)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_actions_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruler_id TEXT NOT NULL,
        action TEXT NOT NULL,
        target TEXT DEFAULT NULL,
        params_json TEXT DEFAULT '{}',
        result TEXT DEFAULT 'success',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 28. Tirik Dunyo Global Holati (World State)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS world_state (
        key TEXT PRIMARY KEY,
        value_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 29. Mish-mishlar va Yangiliklar
    await db.execute("""
    CREATE TABLE IF NOT EXISTS rumors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_ruler TEXT DEFAULT NULL,
        subject TEXT NOT NULL,
        text_key TEXT NOT NULL,
        is_true INTEGER DEFAULT 1,
        spread INTEGER DEFAULT 1,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 30. NPC Sudxo'rlik Qarzlar Tizimi (Loans)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruler_id TEXT NOT NULL,
        character_id INTEGER NOT NULL,
        principal INTEGER NOT NULL,
        rate REAL DEFAULT 0.05,
        due_at TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'active',
        collateral_item_id INTEGER DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 31. Bot Ritsarlar Tizimi (Avtonom NPC o'yinchilar)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS bot_knights (
        character_id INTEGER PRIMARY KEY,
        archetype TEXT NOT NULL,
        schedule TEXT DEFAULT 'day',
        wallet_limit INTEGER DEFAULT 5000,
        last_action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        state_json TEXT DEFAULT '{}'
    );
    """)

    # 32. NPC Dinamik Hukmdor Kvestlari
    await db.execute("""
    CREATE TABLE IF NOT EXISTS npc_quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruler_id TEXT NOT NULL,
        character_id INTEGER DEFAULT NULL,
        template_key TEXT NOT NULL,
        params_json TEXT DEFAULT '{}',
        status TEXT DEFAULT 'available',
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 33. Mavjud jadvallarga yangi ustunlar (Idempotent ALTER TABLE)
    for col_info in [
        ("diplomacy", "pact_type", "TEXT DEFAULT NULL"),
        ("diplomacy", "is_secret", "INTEGER DEFAULT 0"),
        ("diplomacy", "since", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("diplomacy", "grievance", "INTEGER DEFAULT 0"),
        ("characters", "is_bot", "INTEGER DEFAULT 0")
    ]:
        tbl, col, def_val = col_info
        try:
            await db.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {def_val};")
        except Exception:
            pass  # Agar ustun allaqachon mavjud bo'lsa, xatolik e'tiborga olinmaydi

    # 34. 12 ta hukmdorni boshlang'ich profillar bilan to'ldirish (seed)
    await seed_npc_rulers(db)

    # 35. Versiyani qayd etish
    await db.execute("""
    INSERT INTO schema_version (version, applied_at)
    VALUES (?, CURRENT_TIMESTAMP)
    ON CONFLICT(version) DO UPDATE SET applied_at = CURRENT_TIMESTAMP;
    """, (TARGET_SCHEMA_VERSION,))

    await db.commit()
    logging.info(f"✅ NPC Migratsiyasi (Jadvallar 24-32) muvaffaqiyatli tatbiq etildi (v{TARGET_SCHEMA_VERSION}).")
