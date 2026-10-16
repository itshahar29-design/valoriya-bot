from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from game.constants import HIT_ZONES, EQUIPMENT_SLOTS

def main_menu_keyboard(is_owner: bool = False):
    buttons = [
        [
            InlineKeyboardButton(text="⚔️ Arena (1v1 Duel)", callback_data="menu_arena"),
            InlineKeyboardButton(text="🏰 12 Qirollik", callback_data="menu_kingdoms")
        ],
        [
            InlineKeyboardButton(text="🎒 Inventar (8 Slot)", callback_data="menu_inventory"),
            InlineKeyboardButton(text="🔨 Temirchi & Runalar", callback_data="menu_forge")
        ],
        [
            InlineKeyboardButton(text="🗺 Zindonlar (PvE)", callback_data="menu_dungeon"),
            InlineKeyboardButton(text="🎁 Kundalik Sovg'a", callback_data="menu_daily")
        ],
        [
            InlineKeyboardButton(text="🛒 Jonli Bozor (P2P)", callback_data="menu_market"),
            InlineKeyboardButton(text="📜 Kvestlar & Yutuqlar", callback_data="menu_quests")
        ],
        [
            InlineKeyboardButton(text="🐫 Karvon Savdosi", callback_data="menu_trade"),
            InlineKeyboardButton(text="🍻 Taverna & Qimor", callback_data="menu_tavern")
        ],
        [
            InlineKeyboardButton(text="🏰 Gildiya & Qal'alar", callback_data="menu_guild"),
            InlineKeyboardButton(text="⛏ Shaxta & Alximiya", callback_data="menu_professions")
        ],
        [
            InlineKeyboardButton(text="👥 Do'stlarni Taklif Qilish", callback_data="menu_referral"),
            InlineKeyboardButton(text="👑 Oliy Taxt & Turnir", callback_data="menu_tournament")
        ],
        [
            InlineKeyboardButton(text="👤 Profil & 🪪 Karta", callback_data="menu_profile"),
            InlineKeyboardButton(text="🏆 Reyting (Top)", callback_data="menu_top")
        ]
    ]
    if is_owner:
        buttons.append([
            InlineKeyboardButton(text="👑 OLIY BOSHQARUV (God-Mode)", callback_data="menu_owner_god")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def class_selection_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Jangchi (Warrior)", callback_data="select_class_warrior")],
        [InlineKeyboardButton(text="🏹 Mergan Izquvar (Scout)", callback_data="select_class_scout")],
        [InlineKeyboardButton(text="🧙‍♂️ Shogird Sehrgar (Mage)", callback_data="select_class_apprentice_mage")]
    ])

def battle_actions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Oddiy Zarba", callback_data="battle_strike"),
            InlineKeyboardButton(text="🩸 Og'ir Zarba", callback_data="battle_heavy_strike")
        ],
        [
            InlineKeyboardButton(text="🛡 Qalqon Tutish", callback_data="battle_defend"),
            InlineKeyboardButton(text="✨ Maxsus Mahorat", callback_data="battle_skill")
        ],
        [
            InlineKeyboardButton(text="🎯 Tana Qismini Tanlash", callback_data="battle_choose_zone")
        ]
    ])

def hit_zones_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Bosh / Miya", callback_data="zone_head"),
            InlineKeyboardButton(text="Bo'yin", callback_data="zone_neck")
        ],
        [
            InlineKeyboardButton(text="Ko'krak Qafasi", callback_data="zone_torso"),
            InlineKeyboardButton(text="Qorin", callback_data="zone_stomach")
        ],
        [
            InlineKeyboardButton(text="O'ng Qo'l", callback_data="zone_r_arm"),
            InlineKeyboardButton(text="Chap Qo'l", callback_data="zone_l_arm")
        ],
        [
            InlineKeyboardButton(text="Oyoqlar", callback_data="zone_r_leg"),
            InlineKeyboardButton(text="Chov", callback_data="zone_groin")
        ],
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="battle_back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def inventory_qol_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👑 Avto-Kiyinish (Best Gear)", callback_data="qol_auto_equip"),
            InlineKeyboardButton(text="🔨 Hammasini Tuzatish", callback_data="qol_repair_all")
        ],
        [
            InlineKeyboardButton(text="♻️ Axlatni Eritish (Oltin)", callback_data="qol_dismantle_junk"),
            InlineKeyboardButton(text="🎒 Anjomlar Ro'yxati", callback_data="view_all_items")
        ],
        [
            InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
        ]
    ])

