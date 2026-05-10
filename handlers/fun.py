from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import random
import asyncio

router = Router()

states: dict[int: dict[str: list, str: int, str: int]] = {}

def check_for_red(board):
    for row in board:
        counter = 0
        for cell in row:
            if cell == '🔴':
                counter += 1
                if counter == 4:
                    return True
            else:
                counter = 0
    
    for col in range(7):
        counter = 0
        for row in range(6):
            if board[row][col] == '🔴':
                counter += 1
                if counter == 4:
                    return True
            else:
                counter = 0
    
    for row in range(3):
        for col in range(4):
            if (board[row][col] == '🔴' and 
                board[row+1][col+1] == '🔴' and 
                board[row+2][col+2] == '🔴' and 
                board[row+3][col+3] == '🔴'):
                return True
    
    for row in range(3):
        for col in range(3, 7):
            if (board[row][col] == '🔴' and 
                board[row+1][col-1] == '🔴' and 
                board[row+2][col-2] == '🔴' and 
                board[row+3][col-3] == '🔴'):
                return True
    
    return False

def check_for_blue(board):
    for row in board:
        counter = 0
        for cell in row:
            if cell == '🔵':
                counter += 1
                if counter == 4:
                    return True
            else:
                counter = 0
    
    for col in range(7):
        counter = 0
        for row in range(6):
            if board[row][col] == '🔵':
                counter += 1
                if counter == 4:
                    return True
            else:
                counter = 0
    
    for row in range(3):
        for col in range(4):
            if (board[row][col] == '🔵' and 
                board[row+1][col+1] == '🔵' and 
                board[row+2][col+2] == '🔵' and 
                board[row+3][col+3] == '🔵'):
                return True
    
    for row in range(3):
        for col in range(3, 7):
            if (board[row][col] == '🔵' and 
                board[row+1][col-1] == '🔵' and 
                board[row+2][col-2] == '🔵' and 
                board[row+3][col-3] == '🔵'):
                return True
    
    return False

@router.message(Command('c4', 'connect4'))
async def connect4(message: types.Message):
    board = [['⚪' for _ in range(7)] for _ in range(6)]
    turn = random.randint(0, 1)
    
    state = {'board': board, 'turn': turn, 'game_message_id': None}
    
    await show_board(message, state)

async def show_board(message: types.Message, state: dict):
    board = state['board']
    turn = state['turn']
    
    builder = InlineKeyboardBuilder()
    for col in range(1, 8):
        builder.button(text = str(col), callback_data = f"col_{col}")
    builder.adjust(7)
    
    board_text = '\n'.join(''.join(row) for row in board)
    
    if turn == 0:
        sent_message = await message.answer(f"{board_text}\n\nВаш ход, выберите столбец:", reply_markup = builder.as_markup())
    else:
        sent_message = await message.answer("Ход бота...")
        await bot_move(message, state)
    
    state['game_message_id'] = sent_message.message_id
    states[sent_message.message_id] = state

async def bot_move(message: types.Message, state: dict):
    board = state['board']
    
    if all(board[0][col] != '⚪' for col in range(7)):
        if state['game_message_id'] in states:
            del states[state['game_message_id']]
        return await message.answer('Ничья!')
    
    move = random.randint(1, 7)
    while board[0][move - 1] != '⚪':
        move = random.randint(1, 7)
    
    for i in range(5, -1, -1):
        if board[i][move - 1] == '⚪':
            board[i][move - 1] = '🔵'
            state['turn'] = 0
            break
    
    if check_for_blue(board):
        if state['game_message_id'] in states:
            del states[state['game_message_id']]
        await show_board(message, state)
        return await message.answer('Победил бот!')
    
    await asyncio.sleep(1)
    
    await show_board(message, state)

@router.callback_query(lambda c: c.data.startswith('col_'))
async def process_move(callback: types.CallbackQuery):
    state = states.get(callback.message.message_id)
    
    if not state:
        return await callback.answer('Игра не найдена, начните новую /c4')
    
    if state['turn'] == 1:
        return await callback.answer('Сейчас ход бота, подождите')
    
    col = int(callback.data.split('_')[1]) - 1
    board = state['board']
    
    if board[0][col] != '⚪':
        return await callback.answer('Этот столбец заполнен!')
    
    for i in range(5, -1, -1):
        if board[i][col] == '⚪':
            board[i][col] = '🔴'
            state['turn'] = 1
            break
    
    await callback.message.delete()
    if callback.message.message_id in states:
        del states[callback.message.message_id]
    
    if check_for_red(board):
        await show_board(callback.message, state)
        if state['game_message_id'] in states:
            del states[state['game_message_id']]
        return await callback.message.answer('Победил человек!')
    
    if all(board[0][col] != '⚪' for col in range(7)):
        await show_board(callback.message, state)
        if state['game_message_id'] in states:
            del states[state['game_message_id']]
        return await callback.message.answer('Ничья!')
    
    state['turn'] = 1
    await bot_move(callback.message, state)