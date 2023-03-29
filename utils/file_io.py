import json
import os


def remove_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def load_json(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(path: str, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_txt(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def save_txt(path: str, text: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
