import asyncio

from scripts.bot import DiscordBot

SETTINGS_PATH = './settings.ini'
SESSION_ID = 0


def print_warning(text: str):
    print(f"\033[31m{text}")


async def main():
    async with DiscordBot(SETTINGS_PATH, SESSION_ID) as discord_bot:
        run_task = discord_bot.create_run_task()
        exit_task = discord_bot.create_exit_task()

        await asyncio.gather(run_task, exit_task)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("[System] Keyboard Interrupted.")
        print_warning("[System] Do not stop the bot with keyboard interrupt.")
        print_warning("[System] Please press enter to stop the bot properly.")
