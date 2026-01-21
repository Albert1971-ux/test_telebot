import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from deep_translator import GoogleTranslator


from config import API_TOKEN, CITY_NAME  # берем токен и город из config.py


logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет, бро! Я рабочий бот.\n"
        "Пока что я просто отвечаю на /start.\n"
        "Дальше добавим погоду, картинки, голос и перевод текста."
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Я умею:\n"
        "• /start — кратко рассказываю о себе.\n"
        "• /ping — показываю, что бот живой.\n"
        "• Фото — сохраняю картинку в папку img на сервере.\n"
        "• Голосовое — принимаю голос и отвечаю, что получил его.\n"
        "• Любой текст — перевожу на английский язык."
    )


@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("Бот живой, бро ✅")


@dp.message(F.photo)
async def save_photo(message: types.Message):
    photo = message.photo[-1]
    os.makedirs("img", exist_ok=True)
    file_name = f"{message.from_user.id}_{photo.file_id}.jpg"
    file_path = os.path.join("img", file_name)

    await bot.download(photo, destination=file_path)

    await message.answer(f"Фото сохранено в img/{file_name} ✅")


@dp.message(F.voice)
async def handle_voice(message: types.Message):
    await message.answer(
        "Голосовое сообщение получил 🎤\n"
        "Пока я его просто принимаю, без распознавания."
    )


@dp.message(F.text)
async def translate_to_english(message: types.Message):
    original_text = message.text
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(original_text)
        await message.answer(
            "Перевод на английский:\n"
            f"<b>{translated}</b>"
        )
    except Exception:
        await message.answer("Не получилось перевести текст 😔")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
