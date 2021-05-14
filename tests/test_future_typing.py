# -*- coding: future_typing -*-
from typing import Literal


class C:
    def g(t: tuple[int]) -> tuple[int]:
        return t


def f(a: list[int] | dict[str, str], e: Literal["err"] | None = None) -> type[C]:
    x: set[str] = set()
    y: frozenset[str] = frozenset(["y1", "y2"])
    return C


def test_works():
    assert True
