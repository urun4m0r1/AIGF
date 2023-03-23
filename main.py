import os
import json
import openai
from base64 import b64decode
from pathlib import Path
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


DATA_DIR = Path.cwd() / 'data'
IMAGE_DIR = Path.cwd() / 'images'
T2I_PROMPT = "Girl in spacesuit, spaceship inside, Tsutomu Nihei style, Sidonia no Kishi, gigantism, laser generator, multi-story space, futuristic style, Sci-fi, hyperdetail, laser in center, laser from the sky, energy clots, acceleration, light flash, speed, anime, drawing, 8K, HD, super-resolution, manga graphics, Drawing, First-Person, 8K, HD, Super-Resolution"

DATA_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)


def request_image():
    t2i_response = openai.Image.create(
        prompt=T2I_PROMPT,
        n=4,
        size="512x512",
        response_format="b64_json",
    )

    file_name = DATA_DIR / f"{T2I_PROMPT[:5]}-{t2i_response['created']}.json"

    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(t2i_response, file)


def download_image():
    json_path = find_json_path()
    with open(json_path, mode="r", encoding="utf-8") as file:
        response = json.load(file)

    for index, image_dict in enumerate(response["data"]):
        image_data = b64decode(image_dict["b64_json"])
        image_file = IMAGE_DIR / f"{json_path.stem}-{index}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)


def find_json_path():
    for file in DATA_DIR.iterdir():
        if file.suffix == '.json':
            return file


if __name__ == '__main__':
    settings = OpenAISettings(SETTINGS_PATH)
    settings.setup_openai_api_key()
    # talk_to_ai()
    request_image()
    download_image()
