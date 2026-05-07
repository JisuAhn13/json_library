# JSON CRUD 콘솔 애플리케이션 개발 계획

## 목표

`json_lib` 라이브러리를 활용해 JSON 파일을 대화형으로 생성·조회·수정·삭제하는 콘솔 앱 개발.

---

## 1단계 — 요구사항 정의

CRUD 각 기능이 무엇을 의미하는지 명확히 한다.

| 기능 | 동작 |
|---|---|
| **Create** | 새 JSON 파일 생성 / 파일에 새 키-값 추가 |
| **Read** | JSON 파일 전체 출력 / 특정 키 조회 |
| **Update** | 기존 키의 값 수정 |
| **Delete** | 특정 키 삭제 / 파일 전체 삭제 |

---

## 2단계 — 화면 흐름 설계

```
실행
 └─ 파일명 입력 (없으면 새로 생성)
     └─ 메인 메뉴
         ├─ 1. Create  → 키-값 입력 → 저장
         ├─ 2. Read    → 전체 출력 or 키 지정 조회
         ├─ 3. Update  → 키 선택 → 새 값 입력 → 저장
         ├─ 4. Delete  → 키 삭제 or 파일 삭제 선택
         └─ 5. 종료
```

---

## 3단계 — 파일 구조 설계

```
C:/reviewer/Json/
├── app/
│   ├── __init__.py
│   ├── menu.py       # 메뉴 출력 및 입력 처리
│   ├── crud.py       # CRUD 비즈니스 로직
│   └── display.py    # 데이터 출력 포맷
├── run.py            # 진입점 (python run.py 로 실행)
└── tests/
    └── test_crud.py  # CRUD 단위 테스트 추가
```

---

## 4단계 — 구현 순서

### 4-1. `app/crud.py` 먼저 구현
- `create_file(path)` — 새 파일 생성
- `add_key(path, key, value)` — 키-값 추가
- `read_all(path)` — 전체 데이터 반환
- `read_key(path, key)` — 특정 키 값 반환
- `update_key(path, key, value)` — 키 값 수정
- `delete_key(path, key)` — 특정 키 삭제
- `delete_file(path)` — 파일 삭제

### 4-2. `app/display.py` 구현
- JSON 데이터를 보기 좋게 출력하는 함수 모음

### 4-3. `app/menu.py` 구현
- 메인 메뉴 루프
- 각 CRUD 기능으로 분기

### 4-4. `run.py` 구현
- 파일명 입력받아 `menu.py` 실행

---

## 5단계 — 테스트

- `tests/test_crud.py` 에 CRUD 함수별 단위 테스트 작성
- 기존 `json_lib` 테스트(45개)는 그대로 유지

---

## 실행 방법 (완성 후)

```powershell
cd C:\reviewer\Json
python -X utf8 run.py
```

---

## 개발 우선순위

```
crud.py → display.py → menu.py → run.py → test_crud.py
```
비즈니스 로직(crud.py)을 먼저 완성하고 UI(menu.py)를 붙이는 순서로 진행.
