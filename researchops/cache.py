import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class SQLiteCache:

    def __init__(
        self,
        db_path: str = "data/cache.sqlite3",
        default_ttl: int = 86400
    ):
        self.db_path = Path(db_path)
        self.default_ttl = default_ttl

        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):

        with self._connect() as db:

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL
                )
                """
            )

            db.commit()

    @staticmethod
    def create_key(
        namespace: str,
        payload: Any
    ) -> str:

        serialized = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            default=str
        )

        raw_key = f"{namespace}:{serialized}"

        return hashlib.sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

    def get(self, key: str):

        with self._connect() as db:

            row = db.execute(
                """
                SELECT value, expires_at
                FROM cache
                WHERE key = ?
                """,
                (key,)
            ).fetchone()

        if row is None:
            return None

        value, expires_at = row

        # Check expiration
        if (
            expires_at is not None
            and expires_at < time.time()
        ):
            self.delete(key)
            return None

        return json.loads(value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ):

        if ttl is None:
            ttl = self.default_ttl

        if ttl <= 0:
            expires_at = None
        else:
            expires_at = time.time() + ttl

        serialized = json.dumps(
            value,
            ensure_ascii=False,
            default=str
        )

        with self._connect() as db:

            db.execute(
                """
                INSERT OR REPLACE INTO cache
                (
                    key,
                    value,
                    created_at,
                    expires_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    key,
                    serialized,
                    time.time(),
                    expires_at
                )
            )

            db.commit()

    def delete(self, key: str):

        with self._connect() as db:

            db.execute(
                """
                DELETE FROM cache
                WHERE key = ?
                """,
                (key,)
            )

            db.commit()