from __future__ import annotations

from datamint.db.connection import get_connection


SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS generated_datasets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        task VARCHAR(100) NOT NULL,
        domain VARCHAR(100) NOT NULL,
        rows_requested INT NOT NULL,
        features_requested INT NOT NULL,
        description TEXT,
        columns_json JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
]


def setup_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        for statement in SCHEMA_SQL:
            cursor.execute(statement)
        cursor.close()
