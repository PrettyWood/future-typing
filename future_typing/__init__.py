import codecs
import encodings
import io
import sys
from typing import List, Sequence, Tuple
from tokenize import (
    cookie_re,
    generate_tokens,
    tokenize,
    untokenize,
    NAME,
    NUMBER,
    OP,
    STRING,
)

utf_8 = encodings.search_function("utf8")

# Name of `typing` chosen in autoimport
TYPING_NAME = "typing___"

should_transform_union = False
should_transform_generics = False

if sys.version_info[:2] == (3, 9):
    should_transform_union = True
elif sys.version_info[:2] <= (3, 8):
    should_transform_union = True
    should_transform_generics = True


NEW_UNION = {"|": ","}
NEW_GENERICS = {
    "dict": f"{TYPING_NAME}.Dict",
    "frozenset": f"{TYPING_NAME}.FrozenSet",
    "list": f"{TYPING_NAME}.List",
    "set": f"{TYPING_NAME}.Set",
    "tuple": f"{TYPING_NAME}.Tuple",
    "type": f"{TYPING_NAME}.Type",
}

Token = Tuple[int, str]


def _to_generic(token: Token) -> Token:
    tp, val = token
    if tp == NAME and val in NEW_GENERICS:
        return tp, NEW_GENERICS[val]
    else:
        return token


def transform_generics(tokens: List[Token]) -> List[Token]:
    for i, token in enumerate(tokens[:-1]):
        next_tp, next_val = tokens[i+1]
        if next_tp == OP and next_val == "[":
            tokens[i] = _to_generic(token)

    return tokens


def _is_new_union(tokens: Sequence[Token]) -> bool:
    has_union = False

    for tp, val in tokens:
        if tp not in (NAME, NUMBER, OP, STRING):
            return False
        if tp == OP and val == "|":
            has_union = True

    return has_union


def _to_old_union(left: Sequence[Token], right: Sequence[Token], union_name: str) -> List[Token]:
    return [
        (NAME, union_name),
        (OP, "["),
        *left,
        (OP, ","),
        *right,
        (OP, "]")
    ]


def transform_union(tokens: List[Token], *, union_name=f"{TYPING_NAME}.Union") -> List[Token]:
    """Change `|` into `Union` recursively"""
    if not _is_new_union(tokens):
        return tokens

    last_open_bracket, last_closed_bracket, brackets = None, None, 0
    chunks: List[List[Token]] = []

    union_i = None
    chunk: List[Token] = []

    for i, (tp, val) in enumerate(tokens):
        if (tp, val) == (NAME, "Annotated"):
            for j, (t, val) in enumerate(tokens[i:]):
                if t == OP and val == ",":
                    first_comma_index = i + j
                    new_annotated = transform_union(tokens[i+2:first_comma_index])
                    return [*tokens[:i+2], *new_annotated, *tokens[first_comma_index:]]

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
            transform_union(tokens[:union_i], union_name=union_name),
            transform_union(tokens[union_i + 1:], union_name=union_name),
            union_name,
        )
    else:
        return [token for chunk in chunks for token in transform_union(chunk, union_name=union_name)]


def _is_in_generic(tp: int, val: str, tokens: List[Token]) -> bool:
    if tp == OP and val in "|[]":
        return True

    if tp == STRING or tp == OP and val == ",":
        o, c = 0, 0
        for _, val in tokens:
            if val == "[":
                o += 1
            if val == "]":
                c += 1
        return o > c

    return False


def transform_tokens(tokens: List[Token]) -> List[Token]:
    if all(tp == NAME for tp, _ in tokens):
        return tokens

    if should_transform_generics:
        tokens = transform_generics(tokens)
    if should_transform_union:
        tokens = transform_union(tokens)

    return tokens


def decode(content: bytes, errors: str = "strict") -> Tuple[str, int]:
    """
    Replace `int | str` with `typing.Union[int, str]`
    """
    if not content:
        return "", 0

    lines = io.BytesIO(content).readlines()
    first_line = lines[0].decode("utf-8", errors)

    typing_import_line = 0
    # A custom encoding is set or none
    if cookie_re.match(first_line) or not first_line.strip("\n"):
        typing_import_line = 1
        # avoid recursion problems
        if "future_typing" in first_line:
            lines[0] = cookie_re.sub("# -*- coding: utf-8", first_line).encode("utf-8")

    if should_transform_union or should_transform_generics:
        lines.insert(
            typing_import_line, f"import typing as {TYPING_NAME}\n".encode("utf-8")
        )

    content = b"".join(lines)

    g = tokenize(io.BytesIO(content).readline)
    result: List[Token] = []
    tokens_to_change: List[Token] = []

    for tp, val, *_ in g:
        if tp in (NUMBER, NAME, STRING) or _is_in_generic(tp, val, tokens_to_change):
            tokens_to_change.append((tp, val))
        else:
            result.extend(transform_tokens(tokens_to_change))
            result.append((tp, val))
            tokens_to_change = []

    res = untokenize(result).decode("utf-8", errors)
    return res, len(content)


def transform_annotation(annotation: str) -> str:
    all_tokens = generate_tokens(io.StringIO(annotation).readline)
    tokens = [
        (t.type, t.string) for t in all_tokens if t.type in (NAME, NUMBER, OP, STRING)
    ]
    new_tokens = transform_tokens(tokens)
    return "".join(v for _, v in new_tokens)


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):  # pragma: no cover
        if not final:
            return "", 0

        return decode(input, errors)


def search_function(_) -> codecs.CodecInfo:
    return codecs.CodecInfo(
        encode=utf_8.encode,
        decode=decode,
        streamreader=utf_8.streamreader,
        streamwriter=utf_8.streamwriter,
        incrementalencoder=utf_8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        name="future_typing",
    )


def register():  # pragma: no cover
    codecs.register(search_function)


def cli():  # pragma: no cover
    """Command line to run the transform process directly on a file"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Support type hinting generics in standard collections and | as Union"
    )
    parser.add_argument("filename", help="the filename to parse and transform")
    args = parser.parse_args()

    with open(args.filename, "rb") as f:
        register()
        print(f.read().decode("future_typing"))


if __name__ == "__main__":  # pragma: no cover
    cli()
