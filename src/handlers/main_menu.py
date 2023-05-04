from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt
from src.states import MainMenu


class Start:
    def __init__(self, db):
        self.db = db

    async def start_menu(self, unit: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await state.finish()
        if not self.db.check_user(unit.from_user):
            self.db.create_user(unit.from_user)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text='Добавить трату 💰', callback_data='add_spending'),
            types.InlineKeyboardButton(text='Добавить прибыль 🤑', callback_data='add_profit'),
            types.InlineKeyboardButton(text='Статистика 👨‍💻', callback_data='stats'),
            types.InlineKeyboardButton(text='Настройки ⚙', callback_data='settings')
        ]
        keyboard.add(*buttons)
        msg = fmt.text(
                fmt.text(f'Привет, {unit.from_user.first_name}!'),
                fmt.text('Я ', fmt.hbold('Финансовый Помогатор'), '💸'),
                fmt.text('Бот, который поможет тебе разобраться с твоими ', fmt.hunderline('тратами и прибылью.\n')),
                fmt.text('Ты можешь вносить свои траты и прибыль по категориям, получать статистику за период',
                         'и по конкретным категориям и много много прочего.'),
                sep='\n'
            )
        if isinstance(unit, types.Message):
            await unit.answer(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await unit.message.edit_text(msg, parse_mode='HTML', reply_markup=keyboard)
        await state.set_state(MainMenu.anti_input)

    async def anti_input(self, message: types.Message):
        await message.answer('Выберите кнопку! 😬')
