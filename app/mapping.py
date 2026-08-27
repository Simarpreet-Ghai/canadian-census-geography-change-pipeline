import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def build_mapping_results(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE geography_mapping_results
                RESTART IDENTITY;
                """
            )

            cursor.execute(
                """
                INSERT INTO geography_mapping_results (
                    dauid_2021,
                    dauid_2016,
                    dadguid_2021,
                    dadguid_2016,
                    relationship_type,
                    same_id
                )
                SELECT
                    dauid_2021,
                    dauid_2016,
                    dadguid_2021,
                    dadguid_2016,
                    CASE relationship_flag
                        WHEN 1 THEN 'ONE_TO_ONE'
                        WHEN 2 THEN 'ONE_TO_MANY'
                        WHEN 3 THEN 'MANY_TO_ONE'
                        WHEN 4 THEN 'MANY_TO_MANY'
                    END,
                    dauid_2021 = dauid_2016
                FROM staging_da_mappings
                ORDER BY dauid_2021, dauid_2016;
                """
            )

            cursor.execute(
                "SELECT COUNT(*) FROM geography_mapping_results;"
            )
            row_count = cursor.fetchone()[0]

        conn.commit()

    print(f"Loaded mapping results: {row_count}")


if __name__ == "__main__":
    build_mapping_results()