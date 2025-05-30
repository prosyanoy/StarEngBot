import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

client = AsyncOpenAI()

class TranslationModel(BaseModel):
    transcription: str
    translation: str
    example_en: str
    example_ru: str

class Translations(BaseModel):
    word: str
    translations: list[TranslationModel]

async def get_gpt_translations(english_word: str) -> Optional[Translations]:
    try:
        response = await client.responses.parse(
            model="gpt-4.1-nano",
            input=[
                {
                    "role": "system",
                    "content": "You will be provided with a word in English, and your task is return the word with 3 to 5 Russian translations in the format:\n"
                               "{\n"
                               "  \"transcription\": \"<word IPA without slashes>\", \n"
                               "  \"translation\": \"<Russian translation of the word>\",\n"
                               "  \"example_en\": \"<Example of a context sentence with that word meaning>\",\n"
                               "  \"example_ru\": \"<Context sentence translation with that Russian translation of the word>\"\n"
                               "}\n"
                },
                {
                    "role": "user",
                    "content": english_word
                }
            ],
            text_format=Translations,
            max_output_tokens=256,
            temperature=0.5,
            top_p=1,
        )
        return response.output_parsed
    except Exception as e:
        logging.error(f"Ошибка при запросе к GPT: {e}")
        return []

class Options(BaseModel):
    correct: str
    wrong1: str
    wrong2: str
    wrong3: str
    wrong4: str
    wrong5: str
    wrong6: str
    wrong7: str
    wrong8: str
    wrong9: str

async def get_translation_options(english_word: str, level: str) -> Optional[Options]:
    try:
        response = await client.responses.parse(
            model="gpt-4.1-nano",
            input=[
                {
                    "role": "system",
                    "content": f"You are given an English word. You will return its most likely Russian translation and 9 completely wrong and different translation options of the same part of speech that will blur the correct option for {level}1-{level}2 learner."
                },
                {
                    "role": "user",
                    "content": english_word
                }
            ],
            text_format=Options,
            max_output_tokens=256,
            temperature=0.5,
            top_p=1,
        )
        return response.output_parsed
    except Exception as e:
        logging.error(f"Ошибка при запросе к GPT: {e}")
        return []