import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import generate_shop_image  # не забудь, utils возвращает FSInputFile

API_URL = "https://fortnite-api.com/v2/shop"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
scheduler = AsyncIOScheduler()

# Переменная с кэшем изображения
cached_image = None

# Получение данных из API Fortnite
def fetch_shop_data():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()['data']
    categories = []
    for cat_key in ['featured', 'daily', 'specialFeatured', 'specialDaily']:
        if cat_key in data and data[cat_key]['entries']:
            categories.append({
                'name': cat_key.capitalize(),
                'entries': data[cat_key]['entries']
            })
    return categories

# Обновление кэша изображения
async def update_shop_image():
    global cached_image
    try:
        categories = await asyncio.to_thread(fetch_shop_data)
        img_file = await asyncio.to_thread(generate_shop_image, categories)
        cached_image = img_file
        print("✅ Shop image updated")
    except Exception as e:
        print("❌ Failed to update shop image:", e)

# Команда /shop
@router.message(Command("shop"))
async def send_shop(message: Message):
    if cached_image:
        await message.answer_photo(photo=cached_image)
    else:
        await message.answer("Магазин ещё не загружен. Попробуйте позже.")

# Инициализация при старте
async def on_startup():
    await update_shop_image()
    scheduler.add_job(update_shop_image, 'cron', hour=3)
    scheduler.start()
    print("⏰ Scheduler started")

# Основной запуск
async def main():
    dp.include_router(router)
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
