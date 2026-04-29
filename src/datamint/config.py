from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]


def _secret(path: str, default: str | int | None = None):
    """Read Streamlit secrets first, then environment variables."""
    try:
        current = st.secrets
        for part in path.split("."):
            current = current[part]
        return current
    except Exception:
        env_name = path.upper().replace(".", "_")
        return os.getenv(env_name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "DataMint AI")
    app_env: str = os.getenv("APP_ENV", "development")
    mysql_host: str = str(_secret("mysql.HOST", os.getenv("MYSQL_HOST", "localhost")))
    mysql_port: int = int(_secret("mysql.PORT", os.getenv("MYSQL_PORT", 3306)))
    mysql_database: str = str(_secret("mysql.DATABASE", os.getenv("MYSQL_DATABASE", "DataMint_AI")))
    mysql_user: str = str(_secret("mysql.USER", os.getenv("MYSQL_USER", "root")))
    mysql_password: str = str(_secret("mysql.PASSWORD", os.getenv("MYSQL_PASSWORD", "root123")))
    mistral_api_key: str | None = _secret("MISTRAL_API_KEY", os.getenv("MISTRAL_API_KEY")) or _secret("keys.MISTRAL_API_KEY", None)
    mistral_model: str = str(_secret("MISTRAL_MODEL", os.getenv("MISTRAL_MODEL", "mistral-small-latest")))


def get_settings() -> Settings:
    return Settings()
