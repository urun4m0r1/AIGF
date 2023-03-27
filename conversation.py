import openai
from config import AppConfig
from discord import app_commands


class OpenAIConversation:
    def __init__(self, __config: AppConfig):
        self.__config = __config
        openai.organization = self.__config.organization_id
        openai.api_key = self.__config.api_key

        self.__full_prompt = self.__config.formatted_prompt
        self.__response = None

    def __record(self, __prompt: str):
        self.__full_prompt += __prompt # TODO: rolling_prompt_record 적용

    def __read(self) -> str:
        return self.__response.choices[0].text.strip()

    async def __predict(self, __prompt: str):
        self.__record(f"{self.__config.user_name}: {__prompt}\n{self.__config.ai_name}:")
        self.__response = await openai.Completion.acreate(
            engine=self.__config.engine_name,
            prompt=self.__full_prompt,
            temperature=self.__config.temperature,
            max_tokens=self.__config.max_tokens, # TODO: dynamic_max_tokens 적용
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

    def replace_name(self, __user_name: str, __ai_name: str):
        self.__full_prompt = self.__full_prompt.replace(self.__config.user_name, __user_name)
        self.__full_prompt = self.__full_prompt.replace(self.__config.ai_name, __ai_name)
        self.__config.user_name = __user_name
        self.__config.ai_name = __ai_name

    def clear(self):
        self.__full_prompt = self.__config.formatted_prompt
        self.__response = None

    def change_creativity(self, creativity: int):
        self.__config.temperature = creativity / 4

    # TODO: 기능 구현
    def change_intelligence(self, intelligence: int):
        pass

    def change_personality(self, personality: int):
        pass

    def change_mood(self, mood: int):
        pass

    def change_reputation(self, reputation: int):
        pass

    def change_age(self, age: int):
        pass

    def change_relationship(self, relationship: int):
        pass

    def change_title(self, title: str):
        pass

    def change_extra(self, extra: str):
        pass


creativities = [
    app_commands.Choice(name="고지식함", value=0),
    app_commands.Choice(name="단순함", value=1),
    app_commands.Choice(name="폄범함", value=2),
    app_commands.Choice(name="창의적임", value=3),
    app_commands.Choice(name="나사풀린", value=4),
]

intelligences = [
    app_commands.Choice(name="멍청함", value=0),
    app_commands.Choice(name="평범함", value=1),
    app_commands.Choice(name="지적임", value=2),
]

persornalities = [
    app_commands.Choice(name="평범함", value=0),
    app_commands.Choice(name="츤데레", value=1),
    app_commands.Choice(name="얀데레", value=2),
    app_commands.Choice(name="쿨데레", value=3),
    app_commands.Choice(name="메가데레", value=4),
]

moods = [
    app_commands.Choice(name="평범함", value=0),
    app_commands.Choice(name="기쁨", value=1),
    app_commands.Choice(name="슬픔", value=2),
    app_commands.Choice(name="화남", value=3),
    app_commands.Choice(name="놀람", value=4),
    app_commands.Choice(name="무표정", value=5),
]

reputations = [
    app_commands.Choice(name="평범함", value=0),
    app_commands.Choice(name="영웅", value=1),
    app_commands.Choice(name="불한당", value=2),
]

ages = [
    app_commands.Choice(name="유아", value=0),
    app_commands.Choice(name="청소년", value=1),
    app_commands.Choice(name="사춘기", value=2),
    app_commands.Choice(name="대학생", value=3),
    app_commands.Choice(name="성인", value=4),
]

relationships = [
    app_commands.Choice(name="평범함", value=0),
    app_commands.Choice(name="소꿉친구", value=1),
    app_commands.Choice(name="여동생", value=2),
    app_commands.Choice(name="썸녀", value=3),
    app_commands.Choice(name="연인", value=4),
    app_commands.Choice(name="후배", value=5),
    app_commands.Choice(name="선배", value=6),
    app_commands.Choice(name="엄마", value=7),
    app_commands.Choice(name="딸", value=8),
    app_commands.Choice(name="선생님", value=9),
]
