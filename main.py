import asyncio
import logging
from pathlib import Path

from colorama import Fore, Style

from data import prompt_parser, conversation_parser
from data.data_generator import PromptHistoryGenerator
from scripts.bot import DiscordBot
from utils.file_io import load_txt

logging.basicConfig(level=logging.INFO)

SETTINGS_PATH = Path('./settings.ini')
DEFAULT_PROMPT_PATH = Path('./data/prompt.txt')
PROMPT_MODEL_PATH = Path('./data/prompt.yaml')
DEFAULT_CONVERSATION_MODEL_PATH = Path('./data/conversation.yaml')
SESSION_ID = 0


def warning(message: str) -> None:
    logging.warning(f"{Fore.YELLOW}{Style.BRIGHT}{message}{Style.RESET_ALL}")


async def main() -> None:
    async with DiscordBot(SETTINGS_PATH, SESSION_ID) as discord_bot:
        tasks = [
            discord_bot.create_run_task(),
            discord_bot.create_exit_task()
        ]

        await asyncio.gather(*tasks)


def test_prompt_history_generator():
    default_prompt = load_txt(DEFAULT_PROMPT_PATH)
    prompt_model = prompt_parser.parse(PROMPT_MODEL_PATH)
    default_conversation_model = conversation_parser.parse(DEFAULT_CONVERSATION_MODEL_PATH)

    generator = PromptHistoryGenerator(default_prompt, prompt_model, default_conversation_model)

    conversation_model = conversation_parser.parse('./.cache/1234567890.yaml')
    generator.initialize(conversation_model)

    print(generator.get_prompt_history())


if __name__ == '__main__':
    test_prompt_history_generator()

    try:
        # asyncio.run(main())
        pass
    except KeyboardInterrupt:
        warning(
            "[System] Keyboard Interrupted.\n"
            "[System] Do not stop the bot with keyboard interrupt.\n"
            "[System] Please press enter to stop the bot properly."
        )
