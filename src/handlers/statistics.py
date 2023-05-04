from aiogram import types
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt
from src.states import StatsMenu, MainMenu
from datetime import datetime, timedelta
import re


class Statistics:
    def __init__(self, db):
        self.db = db

    async def start(self, call: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await state.set_state(StatsMenu.stats_menu)
        await call.message.delete_reply_markup()
        spending_categories = self.db.get_categories(call.from_user, 'spending')
        profit_categories = self.db.get_categories(call.from_user, 'profit')
        if spending_categories is not None:
            spending = fmt.text(fmt.hunderline('Ваши категории трат:'), ' ', ', '.join(spending_categories), '\n')
        else:
            spending = fmt.text(fmt.hunderline('У вас еще нет категорий трат!\n'))
        if profit_categories is not None:
            profit = fmt.text(fmt.hunderline('Ваши категории прибыли:'), ' ', ', '.join(profit_categories), '\n')
        else:
            profit = fmt.text(fmt.hunderline('У вас еще нет категорий прибыли!\n'))
        try:
            limits = await state.get_data()
            limits = limits['limits']
        except KeyError:
            limits = self.db.get_limits(call.from_user)
            await state.update_data(limits=limits)
        if limits[0] is not None:
            spending_sum = fmt.text(
                'Было потрачено: ', fmt.hitalic(self.db.get_sum(call.from_user, "spending", limits)), ' грн.\n'
            )
            profit_sum = fmt.text(
                'Было получено: ', fmt.hitalic(self.db.get_sum(call.from_user, "profit", limits)), ' грн.\n'
            )
            period = fmt.text(
                'В период с ',
                fmt.hbold(datetime.fromtimestamp(limits[0]).strftime('%d.%m.%Y')),
                ' по ',
                fmt.hbold(datetime.fromtimestamp(limits[1]).strftime('%d.%m.%Y')),
                '\n'
            )
        else:
            period = fmt.text('Внесите какие нибудь данные, чтобы появилась какая нибудь статистика. 🙂\n')
            spending_sum = fmt.text('У вас еще не было трат!\n')
            profit_sum = fmt.text('У вас еще не было прибыли!\n')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться в меню ↩', callback_data='cancel'))
        await call.message.edit_text(
            fmt.text(
                fmt.hbold('МЕНЮ СТАТИСТИКИ 👁\n'),
                spending,
                profit,
                period,
                spending_sum,
                profit_sum,
                fmt.text('/date сменить временной промежуток'),
                fmt.text('/categories показать статистику по категориям'),
                fmt.text('/all прислать ваш ВЕСЬ список транзакций'),
                fmt.text('/edit [id] редактировать какую то конкретную транзакцию, ID конкретной '
                         'транзакции можете посмотреть запросив весь список ваших транзакций'),
                fmt.text('/delete [id] удалить конкретную транзакцию'),
                sep='\n'
            ), parse_mode='HTML', reply_markup=keyboard
        )

    async def change_date(self, message: types.Message, state: FSMContext):
        await state.set_state(StatsMenu.change_date)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        keyboard.add(*['Последний день', 'Последняя неделя', 'Последний месяц'])
        await message.answer(
            fmt.text(
                fmt.hbold('СМЕНА ДАТЫ:\n'),
                fmt.text('Выберите период со списка либо же введите временной промежуток в формате ',
                         fmt.hcode('01.02.2022-20.03.2022')),
                sep='\n'
            ), parse_mode='HTML', reply_markup=keyboard
        )

    async def incorrect_input(self, message: types.Message):
        await message.answer('Выберите команду или кнопку! 😬')

    async def confirm_date(self, message: types.Message, state: FSMContext):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться ↩', callback_data='stats'))
        if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}-\d{1,2}\.\d{1,2}\.\d{4}$', message.text):
            dates = message.text.split('-')
            limits = [
                datetime.strptime(dates[0], '%d.%m.%Y').timestamp(),
                datetime.strptime(dates[1], '%d.%m.%Y') + timedelta(hours=23, minutes=59)
            ]
            limits[1] = limits[1].timestamp()
            await state.update_data(limits=limits)
            await message.answer('Готово!', reply_markup=types.ReplyKeyboardRemove())
            await message.answer('Данные о дате обновлены. ✅', reply_markup=keyboard)
            await state.set_state(MainMenu.anti_input)
        else:
            if message.text == 'Последний день':
                today = datetime.today().strftime('%d.%m.%Y')
                limits = [
                    datetime.strptime(today, '%d.%m.%Y').timestamp(),
                    datetime.strptime(today, '%d.%m.%Y') + timedelta(hours=23, minutes=59)
                ]
                limits[1] = limits[1].timestamp()
                await state.update_data(limits=limits)
                await message.answer('Готово!', reply_markup=types.ReplyKeyboardRemove())
                await message.answer('Данные о дате обновлены. ✅', reply_markup=keyboard)
                await state.set_state(MainMenu.anti_input)
            elif message.text == 'Последняя неделя':
                today = datetime.today().strftime('%d.%m.%Y')
                limits = [
                    datetime.strptime(today, '%d.%m.%Y') - timedelta(days=7),
                    datetime.strptime(today, '%d.%m.%Y') + timedelta(hours=23, minutes=59)
                ]
                limits = [a.timestamp() for a in limits]
                await state.update_data(limits=limits)
                await message.answer('Готово!', reply_markup=types.ReplyKeyboardRemove())
                await message.answer('Данные о дате обновлены. ✅', reply_markup=keyboard)
                await state.set_state(MainMenu.anti_input)
            elif message.text == 'Последний месяц':
                today = datetime.today().strftime('%d.%m.%Y')
                limits = [
                    datetime.strptime(today, '%d.%m.%Y') - timedelta(days=30),
                    datetime.strptime(today, '%d.%m.%Y') + timedelta(hours=23, minutes=59)
                ]
                limits = [a.timestamp() for a in limits]
                await state.update_data(limits=limits)
                await message.answer('Готово!', reply_markup=types.ReplyKeyboardRemove())
                await message.answer('Данные о дате обновлены. ✅', reply_markup=keyboard)
                await state.set_state(MainMenu.anti_input)
            else:
                await message.answer('Неправильный ввод! Читайте инструкции выше 😬')

    async def show_categories(self, message: types.Message, state: FSMContext):
        sp_categories, pr_categories = None, None
        data = await state.get_data()
        if data['limits'] is not None:
            sp_categories = self.db.get_categories_bydate(message.from_user, 'spending', data['limits'])
            pr_categories = self.db.get_categories_bydate(message.from_user, 'profit', data['limits'])
        if sp_categories is None and pr_categories is None:
            await message.answer(
                fmt.text(
                    fmt.hbold('ОШИБКА 😔\n'),
                    fmt.text('К сожалению, у вас еще нет добавленных транзакций.'),
                    fmt.text('Введите новую команду, либо /cancel чтобы вернуться к главному меню.'),
                    sep='\n'
                ), parse_mode='HTML'
            )
        else:
            sp_result, pr_result = [], []
            if sp_categories is not None:
                total_value = self.db.get_sum(message.from_user, 'spending', data['limits'])
                for category in sp_categories:
                    value = self.db.get_sum_bycategory(message.from_user, 'spending', data['limits'], category)
                    sp_result.append(
                        fmt.text(
                            fmt.hunderline(f'{category}:'),
                            fmt.text(f'{value} грн ({round((value/total_value)*100, 2)}%)'),
                            sep=' '
                        )
                    )
            else:
                sp_result.append(fmt.text('К сожалению у вас нет категорий трат 😔'))
            if pr_categories is not None:
                total_value = self.db.get_sum(message.from_user, 'profit', data['limits'])
                for category in pr_categories:
                    value = self.db.get_sum_bycategory(message.from_user, 'profit', data['limits'], category)
                    pr_result.append(
                        fmt.text(
                            fmt.hunderline(f'{category}:'),
                            fmt.text(f'{value} грн ({round((value/total_value)*100, 2)}%)'),
                            sep=' '
                        )
                    )
            else:
                pr_result.append(fmt.text('К сожалению у вас нет категорий прибыли 😔'))
            date_from = datetime.fromtimestamp(data['limits'][0]).strftime('%d.%m.%Y')
            date_to = datetime.fromtimestamp(data['limits'][1]).strftime('%d.%m.%Y')
            await message.answer(
                fmt.text(
                    fmt.hbold('СТАТИСТИКА ПО КАТЕГОРИЯМ:\n'),
                    fmt.text(f'Взят период с {date_from} по {date_to}\n'),
                    fmt.hbold('ТРАТЫ:'),
                    *sp_result,
                    fmt.hbold('\nПРИБЫЛЬ:'),
                    *pr_result,
                    fmt.text('\nВведите другую команду или же /cancel для возврата в главное меню'),
                    sep='\n'
                ), parse_mode='HTML'
            )

    async def get_all(self, message: types.Message):
        data = self.db.get_all_transactions(message.from_user)
        await message.answer_document(types.InputFile(data, filename='transactions.csv'))
        await message.answer(
            fmt.text(
                fmt.text('Все ваши транзакции 🔝'),
                fmt.text('Введите другую команду или же /cancel для возврата в главное меню'),
                sep='\n'
            )
        )

    async def edit_transaction(self, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        try:
            transaction_id = user_data['transaction_id']
            actual_state = await state.get_state()
            if actual_state == 'StatsMenu:edit_category':
                await state.update_data(category=message.text)
            elif actual_state == 'StatsMenu:edit_name':
                await state.update_data(name=message.text)
            elif actual_state == 'StatsMenu:edit_value':
                try:
                    number = float(message.text)
                    if (number.is_integer() or round(number, 2) == number) and number > 0:
                        await state.update_data(value=number)
                    else:
                        await message.reply(
                            fmt.text(
                                'Многовато цифр после запятой 😬\n',
                                fmt.hbold('Давай еще раз!'),
                                sep=''
                            ), parse_mode='HTML'
                        )
                        return
                except ValueError:
                    await message.reply(
                        fmt.text(
                            'Ты либо ввел ', fmt.hbold('буквы'), ', либо вместо ',
                            fmt.hbold('точки'), ' ввел ', fmt.hbold('запятую'), ' 😬\n',
                            fmt.hbold('Давай еще раз!'),
                            sep=''
                        ), parse_mode='HTML'
                    )
                    return
            elif actual_state == 'StatsMenu:edit_date':
                try:
                    dtt = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
                    if dtt > datetime.now():
                        await message.reply('Транзакция в будущем? 😃\nВведи другую дату')
                        return
                    await state.update_data(date=dtt.strftime('%d.%m.%Y %H:%M'))
                except ValueError:
                    await message.reply(
                        fmt.text(
                            'Ошибка ввода. Нужно ввести дату в формате DD.MM.YYYY HH:MM 😬'
                        )
                    )
                    return
        except KeyError:
            transaction_id = message.text.replace('/edit ', '')
        if not transaction_id.isdigit():
            await message.reply('Неправильный ввод, попробуйте ввести /edit 293')
        else:
            if not self.db.check_id(message.from_user, transaction_id):
                await message.reply('У вас не такого ID 😳\nПересмотрите ваш список транзакций!')
            else:
                await state.update_data(transaction_id=transaction_id)
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                buttons = [
                    types.InlineKeyboardButton(text='Изменить категорию 📚', callback_data='edit_category'),
                    types.InlineKeyboardButton(text='Изменить описание 🏷', callback_data='edit_name'),
                    types.InlineKeyboardButton(text='Изменить сумму 💵', callback_data='edit_value'),
                    types.InlineKeyboardButton(text='Изменить время/дату ⏰', callback_data='edit_date'),
                    types.InlineKeyboardButton(text='Сохранить изменения 💾', callback_data='save_edit')
                ]
                keyboard.add(*buttons)
                await state.set_state(MainMenu.anti_input)
                try:
                    user_data = await state.get_data()
                    tp = user_data['tp']
                    value = user_data['value']
                    name = user_data['name']
                    category = user_data['category']
                    date = user_data['date']
                    await message.answer(
                        fmt.hbold('ИЗМЕНЕНИЯ ОБНОВЛЕНЫ ✅'),
                        reply_markup=types.ReplyKeyboardRemove(),
                        parse_mode='HTML'
                    )
                except KeyError:
                    transaction = self.db.get_transaction(message.from_user, transaction_id)
                    tp = 'ТРАТА 'if transaction[0] == 'spending' else 'ПРИБЫЛЬ'
                    value = transaction[1]
                    name = transaction[2]
                    category = transaction[3]
                    date = transaction[4]
                    await state.update_data(
                        tp=tp,
                        value=value,
                        name=name,
                        category=category,
                        date=date
                    )
                await message.answer(
                    fmt.text(
                        fmt.text(fmt.hunderline(f'ТРАНЗАКЦИЯ #{transaction_id}'), ' 🔍\n'),
                        fmt.text(fmt.hbold('Тип: '), fmt.hitalic(f'{tp}')),
                        fmt.text(fmt.hbold('Категория: '), f'{category}'),
                        fmt.text(fmt.hbold('Описание: '), f'{name}'),
                        fmt.text(fmt.hbold('Сумма: '), f'{value} грн'),
                        fmt.text(fmt.hbold('Дата и время: '), f'{date}'),
                        sep='\n'
                    ), parse_mode='HTML', reply_markup=keyboard
                )

    async def edit_category(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state(StatsMenu.edit_category)
        await call.message.delete_reply_markup()
        user_data = await state.get_data()
        default = self.db.get_settings()
        if user_data['tp'] == 'ПРИБЫЛЬ':
            buttons = [default['pr1'], default['pr2'], default['pr3']]
        else:
            buttons = [default['sp1'], default['sp2'], default['sp3']]
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(*buttons)
        await call.message.answer(
            fmt.text(
                'Выберите новую ', fmt.hbold('категорию'), ' со списка, либо введите свое название. 📚'
            ),
            reply_markup=keyboard, parse_mode='HTML'
        )

    async def edit_name(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state(StatsMenu.edit_name)
        await call.message.delete_reply_markup()
        await call.message.answer(
            fmt.text(
                'Напишите новое ', fmt.hbold('название'), ' или ', fmt.hbold('описание'), ' 🏷'
            ), parse_mode='HTML'
        )

    async def edit_value(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state(StatsMenu.edit_value)
        await call.message.delete_reply_markup()
        await call.message.answer(
            fmt.text(
                'Введите новую сумму в формате: ',
                fmt.hcode('1800'), ' или ', fmt.hcode('244.33'), ' 💵'
            ), parse_mode='HTML'
        )

    async def edit_date(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state(StatsMenu.edit_date)
        await call.message.delete_reply_markup()
        await call.message.answer(
            fmt.text(
                'Введите новую дату и время в формате:',
                fmt.hcode('01.01.2000 09:43'), '📆',
                sep=' '
            ), parse_mode='HTML'
        )

    async def save_edit(self, call: types.CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        self.db.update_transaction(call.from_user, user_data)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Вернуться ↩', callback_data='stats'))
        await call.message.answer(
            fmt.hbold('ИЗМЕНЕНИЯ СОХРАНЕНЫ В БАЗЕ 💾✅'),
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def delete_transaction(self, message: types.Message, state: FSMContext):
        transaction_id = message.text.replace('/delete ', '')
        if not transaction_id.isdigit():
            await message.reply('Неправильный ввод, попробуйте ввести /delete 293')
        else:
            if not self.db.check_id(message.from_user, transaction_id):
                await message.reply('У вас не такого ID 😳\nПересмотрите ваш список транзакций!')
            else:
                self.db.delete_transaction(message.from_user, transaction_id)
                await message.answer(
                    fmt.hbold('ТРАНЗАКЦИЯ УСПЕШНО УДАЛЕНА С БАЗЫ ✅'),
                    parse_mode='HTML'
                )
