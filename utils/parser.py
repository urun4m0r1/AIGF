from typing import Optional, Type, Union

Number = Type[Union[int, float]]


def try_parse_number(text: Optional[str], number_type: Number) -> Optional[Number]:
    """Attempt to parse a number from a string, returning None if not possible."""
    return number_type(text) if text is not None and text.isnumeric() else None


def try_parse_int(text: Optional[str]) -> Optional[int]:
    """Attempt to parse an integer from a string, returning None if not possible."""
    return try_parse_number(text, int)


def try_parse_float(text: Optional[str]) -> Optional[float]:
    """Attempt to parse a float from a string, returning None if not possible."""
    return try_parse_number(text, float)
