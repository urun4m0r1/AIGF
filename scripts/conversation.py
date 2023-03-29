import re
import openai
from discord import app_commands

from settings.config import AppConfig
from settings.config_cache import ConfigCache


class OpenAIConversation:
    def __init__(self, config: AppConfig, cache: ConfigCache):
        self._config = config
        self._cache = cache

        openai.organization = config.organization_id
        openai.api_key = config.api_key

        self.prompt = self._cache.load_prompt_format()
        self.history = self._cache.load_history()

    async def _predict(self) -> str:
        try:
            response = await openai.Completion.acreate(
                engine=self._config.engine_name,
                prompt=f"{self.prompt}\n{self.history}",
                temperature=self._get_temperature(),
                max_tokens=self._config.max_tokens,
                top_p=self._config.top_p,
                frequency_penalty=self._config.frequency_penalty,
                presence_penalty=self._config.presence_penalty,
                stop=[f'{self._cache.user_name}:', f'{self._cache.ai_name}:'],
            )
        except openai.error.InvalidRequestError as e:
            if e.user_message.startswith("This model's maximum context length is"):
                self._scroll_history()
                return await self._predict()

            raise e

        return response.choices[0].text.strip()

    def _scroll_history(self):
        print('[Conversation] Scrolling history...')
        lines = self.history.splitlines()[self._config.scroll_amount:]
        self.history = '\n'.join(lines)

    @staticmethod
    def _parse_tokens_from_error(text: str):
        """This model's maximum context length is 4097 tokens, however you requested 10000 tokens (8976 in your prompt
        ; 1024 for the completion). Please reduce your prompt
        ; or completion length."""

        # extract max_tokens, current_tokens, prompt_tokens, and completion_tokens using regex
        max_tokens = int(re.search(r'maximum context length is (\d+)', text).group(1))
        current_tokens = int(re.search(r'requested (\d+) tokens', text).group(1))
        prompt_tokens = int(re.search(r'\((\d+) in your prompt', text).group(1))
        completion_tokens = int(re.search(r'; (\d+) for the completion', text).group(1))

        return max_tokens, current_tokens, prompt_tokens, completion_tokens

    def _get_temperature(self) -> float:
        return creativity_map[self._cache.creativity]

    def _save_prompt(self):
        self._cache.save_prompt(self.prompt)

    def _save_history(self):
        self._cache.save_history(self.history)

    def record_prompt(self, prompt: str):
        self.prompt += prompt
        self._save_prompt()

    def record_history(self, history: str):
        # TODO: token 기반 rolling history 적용
        self.history += history
        self._save_history()

    def erase_history(self):
        self.history = ""
        self._save_history()

    def erase_prompt(self):
        self.prompt = ""
        self._save_prompt()

    async def predict_answer(self, message: str) -> str:
        self.record_history(f"{self._cache.user_name}: {message}\n{self._cache.ai_name}:")

        answer = await self._predict()
        self.record_history(f" {answer}\n")
        return answer

    def replace_history_text(self, old_text: str, new_text: str):
        self.history = self.history.replace(old_text, new_text)
        self._save_history()

    def replace_names(self, user_name: str, ai_name: str):
        self.replace_history_text(self._cache.user_name, user_name)
        self.replace_history_text(self._cache.ai_name, ai_name)
        self._cache.user_name = user_name
        self._cache.ai_name = ai_name
        self._cache.save_settings()
        self.prompt = self._cache.load_prompt_format()

    def change_creativity(self, creativity: int):
        self._cache.creativity = creativity
        self._cache.save_settings()

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


creativity_map = {
    0: 0.1,
    1: 0.3,
    2: 0.5,
    3: 0.7,
    4: 0.9,
}

creativities = [
    app_commands.Choice(name="고지식함", value=0),
    app_commands.Choice(name="명확함", value=1),
    app_commands.Choice(name="평범함", value=2),
    app_commands.Choice(name="창의적임", value=3),
    app_commands.Choice(name="헛소리꾼", value=4),
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
