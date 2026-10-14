from aiogram import Router, F
from aiogram.types import Message
from database.db import get_character_by_user_id
from keyboards.inline_menus import (
    main_menu_keyboard, arena_menu_keyboard, kingdom_list_keyboard,
    inventory_qol_keyboard, owner_god_mode_keyboard
)
from config import OWNER_ID, OWNER_USERNAME

chat_router = Router()

def is_owner_user(user_id: int, username: str | None) -> bool:
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and user_id == OWNER_ID:
        return True
    return False

@chat_router.message(F.text)
async def handle_natural_chat(message: Message):
    # Agar komanda bo'lsa (masalan /start), uni o'z handleri ushlaydi
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text.lower().strip()
    
    char = await get_character_by_user_id(user_id)
    if not char:
        await message.answer(
            "⚔️ *Ser Artur (Qurolbardoringiz):*\n\n"
            "'Hazratim, siz hali ritsarlik qasamyodini qabul qilmadingiz! "
            "Iltimos, avval /start buyrug'ini bering va o'z harbiy sinfingizni tanlang!'",
            parse_mode="Markdown"
        )
        return

    is_owner = bool(char.get("is_owner", 0)) or is_owner_user(user_id, username)

    # 1. ARENA VA JANG INTENTLARI
    if any(k in text for k in ["jang", "arena", "duel", "urush", "urushmoq", "raqib", "chopish", "fight"]):
        await message.answer(
            f"⚔️ *Ser Artur:* 'Qilichingiz qon talab qilmoqda, {char['name']}! Arenada sizning darajangizga munosib dushman kutmoqda!'",
            parse_mode="Markdown",
            reply_markup=arena_menu_keyboard()
        )
        return

    # 2. INVENTAR VA SOVUT INTENTLARI
    if any(k in text for k in ["inventar", "sumka", "qurol", "sovut", "qalqon", "kiyin", "bag", "items"]):
        await message.answer(
            f"🎒 *Ser Artur:* 'Zarur qurol-aslahalaringizni ko'zdan kechiramiz, hazratim. Barcha 8 ta sovut joy-joyidami?'",
            parse_mode="Markdown",
            reply_markup=inventory_qol_keyboard()
        )
        return

    # 3. QIROLLIKLAR VA DIPLOMATIYA INTENTLARI
    if any(k in text for k in ["qirollik", "shahar", "imperiya", "sulton", "qirol", "diplomatiya", "saroy"]):
        await message.answer(
            f"🏰 *Ser Artur:* 'Valoriya qit'asining 12 ta qudratli imperiyasi! Qaysi hukmdor huzuriga elchi yuboramiz?'",
            parse_mode="Markdown",
            reply_markup=kingdom_list_keyboard()
        )
        return

    # 4. TAVERNA INTENTLARI
    if any(k in text for k in ["taverna", "ichish", "dam", "pivo", "dam olish", "charchadim", "tavern"]):
        await message.answer(
            f"🍻 *Ser Artur:* 'Charchadingizmi, ser? 'Qonli Qadah' tavernasiga o'tamiz, u yerda issiq ovqat va dervishlar bor!'",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(is_owner)
        )
        return

    # 5. REYTING INTENTLARI
    if any(k in text for k in ["reyting", "top", "chempion", "kuchli", "kim birinchi"]):
        from handlers.top_handler import get_top_knights
        top_knights = await get_top_knights()
        res = "🏆 *VALORIYA ENG KUCHLI RITSARLARI* 🏆\n\n"
        for i, k in enumerate(top_knights[:5], 1):
            res += f"{i}. ⚔️ *{k['name']}* | Daraja: {k['level']} | G'alaba: {k['wins']}\n"
        await message.answer(res, parse_mode="Markdown", reply_markup=main_menu_keyboard(is_owner))
        return

    # 6. GOD-MODE INTENTLARI (Faqat Owner uchun)
    if is_owner and any(k in text for k in ["god", "yaratuvchi", "admin", "qonli oy", "ajdaho", "rollback"]):
        await message.answer(
            "👑 *Ser Artur (Tiz cho'kib):*\n\n"
            "'Ta'zimdaman, Oliy Yaratuvchi! Butun Valoriya qit'asi va 12 ta imperiya sizning amringizga muntazir!'",
            parse_mode="Markdown",
            reply_markup=owner_god_mode_keyboard()
        )
        return

    # 7. UMUMIY SUHBAT VA NATURAL CHAT ROLEPLAY
    # Foydalanuvchi bilan jonli suhbat qurish:
    if is_owner:
        owner_prefix = "👑 *Oliy Yaratuvchim*"
        greeting = f"{owner_prefix}, buyrug'ingizni eshitaman! Dunyoda har bir imperiya sizning irodangiz bilan nafas olmoqda."
    else:
        greeting = f"Ser *{char['name']}*, sizning sadoqatli qurolbardoringiz Ser Artur xizmatingizda!"

    # Dinamik maslahat
    advice = ""
    if char["hp"] < 50:
        advice = "\n\n⚠️ *Eslatma:* Joningiz kam qolibdi! Arenaga kirmasdan oldin Tavernada quvvatni tiklab oling."
    elif char["gold"] >= 500:
        advice = "\n\n💰 *Maslahat:* Xazinangizda ancha oltin yig'ilibdi! Auksiondan noyob zangori qilich xarid qilishni tavsiya qilaman."
    else:
        advice = "\n\n⚔️ Bugun Arenada 3 ta g'alaba qozonsangiz, Boychibor tulpuringizning sadoqati oshadi!"

    await message.answer(
        f"🗣 *Ser Artur:* \"{message.text}\" — dedingizmi, hazratim?\n\n"
        f"{greeting}{advice}\n\n"
        f"Qayerga yo'l olamiz?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_owner)
    )
