import configparser
from pathlib import Path

from utils.file_io import save_txt, load_txt, save_json, load_json, remove_file

KEY_USER_NAME = 'UserName'
KEY_AI_NAME = 'AIName'
KEY_CREATIVITY = 'Creativity'


class SessionCache:
    def __init__(self,
                 settings_path: Path,
                 prompt_path: Path,
                 history_path: Path,
                 default_prompt: str,
                 section: configparser.SectionProxy):
        self._settings_path = settings_path
        self._prompt_path = prompt_path
        self._history_path = history_path

        self._default_prompt = default_prompt
        self._default_user_name = section.get(KEY_USER_NAME, '')
        self._default_ai_name = section.get(KEY_AI_NAME, '')
        self._default_creativity = section.getint(KEY_CREATIVITY, 0)

        self.user_name = self._default_user_name
        self.ai_name = self._default_ai_name
        self.creativity = self._default_creativity

    def reset_and_save(self):
        self.reset_all()

        self.save_settings()
        self.save_prompt(self._default_prompt)
        self.save_history('')

    def reset_all(self):
        self.user_name = self._default_user_name
        self.ai_name = self._default_ai_name
        self.creativity = self._default_creativity

    def remove_all(self):
        self.remove_prompt()
        self.remove_history()
        self.remove_settings()

    def load_settings(self):
        cache = load_json(self._settings_path)

        self.user_name = str(cache.get(KEY_USER_NAME, self.user_name))
        self.ai_name = str(cache.get(KEY_AI_NAME, self.ai_name))
        self.creativity = int(cache.get(KEY_CREATIVITY, self.creativity))

    def load_prompt_format(self) -> str:
        return load_txt(self._prompt_path).strip().format(self.user_name, self.ai_name)

    def load_prompt(self) -> str:
        return load_txt(self._prompt_path).strip()

    def load_history(self) -> str:
        return load_txt(self._history_path).strip()

    def save_settings(self):
        cache = {
            KEY_USER_NAME: self.user_name,
            KEY_AI_NAME: self.ai_name,
            KEY_CREATIVITY: self.creativity,
        }

        save_json(self._settings_path, cache)

    def save_prompt(self, prompt: str):
        save_txt(self._prompt_path, prompt)

    def save_history(self, history: str):
        save_txt(self._history_path, history)

    def remove_settings(self):
        remove_file(self._settings_path)

    def remove_prompt(self):
        remove_file(self._prompt_path)

    def remove_history(self):
        remove_file(self._history_path)
