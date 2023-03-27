from configparser import ConfigParser

from settings.config_cache import ConfigCache
from utils import parser, file_io

SETTINGS_PATH = './settings.ini'


class AppConfig:

    def __init__(self):
        self._config = ConfigParser()
        self._config.read(SETTINGS_PATH)

        # [Environment]
        self._environment = self._config['Environment']
        self._settings_cache_path = self._environment['SettingsCachePath']
        self.default_prompt_path = self._environment['DefaultPromptPath']
        self.prompt_history_path = self._environment['PromptHistoryPath']
        self.default_prompt = file_io.load_txt(self.default_prompt_path)
        self.prompt_history = file_io.load_txt(self.prompt_history_path)

        # [OpenAI]
        self._ai = self._config['OpenAI']
        self.organization_id = self._ai['OrganizationID']
        self.api_key = self._ai['APIKey']

        # [OpenAI.Parameters]
        self._parameters = self._config['OpenAI.Parameters']
        self.engine_name = self._parameters['EngineName']
        self.max_tokens = int(self._parameters['MaxTokens'])
        self.top_p = float(self._parameters['TopP'])
        self.frequency_penalty = float(self._parameters['FrequencyPenalty'])
        self.presence_penalty = float(self._parameters['PresencePenalty'])

        # [Discord]
        self._discord = self._config['Discord']
        self.bot_token = self._discord['BotToken']

        # [Discord.Servers]
        self._items = self._config.items('Discord.Servers')
        self.server_guilds = parser.parse_guilds(self._items)

        # [Default]
        self._default = self._config['Default']
        self.cache = ConfigCache(self._settings_cache_path, self.default_prompt, self._default)
