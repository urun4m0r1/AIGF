from configparser import ConfigParser
from pathlib import Path
from typing import Iterable

from utils.file_io import remove_file


class AppConfig:
    def __init__(self, path: Path) -> None:
        self._config = ConfigParser()
        self._config.read(path)

        self._init_categories()
        self._init_values()

    def _init_categories(self) -> None:
        self._environment = self._config['Environment']
        self._tokens = self._config['Tokens']
        self._servers = self._config['Servers']

    def _init_values(self) -> None:
        # [Environment]
        self.default_prompt_path = Path(self._environment.get('DEFAULT_PROMPT_PATH', ''))
        self.prompt_model_path = Path(self._environment.get('PROMPT_MODEL_PATH', ''))
        self.conversation_model_path = Path(self._environment.get('CONVERSATION_MODEL_PATH', ''))
        self.cache_path = Path(self._environment.get('CACHE_PATH', ''))

        # [Tokens]
        self.open_ai_organization_id = self._tokens.get('OPEN_AI_ORGANIZATION_ID', '')
        self.open_ai_api_key = self._tokens.get('OPEN_AI_API_KEY', '')
        self.discord_bot_token = self._tokens.get('DISCORD_BOT_TOKEN', '')

        # [Servers]
        self.server_guilds = self._servers.values()

    def get_caches(self) -> Iterable[Path]:
        return Path(self.cache_path).glob('*.yaml')

    def reset_cache(self) -> None:
        remove_file(self.cache_path)
