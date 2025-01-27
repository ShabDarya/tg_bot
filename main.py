import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from middlewares import LoggingMiddleware
from handlers import setup_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())
setup_handlers(dp)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
