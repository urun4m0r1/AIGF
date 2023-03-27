from typing import Optional


def is_text(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip() != ''


def is_int(value: Optional[int]) -> bool:
    return isinstance(value, int)


def is_float(value: Optional[float]) -> bool:
    return isinstance(value, float)


def is_between_ii(value: Optional[int], min_range: int, max_value: int) -> bool:
    return is_int(value) and min_range <= value <= max_value


def is_between_ie(value: Optional[int], min_range: int, max_value: int) -> bool:
    return is_int(value) and min_range <= value < max_value


def is_between_ei(value: Optional[int], min_range: int, max_value: int) -> bool:
    return is_int(value) and min_range < value <= max_value


def is_between_ee(value: Optional[int], min_range: int, max_value: int) -> bool:
    return is_int(value) and min_range < value < max_value
