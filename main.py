from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASEURL", "https://asian-vpn.ru")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DOWNLOADS = "/home/telegram_bot/bots/zloy_yt2tg_bot/downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

@dp.message(Command(commands=["start"]))
async def start(message: Message):
    await message.answer("Привет! Отправь мне ссылку на YouTube, я скачаю видео и дам ссылку.")

@dp.message()
async def download_video(message: Message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        return await message.answer("Это не похоже на ссылку YouTube.")

    try:
        # Получаем ID видео и название
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id")
            title = info.get("title")

        filepath = os.path.join(DOWNLOADS, f"{video_id}.mp4")

        # Отправляем сообщение о скачивании
        msg = await message.answer(f"Скачиваю видео: {title}...")

        # Скачиваем только если файла нет
        if not os.path.exists(filepath):
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": filepath,
                "merge_output_format": "mp4"
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        # Удаляем сообщения
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id)

        # Отправляем один пост с иконками
        text = (
            f"🎬 Ссылка на оригинальный YouTube:\n{url}\n\n"
            f"💾 Ссылка на скачанное видео:\n{BASE_URL}/{video_id}"
        )
        await message.answer(text)

    except Exception as e:
        await message.answer(f"Ошибка при скачивании видео:\n{e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
