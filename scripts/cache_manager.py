import copy
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterable

from data import prompt_parser, conversation_parser
from data.history import History
from scripts.config import AppConfig
from utils.file_io import load_txt, save_yaml, remove_file


class CacheManager:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

        self._default_prompt = load_txt(self.config.default_prompt_path)
        self._prompt_model = prompt_parser.parse(self.config.prompt_model_path)
        self._conversation_model = conversation_parser.parse(self.config.conversation_model_path)

        self.default_history = History(self._default_prompt, self._prompt_model, self._conversation_model)

    def recreate(self, session_id: str) -> History:
        self.remove_cache(session_id)
        return self.create_cache(session_id)

    def get(self, session_id: str) -> History:
        cache = self.load_cache(session_id)
        if cache:
            return cache
        else:
            return self.create_cache(session_id)

    def get_all(self) -> Iterable[History]:
        for cache_path in self._get_caches_path():
            conversation_cache = conversation_parser.parse(cache_path)
            yield History(self._default_prompt, self._prompt_model, conversation_cache)

    def create_cache(self, session_id: str) -> History:
        history = copy.deepcopy(self.default_history)

        session = history.conversation_model.session
        session.id = session_id
        session.creationTime = datetime.now().isoformat()

        messages = history.conversation_model.messages
        messages.clear()

        self.save_cache(history)
        return history

    def load_cache(self, session_id: str) -> Optional[History]:
        caches_path = self._get_caches_path()
        cache_path = next((path for path in caches_path if path.stem == session_id), None)
        if cache_path is None:
            return None

        conversation_cache = conversation_parser.parse(cache_path)
        return History(self._default_prompt, self._prompt_model, conversation_cache)

    def save_cache(self, history: History) -> None:
        session = history.conversation_model.session
        path = self._get_cache_path(session.id)

        save_yaml(path, history.conversation_model.dict())

    def remove_cache(self, session_id: str) -> None:
        remove_file(self._get_cache_path(session_id))

    def remove_caches(self) -> None:
        remove_file(self.config.cache_path)

    def _get_caches_path(self) -> Iterable[Path]:
        return Path(self.config.cache_path).glob('*.yaml')

    def _get_cache_path(self, session_id: str) -> Path:
        return self.config.cache_path / f'{session_id}.yaml'
