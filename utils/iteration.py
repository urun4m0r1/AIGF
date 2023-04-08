from typing import Iterable, Any, Iterator


def trim(elements: Iterable[Any]) -> Iterator[Any]:
    for element in elements:
        if element:
            yield element
