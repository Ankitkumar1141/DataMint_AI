from __future__ import annotations

import io
import json
from typing import Any

import pandas as pd

try:
    from mistralai import Mistral
except ImportError:  # Compatibility with older Mistral SDK layouts
    from mistralai.client import Mistral
from pydantic import BaseModel, Field, ValidationError, field_validator

from datamint.config import get_settings
from datamint.db.connection import get_connection


class DatasetPayload(BaseModel):
    columns: list[str] = Field(min_length=1)
    data: list[list[Any]] = Field(min_length=1)

    @field_validator("columns")
    @classmethod
    def unique_columns(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("Column names must be unique.")
        return value

    @field_validator("data")
    @classmethod
    def non_empty_rows(cls, value: list[list[Any]]) -> list[list[Any]]:
        if not value:
            raise ValueError("Dataset must include at least one row.")
        return value

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.data, columns=self.columns)


def _dataset_prompt(features: int, rows: int, task: str, domain: str, description: str) -> str:
    return f"""
Generate a realistic synthetic tabular dataset.

Requirements:
- Domain: {domain}
- Machine learning task: {task}
- Number of columns/features: exactly {features}
- Number of rows: exactly {rows}
- User description: {description or "No extra description provided."}
- Include realistic column names and plausible values.
- Avoid personally identifiable information such as real names, emails, phone numbers, addresses, national IDs, or account numbers.
- Make the target/label column clear when the selected machine learning task needs one.
- Return only valid JSON. Do not include Markdown, comments, or explanation.

Required JSON shape:
{{
  "columns": ["col1", "col2"],
  "data": [
    ["value", 1],
    ["value", 2]
  ]
}}
""".strip()


def _validate_dimensions(payload: DatasetPayload, features: int, rows: int) -> pd.DataFrame:
    frame = payload.to_frame()
    if frame.shape[1] != features:
        raise ValueError(f"Expected {features} features but received {frame.shape[1]} columns.")
    if len(frame) != rows:
        raise ValueError(f"Expected {rows} rows but received {len(frame)} rows.")
    return frame


def generate_dataset(features: int, rows: int, task: str, domain: str, description: str) -> pd.DataFrame:
    settings = get_settings()
    if not settings.mistral_api_key:
        raise RuntimeError("MISTRAL_API_KEY is missing. Add it to .env or .streamlit/secrets.toml.")

    client = Mistral(api_key=settings.mistral_api_key)
    response = client.chat.complete(
        model=settings.mistral_model,
        messages=[
            {
                "role": "system",
                "content": "You generate safe synthetic datasets and always return strict JSON only.",
            },
            {
                "role": "user",
                "content": _dataset_prompt(features, rows, task, domain, description),
            },
        ],
        temperature=0.6,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"

    try:
        payload = DatasetPayload.model_validate_json(raw)
        return _validate_dimensions(payload, features, rows)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ValueError("Mistral returned invalid dataset JSON. Please try again with a clearer description.") from exc


def save_dataset_metadata(user_id: int, task: str, domain: str, rows: int, features: int, description: str, columns: list[str]) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO generated_datasets
            (user_id, task, domain, rows_requested, features_requested, description, columns_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, task, domain, rows, features, description, json.dumps(columns)),
        )
        cursor.close()


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="dataset")
    return buffer.getvalue()
