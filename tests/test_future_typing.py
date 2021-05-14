# -*- coding: future_typing -*-
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class C:
    def g(t: tuple[int]) -> tuple[int]:
        return t


def f(a: list[int] | dict[str, str], e: Literal["err"] | None = None) -> type[C]:
    x: set[str] = set()
    y: frozenset[str] = frozenset(["y1", "y2"])
    return C


def test_works():
    assert True
