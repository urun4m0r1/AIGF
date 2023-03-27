import openai
from discord import app_commands

from settings.config import AppConfig
from utils import file_io


class OpenAIConversation:
    def __init__(self, _config: AppConfig):
        self._config = _config
        self._cache = _config.cache

        openai.organization = self._config.organization_id
        openai.api_key = self._config.api_key

        self._full_prompt = self._config.prompt_history

    async def _predict(self) -> str:
        response = await openai.Completion.acreate(
            engine=self._config.engine_name,
            prompt=self._full_prompt,
            temperature=self._get_temperature(),
            max_tokens=self._config.max_tokens,  # TODO: dynamic_max_tokens 적용
            top_p=self._config.top_p,
            frequency_penalty=self._config.frequency_penalty,
            presence_penalty=self._config.presence_penalty,
            stop=[f'{self._cache.user_name}:', f'{self._cache.ai_name}:'],
        )

        return response.choices[0].text.strip()

    def _get_temperature(self) -> float:
        return self._cache.creativity / 4

    def _save_history(self):
        file_io.save_txt(self._config.prompt_history_path, self._full_prompt)

    async def predict_answer(self, message: str) -> str:
        self.record_prompt(f"{self._cache.user_name}: {message}\n{self._cache.ai_name}:")
        answer = await self._predict()
        self.record_prompt(f" {answer}\n")
        return answer

    def record_prompt(self, prompt: str):
        self._full_prompt += prompt  # TODO: rolling_prompt_record 적용
        self._save_history()

    def replace_prompt_text(self, old_text: str, new_text: str):
        self._full_prompt = self._full_prompt.replace(old_text, new_text)
        self._save_history()

    def replace_names(self, user_name: str, ai_name: str):
        self.replace_prompt_text(self._cache.user_name, user_name)
        self.replace_prompt_text(self._cache.ai_name, ai_name)
        self._cache.user_name = user_name
        self._cache.ai_name = ai_name
        self._cache.save()

    def reset_prompt(self):
        self._full_prompt = self._cache.get_initial_prompt()
        self._save_history()

    def change_creativity(self, creativity: int):
        self._cache.creativity = creativity
        self._cache.save()

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
