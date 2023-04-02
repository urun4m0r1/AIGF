import asyncio
import logging
from pathlib import Path

from colorama import Fore, Style

from scripts.bot import DiscordBot

logging.basicConfig(level=logging.INFO)

SETTINGS_PATH = Path('./settings.ini')
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


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        warning(
            "[System] Keyboard Interrupted.\n"
            "[System] Do not stop the bot with keyboard interrupt.\n"
            "[System] Please press enter to stop the bot properly."
        )
