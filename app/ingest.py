import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "2021_92-156-X_DA_AD.csv"


def load_raw_correspondence(database_url=DATABASE_URL):
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data file not found: {DATA_PATH}")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE raw_da_correspondence
                RESTART IDENTITY;
                """
            )

            with DATA_PATH.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                with cursor.copy(
                    """
                    COPY raw_da_correspondence (
                        dauid_2021,
                        dauid_2016,
                        dbuid_2021,
                        relationship_flag,
                        dadguid_2021,
                        dadguid_2016,
                        dbdguid_2021
                    )
                    FROM STDIN
                    WITH (
                        FORMAT CSV,
                        HEADER TRUE
                    );
                    """
                ) as copy:
                    while chunk := file.read(1024 * 1024):
                        copy.write(chunk)

            cursor.execute(
                "SELECT COUNT(*) FROM raw_da_correspondence;"
            )
            row_count = cursor.fetchone()[0]

        conn.commit()

    print(f"Loaded raw correspondence rows: {row_count}")


if __name__ == "__main__":
    load_raw_correspondence()