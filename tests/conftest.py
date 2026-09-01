import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

from app.clean import build_staging_mappings
from app.ingest import load_raw_correspondence
from app.mapping import build_mapping_results


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "sql" / "01_create_tables.sql"


@pytest.fixture(scope="session")
def test_database_url():
    with psycopg.connect(TEST_DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            database_name = cursor.fetchone()[0]

    if not database_name.endswith("_test"):
        raise RuntimeError(
            "Tests can only run against a database ending in '_test'"
        )

    return TEST_DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database(test_database_url):
    with psycopg.connect(test_database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DROP TABLE IF EXISTS geography_mapping_results;
                DROP TABLE IF EXISTS staging_da_mappings;
                DROP TABLE IF EXISTS raw_da_correspondence;
                """
            )

            schema_sql = SCHEMA_PATH.read_text()
            cursor.execute(schema_sql)

        conn.commit()

    load_raw_correspondence(test_database_url)
    build_staging_mappings(test_database_url)
    build_mapping_results(test_database_url)