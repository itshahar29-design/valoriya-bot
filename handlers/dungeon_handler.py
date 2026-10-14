import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, update_character,
    get_dungeon_progress, advance_dungeon_floor, DUNGEON_FLOORS
)
from game.battle_engine import BattleEngine

dungeon_router = Router()

@dungeon_router.callback_query(F.data == "menu_dungeon")
async def show_dungeon_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval /start bosing!", show_alert=True)
        return

    max_floor = await get_dungeon_progress(char["id"])
    
    text = (
        "🗺 *VALORIYA TAQIQLANGAN ZINDONLARI (PVE REYDLAR)* 🗺\n\n"
        "Qadimgi zulmat kuchlari qit'a ostidagi g'orlarni egallab olgan.\n"
        "Har bir qavatda afsonaviy mahluqlar va qaroqchilar xazinalari yashiringan!\n\n"
        f"🏆 *Siz yetib borgan eng yuqori qavat:* {max_floor}-Qavat\n\n"
        "Qaysi qavatga tushishga jur'at qilasiz?"
    )

    buttons = []
    for floor_num, info in DUNGEON_FLOORS.items():
        is_unlocked = floor_num <= max_floor
        lock_icon = "⚔️" if is_unlocked else "🔒"
        status_txt = f"{info['name']} (Boss: {info['boss']})" if is_unlocked else f"{floor_num}-Qavat (Qulflangan)"
        
        callback_data = f"enter_dungeon_{floor_num}" if is_unlocked else "dungeon_locked"
        buttons.append([InlineKeyboardButton(text=f"{lock_icon} {floor_num}. {status_txt}", callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dungeon_router.callback_query(F.data == "dungeon_locked")
async def process_locked_dungeon(callback: CallbackQuery):
    await callback.answer("🔒 Ushbu qavat qulflangan! Avvalgi qavat bossini mag'lub etishingiz kerak.", show_alert=True)

@dungeon_router.callback_query(F.data.startswith("enter_dungeon_"))
async def process_enter_dungeon(callback: CallbackQuery):
    floor = int(callback.data.replace("enter_dungeon_", ""))
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return

    floor_info = DUNGEON_FLOORS.get(floor)
    if not floor_info:
        return

    # Bosqich jangi
    attacker = {
        "name": char["name"], "strength": char["strength"], "agility": char["agility"],
        "stamina": char["stamina"], "weapon_attack": 25, "is_defending": False
    }
    boss_hp = floor_info["hp"]
    defender = {
        "name": floor_info["boss"], "hp": boss_hp, "constitution": 20,
        "agility": 15, "stamina": 100, "armor_defense": 15, "is_defending": False
    }

    dmg1, log1, _ = BattleEngine.calculate_round(attacker, defender, "neck", "heavy_strike")
    dmg2, log2, _ = BattleEngine.calculate_round(attacker, defender, "torso", "skill")
    total_damage = dmg1 + dmg2

    # G'alaba yoki mag'lubiyat
    if total_damage >= boss_hp or random.random() < 0.7:
        await advance_dungeon_floor(char["id"], floor)
        await update_character(char["id"], gold=char["gold"] + floor_info["loot_gold"], xp=char["xp"] + floor_info["loot_xp"])
        
        res_text = (
            f"🎉 *ZINDON BOSSI YENGILDI!* 🏆\n\n"
            f"Siz *{floor}-Qavat* hukmdori **{floor_info['boss']}** ni dahshatli zarba bilan yer tishlatdingiz!\n\n"
            f"⚔️ Berilgan jami zarbalar: {total_damage} DMG!\n"
            f"💰 *Qo'lga Kiritilgan Xazina:* +{floor_info['loot_gold']} 🪙 Oltin | +{floor_info['loot_xp']} XP!\n\n"
            f"Keyingi qavat eshiklari ochildi!"
        )
    else:
        res_text = (
            f"🩸 *ZINDONDA OG'IR MAG'LUBIYAT!* 💀\n\n"
            f"**{floor_info['boss']}** o'zining o'lik quroli bilan zarbangizni qaytardi va sizni chekinishga majbur qildi!\n\n"
            f"Qurolbardoringiz Ser Artur sizni hushsiz holda zindondan olib chiqdi.\n"
            f"Kuch to'plab, qayta hujum qiling!"
        )

    buttons = [
        [InlineKeyboardButton(text="🗺 Zindonlar Ro'yxati", callback_data="menu_dungeon")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="menu_main")]
    ]
    await callback.message.edit_text(res_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
