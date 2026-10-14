import random
import asyncio
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_active_groups
from game.constants import BOT_TITLES, BOT_FIRST_NAMES, BOT_EPITHETS

# Guruhda kutilmagan o'ljalar uchun xotira
ACTIVE_DROPS = {}

class NPCBroadcaster:
    @staticmethod
    def generate_spontaneous_event():
        """
        Guruh uchun tasodifiy jonli NPC voqeasi va interaktiv tugmasini yaratadi.
        """
        event_type = random.choice(["challenge", "dervish_drop", "tavern_rumor", "royal_decree"])
        
        # 1. KUTILMAGAN RITSAR CHAQIRUVI (DUEL CHALLENGE)
        if event_type == "challenge":
            title = random.choice(BOT_TITLES)
            name = random.choice(BOT_FIRST_NAMES)
            ep = random.choice(BOT_EPITHETS)
            npc_name = f"{title} {name} {ep}"
            lvl = random.randint(2, 6)
            bounty = lvl * 60

            text = (
                f"⚔️ *KUTILMAGAN DUEL CHAQIRUVI!* 🚪\n\n"
                f"Maydonga *{npc_name}* (Lvl {lvl}) bostirib kirdi!\n\n"
                f"🗣 *'{npc_name}':* \"Hey, bu guruhdagi barcha ritsarlar qo'rqoqmi?! "
                f"Kim maydonga chiqib men bilan kuch sinashadi? Yiqitsangiz, {bounty} Oltin sizniki!\"\n\n"
                f"Maydonda kim birinchi zarbani beradi?"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Maydonga Chiqish!", callback_data=f"gfight_npc_0_{lvl}_berserk")]
            ])
            return text, keyboard

        # 2. DARVESH TEZROQ BOSISH O'LJASI (DOPAMINE SPEED DROP)
        elif event_type == "dervish_drop":
            gold_amount = random.randint(50, 150)
            drop_id = f"drop_{random.randint(1000, 9999)}"
            ACTIVE_DROPS[drop_id] = {"gold": gold_amount, "claimed": False}

            text = (
                f"🔮 *DARVESH SALMON GURUHGA TASHRIF BUYURDI!* 🔮\n\n"
                f"\"Ey saxovatli va jasur zotlar! Men Valoriya yo'llarida yurib, bir xalta sof tillo tangalar topdim.\n"
                f"Qaysi ritsarning qo'li epchil bo'lsa, xazina o'shaniki bo'lsin!\"\n\n"
                f"💰 *Mukofot:* +{gold_amount} Oltin!\n"
                f"⚡️ Kim birinchi bo'lib tugmani bossa, oltinni oladi!"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎁 Oltinni Birinchi Bo'lib Olish!", callback_data=f"claim_dervish_{drop_id}")]
            ])
            return text, keyboard

        # 3. TAVERNA MISH-MISHLARI (TAVERN RUMORS)
        elif event_type == "tavern_rumor":
            rumors = [
                "Qonli Qoya o'rmonlarida qadimiy zangori ajdaho ko'rindi degan gaplar yuribdi... Ritsarlar qurollarini shaylamoqda!",
                "Bugun kechasi 'Qonli Qadah' tavernasiga yangi asalli qora pivo keltirildi! Jangchilarga jon bag'ishlaydi!",
                "Sulton Arslonxon Arenada eng ko'p g'alaba qozongan ritsarga 1000 tillo tanga mukofot va'da qildi!",
                "Auksionda afsonaviy Valoriya qilichlari savdoga qo'yilgani haqida xabarlar kelmoqda."
            ]
            text = (
                f"🍻 *TAVERNA XABARCHISI OTTO SHOVQIN SOLMOQDA:* 🍻\n\n"
                f"\"{random.choice(rumors)}\"\n\n"
                f"Barcha jangchilar diqqatiga: kuchingizni sinab ko'rish uchun `!duel` yoki `!boss` deb yozing!"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Maydonga Chiqish", callback_data="gfight_npc_0_2_defender")]
            ])
            return text, keyboard

        # 4. QIROLLIK SULTONI FARMONI (ROYAL DECREE)
        else:
            text = (
                f"📜 *IMPERATOR VALTER V SULTONLIK E'LONI!* 📜\n\n"
                f"\"Valoriya qit'asining barcha sarhadlarida xizmat qilayotgan jasur ritsarlar!\n"
                f"Kim bugun o'z botirligini ko'rsatib, 12 ta imperiya sharafini himoya qilsa, "
                f"uning ismi imperiya oltin kitobiga yoziladi!\"\n\n"
                f"Qasamyod qilish uchun botga kiring: [@ValoriyaRpgBot](https://t.me/ValoriyaRpgBot)"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👑 Qirollik Xizmati", url="https://t.me/ValoriyaRpgBot")]
            ])
            return text, keyboard

    @staticmethod
    async def send_broadcast_to_all_groups(bot: Bot):
        """
        Bot ulangan barcha faol guruhlarga kutilmagan jonli xabarni yuboradi.
        """
        groups = await get_active_groups()
        if not groups:
            logging.info("Hozircha faol guruhlar mavjud emas.")
            return

        text, keyboard = NPCBroadcaster.generate_spontaneous_event()
        
        for g in groups:
            try:
                await bot.send_message(
                    chat_id=g["chat_id"],
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                logging.info(f"NPC xabari guruhga yuborildi: {g['title']} ({g['chat_id']})")
                await asyncio.sleep(1) # Flood wait oldini olish
            except Exception as e:
                logging.warning(f"Guruhga yuborishda xatolik ({g['chat_id']}): {e}")

async def npc_periodic_broadcaster_loop(bot: Bot):
    """
    Har 15-25 daqiqada bir marta guruhlarga avtonom ravishda xabar yozib turadigan tsikl.
    """
    # Bot ishga tushgach 45 soniyadan keyin birinchi salomlashuv
    await asyncio.sleep(45)
    
    while True:
        try:
            await NPCBroadcaster.send_broadcast_to_all_groups(bot)
        except Exception as e:
            logging.error(f"Broadcaster tsiklida xatolik: {e}")
            
        # Keyingi xabar oralig'i: 15 daqiqadan 25 daqiqagacha tasodifiy vaqt
        interval = random.randint(900, 1500)
        logging.info(f"Keyingi avtomatik NPC xabari {interval // 60} daqiqadan so'ng yuboriladi.")
        await asyncio.sleep(interval)
