from app.menu import run_menu
from json_lib import JsonFile


def main() -> None:
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
