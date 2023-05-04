from aiogram import types
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt
from src.states import SettingsMenu, MainMenu
from config import VERSION


class Settings:
    def __init__(self, db):
        self.db = db

    async def start(self, call: types.CallbackQuery):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text='Настройка категорий 📋', callback_data='category_settings'),
            types.InlineKeyboardButton(text='Сменить валюту 💳', callback_data='coming_soon'),
            types.InlineKeyboardButton(text='Поменять язык 💬', callback_data='coming_soon'),
            types.InlineKeyboardButton(text='О боте и авторе 💻', callback_data='about'),
            types.InlineKeyboardButton(text='Вернуться ↩', callback_data='cancel')
        ]
        keyboard.add(*buttons)
        await call.message.edit_text(
            fmt.text(
                fmt.hbold('МЕНЮ НАСТРОЕК ⚙\n'),
                fmt.text('Добро пожаловать в меню настроек!'),
                fmt.text('Тут вы можете поменять список ваших стандартных предлагаемых '
                         'категорий при добавлений транзакций, поменять валюту, язык бота, '
                         'узнать о боте и авторе.'),
                sep='\n'
            ), reply_markup=keyboard, parse_mode='HTML'
        )

    async def soon(self, call: types.CallbackQuery):
        await call.answer('Этот пункт еще не реализован 😢')

    async def category_settings(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state(SettingsMenu.category_settings)
        await call.message.delete_reply_markup()
        default = self.db.get_settings(call.from_user)
        await call.message.edit_text(
            fmt.text(
                fmt.hbold('ИЗМЕНЕНИЕ КАТЕГОРИЙ ПО УМОЛЧАНИЮ'),
                fmt.text('При добавление новой транзакции либо редактирования старой '
                         'вам предлагается три категории для трат и прибыли в быстром доступе '
                         '(появляющиеся внизу кнопки), в этом меню вы можете их поменять!'),
                fmt.hunderline('Ваши категории в быстром доступе для ТРАТ:'),
                fmt.text(f'{default["sp1"]}\n{default["sp2"]}\n{default["sp3"]}'),
                fmt.hunderline('Ваши категория в быстром доступе для ПРИБЫЛИ:'),
                fmt.text(f'{default["pr1"]}\n{default["pr2"]}\n{default["pr3"]}'),
                fmt.text('Введите новые 6 категорий через ЗАПЯТУЮ, пример:\n',
                         fmt.hcode('Еда,Транспорт,Развлечения,Зарплата,Пособие,Подработка')),
                sep='\n\n'
            ), parse_mode='HTML'
        )

    async def category_confirm(self, message: types.Message, state: FSMContext):
        categories = message.text.split(',')
        if len(categories) != 6:
            await message.reply('Ошибка! Нужно ввести ровно 6 категорий, '
                                '3 на траты, и 3 на прибыли.')
        else:
            self.db.update_categories(message.from_user, categories)
            await state.set_state(MainMenu.anti_input)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Вернуться ↩', callback_data='settings'))
            await message.answer(
                fmt.hbold('ИЗМЕНЕНИЯ СОХРАНЕНЫ В БАЗЕ ✅'),
                reply_markup=keyboard,
                parse_mode='HTML'
            )

    async def about(self, call: types.CallbackQuery):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться ↩', callback_data='settings'))
        await call.message.edit_text(
            fmt.text(
                fmt.hbold('ИНФО\n'),
                fmt.text(fmt.hunderline('Автор бота:'), ' @ledrep0s'),
                fmt.text(fmt.hunderline('Версия:'), f' {VERSION}\n'),
                fmt.text('Этот бот это мой pet-project для портфолио на гитхабе, '
                         'он создавался около недели, и я буду очень рад если кто-то им '
                         'будет пользоваться! Если есть любые замечания или идеи пишите мне в лс.'),
                sep='\n'
            ), reply_markup=keyboard, parse_mode='HTML'
        )
