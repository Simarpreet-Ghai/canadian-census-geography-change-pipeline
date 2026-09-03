# Canadian Census Geography Change Pipeline

A Python and PostgreSQL data pipeline I built using official Statistics Canada data to explore how Ontario census geographies changed between the 2016 and 2021 censuses.

I wanted to work with real census data and see how these areas changed over time, especially whether the same geography ID in both years actually meant the area stayed the same.

## Demo

> 🔊 This demo has audio narration!

https://github.com/user-attachments/assets/717559d5-9bad-4450-b5c6-9807a2282ea0

## Why I Built This

I wanted to work with a real public dataset that had more complexity than data I could generate myself.

While looking through Statistics Canada data, I found their census geography correspondence files. They show how areas from one census relate to areas from another, including one-to-one, one-to-many, many-to-one, and many-to-many relationships.

I thought this would be a good way to get more hands-on experience with data pipelines, PostgreSQL, SQL validation, automated testing, and working through the structure of a real dataset.

## How It Works

```text
Statistics Canada correspondence CSV
                ↓
        PostgreSQL raw table
                ↓
          Ontario filtering
                ↓
      DA-to-DA staging mappings
                ↓
           data validation
                ↓
     relationship classification
                ↓
        same-ID comparison
                ↓
           JSON report
```

The pipeline can be run from one command:

```bash
python -m app.pipeline
```

## Dataset

The project uses Statistics Canada's official **2021 to 2016 Dissemination Area (DA) correspondence data**.

The full source file contains:

```text
499,052 correspondence rows
57,936 unique 2021 DAs
56,590 unique 2016 DAs
```

I narrowed the current analysis to Ontario:

```text
137,888 raw Ontario rows
20,468 unique 2021 Ontario DAs
20,160 unique 2016 Ontario DAs
```

The source file contains dissemination-block-level detail, so multiple raw rows can represent the same DA-to-DA relationship.

After filtering and removing those repeated relationships, the pipeline produces:

```text
20,690 Ontario DA-to-DA mappings
```

## Geography Relationships

I translate Statistics Canada's numeric relationship flags into readable labels:

| Relationship | Mapping Rows |
| --- | ---: |
| ONE_TO_ONE | 19,658 |
| ONE_TO_MANY | 4 |
| MANY_TO_ONE | 475 |
| MANY_TO_MANY | 553 |
| **Total** | **20,690** |

These labels are written from the **2021-to-2016 direction**. For example, `ONE_TO_MANY` means one 2021 DA corresponds to multiple 2016 DAs.

## Most Interesting Finding

I compared the 2021 DA identifiers directly with the 2016 identifiers.

Across **20,468 unique Ontario 2021 DAs**:

```text
19,717 have an exact same-ID match
751 have no exact same-ID match
```

The more interesting result was:

```text
59 DAs keep the same ID across both census years
but are still part of a many-to-many relationship.
```

So even when an ID looks unchanged, the geography behind it may have changed.

That became the main takeaway from the project:

```text
same ID ≠ guaranteed same geography
```

## Validation and Testing

I added SQL-based validation checks instead of assuming that the transformed data was correct just because the pipeline ran successfully.

The staging data is checked for:

- missing required values
- rows outside Ontario
- invalid relationship flags
- duplicate mappings
- invalid DA ID formats
- incorrect census years in DGUIDs

Current validation results:

```text
Missing required values: 0
Non-Ontario rows: 0
Invalid relationship flags: 0
Duplicate mappings: 0
Invalid DA ID formats: 0
Incorrect DGUID years: 0
```

The project also has **5 pytest tests** using a separate PostgreSQL test database.

```text
5 tests passed
```

The tests check the source load, Ontario staging results, data quality, relationship classifications, and the key same-ID findings.

I also added a safety check so destructive test setup can only run against a database whose name ends in `_test`.

## Generated Report

The final results can be written to JSON with:

```bash
python -m app.report
```

This generates:

```text
data/output/geography_change_report.json
```

The values in the report are queried from PostgreSQL when it runs rather than being manually hardcoded.

## Tech Stack

- Python
- PostgreSQL
- SQL
- pandas
- Psycopg
- pytest
- python-dotenv
- Docker
- Git
- Statistics Canada public data

## Running the Project

### Local setup

Clone the repository and create a virtual environment:

```bash
git clone <repository-url>
cd canadian-census-geography-change-pipeline

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create the PostgreSQL databases:

```bash
createdb census_geography
createdb census_geography_test
psql census_geography -f sql/01_create_tables.sql
```

Create a `.env` file based on `.env.example`:

```text
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/census_geography
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/census_geography_test
```

Download the Statistics Canada correspondence CSV and place it at:

```text
data/raw/2021_92-156-X_DA_AD.csv
```

The raw dataset is intentionally not committed to the repository.

Run the pipeline:

```bash
python -m app.pipeline
```

Run the tests:

```bash
python -m pytest -v
```

Generate the report:

```bash
python -m app.report
```

## Running with Docker

With the Statistics Canada CSV in `data/raw/`:

```bash
docker compose -f ./docker-compose.yml build
docker compose -f ./docker-compose.yml up -d db
```

Run the full pipeline:

```bash
docker compose -f ./docker-compose.yml run --rm app python -m app.pipeline
```

Run the tests:

```bash
docker compose -f ./docker-compose.yml run --rm app python -m pytest -v
```

When finished:

```bash
docker compose -f ./docker-compose.yml down
```

I also tested the Docker setup from a **fresh clone** of the repository. The full pipeline reproduced the same results and all 5 tests passed.

## What I Learned

The biggest thing I learned from this project was that understanding what the data represents matters just as much as writing the code that processes it.

At first, 137,888 Ontario rows looked like 137,888 separate relationships. Understanding the block-level structure of the source data was what allowed me to turn it into the 20,690 DA-level mappings I actually wanted to analyze.

I also became much more comfortable with PostgreSQL bulk loading, SQL validation, separating raw/staging/final data, testing against a real database, and using Docker to make a project reproducible outside my own setup.

And the **59 same-ID many-to-many cases** were a good reminder that an identifier matching between two datasets doesn't necessarily mean the thing behind that identifier stayed unchanged.

## Project Metrics

The measured project results are also recorded in [`project_metrics.md`](project_metrics.md) so I can keep the numbers documented without guessing or exaggerating them later.

## License

This project is licensed under the MIT License.
