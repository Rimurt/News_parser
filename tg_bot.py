import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, BaseFilter
from ai import redacter
from db import session, News
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parser import parsing
import asyncio
import logging

load_dotenv()

token = os.getenv("BOT_TOKEN")
channel = str(os.getenv("CHANNEL_ID"))
chat = int(os.getenv("OWNER_ID")) #type:ignore

if token is None:
    raise ValueError("Не найден токен бота в переменной окружения BOT_TOKEN")


bot = Bot(token=token)
dp = Dispatcher()

class Owner(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == int(os.getenv("OWNER_ID")) #type:ignore

@dp.message(Owner(),Command("count"))
async def count_news(message: types.Message):
    not_posted = session.query(News).filter_by(posted=False).count()
    not_redacted = session.query(News).filter_by(content_is_redacted=False).count()
    redacted = session.query(News).filter_by(content_is_redacted=True).count()
    posted = session.query(News).filter_by(posted=True).count()
    await message.answer(f'''Текущие данные:
💹 Отправленных новостей: {posted}
🆕 Неотправленных новостей: {not_posted}
📜 Обработанных новостей: {redacted}
📄 Необработанных новостей: {not_redacted}
''')
    
async def send_post():
    await bot.send_message(chat_id=chat,text="📲 Идёт отправка обработаного поста")
    news = session.query(News).filter_by(posted=False, content_is_redacted=True).first()
    if not news:
        await bot.send_message(chat_id=chat,text="🗿 Постов для отправки нет")
        return
    await bot.send_photo(chat_id=channel, photo=news.image, caption=news.post_content) #type:ignore
    news.posted = True #type:ignore
    session.commit()

async def redac_content():
    chat = int(os.getenv("OWNER_ID")) #type:ignore
    await bot.send_message(chat_id=chat,text="💿 Идёт обработка новостей")
    red = redacter()
    if red is None:
        await bot.send_message(chat_id=chat,text="Новостей для обработки нет")
    elif red is Exception:
        await bot.send_message(chat_id=chat,text=f"⚠ Ошибка!!!\n {str(red)}")
    elif red == "corect":
        await bot.send_message(chat_id=chat,text="✅ Все посты обработаны")

async def try_parsing():
    await bot.send_message(chat_id=chat, text="🤖 Начинаю парсинг новостей...")
    result = await asyncio.to_thread(parsing)
    if result == "error":
        await bot.send_message(chat_id=chat,text="⚠ Не удалось запарсить, скорее всего бота заблокировало")
    elif isinstance(result, int):
        if result > 0:
            await bot.send_message(chat_id=chat, text=f"✅ Парсинг завершён. Добавлено новостей: {result}")
            await redac_content()
        else:
            await bot.send_message(chat_id=chat, text="ℹ️ Парсинг завершён. Новых новостей нет.")

@dp.message()
async def not_owner(message:types.Message):
    if message.from_user.id != int(os.getenv("OWNER_ID")): #type:ignore
        await message.answer("Ты кто? Доступа у тебя нет!")
        return

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_post, "interval", hours=2)
    scheduler.add_job(redac_content, "interval", hours=5)
    scheduler.add_job(try_parsing, "interval", hours=3)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
