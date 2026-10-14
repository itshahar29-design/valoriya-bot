import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import init_db

# Handlers import
from handlers.start_handler import start_router
from handlers.arena_handler import arena_router
from handlers.kingdom_handler import kingdom_router
from handlers.inventory_handler import inventory_router
from handlers.tavern_handler import tavern_router
from handlers.auction_pigeon_handler import auction_router
from handlers.top_handler import top_router
from handlers.owner_handler import owner_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    logging.info("🏰 Valoriya: Boqiy Qirolliklar Urushi tizimi ishga tushmoqda...")
    
    # 1. Initialize SQLite Database
    await init_db()
    logging.info("✅ Relyatsion ma'lumotlar bazasi va 12 imperiya muvaffaqiyatli ishga tushirildi.")

    if not BOT_TOKEN:
        logging.warning("⚠️ Diqqat: .env faylida BOT_TOKEN ko'rsatilmagan! Bot polling boshlanmadi, ammo barcha o'yin tizimlari va testlar to'liq tayyor.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routers registration
    dp.include_router(start_router)
    dp.include_router(arena_router)
    dp.include_router(kingdom_router)
    dp.include_router(inventory_router)
    dp.include_router(tavern_router)
    dp.include_router(auction_router)
    dp.include_router(top_router)
    dp.include_router(owner_router)

    logging.info("🚀 Telegram Bot Polling boshlandi! Qirollik eshiklari ochiq.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
