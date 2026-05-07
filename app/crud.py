from __future__ import annotations

from typing import Any

from json_lib import JsonFile


def _next_id(records: list[dict]) -> int:
    return max((r["id"] for r in records), default=0) + 1


def _load(path: str) -> list[dict]:
    return JsonFile(path).read()


def _save(path: str, records: list[dict]) -> None:
    JsonFile(path).write(records)


def create_record(path: str, fields: dict) -> dict:
    records = _load(path)
    record = {"id": _next_id(records), **fields}
    records.append(record)
    _save(path, records)
    return record


def read_all(path: str) -> list[dict]:
    return _load(path)


def read_by_id(path: str, record_id: int) -> dict:
    for r in _load(path):
        if r["id"] == record_id:
            return r
    raise KeyError(record_id)


def read_by_field(path: str, key: str, value: Any) -> list[dict]:
    return [r for r in _load(path) if r.get(key) == value]


def update_record(path: str, record_id: int, key: str, value: Any) -> dict:
    records = _load(path)
    for r in records:
        if r["id"] == record_id:
            r[key] = value
            _save(path, records)
            return r
    raise KeyError(record_id)


def delete_record(path: str, record_id: int) -> dict:
    records = _load(path)
    for i, r in enumerate(records):
        if r["id"] == record_id:
            deleted = records.pop(i)
            _save(path, records)
            return deleted
    raise KeyError(record_id)
