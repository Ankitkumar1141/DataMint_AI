from __future__ import annotations

import bcrypt

from datamint.db.connection import get_connection


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hash_password(password)),
            )
            return True, "Registered successfully. Please log in."
        except Exception:
            return False, "Username already exists or registration failed."
        finally:
            cursor.close()


def authenticate_user(username: str, password: str) -> dict | None:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username=%s", (username.strip(),))
        user = cursor.fetchone()
        cursor.close()

    if user and verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return None
