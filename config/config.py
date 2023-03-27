from configparser import ConfigParser

from config_cache import ConfigCache
from utils import parser, file_io

SETTINGS_PATH = '../settings.ini'


class AppConfig:

    def __init__(self):
        self._config = ConfigParser()
        self._config.read(SETTINGS_PATH)

        # [General]
        self._general = self._config['General']
        self._settings_cache_path = self._general['SettingsCachePath']

        # [OpenAI]
        self._ai = self._config['OpenAI']
        self.organization_id = self._ai['OrganizationID']
        self.api_key = self._ai['APIKey']

        # [Parameters]
        self._parameters = self._config['Parameters']
        self.engine_name = self._parameters['EngineName']
        self.max_tokens = int(self._parameters['MaxTokens'])
        self.top_p = float(self._parameters['TopP'])
        self.frequency_penalty = float(self._parameters['FrequencyPenalty'])
        self.presence_penalty = float(self._parameters['PresencePenalty'])

        # [Conversation]
        self._conversation = self._config['Conversation']
        self.default_prompt_path = self._conversation['DefaultPromptPath']
        self.prompt_history_path = self._conversation['PromptHistoryPath']
        self.default_prompt = file_io.load_txt(self.default_prompt_path)
        self.prompt_history = file_io.load_txt(self.prompt_history_path)

        # [Discord]
        self._discord = self._config['Discord']
        self.bot_token = self._discord['BotToken']

        # [Servers]
        self._items = self._config.items('Servers')
        self.server_guilds = parser.parse_guilds(self._items)

        # [Default]
        self._default = self._config['Default']
        self.cache = ConfigCache(self._settings_cache_path, self.default_prompt, self._default)
