from aiogram.dispatcher.filters.state import State, StatesGroup


class MainMenu(StatesGroup):
    anti_input = State()


class AddCategory(StatesGroup):
    choose_category = State()
    choose_name = State()
    choose_value = State()
    confirm_change = State()


class StatsMenu(StatesGroup):
    stats_menu = State()
    change_date = State()
    edit_category = State()
    edit_name = State()
    edit_value = State()
    edit_date = State()


class SettingsMenu(StatesGroup):
    category_settings = State()
