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
            InlineKeyboardButton(text="🏛 Auksion & Bozor", callback_data="menu_auction")
        ],
        [
            InlineKeyboardButton(text="🕊 Kaptar Pochtasi", callback_data="menu_pigeon"),
            InlineKeyboardButton(text="🍻 Taverna", callback_data="menu_tavern")
        ],
        [
            InlineKeyboardButton(text="👤 Ritsar Profili", callback_data="menu_profile"),
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

def owner_god_mode_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Cheksiz Xazina (+50k 🪙)", callback_data="god_grant_gold"),
            InlineKeyboardButton(text="⚡️ God-Stats (99k HP/999 Atk)", callback_data="god_max_stats")
        ],
        [
            InlineKeyboardButton(text="🗡 Afsonaviy Qilich (+999)", callback_data="god_spawn_sword"),
            InlineKeyboardButton(text="🛡 Daxlsizlik Qalqoni (+999)", callback_data="god_spawn_shield")
        ],
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
            InlineKeyboardButton(text="📊 Dunyo Telemetriyasi", callback_data="god_inspect"),
            InlineKeyboardButton(text="💾 Yangi Snapshot Saqlash", callback_data="god_save_snapshot")
        ],
        [
            InlineKeyboardButton(text="⏪ 1-Soatlik Rollback Qilish", callback_data="god_rollback"),
            InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")
        ]
    ])
