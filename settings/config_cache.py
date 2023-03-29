import configparser

from utils import file_io
from utils.file_io import save_txt, load_txt

KEY_USER_NAME = 'UserName'
KEY_AI_NAME = 'AIName'
KEY_CREATIVITY = 'Creativity'


class ConfigCache:
    def __init__(self, path: str,
                 prompt_path: str,
                 default_prompt: str,
                 section: configparser.SectionProxy):
        self._path = path
        self._prompt_path = prompt_path
        self._default_prompt = default_prompt

        self.user_name = section[KEY_USER_NAME]
        self.ai_name = section[KEY_AI_NAME]
        self.creativity = int(section[KEY_CREATIVITY])

    def get_initial_prompt(self) -> str:
        return self._default_prompt.format(self.user_name, self.ai_name).strip() + "\n"

    def load_prompt(self) -> str:
        return load_txt(self._prompt_path)

    def save_prompt(self, prompt: str):
        save_txt(self._prompt_path, prompt)

    def save(self):
        cache = {
            KEY_USER_NAME: self.user_name,
            KEY_AI_NAME: self.ai_name,
            KEY_CREATIVITY: self.creativity,
        }

        file_io.save_json(self._path, cache)

    def load(self):
        cache = file_io.load_json(self._path)

        self.user_name = str(cache.get(KEY_USER_NAME, self.user_name))
        self.ai_name = str(cache.get(KEY_AI_NAME, self.ai_name))
        self.creativity = int(cache.get(KEY_CREATIVITY, self.creativity))
