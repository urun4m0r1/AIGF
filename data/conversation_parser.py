from pathlib import Path
from typing import Union

from data.conversation import *
from utils.file_io import load_yaml

PathLike = Union[str, Path]


def parse(data_path: PathLike) -> Model:
    data = load_yaml(data_path)
    return Model.parse_obj(data)
