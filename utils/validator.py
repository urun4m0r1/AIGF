from typing import Optional
from numbers import Real


def is_text(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip()


def is_int(value: Optional[Real]) -> bool:
    return isinstance(value, int)


def is_float(value: Optional[Real]) -> bool:
    return isinstance(value, float)


def is_between_ii(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value <= value <= max_value


def is_between_ie(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value <= value < max_value


def is_between_ei(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value < value <= max_value


def is_between_ee(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value < value < max_value
