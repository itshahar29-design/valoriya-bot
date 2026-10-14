from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_character_by_user_id, update_character
from game.constants import KINGDOMS
from game.emotions_engine import EmotionsEngine
from keyboards.inline_menus import main_menu_keyboard

kingdom_router = Router()

class DiplomacyState(StatesGroup):
    waiting_for_speech = State()

@kingdom_router.callback_query(F.data == "menu_kingdoms")
async def show_kingdoms_list(callback: CallbackQuery):
    buttons = []
    # 12 ta qirollik tugmalari
    for k_id, k_data in KINGDOMS.items():
        buttons.append([
            InlineKeyboardButton(text=f"{k_data['name']}", callback_data=f"view_k_{k_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="menu_main")])
    
    await callback.message.edit_text(
        "🏰 *VALORIYA QIT'ASINING 12 BUYUK AI IMPERIYASI* 🏰\n\n"
        "Har bir imperiya o'z mustaqil aqli, armiyasi, boyligi va hukmdoriga ega. "
        "Birini tanlab, uning saroyiga tashrif buyuring:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@kingdom_router.callback_query(F.data.startswith("view_k_"))
async def view_single_kingdom(callback: CallbackQuery):
    k_id = callback.data.replace("view_k_", "")
    k = KINGDOMS.get(k_id)
    if not k:
        return
        
    text = (
        f"👑 *{k['name']}* 👑\n\n"
        f"🏛 *Poytaxti:* {k['capital']}\n"
        f"👤 *Hukmdori:* {k['ruler']}\n"
        f"📜 *Shiori:* _{k['motto']}_\n"
        f"⚔️ *Harbiy Ustunligi:* {k['specialty']}\n"
        f"🎙 *Ovoz Uslubi:* _{k['voice_style']}_\n\n"
        f"Qanday qarorga kelasiz?"
    )
    
    buttons = [
        [InlineKeyboardButton(text="🍯 Hukmdorga Paxta Qo'yish (Diplomatiya)", callback_data=f"flatter_{k_id}")],
        [InlineKeyboardButton(text="⚔️ Sadoqat Qasamyodi Qilish", callback_data=f"swear_oath_{k_id}")],
        [InlineKeyboardButton(text="⬅️ Barcha Qirolliklar", callback_data="menu_kingdoms")]
    ]
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@kingdom_router.callback_query(F.data.startswith("flatter_"))
async def start_flattery(callback: CallbackQuery, state: FSMContext):
    k_id = callback.data.replace("flatter_", "")
    k = KINGDOMS.get(k_id)
    await state.update_data(target_kingdom=k_id)
    await state.set_state(DiplomatiyaState.waiting_for_speech)
    
    await callback.message.edit_text(
        f"👑 *{k['ruler']} HUZURIDA AUDIENTSIYA* 👑\n\n"
        f"Hukmdor taxtda o'tirib sizga qarab turibdi.\n\n"
        f"✍️ *Unging sha'niga nima deysiz?* (Quyida xabaringizni yozib jo'nating):\n"
        f"_(Masalan: 'Ey adolatli va yengilmas buyuk shohim, qilichingiz quyoshdek porlasin...')_",
        parse_mode="Markdown"
    )

class DiplomatiyaState(StatesGroup):
    waiting_for_speech = State()

@kingdom_router.message(DiplomatiyaState.waiting_for_speech)
async def process_flattery_speech(message: Message, state: FSMContext):
    data = await state.get_data()
    k_id = data.get("target_kingdom", "lionguard")
    speech_text = message.text
    await state.clear()
    
    result = EmotionsEngine.evaluate_player_speech(k_id, speech_text)
    user_id = message.from_user.id
    char = await get_character_by_user_id(user_id)
    
    if char and result["reward_gold"] > 0:
        await update_character(char["id"], gold=char["gold"] + result["reward_gold"], honor=char["honor"] + 10)
        
    await message.answer(
        f"{result['reply']}\n\n"
        f"📊 *Sizning munosabatingiz:* {result['affection_change']:+d} ball\n"
        f"💰 *Mukofot:* +{result['reward_gold']} Oltin",
        reply_markup=main_menu_keyboard(bool(char.get("is_owner", 0) if char else False))
    )

@kingdom_router.callback_query(F.data.startswith("swear_oath_"))
async def swear_oath(callback: CallbackQuery):
    k_id = callback.data.replace("swear_oath_", "")
    k = KINGDOMS.get(k_id)
    user_id = callback.from_user.id
    char = await get_character_by_user_id(user_id)
    
    if not char:
        return
        
    if char["level"] < 3:
        await callback.answer("⚠️ Qasamyod qilish uchun kamida 3-daraja bo'lishingiz kerak!", show_alert=True)
        return
        
    await update_character(char["id"], kingdom_id=k_id, honor=char["honor"] + 50)
    await callback.message.edit_text(
        f"⚡️ *MUQADDAS QASAMYOD QABUL QILINDI!* ⚡️\n\n"
        f"Siz *{k['name']}* bayrog'i ostida xizmat qilishga qasamyod qildingiz!\n\n"
        f"Hukmdor {k['ruler']} sizni qirollik ritsari sifatida e'tirof etdi va har soatlik soliq maoshi tayinladi.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(bool(char.get("is_owner", 0)))
    )
