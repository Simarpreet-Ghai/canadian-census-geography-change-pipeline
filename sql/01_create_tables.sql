CREATE TABLE raw_da_correspondence (
    raw_row_id BIGSERIAL PRIMARY KEY,
    dauid_2021 TEXT NOT NULL,
    dauid_2016 TEXT NOT NULL,
    dbuid_2021 TEXT NOT NULL,
    relationship_flag SMALLINT NOT NULL,
    dadguid_2021 TEXT NOT NULL,
    dadguid_2016 TEXT NOT NULL,
    dbdguid_2021 TEXT NOT NULL
);

CREATE TABLE staging_da_mappings (
    mapping_id BIGSERIAL PRIMARY KEY,
    dauid_2021 TEXT NOT NULL,
    dauid_2016 TEXT NOT NULL,
    relationship_flag SMALLINT NOT NULL,
    dadguid_2021 TEXT NOT NULL,
    dadguid_2016 TEXT NOT NULL
);

