from aiogram import types
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.utils.exceptions import CantParseEntities

from filters import IsGroup
from loader import dp, db
from utils.throttlig import rate_limit


@rate_limit(limit=3)
@dp.message_handler(IsGroup(), Command('help'))
async def command_help(message: types.Message):
    text = f'❔<b>Как пользоваться ботом</b>❔\n\n' \
           f'Всё очень просто, напиши боту название книги и бот выдаст тебе все подходящие книги\n' \
           f'Либо ты можешь воспользоваться более точным поиском, с помощью следующих комманд: 👇\n\n' \
           f'/start - стартовая команда, чтобы впервые запустить бота\n' \
           f'/author <i>имя автора</i> - поиск только по авторам\n' \
           f'/series <i>название серии</i> - поиск только по названию серии\n' \
           f'/rating_b - показывает ТОП 10 книг по скачиваниям\n' \
           f'/rating_a - показывает ТОП 10 авторов по запросам\n' \
           f'/help - вызов справки, если ты забыл как пользоваться ботом🙃\n' \
           f'/report - пожаловаться на спам/рекламу/пользователя\n\n' \
           f'❗Чтобы отправить жалобу на пользователя:\n' \
           f'- Зажать на сообщении от пользователя\n' \
           f'чтобы сообщение выделилось, нажать <b>"Ответить"</b> и прописать команду /report\n\n' \
           f'❔ <b>Как искать книги</b> ❔\n\n' \
           f'Чтобы найти нужную книгу, достаточно написать её название\n' \
           f'Обрати внимание! Название книги без ФИО автора\n' \
           f'Также ты можешь воспользоваться точным поиском 👇\n\n' \
           f'Примеры точных запросов:\n' \
           f'/author Джоан Роулинг\n' \
           f'/author Пушкин\n' \
           f'/series песнь льда и пламени\n' \
           f'/series Голодные Игры\n\n' \
           f'❗Если вы заметили ошибку в работе бота,\n' \
           f'❗Либо у вас есть пожелания по улучшению бота\n' \
           f'Напишите в чат следующим образом 👇\n' \
           f'<pre>!message <i>Ваше сообщение администратору</i></pre>\n\n' \
           f'<b>P.S.</b>\n' \
           f'Книжный бар: @books_bar 📚\n' \
           f'Книги доступны во всех форматах для скачивания\n' \
           f'Инструкция по созданию личной группы: /create_group'
    await message.answer(text)


@rate_limit(limit=3)
@dp.message_handler(IsGroup(), CommandStart())
async def command_start(message: types.Message):
    text = f'Привет, {message.from_user.full_name}! \n\nЯ помогу найти тебе любую книгу!😇\n' \
           f'Чтобы начать, пришли мне название книги 📖\n\n' \
           f'Я также могу производить поиск по ФИО автора или названию книжной серии ☺\n' \
           f'Ты можешь узнать больше обо мне здесь 👉 /help\n' \
           f'@books_bar - книжный бар 📚'

    try:
        await message.answer(text)
    except CantParseEntities:  # Ошибка, если у юзера никнейм не стандарный
        pass
    await db.add_user(user=message.from_user.full_name, telegram_id=message.from_user.id)
