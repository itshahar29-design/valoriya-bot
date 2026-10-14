from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    get_character_by_user_id, get_character_equipment,
    auto_equip_best, repair_all_items, dismantle_junk
)
from keyboards.inline_menus import inventory_qol_keyboard, main_menu_keyboard
from game.constants import EQUIPMENT_SLOTS
from game.dark_engine import DarkEngine
import json

inventory_router = Router()

@inventory_router.callback_query(F.data == "menu_inventory")
async def show_inventory_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        await callback.answer("Avval ro'yxatdan o'ting!", show_alert=True)
        return
        
    items = await get_character_equipment(char["id"])
    equipped = {i["slot_type"]: i for i in items if i["is_equipped"] == 1}
    
    slots_text = []
    for slot_key, slot_name in EQUIPMENT_SLOTS:
        item = equipped.get(slot_key)
        if item:
            durability_str = f"({item['durability']}/{item['max_durability']}🛡)"
            if item["durability"] <= 0:
                durability_str = "(💥 SINIQ - 0🛡)"
            slots_text.append(f"• *{slot_name}:* {item['item_name']} {durability_str}")
        else:
            slots_text.append(f"• *{slot_name}:* _Bo'sh_")
            
    sanity = char.get("sanity", 100)
    badge, _, _ = DarkEngine.get_sanity_status(sanity)
    
    wounds_count = 0
    try:
        w_raw = char.get("wounds_json", "[]")
        w_list = json.loads(w_raw) if isinstance(w_raw, str) else list(w_raw)
        wounds_count = len(w_list)
    except Exception:
        pass

    wound_alert = f" | 🩸 *Travmalar:* {wounds_count} ta" if wounds_count > 0 else ""

    text = (
        f"🎒 *{char['name']} NING 8-SLOTLI ANJOMLARI* 🎒\n\n"
        f"🪙 Oltin: *{char['gold']:,}* | 💎 Yoqut: *{char['gems']}*\n"
        f"❤️ HP: *{char['hp']}/{char['max_hp']}* | ⚡️ Stamina: *{char['stamina']}/100*\n"
        f"🧠 Sanity: *{sanity}%* [{badge}]{wound_alert}\n"
        f"🐎 Ot: *{char['horse_name']}* ({char['horse_bond']}% bog'lanish)\n\n"
        + "\n".join(slots_text) + "\n\n"
        "⚡️ *Tezkor Qulayliklar (QoL):*"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=inventory_qol_keyboard())

@inventory_router.callback_query(F.data == "qol_auto_equip")
async def handle_auto_equip(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    count = await auto_equip_best(char["id"])
    await callback.answer(f"👑 {count} ta eng kuchli anjom avtomatik kiyildi!", show_alert=True)
    await show_inventory_menu(callback)

@inventory_router.callback_query(F.data == "qol_repair_all")
async def handle_repair_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    success, cost, msg = await repair_all_items(char["id"], char["gold"])
    await callback.answer(msg, show_alert=True)
    await show_inventory_menu(callback)

@inventory_router.callback_query(F.data == "qol_dismantle_junk")
async def handle_dismantle_junk(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char:
        return
        
    count, gold = await dismantle_junk(char["id"])
    if count == 0:
        await callback.answer("Eritish uchun keraksiz oddiy o'lja yo'q!", show_alert=True)
    else:
        await callback.answer(f"♻️ {count} ta keraksiz o'lja eritilib, +{gold} Oltin olindi!", show_alert=True)
    await show_inventory_menu(callback)

@inventory_router.callback_query(F.data == "menu_main")
async def return_to_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    is_owner = bool(char.get("is_owner", 0)) if char else False
    
    await callback.message.edit_text(
        f"👑 *BOSH HARBIY QARORGOH* 👑\n\n"
        f"Valoriya qit'asida qanday buyruq berasiz?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_owner)
    )
