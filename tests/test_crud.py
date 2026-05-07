import tempfile
from pathlib import Path

import pytest

from app import crud
from json_lib import JsonFile


def make_file(tmp: Path, records: list) -> str:
    path = str(tmp / "test.json")
    JsonFile(path).write(records)
    return path


# ─────────────────────────────────────────────
# _next_id
# ─────────────────────────────────────────────
class TestNextId:
    def test_next_id_empty_list(self):
        assert crud._next_id([]) == 1

    def test_next_id_with_records(self):
        records = [{"id": 1}, {"id": 3}, {"id": 2}]
        assert crud._next_id(records) == 4


# ─────────────────────────────────────────────
# create_record
# ─────────────────────────────────────────────
class TestCreateRecord:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_create_first_record(self):
        path = make_file(self.tmp, [])
        record = crud.create_record(path, {"name": "홍길동"})
        assert record["id"] == 1

    def test_create_auto_increment_id(self):
        path = make_file(self.tmp, [{"id": 1, "name": "홍길동"}])
        record = crud.create_record(path, {"name": "김철수"})
        assert record["id"] == 2

    def test_create_returns_record_with_id(self):
        path = make_file(self.tmp, [])
        record = crud.create_record(path, {"name": "홍길동"})
        assert "id" in record

    def test_create_preserves_all_fields(self):
        path = make_file(self.tmp, [])
        fields = {"name": "홍길동", "age": 30, "city": "서울"}
        record = crud.create_record(path, fields)
        for k, v in fields.items():
            assert record[k] == v


# ─────────────────────────────────────────────
# read_all
# ─────────────────────────────────────────────
class TestReadAll:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_read_all_empty(self):
        path = make_file(self.tmp, [])
        assert crud.read_all(path) == []

    def test_read_all_returns_all_records(self):
        records = [{"id": 1, "name": "홍길동"}, {"id": 2, "name": "김철수"}]
        path = make_file(self.tmp, records)
        assert crud.read_all(path) == records

    def test_read_all_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            crud.read_all(str(self.tmp / "missing.json"))


# ─────────────────────────────────────────────
# read_by_id
# ─────────────────────────────────────────────
class TestReadById:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = make_file(self.tmp, [
            {"id": 1, "name": "홍길동"},
            {"id": 2, "name": "김철수"},
        ])

    def test_read_by_id_found(self):
        record = crud.read_by_id(self.path, 1)
        assert record["name"] == "홍길동"

    def test_read_by_id_not_found(self):
        with pytest.raises(KeyError):
            crud.read_by_id(self.path, 99)


# ─────────────────────────────────────────────
# read_by_field
# ─────────────────────────────────────────────
class TestReadByField:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = make_file(self.tmp, [
            {"id": 1, "name": "홍길동", "city": "서울"},
            {"id": 2, "name": "김철수", "city": "부산"},
            {"id": 3, "name": "이영희", "city": "서울"},
        ])

    def test_read_by_field_single_match(self):
        results = crud.read_by_field(self.path, "city", "부산")
        assert len(results) == 1
        assert results[0]["id"] == 2

    def test_read_by_field_multiple_match(self):
        results = crud.read_by_field(self.path, "city", "서울")
        assert len(results) == 2

    def test_read_by_field_no_match(self):
        results = crud.read_by_field(self.path, "city", "대전")
        assert results == []


# ─────────────────────────────────────────────
# update_record
# ─────────────────────────────────────────────
class TestUpdateRecord:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = make_file(self.tmp, [
            {"id": 1, "name": "홍길동", "age": 30},
        ])

    def test_update_existing_field(self):
        updated = crud.update_record(self.path, 1, "age", 31)
        assert updated["age"] == 31

    def test_update_adds_new_field(self):
        updated = crud.update_record(self.path, 1, "city", "서울")
        assert updated["city"] == "서울"

    def test_update_not_found_raises(self):
        with pytest.raises(KeyError):
            crud.update_record(self.path, 99, "age", 31)

    def test_update_does_not_change_id(self):
        updated = crud.update_record(self.path, 1, "name", "김철수")
        assert updated["id"] == 1


# ─────────────────────────────────────────────
# delete_record
# ─────────────────────────────────────────────
class TestDeleteRecord:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = make_file(self.tmp, [
            {"id": 1, "name": "홍길동"},
            {"id": 2, "name": "김철수"},
        ])

    def test_delete_removes_record(self):
        crud.delete_record(self.path, 1)
        remaining = crud.read_all(self.path)
        assert all(r["id"] != 1 for r in remaining)

    def test_delete_returns_deleted_record(self):
        deleted = crud.delete_record(self.path, 1)
        assert deleted["id"] == 1
        assert deleted["name"] == "홍길동"

    def test_delete_not_found_raises(self):
        with pytest.raises(KeyError):
            crud.delete_record(self.path, 99)

    def test_delete_does_not_renumber_ids(self):
        crud.delete_record(self.path, 1)
        remaining = crud.read_all(self.path)
        assert remaining[0]["id"] == 2
