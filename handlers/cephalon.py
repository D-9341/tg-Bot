from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hcode, hlink

router = Router()

@router.message(Command("help"))
async def help_cmd(message: types.Message, command: CommandObject = None):
    if command and command.args:
        cmd_name = command.args.strip().lower()
        return await show_command_help(message, cmd_name)
    await show_main_help(message)

async def show_main_help(message: types.Message):
    builder = InlineKeyboardBuilder()

    sections = {
        "Основные": "help_main",
        "Игры": "help_fun", 
        "Утилиты": "help_misc"
    }
    
    for text, callback_data in sections.items():
        builder.add(types.InlineKeyboardButton(text = text, callback_data = callback_data))
    
    builder.adjust(2, 1)
    
    help_text = f"""
{hbold('Помощь по командам бота')}

Используйте кнопки ниже для просмотра команд по разделам.
Или напишите {hcode('/help <команда>')} для подробностей о конкретной команде.

{hbold('Примечания:')}
{hcode('[]')} - необязательные параметры
{hcode('<>')} - обязательные параметры

{hlink('Исходный код', 'https://github.com/D-9341/tg-Bot')} | Cephalon Cy 2026
"""
    await message.answer(help_text, reply_markup = builder.as_markup(), disable_web_page_preview = True)

async def show_command_help(message: types.Message, cmd_name: str):
    help_dict = {
        
        # Игры
        "roll": f"""
{hbold('Команда:')} {hcode('/roll')}
{hbold('Описание:')} Бросить кости
{hbold('Использование:')} {hcode('/roll [аргументы]')}
{hbold('Примеры:')}
• {hcode('/roll')} - случайное число 0-100
• {hcode('/roll 2d20')} - бросить 2 двадцатигранных кубика
• {hcode('/roll 10-100')} - число от 10 до 100
• {hcode('/roll 50')} - число от 0 до 50
        """,
        
        "coin": f"""
{hbold('Команда:')} {hcode('/coin')}
{hbold('Описание:')} Подбросить монетку
{hbold('Использование:')} {hcode('/coin')}
{hbold('Пример:')} {hcode('/coin')}
        """,

        "connect4": f"""
{hbold('Команда:')} {hcode('/connect4')}
{hbold('Описание:')} Игра в 'четыре в ряд'
{hbold('Использование:')} {hcode('/connect4')}
        """,
        
        # Утилиты
        "about": f"""
{hbold('Команда:')} {hcode('/about')}
{hbold('Описание:')} Информация о пользователе
{hbold('Использование:')} {hcode('/about [@юзер]')}
{hbold('Примеры:')}
• {hcode('/about')} - о себе
• {hcode('/about @username')} - о другом пользователе
• Ответьте на сообщение с {hcode('/about')}
        """,
        
        "avatar": f"""
{hbold('Команда:')} {hcode('/avatar')}
{hbold('Описание:')} Получить аватар пользователя
{hbold('Использование:')} {hcode('/avatar [@юзер]')}
{hbold('Примеры:')}
• {hcode('/avatar')} - свой аватар
• {hcode('/avatar @username')} - аватар другого
        """,
    }

    if cmd_name in help_dict:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text = "Назад к списку команд", callback_data = "help_back"))
        
        await message.answer(help_dict[cmd_name], reply_markup = builder.as_markup(), disable_web_page_preview = True)
    else:
        await message.answer(f"Помощь по команде {hcode(cmd_name)} не найдена.\nИспользуйте {hcode('/help')} для просмотра всех команд.")

@router.callback_query(lambda c: c.data.startswith("help_"))
async def help_callback_handler(callback: types.CallbackQuery):
    action = callback.data

    if action == "help_main":
        text = f"""
{hbold('Основные команды:')}

{hcode('/help')} - Эта справка
{hcode('/help <команда>')} - Помощь по конкретной команде
{hcode('/info')} - Информация о боте
       """
    
    # Игры
    elif action == "help_fun":
        text = f"""
{hbold('Игры и развлечения:')}

{hbold('Кости и случайности:')}
{hcode('/roll')} - Случайное число
{hcode('/roll 2d20')} - 2 двадцатигранных кубика
{hcode('/coin')} - Подбросить монетку
        """
    
    # Утилиты
    elif action == "help_misc":
        text = f"""
{hbold('Утилиты:')}

{hbold('Информация:')}
{hcode('/about [@юзер]')} - Информация о пользователе
{hcode('/chatinfo')} - Информация о чате
{hcode('/avatar [@юзер]')} - Получить аватар
        """
    
    elif action == "help_back":
        await callback.message.delete()
        await show_main_help(callback.message)
        return await callback.answer()
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text = "Назад", callback_data = "help_back"))
    
    await callback.message.edit_text(text = text, reply_markup = builder.as_markup(), disable_web_page_preview = True)
    await callback.answer()