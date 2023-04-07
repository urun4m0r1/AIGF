import asyncio
import logging
from pathlib import Path

from colorama import Fore, Style

from scripts.bot import DiscordBot
from scripts.config import AppConfig

logging.basicConfig(level=logging.INFO)

CONFIG_PATH = Path('./config.ini')


def warning(message: str) -> None:
    logging.warning(f"{Fore.YELLOW}{Style.BRIGHT}{message}{Style.RESET_ALL}")


async def main(app_config: AppConfig) -> None:
    async with DiscordBot(app_config) as discord_bot:
        tasks = [
            discord_bot.create_run_task(),
            discord_bot.create_exit_task()
        ]

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        config = AppConfig(CONFIG_PATH)
        asyncio.run(main(config))
    except KeyboardInterrupt:
        warning(
            "[System] Keyboard Interrupted.\n"
            "[System] Do not stop the bot with keyboard interrupt.\n"
            "[System] Please press enter to stop the bot properly."
        )
