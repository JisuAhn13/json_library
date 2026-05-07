import json
import tempfile
from pathlib import Path

import pytest

from json_lib import JsonFile, JsonParser, JsonSchema, ValidationError


# ─────────────────────────────────────────────
# JsonParser
# ─────────────────────────────────────────────
class TestJsonParser:
    def setup_method(self):
        self.parser = JsonParser()

    def test_parse_object(self):
        result = self.parser.parse('{"name": "홍길동", "age": 30}')
        assert result == {"name": "홍길동", "age": 30}

    def test_parse_array(self):
        result = self.parser.parse("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_invalid_raises(self):
        with pytest.raises(ValueError, match="JSON 파싱 오류"):
            self.parser.parse("{invalid}")

    def test_serialize_basic(self):
        text = self.parser.serialize({"a": 1})
        assert json.loads(text) == {"a": 1}

    def test_serialize_indent(self):
        text = self.parser.serialize({"a": 1}, indent=2)
        assert "\n" in text

    def test_serialize_sort_keys(self):
        text = self.parser.serialize({"b": 2, "a": 1}, sort_keys=True)
        assert text.index('"a"') < text.index('"b"')

    def test_serialize_non_serializable_raises(self):
        with pytest.raises(ValueError, match="JSON 직렬화 오류"):
            self.parser.serialize(object())


# ─────────────────────────────────────────────
# JsonFile
# ─────────────────────────────────────────────
class TestJsonFile:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_write_and_read(self):
        jf = JsonFile(self.tmp / "data.json")
        jf.write({"hello": "world"})
        assert jf.read() == {"hello": "world"}

    def test_read_missing_file_raises(self):
        jf = JsonFile(self.tmp / "missing.json")
        with pytest.raises(FileNotFoundError):
            jf.read()

    def test_write_creates_parent_dirs(self):
        jf = JsonFile(self.tmp / "a" / "b" / "c.json")
        jf.write([1, 2, 3])
        assert jf.read() == [1, 2, 3]

    def test_merge_new_file(self):
        jf = JsonFile(self.tmp / "merge.json")
        result = jf.merge({"x": 1})
        assert result == {"x": 1}

    def test_merge_existing_file(self):
        jf = JsonFile(self.tmp / "merge.json")
        jf.write({"a": 1})
        result = jf.merge({"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_merge_overwrites_key(self):
        jf = JsonFile(self.tmp / "merge.json")
        jf.write({"a": 1})
        result = jf.merge({"a": 99})
        assert result["a"] == 99

    def test_merge_non_object_raises(self):
        jf = JsonFile(self.tmp / "arr.json")
        jf.write([1, 2])
        with pytest.raises(TypeError):
            jf.merge({"x": 1})

    def test_exists_and_delete(self):
        jf = JsonFile(self.tmp / "del.json")
        jf.write({})
        assert jf.exists()
        jf.delete()
        assert not jf.exists()

    def test_delete_missing_raises(self):
        jf = JsonFile(self.tmp / "ghost.json")
        with pytest.raises(FileNotFoundError):
            jf.delete()


# ─────────────────────────────────────────────
# JsonSchema
# ─────────────────────────────────────────────
class TestJsonSchemaType:
    def _ok(self, schema, data):
        r = JsonSchema(schema).validate(data)
        assert r.valid, r.errors

    def _fail(self, schema, data):
        r = JsonSchema(schema).validate(data)
        assert not r.valid

    def test_string_type(self):
        self._ok({"type": "string"}, "hello")
        self._fail({"type": "string"}, 123)

    def test_integer_type(self):
        self._ok({"type": "integer"}, 5)
        self._fail({"type": "integer"}, 5.5)
        self._fail({"type": "integer"}, True)

    def test_number_type(self):
        self._ok({"type": "number"}, 3.14)
        self._ok({"type": "number"}, 10)
        self._fail({"type": "number"}, "3.14")

    def test_boolean_type(self):
        self._ok({"type": "boolean"}, True)
        self._fail({"type": "boolean"}, 1)

    def test_null_type(self):
        self._ok({"type": "null"}, None)
        self._fail({"type": "null"}, 0)

    def test_array_type(self):
        self._ok({"type": "array"}, [])
        self._fail({"type": "array"}, {})

    def test_object_type(self):
        self._ok({"type": "object"}, {})
        self._fail({"type": "object"}, [])

    def test_multi_type(self):
        self._ok({"type": ["string", "null"]}, None)
        self._ok({"type": ["string", "null"]}, "hi")
        self._fail({"type": ["string", "null"]}, 1)


class TestJsonSchemaString:
    def _schema(self, **kwargs):
        return {"type": "string", **kwargs}

    def test_min_length(self):
        r = JsonSchema(self._schema(minLength=3)).validate("ab")
        assert not r.valid

    def test_max_length(self):
        r = JsonSchema(self._schema(maxLength=3)).validate("abcd")
        assert not r.valid

    def test_pattern(self):
        r = JsonSchema(self._schema(pattern=r"^\d+$")).validate("abc")
        assert not r.valid
        r2 = JsonSchema(self._schema(pattern=r"^\d+$")).validate("123")
        assert r2.valid


class TestJsonSchemaNumber:
    def test_minimum(self):
        r = JsonSchema({"type": "number", "minimum": 5}).validate(3)
        assert not r.valid

    def test_maximum(self):
        r = JsonSchema({"type": "number", "maximum": 10}).validate(11)
        assert not r.valid

    def test_exclusive_minimum(self):
        r = JsonSchema({"type": "number", "exclusiveMinimum": 5}).validate(5)
        assert not r.valid

    def test_exclusive_maximum(self):
        r = JsonSchema({"type": "number", "exclusiveMaximum": 10}).validate(10)
        assert not r.valid


class TestJsonSchemaArray:
    def test_items(self):
        schema = {"type": "array", "items": {"type": "integer"}}
        r = JsonSchema(schema).validate([1, "two", 3])
        assert not r.valid
        assert any("타입" in e for e in r.errors)

    def test_min_max_items(self):
        assert not JsonSchema({"type": "array", "minItems": 2}).validate([1]).valid
        assert not JsonSchema({"type": "array", "maxItems": 2}).validate([1, 2, 3]).valid


class TestJsonSchemaObject:
    def test_required(self):
        schema = {"type": "object", "required": ["name"]}
        r = JsonSchema(schema).validate({"age": 10})
        assert not r.valid

    def test_properties(self):
        schema = {
            "type": "object",
            "properties": {"age": {"type": "integer"}},
        }
        r = JsonSchema(schema).validate({"age": "thirty"})
        assert not r.valid

    def test_additional_properties_false(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False,
        }
        r = JsonSchema(schema).validate({"name": "Alice", "extra": 1})
        assert not r.valid

    def test_additional_properties_schema(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": {"type": "integer"},
        }
        assert not JsonSchema(schema).validate({"name": "Alice", "score": "high"}).valid
        assert JsonSchema(schema).validate({"name": "Alice", "score": 99}).valid


class TestJsonSchemaCompositions:
    def test_enum(self):
        r = JsonSchema({"enum": ["a", "b", "c"]}).validate("d")
        assert not r.valid

    def test_any_of(self):
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        assert JsonSchema(schema).validate("hello").valid
        assert JsonSchema(schema).validate(1).valid
        assert not JsonSchema(schema).validate([]).valid

    def test_all_of(self):
        schema = {"allOf": [{"type": "integer"}, {"minimum": 5}]}
        assert JsonSchema(schema).validate(10).valid
        assert not JsonSchema(schema).validate(3).valid

    def test_not(self):
        schema = {"not": {"type": "string"}}
        assert JsonSchema(schema).validate(1).valid
        assert not JsonSchema(schema).validate("hi").valid

    def test_one_of(self):
        # 양의 정수 또는 음의 정수 중 정확히 하나만 만족해야 함
        schema = {"oneOf": [{"minimum": 1}, {"maximum": -1}]}
        assert JsonSchema(schema).validate(5).valid       # minimum만 만족
        assert JsonSchema(schema).validate(-5).valid      # maximum만 만족
        assert not JsonSchema(schema).validate(0).valid   # 둘 다 불만족
        assert not JsonSchema(schema).validate(100).valid or \
               JsonSchema({"oneOf": [{"minimum": 1}, {"minimum": 1}]}).validate(5).valid is False
        # 두 조건 모두 만족하면 oneOf 실패
        r = JsonSchema({"oneOf": [{"minimum": 1}, {"minimum": 1}]}).validate(5)
        assert not r.valid


class TestJsonFileCorrupt:
    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_read_corrupt_file_raises(self):
        corrupt = self.tmp / "corrupt.json"
        corrupt.write_text("{invalid json!!}", encoding="utf-8")
        jf = JsonFile(corrupt)
        with pytest.raises(ValueError, match="JSON 파싱 오류"):
            jf.read()


class TestValidationError:
    def test_raise_if_invalid(self):
        r = JsonSchema({"type": "string"}).validate(123)
        with pytest.raises(ValidationError) as exc_info:
            r.raise_if_invalid()
        assert exc_info.value.errors

    def test_raise_if_valid_does_not_raise(self):
        r = JsonSchema({"type": "string"}).validate("ok")
        r.raise_if_invalid()  # 예외 없어야 함
