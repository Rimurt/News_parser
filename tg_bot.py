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

if token is None:
    raise ValueError("Не найден токен бота в переменной окружения BOT_TOKEN")


bot = Bot(token=token)
dp = Dispatcher()

class Owner(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == int(os.getenv("OWNER_ID")) #type:ignore

@dp.message(Owner(),Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет, хозяин!")


async def send_post():
    chat = int(os.getenv("OWNER_ID")) #type:ignore
    await bot.send_message(chat_id=chat,text="Идёт отправка обработаного поста")
    news = session.query(News).filter_by(posted=False, content_is_redacted=True).first()
    if not news:
        await bot.send_message(chat_id=chat,text="Постов для отправки нет")
        return
    await bot.send_photo(chat_id=channel, photo=news.image, caption=news.post_content) #type:ignore
    news.posted = True #type:ignore
    session.commit()

async def redac_content():
    chat = int(os.getenv("OWNER_ID")) #type:ignore
    await bot.send_message(chat_id=chat,text="Идёт обработка новостей")
    red = redacter()
    if red is None:
        await bot.send_message(chat_id=chat,text="Новостей для обработки нет")
    elif red is Exception:
        await bot.send_message(chat_id=chat,text=f"Ошибка!!!\n {str(red)}")
    elif red == "corect":
        await bot.send_message(chat_id=chat,text="Все посты обработаны")

async def try_parsing():
    chat = int(os.getenv("OWNER_ID"))#type:ignore
    result = parsing()
    if result == "error":
        await bot.send_message(chat_id=chat,text="Не удалось запарсить, скорее всего бота заблокировало")
    elif result == "ok":
        await bot.send_message(chat_id=chat,text="Боту удалось спарсить новости!")

@dp.message()
async def not_owner(message:types.Message):
    if message.from_user.id != int(os.getenv("OWNER_ID")): #type:ignore
        await message.answer("Ты кто? Доступа у тебя нет!")
        return

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_post, "interval", hours=3)
    scheduler.add_job(redac_content, "interval", hours=6)
    scheduler.add_job(try_parsing, "interval", hours=5)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


