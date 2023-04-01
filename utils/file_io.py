import json
from pathlib import Path
from typing import Dict, Union

PathLike = Union[str, Path]


def remove_file(path: PathLike) -> None:
    Path(path).unlink(missing_ok=True)


def load_json(path: PathLike) -> Dict:
    try:
        with Path(path).open(encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(path: PathLike, data: Dict) -> None:
    with Path(path).open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_txt_strip(path: PathLike) -> str:
    return load_txt(path).strip()


def load_txt(path: PathLike) -> str:
    return Path(path).read_text(encoding='utf-8', errors='ignore')


def save_txt(path: PathLike, text: str) -> None:
    Path(path).write_text(text, encoding='utf-8')
