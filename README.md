# future-typing
[![Tests](https://github.com/PrettyWood/future-typing/workflows/Tests/badge.svg)](https://github.com/PrettyWood/future-typing/actions)
[![codecov](https://codecov.io/gh/PrettyWood/future-typing/branch/main/graph/badge.svg)](https://codecov.io/gh/PrettyWood/future-typing)
[![pypi](https://img.shields.io/pypi/v/future-typing.svg)](https://pypi.python.org/pypi/future-typing)
[![versions](https://img.shields.io/pypi/pyversions/future-typing.svg)](https://github.com/PrettyWood/future-typing)
[![license](https://img.shields.io/github/license/PrettyWood/future-typing.svg)](https://github.com/PrettyWood/future-typing/blob/master/LICENSE)

Backport for type hinting generics in standard collections and union types as X | Y

_(greatly inspired by [future-annotations](https://github.com/asottile/future-annotations)!)_

## Installation

``` bash
    pip install future_typing
```

## Usage
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


def f(a: list[str] | dict[str, object], b: Literal['pika'] | None = None) -> type[C]:
    x: set[str] = set(a)
    y: frozenset[str] = frozenset(['y1', 'y2'])
    t: tuple[int, int] = (1, 2)
    print(f'it works! a: {a!r}, b: {b!r}')
    return C


f(['a', 'b'], 'pika')
```

```console
$ python3.8 pika.py
it works! a: ['a', 'b'], b: 'pika'

$ mypy pika.py
Success: no issues found in 1 source file
```

## See transformed source
```console
$ python3.8 future_typing.py pika.py
# -*- coding: utf-8 -*-
import typing as typing___
from typing import Literal


class C :
    @staticmethod
    def g (t :typing___.Tuple [int ,...])->typing___.Tuple [int ,...]:
        return t


def f (a :typing___.Union [typing___.List [str ],typing___.Dict [str ,str ]],b :typing___.Union [Literal ['pika'],None ]=None )->typing___.Type [C ]:
    x :typing___.Set [str ]=set (a )
    t :typing___.Tuple [int ,...]=(1 ,2 )
    print (f'it works! a: {a!r}, b: {b!r}')
    return C


f (['a','b'],'pika')
```
