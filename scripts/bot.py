import asyncio
import logging
from asyncio import Task
from typing import Any, Iterator, Tuple

import discord
from colorama import Fore, Style
from discord import app_commands, Object

from data.conversation import Message
from scripts.cache_manager import CacheManager
from scripts.config import AppConfig
from scripts.conversation import Conversation
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
        guild_id = str(interaction.guild_id)
        if guild_id in self.conversations:
            return self.conversations[guild_id]
        else:
            cache = self.cache_manager.get(str(guild_id))
            conversation = Conversation(self.config, self.cache_manager, cache)
            self.conversations[guild_id] = conversation
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
        @self._command(
            name="대화",
            description="인공지능과 대화",
            guilds=self._guilds)
        @app_commands.describe(
            message="메시지")
        async def _send_message(
                interaction: discord.Interaction,
                message: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Receiving message...")

            # noinspection PyUnresolvedReferences
            await interaction.response.defer()
            (question, answer) = await conversation.predict_answer(message)
            result = conversation.format_message(question, answer)
            await interaction.followup.send(result)

            info("[Command] Message sent.")

        @self._command(
            name="재시도",
            description="마지막 대화를 다시 시도",
            guilds=self._guilds)
        async def _retry_predict(interaction: discord.Interaction) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Retrying prediction...")

            # noinspection PyUnresolvedReferences
            await interaction.response.defer()
            (question, answer) = await conversation.re_predict_last()
            result = conversation.format_message(question, answer)
            await interaction.followup.send(result)

        @self._command(
            name="기록",
            description="대화 마지막에 이어서 문장을 삽입",
            guilds=self._guilds)
        @app_commands.describe(
            prompt="프롬프트")
        async def _record_prompt(
                interaction: discord.Interaction,
                prompt: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Recording message...")

            conversation.record_prompt(prompt)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[프롬프트가 기록되었습니다]\n{prompt}")

        @self._command(
            name="바꾸기",
            description="모든 대화에서 특정 단어를 치환",
            guilds=self._guilds)
        @app_commands.describe(
            before="기존 단어",
            after="새 단어")
        async def _replace_prompt_text(
                interaction: discord.Interaction,
                before: str,
                after: str) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Replacing words...")

            conversation.replace_text(before, after)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[단어를 치환했습니다]\n{before} -> {after}")

        @self._command(
            name="이름",
            description="이름 변경",
            guilds=self._guilds)
        @app_commands.describe(
            user_name="당신 이름",
            ai_name="상대 이름")
        async def _replace_names(
                interaction: discord.Interaction,
                user_name: str,
                ai_name: str) -> None:
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

        @self._command(
            name="스왑",
            description="이름 스왑",
            guilds=self._guilds)
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

        @self._command(
            name="정리",
            description="대화 내용 비우기",
            guilds=self._guilds)
        async def _reset_prompt(interaction: discord.Interaction) -> None:
            conversation = self.get_conversation(interaction)
            info("[Command] Clearing conversation...")

            conversation.erase_messages()
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[대화 내용이 비워졌습니다]")

        @self._command(
            name="초기화",
            description="설정 초기화",
            guilds=self._guilds)
        async def _reset_config(interaction: discord.Interaction) -> None:
            info("[Command] Resetting self.config...")

            self.cache_manager.remove_cache(str(interaction.guild_id))
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[모든 설정이 초기화되었습니다]")

        # @self._command(
        #     name="설정",
        #     description="설정 변경 (아직 창의력 빼고 작동 안함)",
        #     guilds=self._guilds)
        # @app_commands.describe(
        #     creativity="창의력",
        #     intelligence="지능",
        #     personality="성격",
        #     mood="기분",
        #     reputation="평판",
        #     age="나이",
        #     relationship="관계",
        #     title="호칭",
        #     extra="추가 설정")
        # @app_commands.choices(
        #     creativity=conv.creativities,
        #     intelligence=conv.intelligences,
        #     personality=conv.persornalities,
        #     mood=conv.moods,
        #     reputation=conv.reputations,
        #     age=conv.ages,
        #     relationship=conv.relationships)
        # async def _config(
        #         interaction: discord.Interaction,
        #         creativity: int = None,
        #         intelligence: int = None,
        #         personality: int = None,
        #         mood: int = None,
        #         reputation: int = None,
        #         age: int = None,
        #         relationship: int = None,
        #         title: str = None,
        #         extra: str = None) -> None:
        #     conversation = self.get_conversation(interaction)
        #     info("[Command] Changing self.config...")
        #
        #     content = ""
        #     if creativity is not None:
        #         conversation.change_creativity(creativity)
        #         content += f"- 창의력: {conv.creativities[creativity].name}\n"
        #     if intelligence is not None:
        #         conversation.change_intelligence(intelligence)
        #         content += f"- 지능: {conv.intelligences[intelligence].name}\n"
        #     if personality is not None:
        #         conversation.change_personality(personality)
        #         content += f"- 성격: {conv.persornalities[personality].name}\n"
        #     if mood is not None:
        #         conversation.change_mood(mood)
        #         content += f"- 기분: {conv.moods[mood].name}\n"
        #     if reputation is not None:
        #         conversation.change_reputation(reputation)
        #         content += f"- 평판: {conv.reputations[reputation].name}\n"
        #     if age is not None:
        #         conversation.change_age(age)
        #         content += f"- 나이: {conv.ages[age].name}\n"
        #     if relationship is not None:
        #         conversation.change_relationship(relationship)
        #         content += f"- 관계: {conv.relationships[relationship].name}\n"
        #     if title is not None:
        #         conversation.change_title(title)
        #         content += f"- 호칭: {title}\n"
        #     if extra is not None:
        #         conversation.change_extra(extra)
        #         content += f"- 추가 설정: {extra}\n"
        #
        #     message = f"[설정이 변경되었습니다]\n{content}"
        #     # noinspection PyUnresolvedReferences
        #     await interaction.response.send_message(message)
