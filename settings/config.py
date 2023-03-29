from configparser import ConfigParser

from settings.config_cache import ConfigCache
from utils.file_io import save_txt, load_txt
from utils.parser import parse_guilds, parse_session_list

SETTINGS_PATH = './settings.ini'


class AppConfig:

    def __init__(self):
        self._config = ConfigParser()
        self._config.read(SETTINGS_PATH)

        # Categories
        self._environment = self._config['Environment']
        self._cache = self._config['Environment.Cache']
        self._ai = self._config['OpenAI']
        self._parameters = self._config['OpenAI.Parameters']
        self._discord = self._config['Discord']
        self._servers = self._config['Discord.Servers']
        self._default = self._config['Default']

        # [Environment]
        self._default_prompt_path = self._environment.get('DefaultPromptPath', '')
        self._cache_path = self._environment.get('CachePath', '')

        # [Environment.Cache]
        self._session_list_name = self._cache.get('SessionListName', '')
        self._settings_cache_name = self._cache.get('SettingsCacheName', '')
        self._prompt_history_name = self._cache.get('PromptHistoryName', '')

        # [OpenAI]
        self.organization_id = self._ai.get('OrganizationID', '')
        self.api_key = self._ai.get('APIKey', '')

        # [OpenAI.Parameters]
        self.engine_name = self._parameters.get('EngineName', '')
        self.max_tokens = self._parameters.getint('MaxTokens', 0)
        self.top_p = self._parameters.getfloat('TopP', 0.0)
        self.frequency_penalty = self._parameters.getfloat('FrequencyPenalty', 0.0)
        self.presence_penalty = self._parameters.getfloat('PresencePenalty', 0.0)

        # [Discord]
        self.bot_token = self._discord.get('BotToken', '')

        # Setup
        self.server_guilds = parse_guilds([item[1] for item in self._servers.items()])
        self.default_prompt = load_txt(self._default_prompt_path)

        # Cache
        self._session_list_path = self._cache_path + self._session_list_name
        session_list_text = load_txt(self._session_list_path)
        session_list = parse_session_list(session_list_text)
        self._session_caches = {}

        for session_id in session_list:
            self.create_config_cache(session_id)

    def get_or_create_cache(self, session_id: int) -> ConfigCache:
        if session_id not in self._session_caches:
            self.create_cache(session_id)

        return self.get_cache(session_id)

    def get_cache(self, session_id: int) -> ConfigCache:
        return self._session_caches[session_id]

    def create_cache(self, session_id: int):
        settings_cache = self.create_config_cache(session_id)
        settings_cache.save()

        session_list = list(self._session_caches.keys())
        session_list_text = ','.join([str(item) for item in session_list])
        save_txt(self._session_list_path, session_list_text)

    def create_config_cache(self, session_id: int) -> ConfigCache:
        settings_cache_path = self._cache_path + self._settings_cache_name.format(session_id)
        prompt_history_path = self._cache_path + self._prompt_history_name.format(session_id)
        settings_cache = ConfigCache(settings_cache_path,
                                     prompt_history_path,
                                     self.default_prompt,
                                     self._default)
        self._session_caches[session_id] = settings_cache
        return settings_cache
