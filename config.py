import discord
from configparser import ConfigParser


class AppConfig:
    SETTINGS_PATH = './settings.ini'

    def __init__(self):
        self.__config = ConfigParser()
        self.__config.read(AppConfig.SETTINGS_PATH)

        # [OpenAI]
        self.__ai = self.__config['OpenAI']
        self.organization_id = self.__ai['OrganizationID']
        self.api_key = self.__ai['APIKey']

        # [Parameters]
        self.__parameters = self.__config['Parameters']
        self.engine_name = self.__parameters['EngineName']
        self.temperature = float(self.__parameters['Temperature'])
        self.max_tokens = int(self.__parameters['MaxTokens'])
        self.top_p = float(self.__parameters['TopP'])
        self.frequency_penalty = float(self.__parameters['FrequencyPenalty'])
        self.presence_penalty = float(self.__parameters['PresencePenalty'])

        # [Conversation]
        self.__conversation = self.__config['Conversation']
        self.user_name = self.__conversation['UserName']
        self.ai_name = self.__conversation['AIName']
        self.prompt_path = self.__conversation['PromptPath']
        self.prompt = self.__read_prompt(self.prompt_path)
        self.formatted_prompt = self.__format_prompt(self.prompt, self.user_name, self.ai_name)

        # [Discord]
        self.__discord = self.__config['Discord']
        self.bot_token = self.__discord['BotToken']

        # [Servers]
        self.__items = self.__config.items('Servers')
        self.server_guilds = self.__parse_guilds(self.__items)

    @staticmethod
    def __read_prompt(__prompt_path: str) -> str:
        with open(__prompt_path, 'r') as __file:
            return __file.read()

    @staticmethod
    def __format_prompt(__prompt: str, __user_name: str, __ai_name: str) -> str:
        return __prompt.format(__user_name, __ai_name).strip() + "\n"

    @staticmethod
    def __parse_guilds(__items: list) -> list:
        return [discord.Object(id=int(__item[1])) for __item in __items]
