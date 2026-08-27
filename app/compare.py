import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def compare_id_matching(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(DISTINCT dauid_2021)
                FROM staging_da_mappings;
                """
            )
            total_2021 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT dauid_2021)
                FROM staging_da_mappings
                WHERE dauid_2021 = dauid_2016;
                """
            )
            same_id_matches = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT dauid_2021
                    FROM staging_da_mappings
                    GROUP BY dauid_2021
                    HAVING BOOL_OR(dauid_2021 = dauid_2016) = FALSE
                ) AS unmatched;
                """
            )
            no_same_id_match = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT dauid_2021)
                FROM staging_da_mappings
                WHERE dauid_2021 = dauid_2016
                  AND relationship_flag = 4;
                """
            )
            complex_same_id = cursor.fetchone()[0]

    print(f"Total 2021 Ontario DAs: {total_2021}")
    print(f"Same-ID matches: {same_id_matches}")
    print(f"No same-ID match: {no_same_id_match}")
    print(f"Same-ID matches with many-to-many relationship: {complex_same_id}")


if __name__ == "__main__":
    compare_id_matching()