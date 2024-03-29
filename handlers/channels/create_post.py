from aiogram import md
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.storage import FSMContext

from filters import IsPrivate
from handlers.channels.strings import text_channel
from keyboards.inline.channel_keyboards import quit_keyboard, user_menu, ua_link_keyboard
from loader import dp, db
from states import Post
from utils.utils import check_link_for_channel, replace_symbols


@dp.message_handler(IsPrivate(), Command('create_post'))
async def create_post(message: types.Message):
    text = f"⚠ Правила публикаций в канале ⚠\n\n" \
           f"<b>Ограничения</b>\n" \
           f" - Фото книги не должно весить более 5 метров\n" \
           f" - Максимально допустимое кол-во символов:\n" \
           f"       - ФИО автора и название книги - 255 символов\n" \
           f"       - Описание - 2000 символов\n" \
           f"Ссылка должна быть в формате: <pre>/b_00000</pre>\n" \
           f"‼ Книга должна быть в библиотеке бота\n\n\n" \
           f"Итак, начнем❕\n" \
           f"<b>Пришли мне изображение книги</b>\n\n"

    await message.answer(text, reply_markup=quit_keyboard)
    await Post.Image.set()


@dp.message_handler(state=Post.Book)
async def get_post_book(message: types.Message, state: FSMContext):
    await state.update_data(book=replace_symbols(message.text[:254]))
    await message.answer('✅ Теперь пришли мне ФИО автора\n'
                         '<i>Если авторов несколько, пожалуйста, перечисли их ФИО через запятую</i>',
                         reply_markup=quit_keyboard)
    await Post.Author.set()


@dp.message_handler(state=Post.Author)
async def get_post_author(message: types.Message, state: FSMContext):
    await state.update_data(author=replace_symbols(message.text[:254]))
    await message.answer('✅ Есть! Теперь пришли описание книги', reply_markup=quit_keyboard)
    await Post.Description.set()


@dp.message_handler(state=Post.Description)
async def get_post_description(message: types.Message, state: FSMContext):
    url = md.hide_link("https://telegra.ph//file/93909ec4609d4bbc71f41.jpg")
    text = f'✅ Есть! Теперь пришли ссылку на книгу\n' \
           f'Как найти ссылку на конкретную книгу👇 {url}'

    await state.update_data(description=replace_symbols(message.text[:2000]))
    await message.answer(text, reply_markup=quit_keyboard)
    await Post.RuLink.set()


@dp.message_handler(state=Post.RuLink)
async def get_post_ru_link(message: types.Message, state: FSMContext):
    link = await check_link_for_channel(message.text, message)
    if not link:  return await Post.RuLink.set()
    await state.update_data(ru_link=message.text)
    await Post.UaLink.set()
    await message.answer('✅ Есть! Теперь пришли ссылку на книгу (если она есть) на украинском языке',
                         reply_markup=ua_link_keyboard())


@dp.message_handler(state=Post.UaLink)
async def get_post_ua_link(message: types.Message, state: FSMContext):
    '''
    Получаем последний стейт и выводим юзеру пост в готовом виде и клавиатуру
    '''
    link = await check_link_for_channel(message.text, message)
    if not link:  return await Post.UaLink.set()

    await state.update_data(ua_link=message.text)

    data = await state.get_data()
    dct = {
        'user_id': message.from_user.id, 'url': data['url'], 'book': data['book'], 'author': data['author'],
        'ru_link': data['ru_link'], 'ua_link': message.text, 'description': data['description']
    }
    post_id = await db.create_post(dct)
    await state.finish()

    text = text_channel(data)
    await message.answer(text, reply_markup=user_menu(post_id=post_id, user_id=message.from_user.id))


@dp.callback_query_handler(text='skip', state=Post.UaLink)
async def skip_adding_ua_link(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dct = {
        'user_id': call.message.from_user.id, 'url': data['url'], 'book': data['book'], 'author': data['author'],
        'ru_link': data['ru_link'], 'ua_link': None, 'description': data['description']
    }
    post_id = await db.create_post(dct)
    await state.finish()

    text = text_channel(data)
    await call.message.answer(text, reply_markup=user_menu(post_id=post_id, user_id=call.message.from_user.id))
