from typing import Optional

import discord


def parse_guilds(items: list) -> list:
    return [discord.Object(id=int(item[1])) for item in items]


def try_parse_int(text: Optional[str]) -> Optional[int]:
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def try_parse_float(text: Optional[str]) -> Optional[float]:
    try:
        return float(text)
    except (ValueError, TypeError):
        return None
