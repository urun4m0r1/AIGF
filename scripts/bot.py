import asyncio
import inspect
import logging
from asyncio import Task
from typing import Any, Iterator, Tuple

import discord
from colorama import Fore, Style
from discord import app_commands, Object, Interaction

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

    def get_conversation(self, interaction: Interaction):
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
        def log_callback(interaction: Interaction) -> None:
            info(f"[Callback] {inspect.stack()[1][3]} / {interaction.channel_id}")

        async def defer(interaction: Interaction) -> None:
            info(f"[Defer] {inspect.stack()[1][3]} / {interaction.channel_id}")
            # noinspection PyUnresolvedReferences
            await interaction.response.defer()

        async def follow(interaction: Interaction, message: str) -> None:
            info(f"[Follow] {inspect.stack()[1][3]} / {interaction.channel_id}")
            # noinspection PyUnresolvedReferences
            await interaction.followup.send(message)

        async def send(interaction: Interaction, message: str) -> None:
            info(f"[Send] {inspect.stack()[1][3]} / {interaction.channel_id}")
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)

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

        decorator_send = self._command(name=SEND, description=SEND_DESC, guilds=self._guilds)
        decorator_retry = self._command(name=RETRY, description=RETRY_DESC, guilds=self._guilds)
        decorator_record = self._command(name=RECORD, description=RECORD_DESC, guilds=self._guilds)
        decorator_replace = self._command(name=REPLACE, description=REPLACE_DESC, guilds=self._guilds)
        decorator_rename = self._command(name=RENAME, description=RENAME_DESC, guilds=self._guilds)
        decorator_swap = self._command(name=SWAP, description=SWAP_DESC, guilds=self._guilds)
        decorator_undo = self._command(name=UNDO, description=UNDO_DESC, guilds=self._guilds)
        decorator_clear = self._command(name=CLEAR, description=CLEAR_DESC, guilds=self._guilds)
        decorator_reset = self._command(name=RESET, description=RESET_DESC, guilds=self._guilds)
        decorator_config = self._command(name=CONFIG, description=CONFIG_DESC, guilds=self._guilds)

        decorator_send_describe = app_commands.describe(message=SEND_ARGS_1)
        decorator_record_describe = app_commands.describe(prompt=RECORD_ARGS_1)
        decorator_replace_describe = app_commands.describe(before=REPLACE_ARGS_1, after=REPLACE_ARGS_2)
        decorator_rename_describe = app_commands.describe(user=RENAME_ARGS_1, ai=RENAME_ARGS_2)
        decorator_config_describe = app_commands.describe(
            creativity=CONFIG_ARGS_1,
            characteristic=CONFIG_ARGS_2,
            relationship=CONFIG_ARGS_3
        )

        decorator_config_choices = app_commands.choices(**choices)

        @decorator_send
        @decorator_send_describe
        async def _message(interaction: Interaction, message: str) -> None:
            log_callback(interaction)

            await defer(interaction)

            conversation = self.get_conversation(interaction)
            prediction = await conversation.send(message)
            result = conversation.format_prediction(*prediction)

            await follow(interaction, result)

        @decorator_retry
        async def _retry(interaction: Interaction) -> None:
            log_callback(interaction)

            await defer(interaction)

            conversation = self.get_conversation(interaction)
            prediction = await conversation.retry()
            if prediction is None:
                await follow(interaction, "[다시 시도할 메시지가 없습니다]")
                return

            result = conversation.format_prediction(*prediction)

            await follow(interaction, result)

        @decorator_record
        @decorator_record_describe
        async def _record(interaction: Interaction, prompt: str) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            conversation.record(prompt)
            result = f"[프롬프트를 기록했습니다]\n({prompt})"

            await send(interaction, result)

        @decorator_replace
        @decorator_replace_describe
        async def _replace(interaction: Interaction, before: str, after: str) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            conversation.replace(before, after)
            result = f"[단어를 치환했습니다]\n{before} -> {after}"

            await send(interaction, result)

        @decorator_rename
        @decorator_rename_describe
        async def _rename(interaction: Interaction, user: str, ai: str) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            previous_user = conversation.user_name
            previous_ai = conversation.ai_name
            conversation.rename(user, ai)
            result = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {user}
        - 상대: {previous_ai} -> {ai}"""

            await send(interaction, result)

        @decorator_swap
        async def _swap(interaction: Interaction) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            previous_user = conversation.user_name
            previous_ai = conversation.ai_name
            conversation.swap()
            result = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {previous_ai}
        - 상대: {previous_ai} -> {previous_user}"""

            await send(interaction, result)

        @decorator_undo
        async def _undo(interaction: Interaction) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            result = conversation.undo()
            if result:
                result = f"[마지막 대화를 취소했습니다]\n{result}"
            else:
                result = "[취소할 내용이 없습니다]"

            await send(interaction, result)

        @decorator_clear
        async def _clear(interaction: Interaction) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            conversation.clear()
            result = "[대화 내용이 비워졌습니다]"

            await send(interaction, result)

        @decorator_reset
        async def _reset(interaction: Interaction) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            conversation.reset()
            result = "[모든 설정이 초기화되었습니다]"

            await send(interaction, result)

        @decorator_config
        @decorator_config_describe
        @decorator_config_choices
        async def _config(interaction: Interaction,
                          creativity: str = None,
                          characteristic: str = None,
                          relationship: str = None) -> None:
            log_callback(interaction)

            conversation = self.get_conversation(interaction)
            content = []

            if creativity is not None:
                conversation.change_creativity(creativity)
                content.append(f"- 창의성: {creativity}")
            if characteristic is not None:
                conversation.change_characteristic(characteristic)
                content.append(f"- 성격: {characteristic}")
            if relationship is not None:
                conversation.change_relationship(relationship)
                content.append(f"- 관계: {relationship}")

            result = '\n'.join(content)

            if not result:
                result = "[설정이 변경되지 않았습니다]"
            else:
                result = f"[설정이 변경되었습니다]\n{result}"

            await send(interaction, result)
