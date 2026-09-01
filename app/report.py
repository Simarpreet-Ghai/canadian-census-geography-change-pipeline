import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "output" / "geography_change_report.json"


def generate_report(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM raw_da_correspondence;
                """
            )
            raw_rows = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT dauid_2021),
                    COUNT(DISTINCT dauid_2016)
                FROM staging_da_mappings;
                """
            )
            staging_rows, unique_2021, unique_2016 = cursor.fetchone()

            cursor.execute(
                """
                SELECT relationship_type, COUNT(*)
                FROM geography_mapping_results
                GROUP BY relationship_type;
                """
            )
            relationship_counts = dict(cursor.fetchall())

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
            same_id_many_to_many = cursor.fetchone()[0]

    report = {
        "source": {
            "dataset": (
                "Statistics Canada 2021 to 2016 "
                "Dissemination Area correspondence"
            ),
            "raw_rows": raw_rows,
        },
        "ontario": {
            "staging_mapping_rows": staging_rows,
            "unique_2021_das": unique_2021,
            "unique_2016_das": unique_2016,
        },
        "relationship_counts": {
            "one_to_one": relationship_counts.get("ONE_TO_ONE", 0),
            "one_to_many": relationship_counts.get("ONE_TO_MANY", 0),
            "many_to_one": relationship_counts.get("MANY_TO_ONE", 0),
            "many_to_many": relationship_counts.get("MANY_TO_MANY", 0),
        },
        "id_comparison": {
            "same_id_matches": same_id_matches,
            "no_same_id_match": no_same_id_match,
            "same_id_many_to_many": same_id_many_to_many,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"Report written to: {OUTPUT_PATH}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    generate_report()