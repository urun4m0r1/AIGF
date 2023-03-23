import openai
from configparser import ConfigParser

SETTINGS_PATH = 'settings.ini'

ENGINE_NAME = 'text-davinci-003'
TEMPERATURE = 0.7
MAX_TOKENS = 1024

USER_NAME = 'User'
AI_NAME = 'AI'
INITIAL_PROMPT = f'''[Conversation with {AI_NAME}]
The following is a conversation with {USER_NAME} and {AI_NAME}.
{AI_NAME} should be answering helpful, creative, clever, and very friendly way.

[Rules]
{AI_NAME}`s answer should be accurate, and relevant to the conversation.
{AI_NAME}`s answer cannot be null or whitespace.

[Conversation]
'''
EXIT_COMMANDS = ['exit', 'quit', 'goodbye', 'bye']
GOODBYE_RESPONSE = 'Goodbye!'


class OpenAISettings:
    def __init__(self, path: str):
        self.__path = path
        self.__config = self.__get_settings()
        self.__organization_id = self.__get_organization_id()
        self.__api_key = self.__get_api_key()

    def __get_settings(self) -> ConfigParser:
        config = ConfigParser()
        config.read(self.__path)
        return config

    def __get_organization_id(self) -> str:
        return self.__config['OpenAI']['OrganizationID']

    def __get_api_key(self) -> str:
        return self.__config['OpenAI']['APIKey']

    def setup_openai_api_key(self):
        openai.organization = self.__organization_id
        openai.api_key = self.__api_key


class OpenAIConversation:
    def __init__(self):
        self.__full_prompt = INITIAL_PROMPT
        self.__ai_response = None

    def get_response(self) -> str:
        return self.__ai_response.choices[0].text.strip()

    def record_history(self, prompt: str):
        self.__full_prompt += prompt

    def set_response(self, input_prompt: str):
        input_prompt += f"\n{AI_NAME}: "
        self.record_history(input_prompt)

        self.__ai_response = openai.Completion.create(
            engine=ENGINE_NAME,
            prompt=self.__full_prompt,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[f'{USER_NAME}:', f'{AI_NAME}:'],
        )


def talk_to_ai():
    conversation = OpenAIConversation()

    while True:
        user_input = input(f"{USER_NAME}: ")
        if user_input.lower() in EXIT_COMMANDS:
            print(GOODBYE_RESPONSE)
            break

        named_user_input = f"{USER_NAME}: {user_input}"
        conversation.set_response(named_user_input)

        response = conversation.get_response()
        named_response = f"{AI_NAME}: {response}"
        print(named_response)

        conversation.record_history(response)
        conversation.record_history('\n')


if __name__ == '__main__':
    settings = OpenAISettings(SETTINGS_PATH)
    settings.setup_openai_api_key()
    talk_to_ai()
