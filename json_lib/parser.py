import json
from typing import Any


class JsonParser:
    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding

    def parse(self, text: str) -> Any:
        """JSON 문자열을 Python 객체로 변환합니다."""
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}") from e

    def serialize(self, data: Any, *, indent: int | None = None, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        """Python 객체를 JSON 문자열로 변환합니다."""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)
        except (TypeError, ValueError) as e:
            raise ValueError(f"JSON 직렬화 오류: {e}") from e
