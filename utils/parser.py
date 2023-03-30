from typing import Optional, Type, Union, Iterable

from discord import Object as DiscordObject

Number = Type[Union[int, float]]


def parse_session_list(value: str) -> Iterable[int]:
    """Parse a string containing session list and return a list of integers."""
    for item in value.strip().splitlines():
        session_id = try_parse_int(item)
        if session_id is not None:
            yield session_id


def parse_guilds(items: Iterable[str]) -> Iterable[DiscordObject]:
    """Convert a list of text to a list of discord.Object instances."""
    for item in items:
        object_id = try_parse_int(item)
        if object_id is not None:
            yield DiscordObject(id=object_id)


def try_parse_number(text: Optional[str], number_type: Number) -> Optional[Number]:
    """Attempt to parse a number from a string, returning None if not possible."""
    return number_type(text) if text is not None and text.isnumeric() else None


def try_parse_int(text: Optional[str]) -> Optional[int]:
    """Attempt to parse an integer from a string, returning None if not possible."""
    return try_parse_number(text, int)


def try_parse_float(text: Optional[str]) -> Optional[float]:
    """Attempt to parse a float from a string, returning None if not possible."""
    return try_parse_number(text, float)
