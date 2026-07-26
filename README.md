# StarEngBot

StarEngBot is a Telegram-based English-learning platform that combines a chat bot, an authenticated Mini App, a REST API, and PostgreSQL storage. It assesses a learner's CEFR band, generates translations and examples with OpenAI, organizes vocabulary into personal collections, and trains words through translation, spelling, pronunciation, context, matching, and spaced repetition.

## Components

- `bot/` — Aiogram bot, placement test, word lookup, collections, and Mini App launcher.
- `backend/` — FastAPI endpoints, Telegram Web App authentication, JWT authorization, learning tasks, pronunciation scoring, and review scheduling.
- `miniapp/` — React/Vite Telegram Mini App with English and Russian UI.
- `cefr/` — CEFR vocabulary data used by the placement test.
- `alembic/` — PostgreSQL database migrations.

**Stack:** Python, Aiogram 3, FastAPI, async SQLAlchemy, PostgreSQL, Alembic, OpenAI API, React 18, Vite, Tailwind CSS, and Telegram Web Apps.

## Run locally

Requirements: Python, Node.js/npm, PostgreSQL, a Telegram bot token, and an OpenAI API key.

```bash
git clone https://github.com/prosyanoy/StarEngBot.git
cd StarEngBot
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the repository root:

```env
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost/stareng
MINI_APP_URL=https://your-public-host/stareng
SECRET_KEY=replace_with_a_long_random_secret
```

Initialize the database and start the bot plus API:

```bash
alembic upgrade head
python main.py
```

The API listens on port `8000`; the Telegram bot runs by long polling in the same process.

Start the Mini App separately:

```bash
cd miniapp
npm install
npm run dev
```

For local API development, change `API_ROOT` in `miniapp/src/lib/api.tsx` to `http://localhost:8000`. Telegram authentication requires launching the Mini App from Telegram with a public HTTPS URL. Build the frontend with `npm run build`.

## Basic flow

1. Run `/start` to take or repeat the 15-word CEFR placement test.
2. Run `/create_collection` to create a vocabulary collection.
3. Send an English word to select an AI-generated translation and save it.
4. Run `/view_collections` to inspect collections and launch learning or review sessions in the Mini App.
