import asyncio
import logging
from asyncio import Task
from typing import Any, Iterator, Tuple

import discord
from colorama import Fore, Style
from discord import app_commands, Object

from scripts.cache_manager import CacheManager
from scripts.config import AppConfig
from scripts.conversation import Conversation
from scripts.ko_kr import *
from utils.parser import try_parse_int


# TODO: 인격 슬롯 3개 변경 가능하게 추가
# TODO: 리롤 버튼 추가
# TODO: AI랑 순서 바꾸는 기능 추가

def info(message: str) -> None:
    logging.info(f"{Fore.WHITE}{Style.BRIGHT}{message}{Style.RESET_ALL}")


class DiscordBot(discord.Client):
    def __init__(self, config: AppConfig) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.config = config

        self._tree = app_commands.CommandTree(self)
        self._command = self._tree.command
        self._guilds = list(self.initialize_guilds())

        self.cache_manager = CacheManager(config)
        self.conversations = dict(self.initialize_conversations())

        self._add_events()
        self._add_commands()

    def get_conversation(self, interaction: discord.Interaction):
        session_id = str(interaction.channel_id)
        if session_id in self.conversations:
            return self.conversations[session_id]
        else:
            cache = self.cache_manager.get(str(session_id))
            conversation = Conversation(self.config, self.cache_manager, cache)
            self.conversations[session_id] = conversation
            return conversation

    def initialize_conversations(self) -> Iterator[Tuple[str, Conversation]]:
        for cache in self.cache_manager.get_all():
            session = cache.conversation_model.session
            yield session.id, Conversation(self.config, self.cache_manager, cache)

    def initialize_guilds(self) -> Iterator[Object]:
        for guild in self.config.server_guilds:
            obj_id = try_parse_int(guild)
            if obj_id is not None:
                obj = Object(id=obj_id)
                yield obj

    def create_run_task(self) -> Task:
        return asyncio.create_task(self.start_infinite_loop())

    def create_exit_task(self) -> Task:
        return asyncio.create_task(self.wait_for_exit())

    async def start_infinite_loop(self) -> None:
        info("[System] Initializing Discord Bot...")
        await self.start(self.config.discord_bot_token)

        info("[System] Discord Bot terminated.")

    async def wait_for_exit(self) -> None:
        message = "[System] Press Enter to exit bot..."
        await asyncio.to_thread(input, f'{message}\n')

        info("[System] Changing presence to offline...")
        await self.change_presence(status=discord.Status.offline)

        info("[System] Stopping Discord Bot...")
        await self.close()

        info("[System] Discord Bot stopped.")

    def _add_events(self) -> None:
        @self.event
        async def on_ready() -> None:
            info("[Event] Changing presence to online...")
            await self.change_presence(status=discord.Status.online, activity=None)

            info("[Event] Syncing server commands...")
            for guild in self._guilds:
                try:
                    info(f"[Event] Syncing commands in '{guild.id}'...")
                    await self._tree.sync(guild=guild)
                except discord.errors.Forbidden:
                    info(f"[Event] Failed to sync commands in '{guild.id}' due to insufficient permissions.")

            info("[Event] Discord Bot is ready.")

        @self.event
        async def on_error(event_method: str, /, *args: Any, **kwargs: Any) -> None:
            logging.exception(f"[Event] Error occurred in '{event_method}' event.")
            logging.error(f"[Event] Args: {args}")
            logging.error(f"[Event] Kwargs: {kwargs}")

    def _add_commands(self) -> None:
        def get_styles(category: str) -> Iterator[str]:
            for trait in self.cache_manager.default_history.prompt_model.traits:
                if trait.category == category:
                    for choice in trait.choices:
                        yield choice.style

        def get_choices(category: str) -> list[app_commands.Choice]:
            return list(app_commands.Choice(name=style, value=style) for style in get_styles(category))

        def get_categories() -> Iterator[str]:
            for trait in self.cache_manager.default_history.prompt_model.traits:
                yield trait.category

        categories = list(get_categories())
        choices = {category: get_choices(category) for category in categories}

        decorator_message = self._command(name=MESSAGE, description=MESSAGE_DESC, guilds=self._guilds)
        decorator_retry = self._command(name=RETRY, description=RETRY_DESC, guilds=self._guilds)
        decorator_record = self._command(name=RECORD, description=RECORD_DESC, guilds=self._guilds)
        decorator_replace = self._command(name=REPLACE, description=REPLACE_DESC, guilds=self._guilds)
        decorator_rename = self._command(name=RENAME, description=RENAME_DESC, guilds=self._guilds)
        decorator_swap = self._command(name=SWAP, description=SWAP_DESC, guilds=self._guilds)
        decorator_clear = self._command(name=CLEAR, description=CLEAR_DESC, guilds=self._guilds)
        decorator_reset = self._command(name=RESET, description=RESET_DESC, guilds=self._guilds)
        decorator_config = self._command(name=CONFIG, description=CONFIG_DESC, guilds=self._guilds)

        decorator_message_describe = app_commands.describe(message=MESSAGE_ARGS_1)
        decorator_replace_describe = app_commands.describe(before=REPLACE_ARGS_1, after=REPLACE_ARGS_2)
        decorator_rename_describe = app_commands.describe(user_name=RENAME_ARGS_1, ai_name=RENAME_ARGS_2)

        decorator_config_describe = app_commands.describe(
            title=CONFIG_ARGS_1,
            **{category: category for category in categories}
        )

        decorator_config_choices = app_commands.choices(**choices)

        @decorator_message
        @decorator_message_describe
        async def _send_message(interaction: discord.Interaction,
                                message: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Receiving message...")

            # noinspection PyUnresolvedReferences
            await interaction.response.defer()
            (question, answer) = await conversation.predict_answer(message)
            result = conversation.format_message(question, answer)
            await interaction.followup.send(result)

            info("[Command] Message sent.")

        @decorator_retry
        async def _retry_predict(interaction: discord.Interaction) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Retrying prediction...")

            # noinspection PyUnresolvedReferences
            await interaction.response.defer()
            (question, answer) = await conversation.re_predict_last()
            result = conversation.format_message(question, answer)
            await interaction.followup.send(result)

        decorator_record_describe = app_commands.describe(prompt=RECORD_ARGS_1)

        @decorator_record
        @decorator_record_describe
        async def _record_prompt(interaction: discord.Interaction,
                                 prompt: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Recording message...")

            conversation.record_prompt(prompt)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[프롬프트가 기록되었습니다]\n{prompt}")

        @decorator_replace
        @decorator_replace_describe
        async def _replace_prompt_text(interaction: discord.Interaction,
                                       before: str, after: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Replacing words...")

            conversation.replace_text(before, after)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[단어를 치환했습니다]\n{before} -> {after}")

        @decorator_rename
        @decorator_rename_describe
        async def _replace_names(interaction: discord.Interaction,
                                 user_name: str, ai_name: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Renaming...")

            previous_user = conversation.user_name
            previous_ai = conversation.ai_name
            conversation.replace_names(user_name, ai_name)

            message = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {user_name}
        - 상대: {previous_ai} -> {ai_name}"""
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)

        @decorator_swap
        async def _swap_names(interaction: discord.Interaction) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Swapping...")

            previous_user = conversation.user_name
            previous_ai = conversation.ai_name
            conversation.swap_names()

            message = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {previous_ai}
        - 상대: {previous_ai} -> {previous_user}"""
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)

        @decorator_clear
        async def _reset_prompt(interaction: discord.Interaction) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Clearing conversation...")

            conversation.erase_messages()
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[대화 내용이 비워졌습니다]")

        @decorator_reset
        async def _reset_config(interaction: discord.Interaction) -> None:
            info("[Command] Resetting self.config...")

            self.cache_manager.remove_cache(str(interaction.guild_id))
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[모든 설정이 초기화되었습니다]")

        @decorator_config
        @decorator_config_describe
        @decorator_config_choices
        async def _config(interaction: discord.Interaction,
                          title: str = None,
                          creativity: str = None,
                          intelligence: str = None,
                          characteristic: str = None,
                          mood: str = None,
                          reputation: str = None,
                          age: str = None,
                          relationship: str = None) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Changing self.config...")

            content = ""
            if title is not None:
                content += f"- 호칭: {title}\n"
            if creativity is not None:
                content += f"- 창의력: {choices['creativity'][creativity]}\n"
            if intelligence is not None:
                content += f"- 지능: {choices['intelligence'][intelligence]}\n"
            if characteristic is not None:
                content += f"- 성격: {choices['characteristic'][characteristic]}\n"
            if mood is not None:
                content += f"- 기분: {choices['mood'][mood]}\n"
            if reputation is not None:
                content += f"- 평판: {choices['reputation'][reputation]}\n"
            if age is not None:
                content += f"- 나이: {choices['age'][age]}\n"
            if relationship is not None:
                content += f"- 관계: {choices['relationship'][relationship]}\n"

            message = f"[설정이 변경되었습니다]\n{content}"
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)
