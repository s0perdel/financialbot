import logging
from config import *
import sys
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt


class Engine:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s] %(levelname)s: %(message)s',
                            datefmt='%H:%M:%S'
                            )
        self.debug_mode = DEBUG
        if self.debug_mode:
            logging.warning('Started in developer mode.')
        if not BOT_TOKEN:
            logging.fatal('No bot_token provided.')
            sys.exit(-1)
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        logging.info('Settings succesfully initialized.')

    async def shutdown(self, dp: Dispatcher):
        self.dp = dp
        await self.dp.storage.close()
        await self.dp.storage.wait_closed()
        if DEBUG:
            await self.bot.send_message(
                ADMIN_ID, fmt.text(
                    '*DEV:* Сервер был отключен ❌'
                ), parse_mode='MarkdownV2'
            )
        logging.info('Shutdown was succesful.')

    async def startup(self, dp: Dispatcher):
        if DEBUG:
            await self.bot.send_message(
                ADMIN_ID, fmt.text(
                    '*DEV:* Сервер был запущен ✅'
                ), parse_mode='MarkdownV2'
            )
        logging.info('Startup was succesfull.')