def owner_god_mode_keyboard(page: int = 1):
    if page == 1:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 +50k Oltin", callback_data="god_grant_gold"),
                InlineKeyboardButton(text="💎 +1,000 Javohir", callback_data="god_grant_gems")
            ],
            [
                InlineKeyboardButton(text="⚡️ God-Stats (99k HP)", callback_data="god_max_stats"),
                InlineKeyboardButton(text="👑 Valoriya Qiroli Bo'lish", callback_data="god_claim_throne_instant")
            ],
            [
                InlineKeyboardButton(text="🗡 Qonli Qilich (+999 ATK)", callback_data="god_spawn_sword"),
                InlineKeyboardButton(text="🛡 Titan Zirhi (+999 DEF)", callback_data="god_spawn_shield")
            ],
            [
                InlineKeyboardButton(text="🔮 Barcha Runalar (x10 Paket)", callback_data="god_spawn_runes"),
                InlineKeyboardButton(text="🧪 Barcha Eliksirlar (x20)", callback_data="god_spawn_potions")
            ],
            [
                InlineKeyboardButton(text="🦄 Qanotli Pegas Tulpori", callback_data="god_spawn_pegasus"),
                InlineKeyboardButton(text="🩸 Iblis Qonli Ahdi (Pact)", callback_data="god_toggle_demon_pact")
            ],
            [
                InlineKeyboardButton(text="➡️ 2-Sahifa: Dunyo & Hodisalar 🌍", callback_data="god_page_2")
            ],
            [
                InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
            ]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🩸 Qonli Oy (Blood Moon)", callback_data="god_blood_moon"),
                InlineKeyboardButton(text="🐉 Ajdaho Reydini Chaqirish", callback_data="god_dragon_raid")
            ],
            [
                InlineKeyboardButton(text="🌧 Oltin Yomg'iri (2x Loot)", callback_data="god_golden_rain"),
                InlineKeyboardButton(text="☄️ Meteor Qulashi (Ofat)", callback_data="god_meteor_storm")
            ],
            [
                InlineKeyboardButton(text="🎁 Barcha Ritsarlarga Airdrop", callback_data="god_airdrop_all"),
                InlineKeyboardButton(text="📢 Barcha Guruhlarga E'lon", callback_data="god_broadcast_all")
            ],
            [
                InlineKeyboardButton(text="💖 Global Shifo (Hamma Tuzalsin)", callback_data="god_mass_heal"),
                InlineKeyboardButton(text="⚡️ Global Qahr (Dushmanlar Yiqilsin)", callback_data="god_mass_smite")
            ],
            [
                InlineKeyboardButton(text="🛒 Bozorni Tozalash (Reset)", callback_data="god_clear_market"),
                InlineKeyboardButton(text="🏰 Qal'alarni Neytral Qilish", callback_data="god_reset_castles")
            ],
            [
                InlineKeyboardButton(text="📊 Dunyo Telemetriyasi", callback_data="god_inspect"),
                InlineKeyboardButton(text="💾 Yangi Snapshot Saqlash", callback_data="god_save_snapshot")
            ],
            [
                InlineKeyboardButton(text="👤 O'yinchilarni Boshqarish Buyruqlari", callback_data="god_player_mgmt_guide"),
                InlineKeyboardButton(text="⏪ 1-Soatlik Rollback Qilish", callback_data="god_rollback")
            ],
            [
                InlineKeyboardButton(text="⬅️ 1-Sahifaga Qaytish", callback_data="god_page_1"),
                InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")
            ]
        ])
