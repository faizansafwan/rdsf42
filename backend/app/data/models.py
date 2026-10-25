SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS actuals (
    start_time TEXT PRIMARY KEY,
    generation_mw REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS forecasts (
    start_time TEXT NOT NULL,
    publish_time TEXT NOT NULL,
    generation_mw REAL NOT NULL,
    PRIMARY KEY (start_time, publish_time)
);

CREATE TABLE IF NOT EXISTS cache_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""
