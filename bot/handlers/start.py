import random
from typing import List

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, Text, Bold
from sqlalchemy import select

from bot.models import CEFR, User
from cefr.lexicon import build_lexicon

LEXICON_DF = build_lexicon()
from bot.ai import get_translation_options

rng = random.SystemRandom()

router = Router()

# ─────────────────────  FSM  ──────────────────────
class TestStates(StatesGroup):
    asking     = State()   # showing a word & options
    finished   = State()   # waiting for user to pick final level

# structure we’ll save in FSM “data”
class QuizData:
    def __init__(
        self,
        queue,                     # required
        totals=None,               # optional when rebuilding
        correct=None,
        curr = 'A'
    ):
        self.queue   = queue
        self.curr = curr
        self.totals  = totals  or {"A": 0, "B": 0, "C": 0}
        self.correct = correct or {"A": 0, "B": 0, "C": 0}

# handlers/start.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from bot.models import User, CEFR

router = Router()

# ────────────────────────────────────────────
async def launch_quiz(message: Message, state: FSMContext):
    """
    Starts the 15-word placement test.
    Can be called from /start OR from any callback.
    """
    # -------- previously the content of start_handler ----------
    queue = []
    rng = random.SystemRandom()
    for band in ("A", "B", "C"):
        sample = (
            LEXICON_DF.query("band == @band")
            .sample(5, random_state=rng.randint(0, 10_000_000))
            [["word"]].values.flatten()
        )
        queue += [(w, band) for w in sample]

    await state.clear()
    await state.update_data(quiz=QuizData(queue).__dict__)
    await ask_next_word(message.chat.id, state, message)
    await message.delete()

# ─────────────────────────  /start  ─────────────────────────
@router.message(Command("start"))
async def start_handler(message: Message, db_session):
    tg_id = message.from_user.id

    result = await db_session.execute(
        select(User).where(User.telegram_id == tg_id)
    )
    user = result.scalars().first()

    if user is None:
        # create empty record
        user = User(telegram_id=tg_id)
        db_session.add(user)
        await db_session.commit()

    # CASE 1 – no level yet
    if user.cefr is None:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔸 Take the placement test",
                    callback_data="start_test")]
            ]
        )
        await message.answer(
            "Welcome! To begin, please take our 15-word placement test.",
            reply_markup=kb
        )
        return

    # CASE 2 – level exists → offer options
    mark = {"A": "✅", "B": "✅", "C": "✅"}      # mark suggested button
    for k in mark:
        mark[k] = "✅" if k == user.cefr.value else ""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🔄 Пройти заново", callback_data="start_test"),
        ], [
            InlineKeyboardButton(text=f"A {mark['A']}", callback_data="set_A"),
            InlineKeyboardButton(text=f"B {mark['B']}", callback_data="set_B"),
            InlineKeyboardButton(text=f"C {mark['C']}", callback_data="set_C"),
        ], [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_start")
        ]]
    )

    await message.answer(
        **Text("Ваш текущий уровень ", Bold(user.cefr.value), "\nЖелаете пройти тест заново или поменять уровень?").as_kwargs(),
        reply_markup=kb,
    )

