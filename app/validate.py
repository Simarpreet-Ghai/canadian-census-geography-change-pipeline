import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def validate_staging(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT dauid_2021),
                    COUNT(DISTINCT dauid_2016)
                FROM staging_da_mappings;
                """
            )

            row_count, unique_2021, unique_2016 = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE dauid_2021 IS NULL
                   OR dauid_2016 IS NULL
                   OR dadguid_2021 IS NULL
                   OR dadguid_2016 IS NULL;
                """
            )
            null_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE dauid_2021 NOT LIKE '35%';
                """
            )
            non_ontario_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE relationship_flag NOT IN (1, 2, 3, 4);
                """
            )
            invalid_flag_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        dauid_2021,
                        dauid_2016,
                        relationship_flag,
                        COUNT(*)
                    FROM staging_da_mappings
                    GROUP BY
                        dauid_2021,
                        dauid_2016,
                        relationship_flag
                    HAVING COUNT(*) > 1
                ) AS duplicates;
                """
            )
            duplicate_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE dauid_2021 !~ '^[0-9]{8}$'
                   OR dauid_2016 !~ '^[0-9]{8}$';
                """
            )
            invalid_id_format_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE dadguid_2021 NOT LIKE '2021%'
                   OR dadguid_2016 NOT LIKE '2016%';
                """
            )
            invalid_dguid_year_count = cursor.fetchone()[0]

    print(f"Staging rows: {row_count}")
    print(f"Unique 2021 DAs: {unique_2021}")
    print(f"Unique 2016 DAs: {unique_2016}")
    print(f"Missing required values: {null_count}")
    print(f"Non-Ontario rows: {non_ontario_count}")
    print(f"Invalid relationship flags: {invalid_flag_count}")
    print(f"Duplicate mappings: {duplicate_count}")
    print(f"Invalid DA ID formats: {invalid_id_format_count}")
    print(f"Incorrect DGUID years: {invalid_dguid_year_count}")


def validate_mapping_results(database_url=DATABASE_URL):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM geography_mapping_results;
                """
            )
            result_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings;
                """
            )
            staging_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM geography_mapping_results
                WHERE relationship_type NOT IN (
                    'ONE_TO_ONE',
                    'ONE_TO_MANY',
                    'MANY_TO_ONE',
                    'MANY_TO_MANY'
                );
                """
            )
            invalid_type_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM geography_mapping_results
                WHERE relationship_type = 'ONE_TO_ONE'
                  AND same_id = FALSE;
                """
            )
            unexpected_one_to_one_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM geography_mapping_results
                WHERE relationship_type = 'MANY_TO_MANY'
                  AND same_id = TRUE;
                """
            )
            complex_same_id_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        dauid_2021,
                        dauid_2016,
                        relationship_type,
                        COUNT(*)
                    FROM geography_mapping_results
                    GROUP BY
                        dauid_2021,
                        dauid_2016,
                        relationship_type
                    HAVING COUNT(*) > 1
                ) AS duplicates;
                """
            )
            duplicate_count = cursor.fetchone()[0]

    print(f"Staging rows: {staging_count}")
    print(f"Mapping result rows: {result_count}")
    print(f"Invalid relationship types: {invalid_type_count}")
    print(
        f"Unexpected one-to-one ID changes: "
        f"{unexpected_one_to_one_count}"
    )
    print(
        f"Same-ID many-to-many mappings: "
        f"{complex_same_id_count}"
    )
    print(f"Duplicate mapping results: {duplicate_count}")


if __name__ == "__main__":
    print("Staging validation")
    validate_staging()

    print("\nMapping validation")
    validate_mapping_results()