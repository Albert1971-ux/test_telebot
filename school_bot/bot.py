import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN  # или API_TOKEN, если так названо в config.py


# ---------- БАЗА ДАННЫХ ----------

def init_db():
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            grade TEXT
        );
        """
    )

    conn.commit()
    conn.close()


def add_student(name: str, age: int, grade: str):
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, age, grade) VALUES (?, ?, ?);",
        (name, age, grade),
    )

    conn.commit()
    conn.close()


def get_all_students():
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, age, grade FROM students;")
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------- СОСТОЯНИЯ ДЛЯ ДИАЛОГА ----------

class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()


# ---------- НАСТРОЙКА БОТА ----------

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,  # если в config.py переменная называется API_TOKEN — напиши token=API_TOKEN
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Добавить ученика"),
        BotCommand(command="list", description="Показать всех учеников"),
    ]
    await bot.set_my_commands(commands)


# ---------- ХЕНДЛЕРЫ ----------

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет, бро! Давай запишу тебя в базу.\nКак тебя зовут?")
    await state.set_state(StudentForm.name)


@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    students = get_all_students()

    if not students:
        await message.answer("Пока ни одного ученика в базе нет, бро.")
        return

    lines = []
    for student_id, name, age, grade in students:
        lines.append(f"{student_id}. {name}, {age} лет, класс {grade}")

    text = "Ученики в базе:\n" + "\n".join(lines)
    await message.answer(text)


@dp.message(StudentForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет? Напиши числом.")
    await state.set_state(StudentForm.age)


@dp.message(StudentForm.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом. Попробуй ещё раз, бро.")
        return

    await state.update_data(age=int(message.text))
    await message.answer("В каком ты классе? Например: 5A или 9Б.")
    await state.set_state(StudentForm.grade)


@dp.message(StudentForm.grade)
async def process_grade(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)

    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    grade = data["grade"]

    try:
        add_student(name=name, age=age, grade=grade)
        await message.answer(
            f"Записал тебя в базу, бро ✅\n\n"
            f"Имя: <b>{name}</b>\n"
            f"Возраст: <b>{age}</b>\n"
            f"Класс: <b>{grade}</b>"
        )
    except Exception:
        logging.exception("Ошибка при сохранении в базу")
        await message.answer("Что-то пошло не так при сохранении в базу 😔")

    await state.clear()


# ---------- ЗАПУСК ----------

async def main():
    init_db()
    logging.info("DB INIT DONE")

    await set_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
