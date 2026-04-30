from __future__ import annotations

import io
import json
import random
from datetime import datetime, timedelta

import pandas as pd

try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import Mistral

from datamint.config import get_settings
from datamint.db.connection import get_connection


def _extract_json(content: str) -> dict:
    content = content.strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()

    if content.startswith("```"):
        content = content.removeprefix("```").strip()

    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    return json.loads(content)


def generate_schema(features: int, task: str, domain: str, description: str) -> dict:
    settings = get_settings()

    if not settings.mistral_api_key:
        raise ValueError("MISTRAL_API_KEY is missing. Add it to .env or .streamlit/secrets.toml.")

    prompt = f"""
You are creating a synthetic dataset schema.

Create exactly {features} columns for a {domain} dataset used for {task}.

Dataset description:
{description}

Return ONLY valid JSON. No markdown. No explanation.

Use this exact JSON format:
{{
  "columns": [
    {{
      "name": "column_name",
      "type": "integer | float | category | date | text | boolean",
      "min": 0,
      "max": 100,
      "categories": ["A", "B", "C"],
      "description": "short meaning of this column"
    }}
  ]
}}

Rules:
- Return exactly {features} columns.
- Do not include an index, id, row_id, or serial number column.
- For integer and float columns, include min and max.
- For category columns, include categories.
- For boolean columns, no min, max, or categories are needed.
- For date columns, no min, max, or categories are needed.
- For text columns, include a short description.
- Make columns realistic for the selected domain and task.
"""

    client = Mistral(api_key=settings.mistral_api_key)

    response = client.chat.complete(
        model=settings.mistral_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    schema = _extract_json(raw)

    if "columns" not in schema:
        raise ValueError("Mistral did not return a valid schema.")

    columns = schema["columns"]

    if len(columns) != features:
        raise ValueError(f"Expected {features} columns but received {len(columns)} columns.")

    return schema


def _generate_value(column: dict, row_index: int):
    column_type = str(column.get("type", "category")).lower().strip()

    if column_type == "integer":
        min_value = int(column.get("min", 0))
        max_value = int(column.get("max", 100))
        return random.randint(min_value, max_value)

    if column_type == "float":
        min_value = float(column.get("min", 0))
        max_value = float(column.get("max", 100))
        return round(random.uniform(min_value, max_value), 2)

    if column_type == "category":
        categories = column.get("categories") or ["A", "B", "C"]
        return random.choice(categories)

    if column_type == "boolean":
        return random.choice([True, False])

    if column_type == "date":
        start_date = datetime.today() - timedelta(days=365 * 3)
        random_days = random.randint(0, 365 * 3)
        return (start_date + timedelta(days=random_days)).date().isoformat()

    if column_type == "text":
        name = column.get("name", "text")
        return f"{name}_sample_{row_index + 1}"

    return random.choice(["A", "B", "C"])


def generate_rows_from_schema(schema: dict, rows: int) -> pd.DataFrame:
    columns = schema["columns"]
    column_names = [column["name"] for column in columns]

    data = []

    for row_index in range(rows):
        row = [_generate_value(column, row_index) for column in columns]
        data.append(row)

    return pd.DataFrame(data, columns=column_names)


def validate_dataframe(
    df: pd.DataFrame,
    expected_features: int,
    expected_rows: int,
) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Generated dataset is empty.")

    if len(df.columns) != expected_features:
        raise ValueError(
            f"Expected {expected_features} columns but received {len(df.columns)} columns."
        )

    if len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows but received {len(df)} rows."
        )

    return df


def generate_dataset(
    features: int,
    rows: int,
    task: str,
    domain: str,
    description: str,
) -> pd.DataFrame:
    schema = generate_schema(
        features=features,
        task=task,
        domain=domain,
        description=description,
    )

    df = generate_rows_from_schema(schema=schema, rows=rows)

    return validate_dataframe(
        df=df,
        expected_features=features,
        expected_rows=rows,
    )


def save_dataset_metadata(
    user_id: int,
    task: str,
    domain: str,
    rows: int,
    features: int,
    description: str,
    columns: list[str],
) -> None:
    columns_json = json.dumps(columns)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO generated_datasets
            (
                user_id,
                task,
                domain,
                rows_requested,
                features_requested,
                description,
                columns_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                task,
                domain,
                rows,
                features,
                description,
                columns_json,
            ),
        )
        cursor.close()


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dataset")

    return output.getvalue()