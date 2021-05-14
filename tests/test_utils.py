import sys

import pytest

from future_typing.utils import transform_annotation

TYPING_MOD = "typing___"
CASES = {
    "str": {
        "3.6-3.8": "str",
        "3.9": "str",
    },
    "list[str]": {"3.6-3.8": f"{TYPING_MOD}.List[str]", "3.9": "list[str]"},
    "str|int": {
        "3.6-3.8": f"{TYPING_MOD}.Union[str,int]",
        "3.9": f"{TYPING_MOD}.Union[str,int]",
    },
    "str|int|float": {
        "3.6-3.8": f"{TYPING_MOD}.Union[{TYPING_MOD}.Union[str,int],float]",
        "3.9": f"{TYPING_MOD}.Union[{TYPING_MOD}.Union[str,int],float]",
    },
    "list[str|int|float]": {
        "3.6-3.8": f"{TYPING_MOD}.List[{TYPING_MOD}.Union[{TYPING_MOD}.Union[str,int],float]]",
        "3.9": f"list[{TYPING_MOD}.Union[{TYPING_MOD}.Union[str,int],float]]",
    },
    "dict[str,int]|float": {
        "3.6-3.8": f"{TYPING_MOD}.Union[{TYPING_MOD}.Dict[str,int],float]",
        "3.9": f"{TYPING_MOD}.Union[dict[str,int],float]",
    },
    "Literal['err']|None": {
        "3.6-3.8": f"{TYPING_MOD}.Union[Literal['err'],None]",
        "3.9": f"{TYPING_MOD}.Union[Literal['err'],None]",
    },
    "create(A, x=1, y='a') | None": {
        "3.6-3.8": f"{TYPING_MOD}.Union[create(A,x=1,y='a'),None]",
        "3.9": f"{TYPING_MOD}.Union[create(A,x=1,y='a'),None]",
    },
    "Annotated[int | float, Constraints(ge=1)]": {
        "3.6-3.8": f"Annotated[{TYPING_MOD}.Union[int,float],Constraints(ge=1)]",
        "3.9": f"Annotated[{TYPING_MOD}.Union[int,float],Constraints(ge=1)]",
    },
    "Annotated[Literal['pika'] | list[str | bytes], Constraints(min_length=2, 'strict')]": {
        "3.6-3.8": f"Annotated[{TYPING_MOD}.Union[Literal['pika'],{TYPING_MOD}.List[{TYPING_MOD}.Union[str,bytes]]],Constraints(min_length=2,'strict')]",
        "3.9": f"Annotated[{TYPING_MOD}.Union[Literal['pika'],list[{TYPING_MOD}.Union[str,bytes]]],Constraints(min_length=2,'strict')]",
    },
    "list[Annotated[str|bytes, Constraints(regex='[a-z]*')]]": {
        "3.6-3.8": f"{TYPING_MOD}.List[Annotated[{TYPING_MOD}.Union[str,bytes],Constraints(regex='[a-z]*')]]",
        "3.9": f"list[Annotated[{TYPING_MOD}.Union[str,bytes],Constraints(regex='[a-z]*')]]",
    },
    "list[Annotated[dict[str, str], 'strict']]": {
        "3.6-3.8": f"{TYPING_MOD}.List[Annotated[{TYPING_MOD}.Dict[str,str],'strict']]",
        "3.9": "list[Annotated[dict[str,str],'strict']]",
    },
}


@pytest.mark.skipif(sys.version_info >= (3, 9), reason="3.6 to 3.8")
@pytest.mark.parametrize(
    "in_str,out_str", ((k, v["3.6-3.8"]) for k, v in CASES.items())
)
def test_transform_annotation_3_6_to_8(in_str, out_str):
    assert transform_annotation(in_str, TYPING_MOD) == out_str


@pytest.mark.skipif(sys.version_info[:2] != (3, 9), reason="3.9")
@pytest.mark.parametrize("in_str,out_str", ((k, v["3.9"]) for k, v in CASES.items()))
def test_transform_annotation_3_9(in_str, out_str):
    assert transform_annotation(in_str, TYPING_MOD) == out_str
