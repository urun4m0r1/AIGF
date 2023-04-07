import re
from datetime import datetime

import openai

from data.conversation import Message
from data.history import History
from scripts.cache_manager import CacheManager
from scripts.config import AppConfig

CREATIVITY_MAP = {
    0: 0.1,
    1: 0.3,
    2: 0.5,
    3: 0.7,
    4: 0.9,
}


class Conversation:
    def __init__(self, config: AppConfig, cache_manager: CacheManager, cache: History):
        self.config = config
        self.cache_manager = cache_manager
        self.cache = cache

        openai.organization = config.open_ai_organization_id
        openai.api_key = config.open_ai_api_key

        self.scroll_amount = cache.settings.scrollAmount
        self.engine_name = cache.settings.engineName
        self.max_tokens = cache.settings.maxTokens
        self.top_p = cache.settings.topP
        self.frequency_penalty = cache.settings.frequencyPenalty
        self.presence_penalty = cache.settings.presencePenalty

    def _save_cache(self):
        self.cache_manager.save_cache(self.cache)

    @property
    def user_name(self) -> str:
        return self.cache.get_sender_name('user')

    @user_name.setter
    def user_name(self, value: str):
        self.cache.participants[0].name = value
        self._save_cache()

    @property
    def ai_name(self) -> str:
        return self.cache.get_sender_name('ai')

    @ai_name.setter
    def ai_name(self, value: str):
        self.cache.participants[1].name = value
        self._save_cache()

    @property
    def prompt(self) -> str:
        return self.cache.get_prompt_history()

    @property
    def temperature(self) -> float:
        return CREATIVITY_MAP[self.cache.settings.creativityLevel]

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
        self._save_cache()

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

    def format_message(self, question: Message, answer: Message) -> str:
        return f"**{self.user_name}**: {question.text}\n**{self.ai_name}**: {answer.text}"

    async def predict_answer(self, message: str) -> (Message, Message):
        question = Message(sender='user', text=message, timestamp=datetime.now().isoformat())
        answer = Message(sender='ai', text='', timestamp='')

        self.cache.messages.append(question)
        self.cache.messages.append(answer)

        answer.text = await self._predict()
        answer.timestamp = datetime.now().isoformat()
        self._save_cache()

        return question, answer

    async def re_predict_last(self) -> (Message, Message):
        if len(self.cache.messages) == 0:
            return ''

        if self.cache.messages[-1].sender in ['user', 'text']:
            return ''

        self.cache.messages = self.cache.messages[:-1]

        answer = Message(sender='ai', text='', timestamp='')

        self.cache.messages.append(answer)

        answer.text = await self._predict()
        answer.timestamp = datetime.now().isoformat()
        self._save_cache()

        return self.cache.messages[-2], answer

    def record_prompt(self, message: str):
        prompt = Message(sender='text', text=message, timestamp=datetime.now().isoformat())

        self.cache.messages.append(prompt)
        self._save_cache()

    def erase_messages(self):
        self.cache.messages.clear()
        self._save_cache()

    def undo(self):
        if len(self.cache.messages) == 0:
            return

        last_message = self.cache.messages[-1]

        if last_message.sender == 'user':
            return

        elif last_message.sender == 'text':
            self.cache.messages = self.cache.messages[:-1]

        elif last_message.sender == 'ai':
            self.cache.messages = self.cache.messages[:-2]

        self._save_cache()

    def replace_text(self, old_text: str, new_text: str):
        for message in self.cache.messages:
            message.text = message.text.replace(old_text, new_text)

        self._save_cache()

    def swap_names(self):
        for message in self.cache.messages:
            message.text = message.text.replace(self.user_name, '{temp}')
            message.text = message.text.replace(self.ai_name, self.user_name)
            message.text = message.text.replace('{temp}', self.ai_name)

        self.user_name, self.ai_name = self.ai_name, self.user_name

        self._save_cache()

    def replace_names(self, user_name: str, ai_name: str):
        for message in self.cache.messages:
            message.text = message.text.replace(self.user_name, user_name)
            message.text = message.text.replace(self.ai_name, ai_name)

        self.user_name = user_name
        self.ai_name = ai_name

        self._save_cache()

    def change_creativity(self, creativity_level: int):
        self.cache.settings.creativityLevel = creativity_level

        self._save_cache()

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