# ─────────────────── callback buttons ──────────────────
@router.callback_query(F.data == "start_test")
async def start_test_button(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    # simply trigger /start of lex_test
    await launch_quiz(cb.message, state)

@router.callback_query(F.data.startswith("set_"))
async def set_level_manually(cb: CallbackQuery, db_session):
    level = cb.data.split("_", 1)[1]           # "A"|"B"|"C"
    result = await db_session.execute(
        select(User).where(User.telegram_id == cb.from_user.id)
    )
    user = result.scalars().first()
    user.cefr = CEFR[level]
    await db_session.commit()
    await cb.answer("Level saved!")
    await cb.message.edit_reply_markup()
    await cb.message.answer(**Text("Выбранный уровень ", Bold(level), ". 👍").as_kwargs())

@router.callback_query(F.data == "cancel_start")
async def cancel_start(cb: CallbackQuery):
    await cb.answer()
    await cb.message.edit_reply_markup()

# ────────────────────  asking phase  ────────────────────
async def ask_next_word(chat_id: int, state: FSMContext, msg: Message):
    data = await state.get_data()
    quiz = QuizData(**data["quiz"])

    if not quiz.queue:        # finished
        await summarize(chat_id, state, quiz, msg)
        return

    word, band = quiz.queue.pop(0)           # take next
    await state.update_data(quiz=quiz.__dict__,
                            current_word=word,
                            current_band=band)

    opts = await get_translation_options(word, quiz.curr)    # your GPT call

    buttons = [
        InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")
        for _, opt in iter(opts)
    ]

    rng.shuffle(buttons)

    # split into chunks of 2 → 5 rows
    rows = [buttons[i:i + 2] for i in range(0, 10, 2)]

    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await state.set_state(TestStates.asking)
    await msg.answer(
        reply_markup=kb,
        **Text("Как переводится ", Bold(word), "?").as_kwargs()
    )

# answer handler
@router.callback_query(TestStates.asking, F.data.startswith("ans_"))
async def check_answer(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    chosen = cb.data.split("ans_", 1)[1]
    data   = await state.get_data()
    quiz   = QuizData(**data["quiz"])
    word   = data["current_word"]
    band   = data["current_band"]

    opts = await get_translation_options(word, quiz.curr)
    quiz.totals[band] += 1
    if quiz.totals[band] == 5:
        quiz.curr = chr(ord(quiz.curr) + 1)
    if chosen == opts.correct:
        quiz.correct[band] += 1
        resp = "✅ Правильно!"
    else:
        resp = f"❌ Ошибка. Правильный ответ: {opts.correct}"

    # update & continue
    await state.update_data(quiz=quiz.__dict__)
    await cb.message.edit_reply_markup()
    await cb.message.answer(resp)
    await ask_next_word(cb.message.chat.id, state, cb.message)

# ─────────────────────  finish  ─────────────────────
async def summarize(chat_id: int, state: FSMContext, quiz: QuizData, msg: Message):
    A,B,C = quiz.correct["A"], quiz.correct["B"], quiz.correct["C"]
    res   = (A + 2*B + 3*C) / 30
    if res < 1/6:
        suggested = "A (Beginner)"
    elif res < 1/2:
        suggested = "B (Intermediate)"
    else:
        suggested = "C (Advanced)"

    # make three buttons, mark suggested with ✅
    def btn(level: str):
        mark = " ✅" if level == suggested[0] else ""
        return InlineKeyboardButton(text=level + mark,
                                    callback_data=f"lvl_{level}")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[btn("A"), btn("B"), btn("C")]]
    )

    results_msg = Text(f"🏁 Тест окончен!\nПравильных слов A1-A2: {A}/5\nПравильных слов B1-B2: {B}/5\nПравильных слов C1-C2: {C}/5\n\n"
        f"Ваш результат: ", Bold(str(int(res * 100)), "%"), "\n"
        f"Предлагаем вам начать на уровне ", Bold("level ", suggested), "\nС чего начнем?:"
    )

    await state.set_state(TestStates.finished)
    await msg.answer(reply_markup=kb, **results_msg.as_kwargs())

# lex_test.py  – replace old callback
@router.callback_query(TestStates.finished, F.data.startswith("lvl_"))
async def level_chosen(cb: CallbackQuery, db_session, state: FSMContext):
    level_str = cb.data.split("_", 1)[1]             # "A" | "B" | "C"
    # 1. upsert user
    result = await db_session.execute(
        select(User).where(User.telegram_id == cb.from_user.id)
    )
    user = result.scalars().first()
    if not user:                               # user may exist w/o cefr
        user = User(telegram_id=cb.from_user.id)

    user.cefr = CEFR[level_str]               # enum member
    db_session.add(user)
    await db_session.commit()

    await cb.answer(f"Уровень {level_str} сохранен!")
    await cb.message.edit_reply_markup()      # remove keyboard
    await cb.message.answer("Отлично! Начнем учиться с этого уровня.")
    await state.clear()
