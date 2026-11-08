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
API_URL = 'https://script.google.com/macros/s/AKfycby4umdZTbo51qy6HYdXRFXjeRfR0aq_SHEY5lV_3s4scbolsLrNKvUs-aK9UEdWMnzyVw/exec';
WEBAPP_URL = 'https://dazzling-tarsier-eb2361.netlify.app'  # ссылка из шага 4 (Netlify/Vercel)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Незавершённые брони: {user_id: {'sheet', 'row', 'team', 'date', 'time'}}
pending = {}


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
        'Привет! Здесь бронируются слоты для команд.\n'
        'Нажмите кнопку «Забронировать», выберите направление и время.',
        reply_markup=kb,
    )


@dp.message(Command('help'))
async def help_cmd(message: Message):
    pending.pop(message.from_user.id, None)
    await message.answer(
        '👋 Привет! Здесь бронируются слоты для команд.\n\n'
        '📅 Как забронировать:\n'
        '1. Нажмите кнопку «Забронировать» слева — откроется мини-апп.\n'
        '2. Выберите направление, время и впишите название команды.\n'
        '3. Нажмите «Забронировать» — вернётесь в чат.\n'
        '4. Нажмите «Поделиться контактом 📱» — и слот ваш.\n\n'
        '⏳ Слот закрепляется только после отправки контакта.\n'
        '🔄 Начать заново: /start'
    )


@dp.message(F.web_app_data)
async def got_slot(message: Message):
    """Мини-апп прислал выбранный слот + название команды."""
    try:
        data = json.loads(message.web_app_data.data)
        sheet = str(data['sheet'])
        row = int(data['row'])
        team = str(data['team']).strip()
        date = str(data['date'])
        time = str(data['time'])
    except (ValueError, KeyError, TypeError):
        await message.answer('Не удалось разобрать данные брони. Откройте мини-апп заново.')
        return

    if not team:
        await message.answer('Название команды обязательно. Откройте мини-апп и укажите его.')
        return

    # Запоминаем бронь до получения контакта
    pending[message.from_user.id] = {
        'sheet': sheet,
        'row': row,
        'team': team,
        'date': date,
        'time': time,
    }

    # Кнопка, при нажатии которой Telegram сам предлагает поделиться контактом
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[KeyboardButton(text='Поделиться контактом 📱', request_contact=True)]],
    )
    when = f'{date} {time}' if date else time
    await message.answer(
        f'Слот выбран: {when} ({sheet})\n'
        f'Команда: {team}\n\n'
        'Нажмите кнопку ниже, чтобы поделиться контактом — после этого бронь закрепится.',
        reply_markup=kb,
    )


@dp.message(F.contact)
async def got_contact(message: Message):
    """Пользователь поделился контактом — завершаем бронь."""
    contact = message.contact

    # Нельзя бронировать чужим контактом
    if contact.user_id != message.from_user.id:
        await message.answer('Пожалуйста, поделитесь именно своим контактом.')
        return

    booking = pending.pop(message.from_user.id, None)
    if booking is None:
        await message.answer('Сначала выберите слот в мини-аппе, затем отправьте контакт.')
        return

    payload = {
        'sheet': booking['sheet'],
        'row': booking['row'],
        'team': booking['team'],
        'name': message.from_user.first_name or 'Гость',
        'phone': contact.phone_number,
        'telegram_id': message.from_user.id,
        'username': message.from_user.username or '',
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_URL,
                data=json.dumps(payload),
                headers={'Content-Type': 'text/plain;charset=utf-8'},
            ) as resp:
                result = await resp.json(content_type=None)
    except Exception:
        # Возвращаем бронь в ожидание — пользователь может попробовать ещё раз
        pending[message.from_user.id] = booking
        await message.answer('Не получилось связаться с таблицей. Попробуйте ещё раз: отправьте контакт повторно.')
        return

    if result.get('ok'):
        when = f"{booking['date']} {booking['time']}" if booking['date'] else booking['time']
        await message.answer(
            f'✅ Бронь зафиксирована!\n'
            f'Направление: {booking["sheet"]}\n'
            f'Когда: {when}\n'
            f'Команда: {booking["team"]}',
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            f'❌ {result.get("reason", "Ошибка бронирования")}\n'
            'Откройте мини-апп и выберите другой слот.',
            reply_markup=ReplyKeyboardRemove(),
        )


@dp.message(F.text)
async def fallback(message: Message):
    """Любое обычное сообщение — мягко возвращаем к делу."""
    await message.answer('Выберите слот через мини-апп: нажмите кнопку слева или /start.')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())