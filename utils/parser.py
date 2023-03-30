from typing import Optional, List, Type, Union

import discord

Number = Type[Union[int, float]]


def parse_session_list(value: str) -> List[int]:
    """Parse a string containing session list and return a list of integers."""
    return [int(item) for item in value.strip().splitlines() if item]


def parse_guilds(items: List[str]) -> List[discord.Object]:
    """Convert a list of strings to a list of discord.Object instances."""
    return [discord.Object(id=int(item)) for item in items]


def try_parse_number(text: Optional[str], number_type: Number) -> Optional[Number]:
    """Attempt to parse a number from a string, returning None if not possible."""
    return number_type(text) if text is not None and text.isnumeric() else None


def try_parse_int(text: Optional[str]) -> Optional[int]:
    """Attempt to parse an integer from a string, returning None if not possible."""
    return try_parse_number(text, int)


def try_parse_float(text: Optional[str]) -> Optional[float]:
    """Attempt to parse a float from a string, returning None if not possible."""
    return try_parse_number(text, float)
