import os
import io
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import generate_shop_image

API_URL = "https://fortnite-api.com/v2/shop"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

cached_image = None

async def fetch_shop_data():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()['data']
    # Формируем список категорий с их товарами
    categories = []
    for cat_key in ['featured', 'daily', 'specialFeatured', 'specialDaily']:
        if cat_key in data and data[cat_key]['entries']:
            categories.append({
                'name': cat_key.capitalize(),
                'entries': data[cat_key]['entries']
            })
    return categories

async def update_shop_image():
    global cached_image
    try:
        categories = await asyncio.to_thread(fetch_shop_data)
        img_bytes = await asyncio.to_thread(generate_shop_image, categories)
        cached_image = img_bytes
        print("Shop image updated")
    except Exception as e:
        print("Failed to update shop image:", e)

@dp.message_handler(commands=['shop'])
async def send_shop(message: types.Message):
    if cached_image:
        await message.answer_photo(cached_image)
    else:
        await message.answer("Магазин ещё не загружен. Попробуйте позже.")

async def on_startup(_):
    await update_shop_image()
    scheduler.add_job(update_shop_image, 'cron', hour=3)
    scheduler.start()
    print("Scheduler started")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
