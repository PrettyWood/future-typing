import io
import sys
from tokenize import NAME, NUMBER, OP, STRING, generate_tokens
from typing import List, Sequence, Tuple

Token = Tuple[int, str]


def transform_annotation(annotation: str, typing_module_name: str = "typing") -> str:
    """Rewrite an annotation (as a string) to be understood for the current python version"""
    if sys.version_info >= (3, 10):
        return annotation

    tokens = get_tokens_from_string(annotation)
    new_tokens = transform_tokens(tokens, typing_module_name)
    return "".join(v for _, v in new_tokens)


def get_tokens_from_string(string: str) -> List[Token]:
    all_tokens = generate_tokens(io.StringIO(string).readline)
    return [
        (t.type, t.string) for t in all_tokens if t.type in (NAME, NUMBER, OP, STRING)
    ]


def transform_tokens(tokens: List[Token], typing_module_name: str) -> List[Token]:
    if all(tp == NAME for tp, _ in tokens):
        return tokens

    if sys.version_info < (3, 10):
        tokens = _transform_union(tokens, typing_module_name)
    if sys.version_info < (3, 9):
        tokens = _transform_generics(tokens, typing_module_name)

    return tokens


def _transform_union(tokens: List[Token], typing_module_name: str) -> List[Token]:
    """Change `|` into `Union` recursively"""
    if not _is_new_union(tokens):
        return tokens

    brackets = 0
    chunks: List[List[Token]] = []

    union_i = None
    chunk: List[Token] = []

    for i, (tp, val) in enumerate(tokens):
        if (tp, val) == (NAME, "Annotated"):
            for j, (t, v) in enumerate(tokens[i:]):
                if t == OP and v == ",":
                    first_comma_index = i + j
                    new_annotated = _transform_union(
                        tokens[i + 2 : first_comma_index], typing_module_name
                    )
                    return [
                        *tokens[: i + 2],
                        *new_annotated,
                        *tokens[first_comma_index:],
                    ]

    for i, (tp, val) in enumerate(tokens):
        if tp == OP and val == "[":
            brackets += 1
            chunk.append((tp, val))
            chunks.append(chunk)
            chunk = []
            continue
        elif tp == OP and val == "]":
            brackets -= 1
            chunks.append(chunk)
            chunk = [(tp, val)]
            continue
        elif val == "|" and not brackets:
            union_i = i

        chunk.append((tp, val))

    chunks.append(chunk)

    if union_i is not None:
        return _to_old_union(
            _transform_union(tokens[:union_i], typing_module_name),
            _transform_union(tokens[union_i + 1 :], typing_module_name),
            typing_module_name,
        )
    else:
        return [
            token
            for chunk in chunks
            for token in _transform_union(chunk, typing_module_name)
        ]


def _is_new_union(tokens: Sequence[Token]) -> bool:
    has_union = False

    for tp, val in tokens:
        if tp not in (NAME, NUMBER, OP, STRING):
            return False
        if tp == OP and val == "|":
            has_union = True

    return has_union


def _to_old_union(
    left: Sequence[Token], right: Sequence[Token], typing_module_name: str
) -> List[Token]:
    return [
        (NAME, f"{typing_module_name}.Union"),
        (OP, "["),
        *left,
        (OP, ","),
        *right,
        (OP, "]"),
    ]


def _transform_generics(tokens: List[Token], typing_module_name: str) -> List[Token]:
    new_generics = {
        "dict": f"{typing_module_name}.Dict",
        "frozenset": f"{typing_module_name}.FrozenSet",
        "list": f"{typing_module_name}.List",
        "set": f"{typing_module_name}.Set",
        "tuple": f"{typing_module_name}.Tuple",
        "type": f"{typing_module_name}.Type",
    }

    def _to_generic(token_: Token) -> Token:
        tp, val = token_
        if tp == NAME and val in new_generics:
            return tp, new_generics[val]
        else:
            return token_

    for i, token in enumerate(tokens[:-1]):
        next_tp, next_val = tokens[i + 1]
        if next_tp == OP and next_val == "[":
            tokens[i] = _to_generic(token)

    return tokens
