import random

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.markdown import hbold

router = Router()

@router.message(Command("roll"))
async def roll_cmd(message: types.Message, command: CommandObject):
    if not command.args:
        rand = random.randint(0, 100)
        if rand == 42:
            await message.answer(f'{message.from_user.mention_html()} получает случайное число (0-100)\n100')
        else:
            rand1 = random.randint(0, 9)
            rand2 = random.randint(0, 9)
            await message.answer(f'{message.from_user.mention_html()} получает случайное число (0-100)\n0{rand1}{rand2}')
        return
    
    args = command.args.strip()

    if ' ' in args:
        parts = args.split()
        if len(parts) == 2:
            try:
                first = int(parts[0]) if parts[0] != '0' else 0
                second = int(parts[1])
                
                if first > second:
                    await message.answer(f'{message.from_user.mention_html()} получает случайное число ({first}-{first})\n{first}')
                else:
                    rand = random.randint(first, second)
                    await message.answer(f'{message.from_user.mention_html()} получает случайное число ({first}-{second})\n{rand}')
            except ValueError:
                await message.answer("Неверный формат чисел")
        return

    try:
        if '-' in args:
            if args.count('-') > 1:
                return await message.answer("Неверный формат. Используйте /roll 10-100")
                
            first_str, second_str = args.split('-')
            first = int(first_str)
            second = int(second_str)
            
            if first > second:
                return await message.answer(f'{message.from_user.mention_html()} получает случайное число ({first}-{first})\n{first}')
            else:
                rand = random.randint(first, second)
                return await message.answer(f'{message.from_user.mention_html()} получает случайное число ({first}-{second})\n{rand}')

        if 'd' in args.lower():
            if args.lower().count('d') != 1:
                return await message.answer("Неверный формат. Используйте /roll 2d20")
            
            dice_amount_str, dice_edges_str = args.lower().split('d')
            
            if not dice_amount_str or not dice_edges_str:
                return await message.answer("Неверный формат. Используйте /roll 2d20")
            
            dice_amount = int(dice_amount_str)
            dice_edges = int(dice_edges_str)

            if dice_amount > 20:
                return await message.answer("Нельзя бросить больше 20 дайсов")
            if dice_edges > 20:
                return await message.answer("Вы не можете кинуть дайс с большим количеством граней, чем 20")

            if dice_amount == 1 and dice_edges == 2:
                return await coin_cmd(message)
            
            if dice_amount > 1:
                results = ''
                result = 0
                for i in range(1, dice_amount + 1):
                    rand = random.randint(1, dice_edges)
                    results += f'{i}. {rand}\n'
                    result += rand
                results += f'В сумме - ||{result}||'
                await message.answer(results)
            else:
                res = random.randint(1, dice_edges)
                total = ''
                if res == 1 and dice_edges == 20:
                    total = ', критический провал'
                if res == 20:
                    total = ', критический успех!'
                await message.answer(f'Получено случайное число: {res}{total}')
            return

        first = int(args)
        rand = random.randint(0, first)
        await message.answer(f'{message.from_user.mention_html()} получает случайное число (0-{first})\n{rand:>02}')
        
    except ValueError:
        await message.answer("Неверный формат. Используйте:\n/roll\n/roll 100\n/roll 2d20\n/roll 10-100\n/roll 10 100")

@router.message(Command("coin"))
async def coin_cmd(message: types.Message):
    coin = random.choice(["ОРЁЛ", "РЕШКА"])
    await message.answer(f"{hbold(message.from_user.mention_html())} подбрасывает монетку: {hbold(coin)}")

@router.message(Command("about", "me"))
async def about_cmd(message: types.Message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user    
    is_bot = "Да" if user.is_bot else "Нет"
    info = f"Информация о пользователе:\n\n"
    info += f"Имя: {user.full_name}\n"
    info += f"ID: {user.id}\n"
    info += f"Username: @{user.username if user.username else 'отсутствует'}\n"
    info += f"Бот: {is_bot}\n"
    
    if user.language_code:
        info += f"Язык: {user.language_code}\n"

    try:
        photos = await message.bot.get_user_profile_photos(user.id, limit=1)
        if photos.photos:
            file_id = photos.photos[0][-1].file_id
            return await message.answer_photo(photo = file_id, caption = info)
    except:
        pass
    
    await message.answer(info)

@router.message(Command("avatar"))
async def avatar_cmd(message: types.Message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    photos = await message.bot.get_user_profile_photos(user.id, limit = 1)
    if photos.photos:
        file_id = photos.photos[0][-1].file_id
        await message.answer_photo(photo = file_id, caption = f"Аватар пользователя {user.mention_html()}")
    else:
        await message.answer("У пользователя нет аватара")

@router.message(Command("chatinfo", "chat", "serverinfo", "guild"))
async def chatinfo_cmd(message: types.Message):
    chat = message.chat
    
    chat_type = "Неизвестно"
    if chat.type == "private":
        chat_type = "Личный чат"
    elif chat.type == "group":
        chat_type = "Группа"
    elif chat.type == "supergroup":
        chat_type = "Супергруппа"
    elif chat.type == "channel":
        chat_type = "Канал"
    
    info = f"Информация о чате:\n\n"
    info += f"Название: {chat.title if hasattr(chat, 'title') else 'Личный чат'}\n"
    info += f"ID: {chat.id}\n"
    info += f"Тип: {chat_type}\n"
    
    if chat.type == "channel" and chat.username:
        info += f"Ссылка: @{chat.username}\n"

    if chat.type == "supergroup":
        try:
            chat_info = await message.bot.get_chat(chat.id)
            if chat_info.description:
                info += f"\nОписание: {chat_info.description}\n"
            
            if chat_info.permissions:
                info += "\nРазрешения:\n"
                perms = []
                if chat_info.permissions.can_send_messages:
                    perms.append("отправка сообщений")
                if chat_info.permissions.can_send_polls:
                    perms.append("опросы")
                if chat_info.permissions.can_send_other_messages:
                    perms.append("другие сообщения")
                if chat_info.permissions.can_add_web_page_previews:
                    perms.append("превью ссылок")
                if chat_info.permissions.can_change_info:
                    perms.append("изменение инфо")
                if chat_info.permissions.can_invite_users:
                    perms.append("приглашение")
                if chat_info.permissions.can_pin_messages:
                    perms.append("закрепление")
                if perms:
                    info += f"Доступно: {', '.join(perms)}\n"
        except:
            pass
    
    await message.answer(info)
