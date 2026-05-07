# json_lib 프로젝트

Python용 JSON 유틸리티 라이브러리. 파싱, 직렬화, 파일 I/O, 스키마 검증 기능 제공.

## 환경

- Python 3.13.9
- pytest 8.4.2
- 외부 의존성 없음 (표준 라이브러리만 사용)

## 프로젝트 구조

```
C:/reviewer/Json/
├── json_lib/
│   ├── __init__.py       # 패키지 진입점 — JsonParser, JsonFile, JsonSchema, ValidationError export
│   ├── parser.py         # JsonParser (파싱 / 직렬화)
│   ├── file_handler.py   # JsonFile (파일 읽기/쓰기/병합/삭제)
│   └── schema.py         # JsonSchema, ValidationError, ValidationResult (스키마 검증)
├── tests/
│   └── test_json_lib.py  # 45개 단위 테스트
├── main.py               # 실행 가능한 데모 스크립트
└── pyproject.toml
```

## 실행 방법

```powershell
# 데모 실행 (파싱·파일·검증 결과 출력)
cd C:\reviewer\Json
python -X utf8 main.py

# 전체 테스트 실행
python -X utf8 -m pytest tests/ -v

# 특정 클래스만 테스트
python -X utf8 -m pytest tests/ -v -k "TestJsonParser"
python -X utf8 -m pytest tests/ -v -k "TestJsonFile"
python -X utf8 -m pytest tests/ -v -k "TestJsonSchema"
```

> `-X utf8` : Windows 콘솔 한글 깨짐 방지 필수 옵션

## API 레퍼런스

### JsonParser (`json_lib/parser.py`)

JSON 문자열 ↔ Python 객체 변환.

```python
from json_lib import JsonParser

parser = JsonParser()

# 파싱 (문자열 → 객체)
data = parser.parse('{"name": "홍길동", "age": 30}')

# 직렬화 (객체 → 문자열)
text = parser.serialize(data, indent=2, sort_keys=False, ensure_ascii=False)
```

| 메서드 | 설명 | 예외 |
|---|---|---|
| `parse(text)` | JSON 문자열 → Python 객체 | `ValueError` (파싱 오류) |
| `serialize(data, *, indent, sort_keys, ensure_ascii)` | Python 객체 → JSON 문자열 | `ValueError` (직렬화 불가 타입) |

---

### JsonFile (`json_lib/file_handler.py`)

JSON 파일 읽기/쓰기/병합/삭제.

```python
from json_lib import JsonFile

jf = JsonFile("data.json")

jf.write({"key": "value"})        # 파일 저장 (없으면 생성, 부모 디렉토리 자동 생성)
data = jf.read()                  # 파일 읽기
merged = jf.merge({"extra": 123}) # 기존 내용에 dict 병합 후 저장
jf.delete()                       # 파일 삭제
jf.exists()                       # 파일 존재 여부 확인 (bool)
```

| 메서드 | 설명 | 예외 |
|---|---|---|
| `write(data, *, indent, sort_keys, ensure_ascii)` | 객체를 파일로 저장 | `ValueError` |
| `read()` | 파일을 읽어 객체 반환 | `FileNotFoundError`, `ValueError` |
| `merge(patch)` | 기존 파일에 dict 병합 저장 | `TypeError` (대상이 dict 아닐 때) |
| `delete()` | 파일 삭제 | `FileNotFoundError` |
| `exists()` | 파일 존재 여부 | — |

---

### JsonSchema (`json_lib/schema.py`)

JSON 데이터가 스키마 규칙에 맞는지 검증.

```python
from json_lib import JsonSchema, ValidationError

schema = JsonSchema({
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age":  {"type": "integer", "minimum": 0, "maximum": 150}
    }
})

result = schema.validate(data)
print(result.valid)   # True / False
print(result.errors)  # 오류 메시지 목록

result.raise_if_invalid()  # 실패 시 ValidationError 발생
```

**지원 키워드:**

| 분류 | 키워드 |
|---|---|
| 타입 | `type` (`string`, `integer`, `number`, `boolean`, `array`, `object`, `null`), 다중 타입 `["string", "null"]` |
| 공통 | `enum` |
| 문자열 | `minLength`, `maxLength`, `pattern` |
| 숫자 | `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum` |
| 배열 | `items`, `minItems`, `maxItems` |
| 객체 | `properties`, `required`, `additionalProperties` |
| 조합 | `anyOf`, `oneOf`, `allOf`, `not` |

**ValidationResult:**

| 속성/메서드 | 설명 |
|---|---|
| `.valid` | 검증 통과 여부 (`bool`) |
| `.errors` | 오류 메시지 목록 (`list[str]`) |
| `.raise_if_invalid()` | 실패 시 `ValidationError` 발생 |
