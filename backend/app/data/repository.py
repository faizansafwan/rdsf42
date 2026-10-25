"""SQLite data access — only layer that touches the database."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.data.models import SCHEMA_SQL

META_LAST_UPDATED = "last_updated"
META_STALE = "stale"


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class WindRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._memory_conn: sqlite3.Connection | None = None
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        if self.database_path == ":memory:":
            if self._memory_conn is None:
                self._memory_conn = sqlite3.connect(
                    ":memory:",
                    detect_types=sqlite3.PARSE_DECLTYPES,
                    check_same_thread=False,
                )
                self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn
        conn = sqlite3.connect(self.database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        conn = self.connect()
        conn.executescript(SCHEMA_SQL)
        conn.commit()

    def upsert_actuals(self, rows: list[dict]) -> int:
        if not rows:
            return 0
        conn = self.connect()
        conn.executemany(
                """
                INSERT INTO actuals (start_time, generation_mw)
                VALUES (?, ?)
                ON CONFLICT(start_time) DO UPDATE SET generation_mw = excluded.generation_mw
                """,
                [( _iso(r["start_time"]), r["generation_mw"]) for r in rows],
            )
        conn.commit()
        return len(rows)

    def upsert_forecasts(self, rows: list[dict]) -> int:
        if not rows:
            return 0
        conn = self.connect()
        conn.executemany(
                """
                INSERT INTO forecasts (start_time, publish_time, generation_mw)
                VALUES (?, ?, ?)
                ON CONFLICT(start_time, publish_time) DO UPDATE SET
                    generation_mw = excluded.generation_mw
                """,
                [
                    (_iso(r["start_time"]), _iso(r["publish_time"]), r["generation_mw"])
                    for r in rows
                ],
            )
        conn.commit()
        return len(rows)

    def get_actuals(self, start: datetime, end: datetime) -> list[dict]:
        conn = self.connect()
        cur = conn.execute(
                """
                SELECT start_time, generation_mw FROM actuals
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
                """,
                (_iso(start), _iso(end)),
            )
        return [
            {"start_time": _parse_iso(r["start_time"]), "generation_mw": r["generation_mw"]}
            for r in cur.fetchall()
        ]

    def get_forecasts(self, start: datetime, end: datetime) -> list[dict]:
        conn = self.connect()
        cur = conn.execute(
                """
                SELECT start_time, publish_time, generation_mw FROM forecasts
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time, publish_time
                """,
                (_iso(start), _iso(end)),
            )
        return [
            {
                "start_time": _parse_iso(r["start_time"]),
                "publish_time": _parse_iso(r["publish_time"]),
                "generation_mw": r["generation_mw"],
            }
            for r in cur.fetchall()
        ]

    def set_meta(self, key: str, value: str) -> None:
        conn = self.connect()
        conn.execute(
                """
                INSERT INTO cache_meta (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
        conn.commit()

    def get_meta(self, key: str) -> str | None:
        conn = self.connect()
        row = conn.execute(
            "SELECT value FROM cache_meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def cache_status(self) -> tuple[bool, str | None]:
        stale_raw = self.get_meta(META_STALE)
        stale = stale_raw == "true"
        return stale, self.get_meta(META_LAST_UPDATED)
