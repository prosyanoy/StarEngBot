from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.models import User, Collection, AddedWord, Word, Translation
from bot.config import MINI_APP_URL
from bot.handlers.words import AddWordStates

router = Router()

def to_ipa(s):
    if s is None:
        return ""
    return ' /' + s + '/'

@router.message(Command("view_collections"))
async def view_collections_handler(message: Message, db_session: AsyncSession):
    if db_session is None:
        await message.answer("Ошибка доступа к базе данных.")
        return
    result = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = result.scalars().first()
    if not user:
        await message.answer("Пользователь не найден. Сначала создайте коллекцию.")
        return
    result = await db_session.execute(select(Collection).where(Collection.user_id == user.id))
    collections = result.scalars().all()
    if not collections:
        await message.answer("У вас пока нет коллекций.")
        return
    text_lines = []
    now = datetime.now()
    for col in collections:
        count_result = await db_session.execute(
            select(func.count(AddedWord.id)).where(
                AddedWord.collection_id == col.id,
                AddedWord.user_id == user.id,
                AddedWord.next_repeat == None
            )
        )
        ready_to_learn = count_result.scalar()
        count_result = await db_session.execute(
            select(func.count(AddedWord.id)).where(
                AddedWord.collection_id == col.id,
                AddedWord.user_id == user.id,
                AddedWord.next_repeat <= now
            )
        )
        ready_to_repeat = count_result.scalar()
        text_lines.append(
            f"Коллекция: {col.name}\n"
            f"Слов готовых к изучению: {ready_to_learn}\n"
            f"Слов готовых к повторению: {ready_to_repeat}\n"
        )
    text = "\n".join(text_lines)
    await message.answer(text)
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for col in collections:
        if ready_to_repeat > 0:
            web_app_url = f"{MINI_APP_URL}/translate/{col.id}?mode=repeat"
        else:
            web_app_url = f"{MINI_APP_URL}/learn/{col.id}"
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Show {col.name}", callback_data=f"show_{col.id}"),
            InlineKeyboardButton(text=f"Learn {col.name}", web_app=WebAppInfo(url=web_app_url))
        ])
    await message.answer("Выберите действие для каждой коллекции:", reply_markup=kb)

@router.callback_query(F.data.startswith("show_"))
async def show_collection_handler(callback: CallbackQuery, db_session: AsyncSession):
    await callback.answer()
    col_id = int(callback.data.split("_")[1])
    if db_session is None:
        await callback.message.answer("Ошибка доступа к базе данных.")
        return
    result = await db_session.execute(
        select(AddedWord, Word, Translation)
        .join(Word, AddedWord.word_id == Word.id)
        .join(Translation, AddedWord.translation_id == Translation.id)
        .where(AddedWord.collection_id == col_id)
    )
    rows = result.all()
    if not rows:
        await callback.message.answer("В коллекции пока нет слов.")
        return
    lines = []
    now = datetime.now()
    for added_word, word, translation in rows:
        if added_word.next_repeat is not None and added_word.next_repeat > now:
            lines.append(f"• {word.english_word}{to_ipa(translation.transcription)} → {translation.translation} [повтор в {added_word.next_repeat}]")
        else:
            lines.append(f"• {word.english_word}{to_ipa(translation.transcription)} → {translation.translation} [готово к изучению]")
    text = "\n".join(lines)
    await callback.message.answer(text)

@router.callback_query(F.data.startswith("learn_"))
async def learn_collection_handler(callback: CallbackQuery):
    await callback.answer()
    col_name = callback.data.split("_")[1]
    await callback.message.answer(f"Открываем коллекцию {col_name}")

class CreateCollectionStates(StatesGroup):
    waiting_for_collection_name = State()

@router.message(Command("create_collection"))
async def create_collection_handler(message: Message, state: FSMContext):
    await message.answer("Введите название новой коллекции:")
    await state.set_state(CreateCollectionStates.waiting_for_collection_name)

@router.message(CreateCollectionStates.waiting_for_collection_name)
async def process_collection_name(message: Message, state: FSMContext, db_session: AsyncSession):
    collection_name = message.text.strip()
    if not collection_name:
        await message.answer("Название не может быть пустым. Попробуйте ещё раз.")
        return
    if db_session is None:
        await message.answer("Ошибка доступа к базе данных.")
        return
    from bot.models import User
    result = await db_session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = result.scalars().first()
    if not user:
        user = User(telegram_id=message.from_user.id)
        db_session.add(user)
        await db_session.flush()
    new_collection = Collection(name=collection_name, user_id=user.id)
    db_session.add(new_collection)
    await db_session.commit()
    await message.answer(f"Новая коллекция '{collection_name}' создана!")
    await state.set_state(AddWordStates.waiting_for_new_word)
