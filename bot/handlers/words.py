import logging
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, Text, Bold
from spellchecker import SpellChecker

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.models import User, Word, Collection, Translation, AddedWord
from pydantic import BaseModel
from bot.ai import TranslationModel, Translations, get_gpt_translations


router = Router()

# FSM-состояния для добавления слова
class AddWordStates(StatesGroup):
    waiting_for_new_word = State()
    waiting_for_corrected_choice = State()
    waiting_for_translation_choice = State()
    waiting_for_collection_choice = State()


async def check_collections(callback: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    if db_session is None:
        await callback.message.answer("Ошибка доступа к базе данных.")
        await state.clear()
        return
    # Получаем пользователя (или создаём, если отсутствует)
    result = await db_session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = result.scalars().first()
    if not user:
        user = User(telegram_id=callback.from_user.id)
        db_session.add(user)
        await db_session.flush()
    result = await db_session.execute(select(Collection).where(Collection.user_id == user.id))
    collections = result.scalars().all()
    if not collections:
        await callback.message.answer(
            "У вас ещё нет коллекций. Сначала создайте коллекцию командой /create_collection."
        )
        await state.clear()
        return None
    return collections

async def fetch_translations_from_db(
    word: str,
    session: AsyncSession
) -> Optional[Translations]:

    result = await session.execute(
        select(Translation)
        .join(Word)                       # INNER JOIN words
        .where(Word.english_word == word)
        .options(joinedload(Translation.word))   # optional – eager-load
    )

    translations = result.scalars().all()        # list[Translation]

    if not translations:
        return None

    models = [
        TranslationModel(
            transcription=t.transcription or "",
            translation=t.translation,
            example_en=t.example_en or "",
            example_ru=t.example_ru or "",
        )
        for t in translations
    ]

    return Translations(word=word, translations=models)

# ------------ add word -----------------------------------------------
@router.message(AddWordStates.waiting_for_new_word, lambda m: m.text and not m.text.startswith("/"))
async def auto_add_word(message: Message,
                        state: FSMContext,
                        db_session: AsyncSession):
    english_word = message.text.strip()
    await process_english_word(
        english_word,
        state,
        db_session,
        message=message
    )

# ------------------------------------------------------------------
async def process_english_word(
    english_word: str,
    state: FSMContext,
    db_session: AsyncSession,
    message: Optional[Message] = None,
    callback: Optional[CallbackQuery] = None
):
    english_word = english_word.lower()
    if callback:
        message = callback.message
    else:
        spell = SpellChecker()
        if bool(spell.unknown([english_word])):
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=c, callback_data=f"cr_{c}")]
                                 for c in spell.candidates(english_word)]
            )
            if not kb.inline_keyboard:
                await message.answer("Указанное слово не найдено. Try again 🙂")
                return
            await message.answer(
                "Указанное слово не найдено. Возможно, вы имели в виду:",
                reply_markup=kb
            )
            await state.set_state(AddWordStates.waiting_for_corrected_choice)
            return

    # 1. пытаемся найти переводы в базе
    translations_data = await fetch_translations_from_db(english_word, db_session)

    # 2. если их нет — запрашиваем GPT
    if translations_data is None:
        translations_data = await get_gpt_translations(english_word)
        if translations_data is None:
            await message.answer("Не удалось получить переводы. Попробуйте позже.")
            await state.clear()
            return

    # 3. сохраняем в FSM
    await state.update_data(translations=translations_data)

    # 4. выводим варианты
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    content_lines = [Text(f"Переводы слова {translations_data.word}"), Text("Выберите один:\n")]
    for idx, item in enumerate(translations_data.translations):
        content_lines.append(
            Text(f"{idx + 1}. ", Bold(item.translation), f" /{item.transcription}/\n", Bold(item.example_en), "\n",
                 item.example_ru, "\n"))
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=item.translation, callback_data=f"tr_{idx}")
        ])

    await message.answer(**as_list(*content_lines).as_kwargs(), reply_markup=kb)
    await state.set_state(AddWordStates.waiting_for_translation_choice)

