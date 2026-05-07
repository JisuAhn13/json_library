from __future__ import annotations

import json
from typing import Any

from app import crud, display


def parse_value(text: str) -> Any:
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    try:
        v = json.loads(text)
        if isinstance(v, (list, dict)):
            return v
    except Exception:
        pass
    return text


def confirm(prompt: str) -> bool:
    return input(prompt).strip().lower() in ("y", "yes")


def input_required(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("값을 입력해주세요.")


def handle_create(filepath: str) -> None:
    print("\n[Create] 새 레코드 추가")
    fields: dict = {}
    while True:
        key = input("필드명 입력 (완료: Enter) > ").strip()
        if not key:
            break
        if key == "id":
            display.print_error("id 필드는 직접 입력할 수 없습니다.")
            continue
        value = input("값 입력 > ").strip()
        fields[key] = parse_value(value)

    if not fields:
        display.print_error("입력된 필드가 없습니다.")
        return

    record = crud.create_record(filepath, fields)
    display.print_separator()
    print("저장 완료:")
    display.print_record(record)


def handle_read(filepath: str) -> None:
    records = crud.read_all(filepath)
    if not records:
        display.print_error("저장된 데이터가 없습니다.")
        return

    print("\n[Read]")
    print("1. 전체 목록\n2. ID로 검색\n3. 키-값으로 검색")
    choice = input("선택 > ").strip()

    if choice == "1":
        display.print_records(records)

    elif choice == "2":
        try:
            record_id = int(input_required("검색할 ID > "))
            record = crud.read_by_id(filepath, record_id)
            display.print_separator()
            display.print_record(record)
            display.print_separator()
        except (KeyError, ValueError):
            display.print_error("해당 ID의 레코드가 없습니다.")

    elif choice == "3":
        key = input_required("검색할 필드명 > ")
        value = parse_value(input_required("검색할 값 > "))
        results = crud.read_by_field(filepath, key, value)
        if results:
            display.print_records(results)
        else:
            display.print_error("검색 결과가 없습니다.")

    else:
        display.print_error("1~3 사이의 번호를 입력하세요.")


def handle_update(filepath: str) -> None:
    records = crud.read_all(filepath)
    if not records:
        display.print_error("저장된 데이터가 없습니다.")
        return

    print("\n[Update] 레코드 수정")
    try:
        record_id = int(input_required("수정할 레코드 ID > "))
        record = crud.read_by_id(filepath, record_id)
    except (KeyError, ValueError):
        display.print_error("해당 ID의 레코드가 없습니다.")
        return

    print("\n현재 데이터:")
    display.print_record(record)

    while True:
        key = input_required("수정할 필드명 > ")
        if key == "id":
            display.print_error("id 필드는 수정할 수 없습니다.")
            continue
        break

    print(f"현재 값 : {record.get(key, '(없음)')}")
    new_value = parse_value(input("새 값 입력 > ").strip())

    updated = crud.update_record(filepath, record_id, key, new_value)
    display.print_separator()
    print("수정 완료:")
    display.print_record(updated)


def handle_delete(filepath: str) -> None:
    records = crud.read_all(filepath)
    if not records:
        display.print_error("저장된 데이터가 없습니다.")
        return

    print("\n[Delete] 레코드 삭제")
    try:
        record_id = int(input_required("삭제할 레코드 ID > "))
        record = crud.read_by_id(filepath, record_id)
    except (KeyError, ValueError):
        display.print_error("해당 ID의 레코드가 없습니다.")
        return

    print("\n삭제 대상:")
    display.print_record(record)

    if confirm("\n정말 삭제하시겠습니까? (y/n) > "):
        crud.delete_record(filepath, record_id)
        display.print_separator()
        display.print_success(f"ID {record_id} 레코드가 삭제되었습니다.")
    else:
        print("삭제가 취소되었습니다.")


def run_menu(filepath: str) -> None:
    while True:
        try:
            count = len(crud.read_all(filepath))
        except FileNotFoundError:
            count = 0

        display.print_menu(filepath, count)
        choice = input("선택 > ").strip()

        if choice == "1":
            handle_create(filepath)
        elif choice == "2":
            handle_read(filepath)
        elif choice == "3":
            handle_update(filepath)
        elif choice == "4":
            handle_delete(filepath)
        elif choice == "5":
            print("앱을 종료합니다.")
            break
        else:
            display.print_error("1~5 사이의 번호를 입력하세요.")
