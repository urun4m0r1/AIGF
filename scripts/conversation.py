import re
import openai
from discord import app_commands

from scripts.config import AppConfig

class OpenAIConversation:
    def __init__(self, config: AppConfig):
        self._config = config

        openai.organization = config.open_ai_organization_id
        openai.api_key = config.open_ai_api_key

        self.prompt = None
        self.history = self._cache.load_history()

        self.initialize_prompt()

    def initialize_prompt(self):
        self.prompt = self._config.default_prompt.format(self._cache.user_name, self._cache.ai_name)

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

    def _save_history(self):
        self._cache.save_history(self.history)

    def record_history(self, history: str):
        # TODO: token 기반 rolling history 적용
        self.history += history
        self._save_history()

    def erase_history(self):
        self.history = ""
        self._save_history()

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
        self.initialize_prompt()

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