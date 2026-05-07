from __future__ import annotations

import json

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
