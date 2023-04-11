import copy
import re
from datetime import datetime
from typing import Optional, Tuple

import openai

from data.conversation import Message
from data.history import History
from scripts.cache_manager import CacheManager
from scripts.config import AppConfig

TEMPERATURE_MAP = {
    "로봇": 0.0,
    "단순함": 0.3,
    "명확함": 0.5,
    "보통": 0.7,
    "융퉁성": 0.9,
    "창의적": 1.3,
    "헛소리": 1.5,
}


class Conversation:
    def __init__(self, config: AppConfig, cache_manager: CacheManager, cache: History) -> None:
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

    def _save_cache(self) -> None:
        self.cache_manager.save_cache(self.cache)

    @property
    def user_name(self) -> str:
        return self.cache.get_sender_name('user')

    @property
    def ai_name(self) -> str:
        return self.cache.get_sender_name('ai')

    @user_name.setter
    def user_name(self, value: str) -> None:
        self.cache.participants[0].name = value
        self._save_cache()

    @ai_name.setter
    def ai_name(self, value: str) -> None:
        self.cache.participants[1].name = value
        self._save_cache()

    @property
    def prompt(self) -> str:
        return self.cache.get_prompt_history()

    @property
    def temperature(self) -> float:
        for trait in self.cache.settings.traits:
            if trait.category == 'creativity':
                return TEMPERATURE_MAP[trait.style]

        return 0

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

    def _scroll_history(self) -> None:
        print('[Conversation] Scrolling history...')
        self.cache.messages = self.cache.messages[self.scroll_amount:]
        self._save_cache()

    @staticmethod
    def _parse_tokens_from_error(text: str) -> Tuple[int, int, int, int]:
        """This model's maximum context length is 4097 tokens, however you requested 10000 tokens (8976 in your prompt
        ; 1024 for the completion). Please reduce your prompt
        ; or completion length."""

        # extract max_tokens, current_tokens, prompt_tokens, and completion_tokens using regex
        max_tokens = int(re.search(r'maximum context length is (\d+)', text).group(1))
        current_tokens = int(re.search(r'requested (\d+) tokens', text).group(1))
        prompt_tokens = int(re.search(r'\((\d+) in your prompt', text).group(1))
        completion_tokens = int(re.search(r'; (\d+) for the completion', text).group(1))

        return max_tokens, current_tokens, prompt_tokens, completion_tokens

    def format_prediction(self, question: Message, answer: Message) -> str:
        return f"**{self.user_name}**: {question.text}\n**{self.ai_name}**: {answer.text}"

    async def send(self, message: str) -> Tuple[Message, Message]:
        question = Message(sender='user', text=message, timestamp=datetime.now().isoformat())
        answer = Message(sender='ai', text='', timestamp='')

        self.cache.messages.append(question)
        self.cache.messages.append(answer)

        answer.text = await self._predict()
        answer.timestamp = datetime.now().isoformat()
        self._save_cache()

        return question, answer

    async def retry(self) -> Optional[Tuple[Message, Message]]:
        if len(self.cache.messages) < 2:
            return None

        last_message = self.cache.messages[-1]

        if last_message.sender != 'ai':
            return None

        last_message.text = ''
        last_message.text = await self._predict()
        last_message.timestamp = datetime.now().isoformat()

        self._save_cache()

        return self.cache.messages[-2], last_message

    def record(self, message: str) -> None:
        prompt = Message(sender='text', text=message, timestamp=datetime.now().isoformat())

        self.cache.messages.append(prompt)
        self._save_cache()

    def replace(self, before: str, after: str) -> None:
        for message in self.cache.messages:
            message.text = message.text.replace(before, after)

        self._save_cache()

    def modify(self, message: str) -> Optional[Tuple[Message, Message]]:
        if len(self.cache.messages) < 1:
            return None

        last_message = self.cache.messages[-1]
        last_message_copy = copy.deepcopy(last_message)

        last_message.text = message
        self._save_cache()
        return last_message_copy, last_message

    def rename(self, user: str, ai: str) -> None:
        for message in self.cache.messages:
            message.text = message.text.replace(self.user_name, user)
            message.text = message.text.replace(self.ai_name, ai)

        self.cache.participants[0].name = user
        self.cache.participants[1].name = ai

        self._save_cache()

    def swap(self) -> None:
        prev_user = self.user_name
        prev_ai = self.ai_name

        for message in self.cache.messages:
            message.text = message.text.replace(prev_user, '{temp}')
            message.text = message.text.replace(prev_ai, prev_user)
            message.text = message.text.replace('{temp}', prev_ai)

        self.cache.participants[0].name = prev_ai
        self.cache.participants[1].name = prev_user

        self._save_cache()

    def undo(self) -> str:
        if len(self.cache.messages) == 0:
            return ''

        last_message = self.cache.messages[-1]

        if last_message.sender == 'user':
            return ''

        elif last_message.sender == 'text':
            self.cache.messages = self.cache.messages[:-1]
            self._save_cache()
            return f'~~({last_message.text})~~'

        elif last_message.sender == 'ai':
            last_user_message = self.cache.messages[-2]
            self.cache.messages = self.cache.messages[:-2]
            self._save_cache()
            return f"~~{self.format_prediction(last_user_message, last_message)}~~"

    def clear(self) -> None:
        self.cache.messages.clear()
        self._save_cache()

    def reset(self) -> None:
        session_id = self.cache.session.id
        self.cache = self.cache_manager.recreate(session_id)

    def print(self) -> str:
        return self.cache.get_full_messages()

    def debug(self) -> str:
        return self.cache.get_prompt_history()

    def change_creativity(self, creativity: str) -> None:
        for trait in self.cache.settings.traits:
            if trait.category == 'creativity':
                trait.style = creativity
                break

        self._save_cache()

    def change_characteristic(self, characteristic: str) -> None:
        for trait in self.cache.settings.traits:
            if trait.category == 'characteristic':
                trait.style = characteristic
                break

        self._save_cache()

    def change_relationship(self, relationship: str) -> None:
        for trait in self.cache.settings.traits:
            if trait.category == 'relationship':
                trait.style = relationship
                break

        self._save_cache()

