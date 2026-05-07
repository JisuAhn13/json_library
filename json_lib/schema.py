from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        if not self.valid:
            raise ValidationError(self.errors)


_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


class JsonSchema:
    """
    JSON Schema 하위 집합 검증기입니다.

    지원 키워드:
        type, properties, required, additionalProperties,
        items, minItems, maxItems,
        minimum, maximum, minLength, maxLength, pattern,
        enum, anyOf, oneOf, allOf, not
    """

    def __init__(self, schema: dict):
        self.schema = schema

    def validate(self, data: Any) -> ValidationResult:
        errors: list[str] = []
        self._validate_node(data, self.schema, "$", errors)
        return ValidationResult(valid=not errors, errors=errors)

    # ------------------------------------------------------------------
    # 내부 검증 로직
    # ------------------------------------------------------------------

    def _validate_node(self, data: Any, schema: dict | bool, path: str, errors: list[str]) -> None:
        if isinstance(schema, bool):
            if not schema:
                errors.append(f"{path}: 이 값은 허용되지 않습니다.")
            return

        self._check_type(data, schema, path, errors)
        self._check_enum(data, schema, path, errors)
        self._check_string(data, schema, path, errors)
        self._check_number(data, schema, path, errors)
        self._check_array(data, schema, path, errors)
        self._check_object(data, schema, path, errors)
        self._check_any_of(data, schema, path, errors)
        self._check_one_of(data, schema, path, errors)
        self._check_all_of(data, schema, path, errors)
        self._check_not(data, schema, path, errors)

    def _check_type(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "type" not in schema:
            return
        expected = schema["type"]
        if isinstance(expected, list):
            types = expected
        else:
            types = [expected]

        for t in types:
            py_type = _TYPE_MAP.get(t)
            if py_type is None:
                continue
            if isinstance(py_type, tuple):
                if isinstance(data, py_type) and not (t == "number" and isinstance(data, bool)):
                    return
            else:
                if isinstance(data, py_type) and not (t == "integer" and isinstance(data, bool)):
                    return
        errors.append(f"{path}: 타입이 올바르지 않습니다. 예상={types}, 실제={type(data).__name__}")

    def _check_enum(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "enum" not in schema:
            return
        if data not in schema["enum"]:
            errors.append(f"{path}: 허용된 값이 아닙니다. 허용={schema['enum']}, 실제={data!r}")

    def _check_string(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if not isinstance(data, str):
            return
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: 문자열 길이가 너무 짧습니다. 최소={schema['minLength']}, 실제={len(data)}")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(f"{path}: 문자열 길이가 너무 깁니다. 최대={schema['maxLength']}, 실제={len(data)}")
        if "pattern" in schema:
            import re
            if not re.search(schema["pattern"], data):
                errors.append(f"{path}: 패턴과 일치하지 않습니다. pattern={schema['pattern']!r}")

    def _check_number(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if not isinstance(data, (int, float)) or isinstance(data, bool):
            return
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: 값이 너무 작습니다. 최소={schema['minimum']}, 실제={data}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: 값이 너무 큽니다. 최대={schema['maximum']}, 실제={data}")
        if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: 값이 exclusiveMinimum 이하입니다. 최솟값(미포함)={schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
            errors.append(f"{path}: 값이 exclusiveMaximum 이상입니다. 최댓값(미포함)={schema['exclusiveMaximum']}")

    def _check_array(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if not isinstance(data, list):
            return
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: 배열 항목이 너무 적습니다. 최소={schema['minItems']}, 실제={len(data)}")
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{path}: 배열 항목이 너무 많습니다. 최대={schema['maxItems']}, 실제={len(data)}")
        if "items" in schema:
            for i, item in enumerate(data):
                self._validate_node(item, schema["items"], f"{path}[{i}]", errors)

    def _check_object(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if not isinstance(data, dict):
            return
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"{path}: 필수 필드가 없습니다. field={key!r}")
        props = schema.get("properties", {})
        for key, sub_schema in props.items():
            if key in data:
                self._validate_node(data[key], sub_schema, f"{path}.{key}", errors)
        additional = schema.get("additionalProperties", True)
        if additional is False:
            for key in data:
                if key not in props:
                    errors.append(f"{path}: 허용되지 않는 추가 필드입니다. field={key!r}")
        elif isinstance(additional, dict):
            for key in data:
                if key not in props:
                    self._validate_node(data[key], additional, f"{path}.{key}", errors)

    def _check_any_of(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "anyOf" not in schema:
            return
        for sub in schema["anyOf"]:
            sub_errors: list[str] = []
            self._validate_node(data, sub, path, sub_errors)
            if not sub_errors:
                return
        errors.append(f"{path}: anyOf 조건 중 하나도 만족하지 않습니다.")

    def _check_one_of(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "oneOf" not in schema:
            return
        matched = sum(
            1 for sub in schema["oneOf"]
            if not (errs := [], self._validate_node(data, sub, path, errs))[0] and not errs
        )
        if matched != 1:
            errors.append(f"{path}: oneOf 조건 중 정확히 하나만 만족해야 합니다. (만족 수={matched})")

    def _check_all_of(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "allOf" not in schema:
            return
        for sub in schema["allOf"]:
            self._validate_node(data, sub, path, errors)

    def _check_not(self, data: Any, schema: dict, path: str, errors: list[str]) -> None:
        if "not" not in schema:
            return
        sub_errors: list[str] = []
        self._validate_node(data, schema["not"], path, sub_errors)
        if not sub_errors:
            errors.append(f"{path}: not 조건을 만족하면 안 됩니다.")
