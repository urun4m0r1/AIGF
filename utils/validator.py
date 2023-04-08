from numbers import Real
from typing import Optional


def is_text(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip()


def is_int(value: Optional[Real]) -> bool:
    return isinstance(value, int)


def is_float(value: Optional[Real]) -> bool:
    return isinstance(value, float)


def is_between(value: Optional[Real], min_value: Real, max_value: Real,
               left_inclusive: bool = True,
               right_inclusive: bool = False) -> bool:
    if left_inclusive and right_inclusive:
        return is_between_ii(value, min_value, max_value)
    elif left_inclusive and not right_inclusive:
        return is_between_ie(value, min_value, max_value)
    elif not left_inclusive and right_inclusive:
        return is_between_ei(value, min_value, max_value)
    else:
        return is_between_ee(value, min_value, max_value)


def is_between_ii(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value <= value <= max_value


def is_between_ie(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value <= value < max_value


def is_between_ei(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value < value <= max_value


def is_between_ee(value: Optional[Real], min_value: Real, max_value: Real) -> bool:
    return isinstance(value, Real) and min_value < value < max_value
