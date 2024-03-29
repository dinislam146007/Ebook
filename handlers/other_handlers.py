import re

from aiogram import types
from aiogram.utils.exceptions import CantRestrictSelf, CantRestrictChatOwner

from loader import dp
from utils.throttlig import rate_limit


@rate_limit(limit=3)
@dp.message_handler(regexp=re.compile(r'^/.+'))
async def other_command(message: types.Message):
    # Проверям на любую битую ссылку
    text = f'У меня нет такой комманды 😨\n' \
           f'Попробуй еще раз\n' \
           f'Либо можешь ознакомится со справкой 👉 /help'
    return await message.answer(text)


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def check_new_user(message: types.Message):
    '''
    Проверка нового юзера вступившего в группу, чтобы не было ботов в группе
    '''
    new_user = message.new_chat_members[0]
    telegram_bots = ['Channel_Bot', 'GroupAnonymousBot']
    if new_user.is_bot and message.from_user.username not in telegram_bots:
        await message.answer(f'Пользователь {new_user.get_mention()} был кикнут!\n'
                             f'Причина: Вход в группу разрешен только людям 🤖')
        try:
            await dp.bot.kick_chat_member(message.chat.id, new_user.id)             # Кик на бота
        except CantRestrictSelf:
            pass
        except CantRestrictChatOwner:
            pass
        await dp.bot.kick_chat_member(message.chat.id, message.from_user.id)    # Кик на юзера который привел бота
