import logging
from aiogram import Bot
from database.db import get_setting, set_setting
from config import OWNER_ID, OWNER_USERNAME

async def get_required_channel() -> str:
    channel = await get_setting("required_channel", "")
    return channel.strip()

async def is_subscribed_to_channel(bot: Bot, user_id: int, username: str | None = None) -> tuple[bool, str]:
    """
    Foydalanuvchining majburiy kanalga a'zo ekanligini tekshiradi.
    (True, channel_username) yoki (False, channel_username) qaytaradi.
    """
    # 1. Owner har doim ruxsatga ega
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True, ""
    if OWNER_ID and user_id == OWNER_ID:
        return True, ""

    channel = await get_required_channel()
    if not channel:
        return True, ""

    # @ belgisini to'g'irlash
    formatted_channel = channel if channel.startswith("@") or channel.startswith("-100") else f"@{channel}"

    try:
        member = await bot.get_chat_member(chat_id=formatted_channel, user_id=user_id)
        if member.status in ["creator", "administrator", "member", "restricted"]:
            return True, formatted_channel
        return False, formatted_channel
    except Exception as e:
        # Agar bot kanalda admin bo'lmasa yoki kanal topilmasa, o'yin to'xtab qolmasligi uchun o'tkazib yuboradi
        logging.warning(f"Kanal a'zoligini tekshirishda xatolik ({formatted_channel}): {e}")
        return True, formatted_channel
