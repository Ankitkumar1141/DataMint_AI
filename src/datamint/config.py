from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_secret(section: str, key: str, default=None):
    try:
        return st.secrets.get(section, {}).get(key, default)
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "DataMint AI"

    # MySQL settings
    mysql_host: str = os.getenv("MYSQL_HOST") or _get_secret("mysql", "HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT") or _get_secret("mysql", "PORT", 3306))
    mysql_user: str = os.getenv("MYSQL_USER") or _get_secret("mysql", "USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD") or _get_secret("mysql", "PASSWORD", "root123")
    mysql_database: str = os.getenv("MYSQL_DATABASE") or _get_secret("mysql", "DATABASE", "Datamint_AI")

    # Mistral settings
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY") or _get_secret("keys", "MISTRAL_API_KEY", "")
    mistral_model: str = os.getenv("MISTRAL_MODEL") or _get_secret(
        "keys",
        "MISTRAL_MODEL",
        "mistral-small-latest",
    )

    # Backward-compatible aliases for old code
    @property
    def MYSQL_HOST(self) -> str:
        return self.mysql_host

    @property
    def MYSQL_PORT(self) -> int:
        return self.mysql_port

    @property
    def MYSQL_USER(self) -> str:
        return self.mysql_user

    @property
    def MYSQL_PASSWORD(self) -> str:
        return self.mysql_password

    @property
    def MYSQL_DATABASE(self) -> str:
        return self.mysql_database

    @property
    def MISTRAL_API_KEY(self) -> str:
        return self.mistral_api_key

    @property
    def MISTRAL_MODEL(self) -> str:
        return self.mistral_model


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()