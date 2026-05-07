# Phase 4 — 구현 순서

## 목표

의존성 순서에 따라 하위 레이어부터 구현해 각 단계를 독립적으로 검증한다.

---

## 구현 순서

```
Step 1. app/crud.py
Step 2. app/display.py
Step 3. app/menu.py
Step 4. run.py
```

---

## Step 1. `app/crud.py`

### 전체 구조

```python
from __future__ import annotations
from typing import Any
from json_lib import JsonFile


def _next_id(records: list[dict]) -> int:
    """현재 레코드 중 최대 id + 1 반환. 비어 있으면 1."""
    return max((r["id"] for r in records), default=0) + 1


def _load(path: str) -> list[dict]:
    return JsonFile(path).read()


def _save(path: str, records: list[dict]) -> None:
    JsonFile(path).write(records)


def create_record(path: str, fields: dict) -> dict:
    """fields에 id를 자동 부여해 저장 후 반환."""
    records = _load(path)
    record = {"id": _next_id(records), **fields}
    records.append(record)
    _save(path, records)
    return record


def read_all(path: str) -> list[dict]:
    return _load(path)


def read_by_id(path: str, record_id: int) -> dict:
    """id 일치 레코드 반환. 없으면 KeyError."""
    for r in _load(path):
        if r["id"] == record_id:
            return r
    raise KeyError(record_id)


def read_by_field(path: str, key: str, value: Any) -> list[dict]:
    """key==value 인 레코드 목록 반환."""
    return [r for r in _load(path) if r.get(key) == value]


def update_record(path: str, record_id: int, key: str, value: Any) -> dict:
    """id 레코드의 key 필드를 value로 수정 후 반환. 없으면 KeyError."""
    records = _load(path)
    for r in records:
        if r["id"] == record_id:
            r[key] = value
            _save(path, records)
            return r
    raise KeyError(record_id)


def delete_record(path: str, record_id: int) -> dict:
    """id 레코드를 삭제하고 삭제된 레코드 반환. 없으면 KeyError."""
    records = _load(path)
    for i, r in enumerate(records):
        if r["id"] == record_id:
            deleted = records.pop(i)
            _save(path, records)
            return deleted
    raise KeyError(record_id)
```

---

## Step 2. `app/display.py`

```python
import json
from typing import Any

SEPARATOR = "-" * 42

def print_separator() -> None:
    print(SEPARATOR)

def print_menu(filename: str, count: int) -> None:
    print(f"\n[파일: {filename} / {count}건]")
    print("1. Create\n2. Read\n3. Update\n4. Delete\n5. 종료")

def print_record(record: dict) -> None:
    print(json.dumps(record, ensure_ascii=False, indent=2))

def print_records(records: list[dict]) -> None:
    print_separator()
    print(f"총 {len(records)}건")
    for i, r in enumerate(records, 1):
        print(f"[{i}] {json.dumps(r, ensure_ascii=False)}")
    print_separator()

def print_success(msg: str) -> None:
    print(f"성공: {msg}")

def print_error(msg: str) -> None:
    print(f"오류: {msg}")
```

---

## Step 3. `app/menu.py`

### `parse_value` 타입 추론

```python
def parse_value(text: str) -> Any:
    if text == "null":   return None
    if text == "true":   return True
    if text == "false":  return False
    try: return int(text)
    except ValueError: pass
    try: return float(text)
    except ValueError: pass
    try:
        v = json.loads(text)
        if isinstance(v, (list, dict)):
            return v
    except Exception:
        pass
    return text
```

### `handle_create` 흐름

```
빈 줄 입력까지 필드명-값 반복 수집
→ fields 딕셔너리 구성
→ crud.create_record 호출
→ display.print_record 출력
```

### `handle_read` 흐름

```
1/2/3 선택
  1 → crud.read_all → display.print_records
  2 → ID 입력 → crud.read_by_id → display.print_record
  3 → 필드명, 값 입력 → crud.read_by_field → display.print_records
```

### `handle_update` 흐름

```
ID 입력 → crud.read_by_id (존재 확인)
→ 현재 레코드 출력
→ 필드명 입력 (id 입력 시 오류)
→ 현재 값 출력
→ 새 값 입력
→ crud.update_record
→ 수정된 레코드 출력
```

### `handle_delete` 흐름

```
ID 입력 → crud.read_by_id (존재 확인)
→ 삭제 대상 레코드 출력
→ confirm("정말 삭제하시겠습니까? (y/n)")
  y → crud.delete_record → 성공 메시지
  n → "삭제가 취소되었습니다."
```

---

## Step 4. `run.py`

```python
import json
from pathlib import Path
from app.menu import run_menu
from json_lib import JsonFile

def main():
    print("=== JSON CRUD 콘솔 앱 ===")
    filename = input("파일명 입력 (예: data.json) > ").strip()
    if not filename:
        print("파일명을 입력해야 합니다.")
        return

    jf = JsonFile(filename)
    if not jf.exists():
        jf.write([])
        print(f"새 파일 생성: {filename}")

    run_menu(filename)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n앱을 종료합니다.")
```

---

## 공통 주의사항

- 빈 입력은 재입력 요청으로 처리한다.
- `id` 필드 수정 시도는 오류 메시지 출력 후 필드명 재입력.
- `y/n` 확인은 `y`, `Y` 모두 긍정으로 처리한다.
- 모든 예외는 `menu.py`에서 catch해 `display.print_error`로 출력한다.
