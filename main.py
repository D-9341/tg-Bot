import asyncio
import aiogram
import importlib
import os

from pathlib import Path
from dotenv import load_dotenv

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

CWD = Path.cwd()
load_dotenv(CWD / 'vars.env')
TOKEN = os.getenv("TOKEN")

client = aiogram.Bot(token = TOKEN, default = DefaultBotProperties(parse_mode = ParseMode.HTML))
storage = MemoryStorage()
dp = aiogram.Dispatcher(storage = storage)

async def setup_commands(client: aiogram.Bot):
    commands = [
        BotCommand(command = "help", description = "Помощь по командам"),
        BotCommand(command = "roll", description = "Получить случайное число/кинуть кости"),
        BotCommand(command = "coin", description = "Подбросить монетку"),
        BotCommand(command = "about", description = "Информация о пользователе"),
        BotCommand(command = "chatinfo", description = "Информация о чате"),
    ]
    
    await client.set_my_commands(commands, scope = BotCommandScopeDefault())

async def init():
    for file in os.listdir(CWD / "handlers"):
        if not file.startswith("_"):
            module = importlib.import_module(f"handlers.{file[:-3]}")
            if hasattr(module, "router"):
                dp.include_router(module.router)
                print(f"Модуль {file[:-3]} загружен")

async def on_ready():
    await setup_commands(client)
    print("Бот запущен")

async def main():
    await init()
    await on_ready()
    await client.delete_webhook(drop_pending_updates = True)
    await dp.start_polling(client)

if __name__ == "__main__":
    asyncio.run(main())