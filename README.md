# future-typing
[![Tests](https://github.com/PrettyWood/future-typing/workflows/Tests/badge.svg)](https://github.com/PrettyWood/future-typing/actions)
[![codecov](https://codecov.io/gh/PrettyWood/future-typing/branch/main/graph/badge.svg)](https://codecov.io/gh/PrettyWood/future-typing)
[![pypi](https://img.shields.io/pypi/v/future-typing.svg)](https://pypi.python.org/pypi/future-typing)
[![versions](https://img.shields.io/pypi/pyversions/future-typing.svg)](https://github.com/PrettyWood/future-typing)
[![license](https://img.shields.io/github/license/PrettyWood/future-typing.svg)](https://github.com/PrettyWood/future-typing/blob/master/LICENSE)

Use generic type hints and new union syntax `|` with python 3.6+

If you just want to use new annotations for type checkers like `mypy`, then do not use this library
and simply add `from __future__ import annotations`.
But if you want to use those annotations at runtime, then you may be at the right place!

This library exposes:

- `transform_annotation`, which will transform `list[str|int|float]` into
  * `typing.List[typing.Union[str, int, float]]` for python 3.6 to 3.8
  * `list[typing.Union[str, int, float]]` for python 3.9 (since generic types are natively supported)

- a custom source code encoding `future_typing` that you can use to trigger the transformation at
  interpretation time

- a CLI to see the transformed source

## Installation

``` bash
    pip install future_typing
```

## Codec
Just add this custom source code encoding at the top of your file
```
# -*- coding: future_typing -*-
```

and then use `|` and `list[str]`, `dict[str, int]`, ... as if you were using `python 3.10`

```python
# -*- coding: future_typing -*-
from typing import Literal


class C:
    @staticmethod
    def g(t: tuple[int, ...]) -> tuple[int, ...]:
        return t


def f(a: list[str | int] | dict[str, str], b: Literal['pika'] | None = None) -> type[C]:
    x: set[str | int] = set(a)
    y: frozenset[str] = frozenset(['y1', 'y2'])
    t: tuple[int, ...] = (1, 2)
    print(f'it works! a: {a!r}, b: {b!r}')
    return C


f(['a', 'b', 1], 'pika')
```

```console
$ python3.8 pika.py
it works! a: ['a', 'b'], b: 'pika'

$ mypy pika.py
Success: no issues found in 1 source file
```

## CLI
```console
$ future_typing pika.py
import typing as typing___
from typing import Literal


class C :
    @staticmethod
    def g (t :typing___.Tuple [int ,...])->typing___.Tuple [int ,...]:
        return t


def f (a :typing___.Union [typing___.List [typing___.Union [str ,int ]],typing___.Dict [str ,str ]],b :typing___.Union [Literal ['pika'],None ]=None )->typing___.Type [C ]:
    x :typing___.Set [typing___.Union [str ,int ]]=set (a )
    y :typing___.FrozenSet [str ]=frozenset (['y1','y2'])
    t :typing___.Tuple [int ,...]=(1 ,2 )
    print (f'it works! a: {a!r}, b: {b!r}')
    return C


f (['a','b',1 ],'pika')
```
