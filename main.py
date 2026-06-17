# main.py
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import offer
import os

load_dotenv()
toke = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=toke)
    dp = Dispatcher()

    dp.include_router(offer)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())