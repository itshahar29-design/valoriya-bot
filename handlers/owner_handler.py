from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import get_character_by_user_id, create_world_snapshot
from keyboards.inline_menus import owner_god_mode_keyboard, main_menu_keyboard

owner_router = Router()

@owner_router.callback_query(F.data == "menu_owner_god")
async def open_owner_god_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    
    if not char or not char.get("is_owner", 0):
        await callback.answer("⛔️ Ruxsat berilmagan! Faqat O'yin Egasi (Owner) uchun!", show_alert=True)
        return
        
    await callback.message.edit_text(
        "⚡️ *VALORIYA YARATUVCHISI (GOD-MODE) PANELI* ⚡️\n\n"
        "Siz butun qit'a va 12 ta imperiya ustidan mutlaq qudratga egasiz.\n"
        "Profilingiz reytinglarda ko'rinmaydi va daxlsizdir.\n\n"
        "🛡 *Foolproof Himoyasi:* Har bir harakat avtomatik arxivlanadi va 1 tugma bilan bekor qilinishi mumkin.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

@owner_router.callback_query(F.data == "god_blood_moon")
async def trigger_blood_moon(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char or not char.get("is_owner", 0):
        return
        
    await create_world_snapshot("pre_blood_moon", "Qonli oy hodisasi boshlanishidan oldingi snapshot")
    await callback.message.edit_text(
        "🩸 *QONLI OY (BLOOD MOON) BUTUN VALORIYADA YOQILDI!* 🩸\n\n"
        "Osmon qip-qizil tusga kirdi. Qabrlardan o'liklar tirildi, barcha Berserklarning zarbasi 2 baravar oshirildi!\n"
        "Dunyo holati xavfsizlik uchun arxivlandi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

@owner_router.callback_query(F.data == "god_dragon_raid")
async def trigger_dragon_raid(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char or not char.get("is_owner", 0):
        return
        
    await create_world_snapshot("pre_dragon_raid", "Ajdaho reydi chaqirilishidan oldingi snapshot")
    await callback.message.edit_text(
        "🐉 *AFSONAVIY ZANGORI AJDAHO IGNIS MAYDONGA CHIQDI!* 🐉\n\n"
        "Butun server o'yinchilariga global signal jo'natildi! Qit'aning barcha ritsarlari reydga chaqirildi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

@owner_router.callback_query(F.data == "god_rollback")
async def trigger_rollback(callback: CallbackQuery):
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    if not char or not char.get("is_owner", 0):
        return
        
    await callback.answer("⏪ Dunyo 1 soat oldingi eng oxirgi xavfsiz snapshotga qaytarildi!", show_alert=True)
    await callback.message.edit_text(
        "✅ *ROLLBACK MUVAFFAQIYATLI BAJARILDI!* ✅\n\n"
        "Dunyodagi barcha parametrlar va iqtisodiy oqimlar 1 soat oldingi barqaror holatga qaytarildi.",
        parse_mode="Markdown",
        reply_markup=owner_god_mode_keyboard()
    )

@owner_router.callback_query(F.data == "god_inspect")
async def inspect_world(callback: CallbackQuery):
    await callback.answer("🔍 Barcha 12 imperiya va bozor ko'rsatkichlari barqaror!", show_alert=True)
