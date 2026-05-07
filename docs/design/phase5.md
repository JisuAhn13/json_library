# Phase 5 — 테스트 계획

## 목표

`app/crud.py`의 모든 함수를 단위 테스트로 검증하고, 기존 `json_lib` 테스트(45개)와 함께 전체 회귀 테스트를 통과시킨다.

---

## 테스트 파일 위치

```
tests/
├── test_json_lib.py   # 기존 45개 — 수정 없음
└── test_crud.py       # 신규 작성
```

---

## `tests/test_crud.py` 테스트 목록

### TestCreateRecord

| 테스트명 | 검증 내용 |
|---|---|
| `test_create_first_record` | 빈 파일에 첫 레코드 저장 시 id=1 부여 확인 |
| `test_create_auto_increment_id` | 두 번째 레코드 id가 2인지 확인 |
| `test_create_returns_record_with_id` | 반환값에 id 필드가 포함되는지 확인 |
| `test_create_preserves_all_fields` | 입력한 모든 필드가 저장되는지 확인 |

### TestReadAll

| 테스트명 | 검증 내용 |
|---|---|
| `test_read_all_empty` | 빈 파일에서 빈 리스트 반환 |
| `test_read_all_returns_all_records` | 저장된 레코드 전체 반환 확인 |
| `test_read_all_missing_file_raises` | 파일 없을 때 `FileNotFoundError` 발생 |

### TestReadById

| 테스트명 | 검증 내용 |
|---|---|
| `test_read_by_id_found` | 존재하는 id로 정확한 레코드 반환 |
| `test_read_by_id_not_found` | 없는 id 조회 시 `KeyError` 발생 |

### TestReadByField

| 테스트명 | 검증 내용 |
|---|---|
| `test_read_by_field_single_match` | 일치하는 레코드 1건 반환 |
| `test_read_by_field_multiple_match` | 일치하는 레코드 여러 건 반환 |
| `test_read_by_field_no_match` | 일치 없으면 빈 리스트 반환 |

### TestUpdateRecord

| 테스트명 | 검증 내용 |
|---|---|
| `test_update_existing_field` | 필드 값이 새 값으로 교체되는지 확인 |
| `test_update_adds_new_field` | 없던 필드를 새로 추가할 수 있는지 확인 |
| `test_update_not_found_raises` | 없는 id 수정 시 `KeyError` 발생 |
| `test_update_does_not_change_id` | id 필드 이외 필드만 수정되는지 확인 |

### TestDeleteRecord

| 테스트명 | 검증 내용 |
|---|---|
| `test_delete_removes_record` | 삭제 후 해당 레코드가 목록에 없는지 확인 |
| `test_delete_returns_deleted_record` | 삭제된 레코드가 반환되는지 확인 |
| `test_delete_not_found_raises` | 없는 id 삭제 시 `KeyError` 발생 |
| `test_delete_does_not_renumber_ids` | 삭제 후 남은 레코드 id가 변경되지 않는지 확인 |

### TestNextId (내부 함수)

| 테스트명 | 검증 내용 |
|---|---|
| `test_next_id_empty_list` | 빈 목록에서 1 반환 |
| `test_next_id_with_records` | 최대 id + 1 반환 |

---

## 테스트 실행 방법

```powershell
# 신규 CRUD 테스트만
python -X utf8 -m pytest tests/test_crud.py -v

# 전체 테스트 (기존 45개 + 신규)
python -X utf8 -m pytest tests/ -v
```

---

## 완료 기준

| 항목 | 기준 |
|---|---|
| 신규 테스트 | 전체 통과 |
| 기존 테스트 | 기존 45개 모두 통과 유지 |
| 커버리지 목표 | `app/crud.py` 함수 100% |
