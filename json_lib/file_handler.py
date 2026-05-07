import json
import os
from pathlib import Path
from typing import Any


class JsonFile:
    def __init__(self, path: str | Path, encoding: str = "utf-8"):
        self.path = Path(path)
        self.encoding = encoding

    def read(self) -> Any:
        """JSON 파일을 읽어 Python 객체로 반환합니다."""
        if not self.path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.path}")
        try:
            with open(self.path, "r", encoding=self.encoding) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류 ({self.path}): {e}") from e

    def write(self, data: Any, *, indent: int | None = 2, ensure_ascii: bool = False, sort_keys: bool = False) -> None:
        """Python 객체를 JSON 파일로 저장합니다. 디렉토리가 없으면 자동 생성합니다."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path, "w", encoding=self.encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)
        except (TypeError, ValueError) as e:
            raise ValueError(f"JSON 직렬화 오류: {e}") from e

    def merge(self, patch: dict, *, indent: int | None = 2) -> Any:
        """기존 JSON 파일에 딕셔너리를 병합하고 저장합니다. 파일이 없으면 새로 생성합니다."""
        existing = self.read() if self.path.exists() else {}
        if not isinstance(existing, dict):
            raise TypeError("병합 대상은 JSON 오브젝트(dict)여야 합니다.")
        existing.update(patch)
        self.write(existing, indent=indent)
        return existing

    def exists(self) -> bool:
        return self.path.exists()

    def delete(self) -> None:
        """JSON 파일을 삭제합니다."""
        if not self.path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.path}")
        os.remove(self.path)
