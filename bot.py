import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

# ====== НАСТРОЙКИ

# Токен берём из переменной окружения, а не из кода — так безопасно.
# Перед запуском: set BOT_TOKEN=ваш-токен   (Windows cmd)
TOKEN = os.environ.get('BOT_TOKEN', '')

# Бронь отправляет мини-апп напрямую в Apps Script, поэтому боту ссылки
# на скрипт и на страницу не нужны. Единственный вход в мини-апп —
# кнопка меню «Бронирование», её адрес задаётся в @BotFather:
# Bot Settings → Menu Button → https://dazzling-tarsier-eb2361.netlify.app/?v=10
#
# На случай, если ссылки понадобятся снова:
# API_URL = 'https://script.google.com/macros/s/AKfycbwyUzCYsnpB8FBdNWM4KEWQD3qp-FTUUUP-QfveWIzGryXBMxpkvTRcTe3Jux-Rv71n1A/exec'
# WEBAPP_URL = 'https://dazzling-tarsier-eb2361.netlify.app/?v=10'

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        'Привет! Здесь бронируются слоты для команд на онлайн-пичти '
        'Академии Финтеха.\n\n'
        'Нажмите кнопку «Бронирование» внизу чата (рядом с полем ввода) — '
        'откроется окно, где нужно выбрать задачу, дату, время и указать '
        'название команды. Бронь запишется сразу, а подтверждение придёт '
        'сообщением от бота.',
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command('help'))
async def help_cmd(message: Message):
    await message.answer(
        '👋 Привет! Здесь бронируются слоты для команд на онлайн-пичти '
        'Академии Финтеха.\n\n'
        '📅 Как забронировать:\n'
        '1. Нажмите кнопку «Бронирование» внизу чата — откроется мини-апп.\n'
        '2. Выберите задачу, время и впишите название команды, Имя и контакт.\n'
        '3. Нажмите «Забронировать» и возвращайтесь в чат.\n'
        '⏳ Слот закрепляется только после отправки.\n'
        '🔄 Начать заново: /start',
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(F.text)
async def fallback(message: Message):
    """Любое обычное сообщение — мягко возвращаем к делу."""
    await message.answer(
        'Бронирование — через кнопку «Бронирование» внизу чата '
        '(рядом с полем ввода). Если её нет — отправьте /start.'
    )


async def main():
    print('Запущен актуальный bot.py: клавиатура отключена, вход — через кнопку меню')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
