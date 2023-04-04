from data.prompt import *
from utils.file_io import load_yaml

DATA_PATH = 'prompt.yaml'


def parse() -> Model:
    data = load_yaml(DATA_PATH)
    return Model.parse_obj(data)
