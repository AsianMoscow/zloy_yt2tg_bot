from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram import F
import yt_dlp

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASEURL")


bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- Функция извлечения ID из YouTube ссылки ---
def get_video_id(link: str) -> str | None:
    # Поддержка разных форматов ссылок
    import re
    patterns = [
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        if m := re.search(pattern, link):
            return m.group(1)
    return None


# --- Команда /start ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Отправь мне ссылку на YouTube-видео, а я дам ссылку на скачивание.")


# --- Обработка всех сообщений со ссылкой ---
@dp.message(F.text)
async def get_video(message: Message):
    url = message.text.strip()

    video_id = get_video_id(url)
    if not video_id:
        await message.answer("Это не похоже на ссылку YouTube 🙃")
        return

    # Папка для загрузок
    downloads_dir = os.getenv("DOWNLOADS", "downloads")

    # Создаем папку, если её нет
    os.makedirs(downloads_dir, exist_ok=True)

    output_path = os.path.join(downloads_dir, f"{video_id}.mp4")

    # Если файл уже скачан — не скачиваем снова
    if not os.path.exists(output_path):
        await message.answer("⏳ Скачиваю видео...")

        # Параметры скачивания
        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4/bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            await message.answer(f"Ошибка загрузки: {e}")
            return

    # Отдаём ссылку на скачивание
    download_link = f"{BASE_URL}/{video_id}"
    await message.answer(f"Готово!\n👉 {download_link}")


# --- Запуск ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
