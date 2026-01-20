import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties  # <- ДОБАВИЛИ ЭТО

API_TOKEN = "7967873974:AAGWPbhnHjQ-Yjvg3QIPH2eBz1TtiMv5Sco"
WEATHER_API_KEY = "0b19c70f069eb509882e45bc89f535ce"
CITY = "Syktyvkar"

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # <- ВОТ ТАК ТЕПЕРЬ
)
dp = Dispatcher()



@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет, бро! Я бот-прогноз погоды для Сыктывкара.\n"
        "Нажми /help, чтобы узнать, что я умею."
    )


@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать это сообщение\n"
        "/weather - показать текущую погоду в Сыктывкаре"
    )


@dp.message(Command(commands=["weather"]))
async def cmd_weather(message: Message):
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        )
        response = requests.get(url, timeout=10)
        print("STATUS:", response.status_code)
        print("TEXT:", response.text)

        data = response.json()

        if data.get("cod") != 200:
            await message.answer(f"Ошибка от сервиса погоды: {data.get('message', 'неизвестно')}")
            return

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]

        await message.answer(
            f"Погода в {CITY}:\n"
            f"🌡 Температура: {temp}°C\n"
            f"🌥 Условия: {description}"
        )
    except Exception as e:
        await message.answer("Произошла ошибка при получении погоды.")
        print("EXCEPTION:", e)



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


