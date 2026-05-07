from json_lib import JsonParser, JsonFile, JsonSchema

SEPARATOR = "-" * 40

def demo_parser():
    print(SEPARATOR)
    print("[1] JSON 파싱 / 직렬화")
    print(SEPARATOR)

    parser = JsonParser()

    text = '{"name": "홍길동", "age": 30, "skills": ["Python", "JSON"]}'
    data = parser.parse(text)
    print("입력 문자열:", text)
    print("파싱 결과  :", data)

    serialized = parser.serialize(data, indent=2)
    print("직렬화 결과:\n" + serialized)


def demo_file():
    print(SEPARATOR)
    print("[2] 파일 저장 / 읽기 / 병합")
    print(SEPARATOR)

    jf = JsonFile("output.json")

    original = {"name": "홍길동", "age": 30}
    jf.write(original)
    print("저장한 데이터:", original)

    loaded = jf.read()
    print("읽어온 데이터:", loaded)

    merged = jf.merge({"city": "서울", "age": 31})
    print("병합 후 데이터:", merged)
    print("저장된 파일   : output.json")


def demo_schema():
    print(SEPARATOR)
    print("[3] 스키마 검증")
    print(SEPARATOR)

    schema = JsonSchema({
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age":  {"type": "integer", "minimum": 0, "maximum": 150},
            "city": {"type": "string"}
        }
    })

    good = {"name": "홍길동", "age": 31, "city": "서울"}
    result = schema.validate(good)
    print(f"유효한 데이터  : {good}")
    print(f"검증 결과      : {'통과' if result.valid else '실패'}")

    print()

    bad = {"age": -5}
    result2 = schema.validate(bad)
    print(f"잘못된 데이터  : {bad}")
    print(f"검증 결과      : {'통과' if result2.valid else '실패'}")
    print("오류 목록:")
    for err in result2.errors:
        print("  -", err)


if __name__ == "__main__":
    demo_parser()
    print()
    demo_file()
    print()
    demo_schema()
    print(SEPARATOR)
    print("완료!")
