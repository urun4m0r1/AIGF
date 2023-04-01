from configparser import ConfigParser
from pathlib import Path
from typing import Iterable

from settings.session_cache import SessionCache
from utils.file_io import save_txt, load_txt
from utils.parser import parse_guilds, parse_sessions_list


class AppConfig:
    def __init__(self, path: str) -> None:
        self._config = ConfigParser()
        self._config.read(path)

        self._init_categories()
        self._init_values()
        self._init()

    def _init_categories(self):
        self._environment = self._config['Environment']
        self._cache = self._config['Environment.Cache']
        self._ai = self._config['OpenAI']
        self._parameters = self._config['OpenAI.Parameters']
        self._discord = self._config['Discord']
        self._servers = self._config['Discord.Servers']
        self._default = self._config['Default']

    def _init_values(self):
        # [Environment]
        self._default_prompt_path = Path(self._environment.get('DefaultPromptPath', ''))
        self._cache_path = Path(self._environment.get('CachePath', ''))

        # [Environment.Cache]
        self._sessions_list_name = self._cache.get('SessionsListName', '')
        self._settings_name = self._cache.get('SettingsName', '')
        self._prompt_name = self._cache.get('PromptName', '')
        self._history_name = self._cache.get('HistoryName', '')

        # [OpenAI]
        self.organization_id = self._ai.get('OrganizationID', '')
        self.api_key = self._ai.get('APIKey', '')

        # [OpenAI.Parameters]
        self.scroll_amount = self._parameters.getint('ScrollAmount', 0)
        self.engine_name = self._parameters.get('EngineName', '')
        self.max_tokens = self._parameters.getint('MaxTokens', 0)
        self.top_p = self._parameters.getfloat('TopP', 0.0)
        self.frequency_penalty = self._parameters.getfloat('FrequencyPenalty', 0.0)
        self.presence_penalty = self._parameters.getfloat('PresencePenalty', 0.0)

        # [Discord]
        self.bot_token = self._discord.get('BotToken', '')

    def _init(self):
        # Setup
        self.server_guilds = list(parse_guilds(self._servers.values()))
        self.default_prompt = load_txt(self._default_prompt_path)

        # Cache
        self._sessions_list_path = self._cache_path / self._sessions_list_name
        sessions = self._load_sessions_list()

        self._session_caches = {session_id: self._create_session_cache(session_id) for session_id in sessions}

        for session_cache in self._session_caches.values():
            session_cache.load_settings()

    def _create_session_cache(self, session_id: int) -> SessionCache:
        settings_path = self._cache_path / self._settings_name.format(session_id)
        prompt_path = self._cache_path / self._prompt_name.format(session_id)
        history_path = self._cache_path / self._history_name.format(session_id)

        session_cache = SessionCache(
            settings_path,
            prompt_path,
            history_path,
            self.default_prompt,
            self._default)

        return session_cache

    def _load_sessions_list(self) -> Iterable[int]:
        sessions_list = load_txt(self._sessions_list_path)
        return parse_sessions_list(sessions_list)

    def _save_sessions_list(self) -> None:
        sessions_list = '\n'.join(str(item) for item in self._session_caches.keys())
        save_txt(self._sessions_list_path, sessions_list)

    def is_cache_exists(self, session_id: int) -> bool:
        return session_id in self._session_caches

    def create_cache(self, session_id: int) -> SessionCache:
        if self.is_cache_exists(session_id):
            raise ValueError(f'Session cache with id {session_id} already exists')

        session_cache = self._create_session_cache(session_id)
        session_cache.reset_and_save()

        self._session_caches[session_id] = session_cache
        self._save_sessions_list()

        return session_cache

    def get_cache(self, session_id: int) -> SessionCache:
        if not self.is_cache_exists(session_id):
            raise ValueError(f'Session cache with id {session_id} does not exist')

        return self._session_caches[session_id]

    def get_or_create_cache(self, session_id: int) -> SessionCache:
        if self.is_cache_exists(session_id):
            return self.get_cache(session_id)
        else:
            self.create_cache(session_id)

    def remove_cache(self, session_id: int) -> None:
        if not self.is_cache_exists(session_id):
            return

        session_cache = self.get_cache(session_id)
        session_cache.remove_all()

        del self._session_caches[session_id]
        self._save_sessions_list()

    def remove_all_caches(self) -> None:
        for session_cache in self._session_caches.values():
            session_cache.remove_all()

        self._session_caches.clear()
        self._save_sessions_list()
