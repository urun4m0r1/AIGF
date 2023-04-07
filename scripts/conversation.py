import re

import openai

from data.history import History
from scripts.config import AppConfig

CREATIVITY_MAP = {
    0: 0.1,
    1: 0.3,
    2: 0.5,
    3: 0.7,
    4: 0.9,
}


class Conversation:
    def __init__(self, config: AppConfig, cache: History):
        self.config = config
        self.cache = cache

        openai.organization = config.open_ai_organization_id
        openai.api_key = config.open_ai_api_key

        self.scroll_amount = cache.settings.scrollAmount
        self.engine_name = cache.settings.engineName
        self.max_tokens = cache.settings.maxTokens
        self.top_p = cache.settings.topP
        self.frequency_penalty = cache.settings.frequencyPenalty
        self.presence_penalty = cache.settings.presencePenalty

    @property
    def user_name(self) -> str:
        return self.cache.get_sender_name('user')

    @property
    def ai_name(self) -> str:
        return self.cache.get_sender_name('ai')

    @property
    def prompt(self) -> str:
        return self.cache.get_full_prompt()

    @property
    def temperature(self) -> float:
        return CREATIVITY_MAP[self.creativity_level]

    @property
    def creativity_level(self) -> int:
        return self.cache.settings.creativityLevel

    @creativity_level.setter
    def creativity_level(self, value: int):
        self.cache.settings.creativityLevel = value

    @property
    def senders_swapped(self) -> bool:
        return self.cache.settings.sendersSwapped

    @senders_swapped.setter
    def senders_swapped(self, value: bool):
        self.cache.settings.sendersSwapped = value

    async def _predict(self) -> str:
        try:
            response = await openai.Completion.acreate(
                engine=self.engine_name,
                prompt=self.prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=[f'{self.user_name}:', f'{self.ai_name}:'],
            )
        except openai.error.InvalidRequestError as e:
            if e.user_message.startswith("This model's maximum context length is"):
                self._scroll_history()
                return await self._predict()

            raise e

        return response.choices[0].text.strip()

    def _scroll_history(self):
        print('[Conversation] Scrolling history...')
        self.cache.messages = self.cache.messages[self.scroll_amount:]

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

    async def predict_answer(self, message: str) -> str:
        self.record_history(f"\n{self.user_name}: {message}\n{self.ai_name}:")

        answer = await self._predict()
        self.record_history(f" {answer}\n")
        return answer

    def _save_history(self):
        self.cache.save_history(self.history)

    def record_history(self, history: str):
        # TODO: token 기반 rolling history 적용
        self.history += history
        self._save_history()

    def erase_history(self):
        self.history = ""
        self._save_history()

    def replace_history_text(self, old_text: str, new_text: str):
        self.history = self.history.replace(old_text, new_text)
        self._save_history()

    def replace_names(self, user_name: str, ai_name: str):
        self.replace_history_text(self.cache.user_name, user_name)
        self.replace_history_text(self.cache.ai_name, ai_name)
        self.cache.user_name = user_name
        self.cache.ai_name = ai_name
        self.cache.save_settings()
        self.initialize_prompt()

    def change_creativity(self, creativity: int):
        self.cache.creativity = creativity
        self.cache.save_settings()

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
