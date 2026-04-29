import pytest

from datamint.services.dataset import DatasetPayload


def test_dataset_payload_to_frame():
    payload = DatasetPayload(columns=["age", "income"], data=[[30, 1000], [40, 2000]])
    df = payload.to_frame()
    assert list(df.columns) == ["age", "income"]
    assert len(df) == 2


def test_dataset_payload_rejects_duplicate_columns():
    with pytest.raises(ValueError):
        DatasetPayload(columns=["age", "age"], data=[[30, 31]])
