from aiogram import types
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt
from src.states import AddCategory, MainMenu
from datetime import datetime


class AddChange:
    def __init__(self, db):
        self.db = db

    async def start_spend(self, call: types.CallbackQuery, state: FSMContext):
        await state.update_data(type='spending')
        await state.update_data(text='траты')
        user_data = await state.get_data()
        await call.message.delete_reply_markup()
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        default = self.db.get_settings(call.from_user)
        buttons = [default['sp1'], default['sp2'], default['sp3']]
        keyboard.add(*buttons)
        await call.message.answer(
            fmt.text(
                'Выберите ', fmt.hbold('категорию'), f' {user_data["text"]} со списка, либо введите свое название. 📚'
            ),
            reply_markup=keyboard, parse_mode='HTML'
        )
        await state.set_state(AddCategory.choose_category)

    async def start_profit(self, call: types.CallbackQuery, state: FSMContext):
        await state.update_data(type='profit')
        await state.update_data(text='прибыли')
        user_data = await state.get_data()
        await call.message.delete_reply_markup()
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        default = self.db.get_settings(call.from_user)
        buttons = [default['pr1'], default['pr2'], default['pr3']]
        keyboard.add(*buttons)
        await call.message.answer(
            fmt.text(
                'Выберите ', fmt.hbold('категорию'), f' {user_data["text"]} со списка, либо введите свое название. 📚'
            ),
            reply_markup=keyboard, parse_mode='HTML'
        )
        await state.set_state(AddCategory.choose_category)

    async def category(self, message: types.Message, state: FSMContext):
        await state.update_data(category=message.text)
        user_data = await state.get_data()
        await message.answer(
            fmt.text(
                'Напишите ', fmt.hbold('название'), f' {user_data["text"]} или же ее ', fmt.hbold('описание'), ' 🏷'
            ), parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddCategory.choose_name)

    async def name(self, message: types.Message, state: FSMContext):
        await state.update_data(name=message.text)
        user_data = await state.get_data()
        await message.answer(
            fmt.text(
                f'Введите сумму {user_data["text"]} в формате: ',
                fmt.hcode('1800'), ' или ', fmt.hcode('244.33'), ' 💵'
            ), parse_mode='HTML'
        )
        await state.set_state(AddCategory.choose_value)

    async def value(self, message: types.Message, state: FSMContext):
        try:
            number = float(message.text)
            if (number.is_integer() or round(number, 2) == number) and number > 0:
                await state.update_data(value=number)
                await state.update_data(time=datetime.now().timestamp())
                user_data = await state.get_data()
                time = datetime.fromtimestamp(user_data["time"]).strftime("%d.%m.%Y %H:%M")
                keyboard = types.InlineKeyboardMarkup()
                buttons = [
                    types.InlineKeyboardButton(text='Да ✅', callback_data='confirm'),
                    types.InlineKeyboardButton(text='Отмена ❌', callback_data='cancel')
                ]
                keyboard.add(*buttons)
                await message.answer(
                    fmt.text(
                        fmt.hbold('Давайте перепроверим!\n'),
                        fmt.text(fmt.hunderline('Дата и время:'), f' {time}'),
                        fmt.text(fmt.hunderline('Категория:'), f' {user_data["category"]}'),
                        fmt.text(fmt.hunderline('Описание:'), f' {user_data["name"]}'),
                        fmt.text(fmt.hunderline('Сумма:'), f' {user_data["value"]}\n'),
                        fmt.hbold('Все верно?'),
                        sep='\n'
                    ), parse_mode='HTML', reply_markup=keyboard
                )
                await state.set_state(AddCategory.confirm_change)
            else:
                await message.reply(
                    fmt.text(
                        'Многовато цифр после запятой 😬\n',
                        fmt.hbold('Давай еще раз!'),
                        sep=''
                    ), parse_mode='HTML'
                )
        except ValueError:
            await message.reply(
                fmt.text(
                    'Ты либо ввел ', fmt.hbold('буквы'), ', либо вместо ',
                    fmt.hbold('точки'), ' ввел ', fmt.hbold('запятую'), ' 😬\n',
                    fmt.hbold('Давай еще раз!'),
                    sep=''
                ), parse_mode='HTML'
            )

    async def confirm(self, call: types.CallbackQuery, state: FSMContext):
        await call.message.delete_reply_markup()
        user_data = await state.get_data()
        self.db.add_transaction(user_data, call.from_user)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться в меню ↩', callback_data='cancel'))
        await call.message.answer('Отлично! База обновлена. 💾', reply_markup=keyboard)
        await state.set_state(MainMenu.anti_input)
