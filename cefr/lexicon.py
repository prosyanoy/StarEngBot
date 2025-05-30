import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
CSV_AB   = DATA_DIR / "data/a1b2.csv"
CSV_C    = DATA_DIR / "data/c1c2.csv"

def _read_and_normalise(csv_path: Path) -> pd.DataFrame:
    """
    Читаем CSV и приводим к формату: word, pos, CEFR
    (пропускаем заголовок на 1-й строке, если он там есть - см. скрины)
    """
    df = (
        pd.read_csv(csv_path)
          .rename(columns={"headword": "word"})   # унифицируем
          .loc[:, ["word", "pos", "CEFR"]]        # оставляем нужное
          .dropna(subset=["word", "CEFR"])        # на всякий
          .assign(
            word=lambda d: d["word"].str.split("/").str[0].str.strip(),
            CEFR=lambda d: d["CEFR"].str.upper().str.strip()  # A1…
          )
    )
    return df

def build_lexicon() -> pd.DataFrame:
    # читаем оба куска
    df_ab = _read_and_normalise(CSV_AB)
    df_c  = _read_and_normalise(CSV_C)

    # склеиваем
    df = pd.concat([df_ab, df_c], ignore_index=True)

    # добавляем обобщённый band  A/B/C
    df["band"] = df["CEFR"].str[0]          # берём первую букву уровня

    # удаляем возможные дубликаты «слово + pos»
    df = df.drop_duplicates(subset=["word", "pos"])

    return df