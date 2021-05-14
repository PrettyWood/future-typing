import sys
import types
import typing

import pytest

from future_typing.codec import decode

input = b"""\
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class C:
    l: list[int|str] = [1, 'q']

    def g(t: tuple[int]) -> tuple[int]:
        return t

def f(a: list[int] | dict[str, str], e: Literal['err'] | None = None) -> type[C]:
    x: set[str] = set()
    y: frozenset[str] = frozenset(['y1', 'y2'])
    return C
"""


def create_module(code, name):
    module = types.ModuleType(name)
    exec(code, module.__dict__)
    return module


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="requires < 3.10")
def test_decode():
    with pytest.raises(TypeError, match="TypeError: unsupported operand type(s) for |"):
        create_module(input, "mymod")

    mymod = create_module(decode(input)[0], "mymod")
    assert mymod.C.g((2, 3)) == (2, 3)

    if sys.version_info[:2] == (3, 9):
        assert mymod.C.__annotations__ == {"l": list[typing.Union[int, str]]}
    else:
        assert mymod.C.__annotations__ == {"l": typing.List[typing.Union[int, str]]}
