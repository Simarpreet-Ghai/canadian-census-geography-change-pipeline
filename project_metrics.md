# Project Metrics

I wanted to keep track of the main numbers from the project so I can use them later without guessing or exaggerating anything.

## Source Data

The project uses Statistics Canada's official 2021 to 2016 Dissemination Area correspondence data.

```text
Source correspondence rows: 499,052
Unique 2021 DAs across Canada: 57,936
Unique 2016 DAs across Canada: 56,590
```

The current project scope is Ontario.

```text
Ontario raw correspondence rows: 137,888
Unique Ontario 2021 DAs: 20,468
Unique Ontario 2016 DAs: 20,160
```

## Staging Transformation

The source correspondence file contains dissemination-block-level detail, so the same DA-to-DA relationship can appear across multiple raw rows.

After filtering to Ontario and removing repeated DA relationships:

```text
137,888 Ontario raw rows
→ 20,690 DA-to-DA staging mappings
```

The staging data preserves:

```text
20,468 unique 2021 Ontario DAs
20,160 unique 2016 Ontario DAs
```

## Geography Relationships

At the unique 2021 DA level, the official relationship flags contain:

```text
One-to-one:   19,658
One-to-many:       2
Many-to-one:     475
Many-to-many:    333
```

Because one geography can correspond to multiple geographies, the final DA-to-DA mapping table contains:

```text
ONE_TO_ONE:   19,658 mapping rows
ONE_TO_MANY:       4 mapping rows
MANY_TO_ONE:     475 mapping rows
MANY_TO_MANY:    553 mapping rows
```

Total:

```text
20,690 classified mapping rows
```

## Simple ID Comparison

Across the 20,468 unique 2021 Ontario dissemination areas:

```text
Exact same-ID match: 19,717
No exact same-ID match: 751
```

This means about 3.67% of the 2021 Ontario DAs do not have an exact same-ID match in the 2016 correspondence data.

A more important finding is:

```text
59 DAs have the same 2016 and 2021 ID
but are still part of a many-to-many relationship.
```

This shows why matching geography IDs alone does not guarantee that the underlying census geography stayed unchanged.

## Data Validation

Current staging validation results:

```text
Missing required values: 0
Non-Ontario rows: 0
Invalid relationship flags: 0
Duplicate mappings: 0
Invalid DA ID formats: 0
Incorrect DGUID years: 0
```

Current mapping validation results:

```text
Staging rows: 20,690
Mapping result rows: 20,690
Invalid relationship types: 0
Unexpected one-to-one ID changes: 0
Duplicate mapping results: 0
Same-ID many-to-many mappings: 59
```

All 20,690 staging mappings are represented in the final mapping-results table.

## Automated Testing

The project currently has 5 automated pytest tests using a separate PostgreSQL test database.

```text
5 tests passed
```

The tests verify:

- all 499,052 source rows are loaded
- Ontario staging counts match the measured dataset
- staging data passes core quality checks
- geography relationship classifications match the source data
- the key same-ID comparison results are reproducible

## Notes

These numbers describe the Statistics Canada correspondence dataset and the current Ontario-focused project scope.

They should not be described as model accuracy, prediction accuracy, or production-scale performance metrics.