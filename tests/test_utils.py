import sys

import pytest

from future_typing import transform_annotation


@pytest.mark.skipif(sys.version_info >= (3, 9), reason="3.6 to 3.8")
@pytest.mark.parametrize(
    "in_str,out_str",
    [
        (
            "str",
            "str"
        ),
        (
            "list[str]",
            "typing___.List[str]"
        ),
        (
            "str|int",
            "typing___.Union[str,int]"
        ),
        (
            "str|int|float",
            "typing___.Union[typing___.Union[str,int],float]"
        ),
        (
            "list[str|int|float]",
            "typing___.List[typing___.Union[typing___.Union[str,int],float]]",
        ),
        (
            "dict[str,int]|float",
            "typing___.Union[typing___.Dict[str,int],float]"
        ),
        (
            "Literal['err']|None",
            "typing___.Union[Literal['err'],None]"),
        (
            "create(A, x=1, y='a') | None",
            "typing___.Union[create(A,x=1,y='a'),None]"),
        (
            "Annotated[int | float, Constraints(ge=1)]",
            "Annotated[typing___.Union[int,float],Constraints(ge=1)]"
        ),
        (
            "Annotated[Literal['pika'] | list[str | bytes], Constraints(min_length=2, 'strict')]",
            "Annotated[typing___.Union[Literal['pika'],typing___.List[typing___.Union[str,bytes]]],Constraints(min_length=2,'strict')]"
        ),
        (
            "list[Annotated[str|bytes, Constraints(regex='[a-z]*')]]",
            "typing___.List[Annotated[typing___.Union[str,bytes],Constraints(regex='[a-z]*')]]"
        ),
        (
            "list[Annotated[dict[str, str], 'strict']]",
            "typing___.List[Annotated[typing___.Dict[str,str],'strict']]"
        ),
    ],
)
def test_transform_annotation(in_str, out_str):
    assert transform_annotation(in_str) == out_str


@pytest.mark.skipif(sys.version_info[:2] != (3, 9), reason="3.9")
@pytest.mark.parametrize(
    "in_str,out_str",
    [
        (
            "str",
            "str"
        ),
        (
            "list[str]",
            "list[str]"
        ),
        (
            "str|int",
            "typing___.Union[str,int]"
        ),
        (
            "str|int|float",
            "typing___.Union[typing___.Union[str,int],float]"
        ),
        (
            "list[str|int|float]",
            "list[typing___.Union[typing___.Union[str,int],float]]",
        ),
        (
            "dict[str,int]|float",
            "typing___.Union[dict[str,int],float]"
        ),
        (
            "Literal['err']|None",
            "typing___.Union[Literal['err'],None]"),
        (
            "create(A, x=1, y='a') | None",
            "typing___.Union[create(A,x=1,y='a'),None]"),
        (
            "Annotated[int | float, Constraints(ge=1)]",
            "Annotated[typing___.Union[int,float],Constraints(ge=1)]"
        ),
        (
            "Annotated[Literal['pika'] | list[str | bytes], Constraints(min_length=2, 'strict')]",
            "Annotated[typing___.Union[Literal['pika'],list[typing___.Union[str,bytes]]],Constraints(min_length=2,'strict')]"
        ),
        (
            "list[Annotated[str|bytes, Constraints(regex='[a-z]*')]]",
            "list[Annotated[typing___.Union[str,bytes],Constraints(regex='[a-z]*')]]"
        ),
        (
            "list[Annotated[dict[str, str], 'strict']]",
            "list[Annotated[dict[str,str],'strict']]"
        ),
    ],
)
def test_transform_annotation(in_str, out_str):
    assert transform_annotation(in_str) == out_str
