from pathlib import Path

from data.prompt import *
from utils.file_io import load_yaml

CURRENT_DIR = Path(__file__).parent
DATA_PATH = 'prompt.yaml'


def parse() -> Model:
    data = load_yaml(CURRENT_DIR / DATA_PATH)
    return Model.parse_obj(data)
