import openai
from config import AppConfig


class OpenAIConversation:
    def __init__(self, __config: AppConfig):
        self.__config = __config
        openai.organization = self.__config.organization_id
        openai.api_key = self.__config.api_key

        self.__full_prompt = self.__config.formatted_prompt
        self.__response = None

    def __record(self, __prompt: str):
        self.__full_prompt += __prompt

    def __read(self) -> str:
        return self.__response.choices[0].text.strip()

    async def __predict(self, __prompt: str):
        self.__record(f"{self.__config.user_name}: {__prompt}\n{self.__config.ai_name}:")
        self.__response = await openai.Completion.acreate(
            engine=self.__config.engine_name,
            prompt=self.__full_prompt,
            temperature=self.__config.temperature,
            max_tokens=self.__config.max_tokens,
            top_p=self.__config.top_p,
            frequency_penalty=self.__config.frequency_penalty,
            presence_penalty=self.__config.presence_penalty,
            stop=[f'{self.__config.user_name}:', f'{self.__config.ai_name}:'],
        )

        self.__record(f" {self.__read()}\n")

        print(self.__full_prompt)
        print("=====================================")

    async def process(self, __message: str) -> str:
        await self.__predict(__message)
        return f"{self.__config.user_name}: {__message}\n{self.__config.ai_name}: {self.__read()}"

    def clear(self):
        self.__full_prompt = self.__config.formatted_prompt
        self.__response = None
