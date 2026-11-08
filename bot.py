import asyncio
import json

import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

# ====== НАСТРОЙКИ

import os
TOKEN = os.environ.get('BOT_TOKEN', '')
API_URL = 'https://script.google.com/macros/s/AKfycbx6ofCXATpfw414ebLe5etnm5-X6x00UM_FdRqPQyGXZYcc9N5vghSyf56jkScsizgohQ/exec';  # ссылка из script.google
WEBAPP_URL = 'https://dazzling-tarsier-eb2361.netlify.app/?v=6' # ссылка из Netlify

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(
            text='Забронировать',
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]],
    )
    await message.answer(
        'Привет! Здесь бронируются слоты для команд на онлайн-пичти Академии Финтеха.\n\n'
        'Нажмите кнопку «Забронировать», выберите задачц, '
        'дату и время — бронь запишется сразу из мини-аппа.',
        reply_markup=kb,
    )


@dp.message(Command('help'))
async def help_cmd(message: Message):
    await message.answer(
      
        '👋 Привет! Здесь бронируются слоты для команд на онлайн-пичти Академии Финтеха.\n\n'
        '📅 Как забронировать:\n'
        '1. Нажмите кнопку «Забронировать» слева — откроется мини-апп.\n'
        '2. Выберите задачу, время и впишите название команды, Имя и контакт.\n'
        '3. Нажмите «Забронировать» и возвращайтесь в чат.\n'
        '⏳ Слот закрепляется только после отправки.\n'
        '🔄 Начать заново: /start'
    )


@dp.message(F.text)
async def fallback(message: Message):
    """Любое обычное сообщение — мягко возвращаем к делу."""
    await message.answer(
        'Бронирование — через мини-апп: нажмите кнопку «Забронировать» '
        'или отправьте /start.'
    )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
