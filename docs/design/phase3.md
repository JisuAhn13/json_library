# Phase 3 — 파일 구조 설계

## 목표

코드를 역할별로 분리해 각 파일의 책임을 단일하게 유지한다.

---

## 디렉토리 구조

```
C:/reviewer/Json/
├── app/
│   ├── __init__.py
│   ├── crud.py       # CRUD 비즈니스 로직 (레코드 단위)
│   ├── display.py    # 출력 포맷 담당
│   └── menu.py       # 메뉴 루프 및 사용자 입력 처리
├── run.py            # 진입점
├── docs/
│   └── design/
│       ├── phase1.md ~ phase5.md
├── json_lib/         # 기존 라이브러리 (수정 없음)
├── tests/
│   ├── test_json_lib.py   # 기존 45개 테스트 (수정 없음)
│   └── test_crud.py       # 신규 CRUD 테스트
├── plan.md
├── CLAUDE.md
└── pyproject.toml
```

---

## 각 파일의 역할

### `run.py` — 진입점

- 파일명 입력받기
- 파일이 없으면 빈 배열(`[]`)로 새로 생성
- `menu.py`의 메인 루프 호출
- `KeyboardInterrupt` 처리

```python
from app.menu import run_menu
```

---

### `app/crud.py` — 비즈니스 로직

`json_lib`를 직접 사용하는 유일한 레이어. 순수 함수로 구성.

```python
from json_lib import JsonFile
```

| 함수 | 시그니처 | 반환 |
|---|---|---|
| `create_record` | `(path, fields: dict) → dict` | 저장된 레코드 (id 포함) |
| `read_all` | `(path) → list[dict]` | 전체 레코드 목록 |
| `read_by_id` | `(path, id: int) → dict` | 해당 레코드 |
| `read_by_field` | `(path, key: str, value) → list[dict]` | 일치하는 레코드 목록 |
| `update_record` | `(path, id: int, key: str, value) → dict` | 수정된 레코드 |
| `delete_record` | `(path, id: int) → dict` | 삭제된 레코드 |
| `_next_id` | `(records: list) → int` | 다음 id 값 (내부 함수) |

---

### `app/display.py` — 출력 포맷

화면 출력 함수를 모두 여기에 모은다. `crud.py`는 출력하지 않는다.

| 함수 | 역할 |
|---|---|
| `print_menu(filename, count)` | 메인 메뉴 출력 (파일명, 레코드 수 포함) |
| `print_record(record)` | 레코드 한 건 출력 |
| `print_records(records)` | 레코드 목록 출력 (번호 포함) |
| `print_success(msg)` | 성공 메시지 출력 |
| `print_error(msg)` | 오류 메시지 출력 |
| `print_separator()` | 구분선 출력 |

---

### `app/menu.py` — 메뉴 루프

사용자 입력 → `crud.py` 호출 → `display.py`로 출력.

```python
from app import crud, display
```

| 함수 | 역할 |
|---|---|
| `run_menu(filepath)` | 메인 루프 (1~5 선택 반복) |
| `handle_create(filepath)` | 필드 반복 입력 → create_record 호출 |
| `handle_read(filepath)` | 전체/ID/키 검색 선택 |
| `handle_update(filepath)` | ID 선택 → 필드 수정 |
| `handle_delete(filepath)` | ID 선택 → 확인 후 삭제 |
| `parse_value(text)` | 입력 문자열 → Python 타입 변환 |
| `confirm(prompt)` | y/n 입력받아 bool 반환 |

---

## 레이어 의존 방향

```
run.py
  └─ menu.py
       ├─ crud.py
       │    └─ json_lib (JsonFile)
       └─ display.py
```

- `crud.py`는 `display.py`를 호출하지 않는다.
- `json_lib`는 수정하지 않는다.
