import os
import asyncio
import logging
from aiohttp import web
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
from handlers.group_handler import group_router
from handlers.chat_ai_handler import chat_router
from handlers.daily_handler import daily_router
from handlers.forge_handler import forge_router
from handlers.dungeon_handler import dungeon_router
from game.npc_broadcaster import npc_periodic_broadcaster_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start_web_server():
    """Render.com Free Tier Web Service uchun mini HTTP server"""
    async def handle_ping(request):
        return web.Response(text="👑 Valoriya: Boqiy Qirolliklar Urushi 24/7 ishlab turibdi!")

    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"🌐 Bepul Web Server {port}-portda ishga tushdi.")

async def main():
    logging.info("🏰 Valoriya: Boqiy Qirolliklar Urushi tizimi ishga tushmoqda...")
    
    # 1. Initialize SQLite Database
    await init_db()
    logging.info("✅ Relyatsion ma'lumotlar bazasi va 12 imperiya muvaffaqiyatli ishga tushirildi.")

    # 2. Start lightweight web server for Render Free Web Service tier
    await start_web_server()

    if not BOT_TOKEN:
        logging.warning("⚠️ Diqqat: .env faylida BOT_TOKEN ko'rsatilmagan! Bot polling boshlanmadi, ammo barcha o'yin tizimlari va testlar to'liq tayyor.")
        # Agar token qo'yilmagan bo'lsa ham web server to'xtab qolmasligi uchun kutib turadi
        while True:
            await asyncio.sleep(3600)
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
    dp.include_router(daily_router)
    dp.include_router(forge_router)
    dp.include_router(dungeon_router)
    dp.include_router(owner_router)
    dp.include_router(group_router)
    dp.include_router(chat_router)

    logging.info("🚀 Telegram Bot Polling boshlandi! Qirollik eshiklari ochiq.")
    # Start autonomous periodic NPC broadcaster
    asyncio.create_task(npc_periodic_broadcaster_loop(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
