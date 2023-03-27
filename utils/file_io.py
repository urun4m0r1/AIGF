import json

FILE_ENCODING = "utf-8"


def load_json(path: str) -> dict:
    try:
        with open(path, 'r', encoding=FILE_ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(path: str, data: dict):
    with open(path, 'w', encoding=FILE_ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_txt(path: str) -> str:
    try:
        with open(path, 'r', encoding=FILE_ENCODING) as f:
            return f.read()
    except FileNotFoundError:
        return ''


def save_txt(path: str, text: str):
    with open(path, 'w', encoding=FILE_ENCODING) as f:
        f.write(text)
