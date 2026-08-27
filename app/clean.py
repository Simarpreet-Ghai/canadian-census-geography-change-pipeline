import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def build_staging_mappings(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE staging_da_mappings
                RESTART IDENTITY;
                """
            )

            cursor.execute(
                """
                INSERT INTO staging_da_mappings (
                    dauid_2021,
                    dauid_2016,
                    relationship_flag,
                    dadguid_2021,
                    dadguid_2016
                )
                SELECT DISTINCT
                    dauid_2021,
                    dauid_2016,
                    relationship_flag,
                    dadguid_2021,
                    dadguid_2016
                FROM raw_da_correspondence
                WHERE dauid_2021 LIKE '35%'
                ORDER BY dauid_2021, dauid_2016;
                """
            )

            cursor.execute(
                "SELECT COUNT(*) FROM staging_da_mappings;"
            )
            row_count = cursor.fetchone()[0]

        conn.commit()

    print(f"Loaded staging mappings: {row_count}")


if __name__ == "__main__":
    build_staging_mappings()