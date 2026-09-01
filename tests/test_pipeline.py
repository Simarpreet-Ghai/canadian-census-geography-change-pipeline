import psycopg


def test_raw_correspondence_loaded(test_database_url):
    with psycopg.connect(test_database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM raw_da_correspondence;
                """
            )
            row_count = cursor.fetchone()[0]

    assert row_count == 499052


def test_ontario_staging_counts(test_database_url):
    with psycopg.connect(test_database_url) as conn:
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

    assert row_count == 20690
    assert unique_2021 == 20468
    assert unique_2016 == 20160


def test_staging_data_quality(test_database_url):
    with psycopg.connect(test_database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_da_mappings
                WHERE dauid_2021 IS NULL
                   OR dauid_2016 IS NULL
                   OR dadguid_2021 IS NULL
                   OR dadguid_2016 IS NULL
                   OR dauid_2021 NOT LIKE '35%'
                   OR relationship_flag NOT IN (1, 2, 3, 4)
                   OR dauid_2021 !~ '^[0-9]{8}$'
                   OR dauid_2016 !~ '^[0-9]{8}$';
                """
            )
            invalid_rows = cursor.fetchone()[0]

    assert invalid_rows == 0


def test_mapping_relationship_counts(test_database_url):
    with psycopg.connect(test_database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT relationship_type, COUNT(*)
                FROM geography_mapping_results
                GROUP BY relationship_type;
                """
            )
            relationship_counts = dict(cursor.fetchall())

    assert relationship_counts == {
        "ONE_TO_ONE": 19658,
        "ONE_TO_MANY": 4,
        "MANY_TO_ONE": 475,
        "MANY_TO_MANY": 553,
    }


def test_same_id_baseline_results(test_database_url):
    with psycopg.connect(test_database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(DISTINCT dauid_2021)
                FROM staging_da_mappings
                WHERE dauid_2021 = dauid_2016;
                """
            )
            same_id_count = cursor.fetchone()[0]

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
            no_same_id_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT dauid_2021)
                FROM staging_da_mappings
                WHERE dauid_2021 = dauid_2016
                  AND relationship_flag = 4;
                """
            )
            complex_same_id_count = cursor.fetchone()[0]

    assert same_id_count == 19717
    assert no_same_id_count == 751
    assert complex_same_id_count == 59