@router.callback_query(AddWordStates.waiting_for_corrected_choice, F.data.startswith("cr_"))
async def process_corrected_choice(callback: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    english_word = callback.data.split("_")[1]
    await process_english_word(english_word, state, db_session, callback=callback)

@router.callback_query(AddWordStates.waiting_for_translation_choice, F.data.startswith("tr_"))
async def process_translation_choice(callback: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    await callback.answer()
    idx = int(callback.data.split("_")[1])
    state_data = await state.get_data()
    tr: Translations = state_data.get("translations")
    word: str = tr.word
    translations = tr.translations
    if idx < 0 or idx >= len(translations):
        await callback.message.answer("Неверный выбор. Попробуйте заново.")
        await state.clear()
        return
    chosen_translation = translations[idx]
    await state.update_data(chosen_translation=chosen_translation)
    collections = await check_collections(callback, state, db_session)
    if not collections:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for col in collections:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=col.name, callback_data=f"col_{col.id}")
        ])
    await callback.message.answer(
        f"Вы выбрали перевод: {chosen_translation.translation}\nТеперь выберите коллекцию:",
        reply_markup=kb
    )
    await state.set_state(AddWordStates.waiting_for_collection_choice)

@router.callback_query(AddWordStates.waiting_for_collection_choice, F.data.startswith("col_"))
async def process_collection_choice(
    callback: CallbackQuery,
    state: FSMContext,
    db_session: AsyncSession         # берём из middleware
):
    await callback.answer()
    col_id = int(callback.data.split("_")[1])

    state_data        = await state.get_data()
    tr: Translations  = state_data["translations"]          # объект Translations
    chosen            = state_data["chosen_translation"]    # dict одного перевода

    # ---------- 1. берём (или создаём) Word ----------
    result    = await db_session.execute(
        select(Word).where(Word.english_word == tr.word)
    )
    word_obj  = result.scalars().first()
    if not word_obj:
        word_obj = Word(english_word=tr.word)
        db_session.add(word_obj)
        await db_session.flush()

    # ---------- 2. загружаем ВСЕ уже существующие переводы слова ----------
    result = await db_session.execute(
        select(Translation).where(Translation.word_id == word_obj.id)
    )
    existing = {t.translation: t for t in result.scalars().all()}     # dict по тексту перевода

    # ---------- 3. проходим по каждому переводу из GPT (или из БД) ----------
    added_translation_objs: list[Translation] = []
    for t in tr.translations:
        if t.translation in existing:
            # перевод уже есть — используем существующий объект
            tr_obj = existing[t.translation]
        else:
            # нового нет — добавляем в таблицу translations
            tr_obj = Translation(
                word_id      = word_obj.id,
                translation  = t.translation,
                transcription= t.transcription,
                example_en   = t.example_en,
                example_ru   = t.example_ru
            )
            db_session.add(tr_obj)
            await db_session.flush()
        added_translation_objs.append(tr_obj)

    # ---------- 4. получаем (или создаём) пользователя ----------
    result = await db_session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalars().first()
    if not user:
        user = User(telegram_id=callback.from_user.id)
        db_session.add(user)
        await db_session.flush()

    # ---------- 5. добавляем запись в added_words ТОЛЬКО для выбранного перевода ----------
    chosen_text = chosen.translation
    translation_obj = next(t for t in added_translation_objs if t.translation == chosen_text)

    added = AddedWord(
        word_id       = word_obj.id,
        translation_id= translation_obj.id,
        user_id       = user.id,
        collection_id = col_id,
        next_repeat   = None
    )
    db_session.add(added)
    await db_session.commit()

    await callback.message.answer(**Text("Слово ", Bold(tr.word),  f" добавлено в коллекцию с переводом «{chosen_text}».").as_kwargs())
    await state.set_state(AddWordStates.waiting_for_new_word)
