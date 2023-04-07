import asyncio
import logging
from asyncio import Task
from pathlib import Path
from typing import Any

import discord
from colorama import Fore, Style
from discord import app_commands

from scripts import conversation as conv
from scripts.config import AppConfig


# TODO: 인격 슬롯 3개 변경 가능하게 추가
# TODO: 리롤 버튼 추가
# TODO: AI랑 순서 바꾸는 기능 추가

def info(message: str) -> None:
    logging.info(f"{Fore.WHITE}{Style.BRIGHT}{message}{Style.RESET_ALL}")


class DiscordBot(discord.Client):
    def __init__(self, settings_path: Path, session_id: int) -> None:
        self.settings_path = settings_path
        self.session_id = session_id

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        self.config = AppConfig(self.settings_path)
        self.cache = self.config.get_or_create_cache(self.session_id)
        self.ai = conv.OpenAIConversation(self.config, self.cache)

        self.add_events()
        self.add_commands()

    def create_run_task(self) -> Task:
        info("[System] Initializing Discord Bot...")
        return asyncio.create_task(self.start(self.config.bot_token))

    def create_exit_task(self) -> Task:
        message = "[System] Press Enter to exit bot..."
        return asyncio.create_task(self.wait_for_exit(message))

    async def wait_for_exit(self, message: str) -> None:
        await asyncio.to_thread(input, f'{message}\n')
        await self.stop_bot()

    async def stop_bot(self) -> None:
        info("[System] Changing presence to offline...")
        await self.change_presence(status=discord.Status.offline)

        info("[System] Stopping Discord Bot...")
        await self.close()

        info("[System] Discord Bot stopped.")

    def format_message(self, message: str, answer: str) -> str:
        user_name = self.cache.user_name
        ai_name = self.cache.ai_name
        return f"**{user_name}**: {message}\n**{ai_name}**: {answer}"

    def reset_config(self) -> None:
        self.config.remove_cache(self.session_id)

        self.config = AppConfig(self.settings_path)
        self.cache = self.config.get_or_create_cache(self.session_id)
        self.ai = conv.OpenAIConversation(self.config, self.cache)

    def add_events(self) -> None:
        @self.event
        async def on_ready() -> None:
            info("[Event] Changing presence to online...")
            await self.change_presence(status=discord.Status.online, activity=None)

            info("[Event] Syncing server commands...")
            for guild in self.config.server_guilds:
                try:
                    info(f"[Event] Syncing commands in '{guild.id}'...")
                    await self.tree.sync(guild=guild)
                except discord.errors.Forbidden:
                    info(f"[Event] Failed to sync commands in '{guild.id}' due to insufficient permissions.")

            info("[Event] Discord Bot is ready.")

        @self.event
        async def on_error(event_method: str, /, *args: Any, **kwargs: Any) -> None:
            logging.exception(f"[Event] Error occurred in '{event_method}' event.")
            logging.error(f"[Event] Args: {args}")
            logging.error(f"[Event] Kwargs: {kwargs}")

    def add_commands(self) -> None:
        @self.tree.command(
            name="대화",
            description="인공지능과 대화",
            guilds=self.config.server_guilds
        )
        @app_commands.describe(
            message="메시지"
        )
        async def _send_message(
                interaction: discord.Interaction,
                message: str
        ) -> None:
            info("[Command] Receiving message...")

            # noinspection PyUnresolvedReferences
            await interaction.response.defer()
            answer = await self.ai.predict_answer(message)
            await interaction.followup.send(self.format_message(message, answer))

            info("[Command] Message sent.")

        @self.tree.command(
            name="기록",
            description="대화 마지막에 이어서 문장을 삽입",
            guilds=self.config.server_guilds
        )
        @app_commands.describe(
            prompt="프롬프트"
        )
        async def _record_prompt(
                interaction: discord.Interaction,
                prompt: str
        ) -> None:
            info("[Command] Recording message...")

            self.ai.record_history(f"\n{prompt}\n\n")
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[프롬프트가 기록되었습니다]\n{prompt}")

        @self.tree.command(
            name="바꾸기",
            description="모든 대화에서 특정 단어를 치환",
            guilds=self.config.server_guilds
        )
        @app_commands.describe(
            before="기존 단어",
            after="새 단어"
        )
        async def _replace_prompt_text(
                interaction: discord.Interaction,
                before: str,
                after: str
        ) -> None:
            info("[Command] Replacing words...")

            self.ai.replace_history_text(before, after)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(f"[단어를 치환했습니다]\n{before} -> {after}")

        @self.tree.command(
            name="이름",
            description="이름 변경",
            guilds=self.config.server_guilds
        )
        @app_commands.describe(
            user_name="당신 이름",
            ai_name="상대 이름"
        )
        async def _replace_names(
                interaction: discord.Interaction,
                user_name: str,
                ai_name: str
        ) -> None:
            info("[Command] Renaming...")

            previous_user = self.cache.user_name
            previous_ai = self.cache.ai_name
            self.ai.replace_names(user_name, ai_name)

            message = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {user_name}
        - 상대: {previous_ai} -> {ai_name}"""
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)

        @self.tree.command(
            name="스왑",
            description="이름 스왑",
            guilds=self.config.server_guilds
        )
        async def _swap_names(interaction: discord.Interaction) -> None:
            info("[Command] Swapping...")

            previous_user = self.cache.user_name
            previous_ai = self.cache.ai_name
            self.ai.replace_names("TEMP", previous_user)
            self.ai.replace_names(previous_ai, previous_user)

            message = f"""[이름이 변경되었습니다]
        - 당신: {previous_user} -> {previous_ai}
        - 상대: {previous_ai} -> {previous_user}"""
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)

        @self.tree.command(
            name="정리",
            description="대화 내용 비우기",
            guilds=self.config.server_guilds
        )
        async def _reset_prompt(interaction: discord.Interaction) -> None:
            info("[Command] Clearing conversation...")

            self.ai.erase_history()
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[대화 내용이 비워졌습니다]")

        @self.tree.command(
            name="초기화",
            description="설정 초기화",
            guilds=self.config.server_guilds
        )
        async def _reset_config(interaction: discord.Interaction) -> None:
            info("[Command] Resetting self.config...")

            self.reset_config()
            self.ai.erase_history()
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message("[모든 설정이 초기화되었습니다]")

        @self.tree.command(
            name="설정",
            description="설정 변경 (아직 창의력 빼고 작동 안함)",
            guilds=self.config.server_guilds
        )
        @app_commands.describe(
            creativity="창의력",
            intelligence="지능",
            personality="성격",
            mood="기분",
            reputation="평판",
            age="나이",
            relationship="관계",
            title="호칭",
            extra="추가 설정"
        )
        @app_commands.choices(
            creativity=conv.creativities,
            intelligence=conv.intelligences,
            personality=conv.persornalities,
            mood=conv.moods,
            reputation=conv.reputations,
            age=conv.ages,
            relationship=conv.relationships
        )
        async def _config(
                interaction: discord.Interaction,
                creativity: int = None,
                intelligence: int = None,
                personality: int = None,
                mood: int = None,
                reputation: int = None,
                age: int = None,
                relationship: int = None,
                title: str = None,
                extra: str = None
        ) -> None:
            info("[Command] Changing self.config...")

            content = ""
            if creativity is not None:
                self.ai.change_creativity(creativity)
                content += f"- 창의력: {conv.creativities[creativity].name}\n"
            if intelligence is not None:
                self.ai.change_intelligence(intelligence)
                content += f"- 지능: {conv.intelligences[intelligence].name}\n"
            if personality is not None:
                self.ai.change_personality(personality)
                content += f"- 성격: {conv.persornalities[personality].name}\n"
            if mood is not None:
                self.ai.change_mood(mood)
                content += f"- 기분: {conv.moods[mood].name}\n"
            if reputation is not None:
                self.ai.change_reputation(reputation)
                content += f"- 평판: {conv.reputations[reputation].name}\n"
            if age is not None:
                self.ai.change_age(age)
                content += f"- 나이: {conv.ages[age].name}\n"
            if relationship is not None:
                self.ai.change_relationship(relationship)
                content += f"- 관계: {conv.relationships[relationship].name}\n"
            if title is not None:
                self.ai.change_title(title)
                content += f"- 호칭: {title}\n"
            if extra is not None:
                self.ai.change_extra(extra)
                content += f"- 추가 설정: {extra}\n"

            message = f"[설정이 변경되었습니다]\n{content}"
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(message)
