# -*- coding: future_typing -*-
from typing_extensions import Literal


class C:
    @staticmethod
    def g(t: tuple[int, ...]) -> tuple[int, ...]:
        return t


def f(a: list[str] | dict[str, str], b: Literal['pika'] | None = None) -> type[C]:
    x: set[str] = set(a)
    t: tuple[int, ...] = (1, 2)
    print(f'it works! a: {a!r}, b: {b!r}')
    return C


f(['a', 'b'], 'pika')
