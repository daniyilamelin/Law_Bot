from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import asyncio
from aiogram import Dispatcher, Bot
from handlers import offer
import os

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST") 
WEBHOOK_PATH = f"/webhook/{os.getenv('BOT_TOKEN')}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


bot = Bot(token = os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def on_startup(app):
    dp.include_router(offer)
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

async def healthcheck(request):
    return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    return app

if __name__ == '__main__':
    async def start():
        app = await main()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
        await site.start()
        await asyncio.Event().wait()
    
    asyncio.run(start())
