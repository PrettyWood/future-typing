# -*- coding: future_typing -*-
import io
import sys
import typing
from tokenize import generate_tokens, NAME, NUMBER, OP, STRING

import pytest

import future_typing

try:
    get_args, get_origin = typing.get_args, typing.get_origin
except AttributeError:

    def get_args(tp):
        return getattr(tp, "__args__", ())

    def get_origin(tp):
        """Only Partial implementation of `get_origin` for 3.6 for test purpose"""
        typing_to_builtin_map = {
            typing.Dict: dict,
            typing.List: list,
        }

        origin = getattr(tp, "__origin__", None)
        return typing_to_builtin_map.get(origin, origin)


@pytest.mark.parametrize(
    "input_,output_",
    [
        ("str", "str"),
        ("list[str]", "list[str]"),
        ("str|int", "Union[str,int]"),
        ("str|int|float", "Union[Union[str,int],float]"),
        ("list[str|int|float]", "list[Union[Union[str,int],float]]"),
        ("dict[str,int]|float", "Union[dict[str,int],float]"),
        ("list[int | float]", "list[Union[int,float]]"),
        ("Literal['err']|None", "Union[Literal['err'],None]"),
        ("create(A, x=1, y='a') | None", "Union[create(A,x=1,y='a'),None]"),
    ],
)
def test_transform_union(input_, output_):
    all_tokens = generate_tokens(io.StringIO(input_).readline)
    tokens = [(t.type, t.string) for t in all_tokens if t.type in (NAME, NUMBER, OP, STRING)]
    new_tokens = future_typing.transform_union(tokens, union_name="Union")
    new_output = "".join(v for _, v in new_tokens)
    assert new_output == output_


input = b"""\
from typing import Literal

class C:
    def g(t: tuple[int]) -> tuple[int]:
        return t

def f(a: list[int] | dict[str, str], e: Literal['err'] | None = None) -> type[C]:
    x: set[str] = set()
    y: frozenset[str] = frozenset(['y1', 'y2'])
    return C
"""


@pytest.mark.skipif(sys.version_info[:2] != (3, 10), reason="requires 3.10")
def test_decode_3_10():
    import types

    assert future_typing.decode(input)[0] == (
        "from typing import Literal \n"
        "\n"
        "class C :\n"
        "    def g (t :tuple [int ])->tuple [int ]:\n"
        "        return t \n"
        "\n"
        "def f (a :list [int ]|dict [str ,str ],e :Literal ['err']|None =None )->type [C ]:\n"
        "    x :set [str ]=set ()\n"
        "    y :frozenset [str ]=frozenset (['y1','y2'])\n"
        "    return C \n"
    )

    assert get_origin(list[str]) is list
    assert get_args(list[str]) == (str,)
    assert get_origin(list[str] | dict[str, str]) is types.Union
    assert get_args(list[str] | dict[str, str]) == (list[str], dict[str, str])


@pytest.mark.skipif(sys.version_info[:2] != (3, 9), reason="requires 3.9")
def test_3_9():
    assert future_typing.decode(input)[0] == (
        "import typing as typing___ \n"
        "from typing import Literal \n"
        "\n"
        "class C :\n"
        "    def g (t :tuple [int ])->tuple [int ]:\n"
        "        return t \n"
        "\n"
        "def f (a :typing___.Union [list [int ],dict [str ,str ]],e :typing___.Union [Literal ['err'],None ]=None )->type [C ]:\n"
        "    x :set [str ]=set ()\n"
        "    y :frozenset [str ]=frozenset (['y1','y2'])\n"
        "    return C \n"
    )
    assert get_origin(list[str]) is list
    assert get_args(list[str]) == (str,)
    assert get_origin(list[str] | dict[str, str]) is typing.Union
    assert get_args(list[str] | dict[str, str]) == (list[str], dict[str, str])


@pytest.mark.skipif(sys.version_info[:2] >= (3, 9), reason="requires 3.8-")
def test_decode_3_6_to_8():
    assert future_typing.decode(input)[0] == (
        "import typing as typing___ \n"
        "from typing import Literal \n"
        "\n"
        "class C :\n"
        "    def g (t :typing___.Tuple [int ])->typing___.Tuple [int ]:\n"
        "        return t \n"
        "\n"
        "def f (a :typing___.Union [typing___.List [int ],typing___.Dict [str ,str ]],e :typing___.Union [Literal ['err'],None ]=None )->typing___.Type [C ]:\n"
        "    x :typing___.Set [str ]=set ()\n"
        "    y :typing___.FrozenSet [str ]=frozenset (['y1','y2'])\n"
        "    return C \n"
    )

    assert get_origin(list[str]) is list
    assert get_args(list[str]) == (str,)
    assert get_origin(list[str] | dict[str, str]) is typing.Union
    assert get_args(list[str] | dict[str, str]) == (typing.List[str], typing.Dict[str, str])
