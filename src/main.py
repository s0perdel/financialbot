from aiogram import executor
from aiogram.dispatcher.filters import Text, Command
from utils import Engine
from database import Database
from src.states import *
from handlers.main_menu import Start
from handlers.add_change import AddChange
from handlers.statistics import Statistics
from handlers.settings import Settings

# TODO: вынести в отдельный файл кнопки, и все конструкции с текстом
# TODO: глобальный рефакторинг, пересмотр на костыльность
# TODO: добавить английский и украинский язык
# TODO: добавить режим смены валюты

utils = Engine()
db = Database()

main_menu = Start(db)
add_change = AddChange(db)
stats = Statistics(db)
settings = Settings(db)

utils.dp.register_callback_query_handler(main_menu.start_menu, Text('cancel'), state='*')
utils.dp.register_message_handler(main_menu.start_menu, commands=['start', 'cancel', 'help'], state='*')

utils.dp.register_message_handler(main_menu.anti_input, state=AddCategory.confirm_change)
utils.dp.register_message_handler(main_menu.anti_input, state=MainMenu.anti_input)

utils.dp.register_callback_query_handler(add_change.start_spend, Text('add_spending'), state=MainMenu.anti_input)
utils.dp.register_callback_query_handler(add_change.start_profit, Text('add_profit'), state=MainMenu.anti_input)
utils.dp.register_message_handler(add_change.category, state=AddCategory.choose_category)
utils.dp.register_message_handler(add_change.name, state=AddCategory.choose_name)
utils.dp.register_message_handler(add_change.value, state=AddCategory.choose_value)
utils.dp.register_callback_query_handler(add_change.confirm, Text('confirm'), state=AddCategory.confirm_change)

utils.dp.register_callback_query_handler(stats.start, Text('stats'), state='*')
utils.dp.register_message_handler(stats.change_date, Command('date'), state=StatsMenu.stats_menu)
utils.dp.register_message_handler(stats.show_categories, Command('categories'), state=StatsMenu.stats_menu)
utils.dp.register_message_handler(stats.get_all, Command('all'), state=StatsMenu.stats_menu)
utils.dp.register_message_handler(stats.edit_transaction, Command('edit'), state=StatsMenu.stats_menu)
utils.dp.register_message_handler(stats.delete_transaction, Command('delete'), state=StatsMenu.stats_menu)
utils.dp.register_message_handler(stats.incorrect_input, state=StatsMenu.stats_menu)

utils.dp.register_message_handler(stats.confirm_date, state=StatsMenu.change_date)

utils.dp.register_callback_query_handler(stats.edit_category, Text('edit_category'), state=MainMenu.anti_input)
utils.dp.register_message_handler(stats.edit_transaction, state=StatsMenu.edit_category)
utils.dp.register_callback_query_handler(stats.edit_name, Text('edit_name'), state=MainMenu.anti_input)
utils.dp.register_message_handler(stats.edit_transaction, state=StatsMenu.edit_name)
utils.dp.register_callback_query_handler(stats.edit_value, Text('edit_value'), state=MainMenu.anti_input)
utils.dp.register_message_handler(stats.edit_transaction, state=StatsMenu.edit_value)
utils.dp.register_callback_query_handler(stats.edit_date, Text('edit_date'), state=MainMenu.anti_input)
utils.dp.register_message_handler(stats.edit_transaction, state=StatsMenu.edit_date)
utils.dp.register_callback_query_handler(stats.save_edit, Text('save_edit'), state=MainMenu.anti_input)

utils.dp.register_callback_query_handler(settings.start, Text('settings'), state='*')
utils.dp.register_callback_query_handler(settings.soon, Text('coming_soon'), state='*')
utils.dp.register_callback_query_handler(settings.category_settings, Text('category_settings'), state='*')
utils.dp.register_message_handler(settings.category_confirm, state=SettingsMenu.category_settings)
utils.dp.register_callback_query_handler(settings.about, Text('about'), state='*')

if __name__ == '__main__':
    executor.start_polling(
        utils.dp,
        skip_updates=True,
        on_startup=utils.startup,
        on_shutdown=utils.shutdown
    )
