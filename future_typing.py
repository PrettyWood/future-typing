import codecs
import encodings
import io
import sys
from typing import List, Tuple
from tokenize import (
    cookie_re,
    tokenize,
    untokenize,
    NAME,
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


def transform_tokens(tokens: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """
    Transform a list of [(NAME, 'list'), (OP, '['), (NAME, 'str'), (OP, ']')]
    into [(NAME, 'typing.List'), (OP, '|'), (NAME, 'str')
    """
    if not (should_transform_union or should_transform_generics):
        return tokens

    has_union = False
    union_chunks: List[List[Tuple[int, str]]] = []

    current_chunk: List[Tuple[int, str]] = []
    for i, (tp, val) in enumerate(tokens):
        if should_transform_generics and tp == NAME and val in NEW_GENERICS:
            try:
                next_tp, next_val = tokens[i + 1]
                if next_tp == OP and next_val == "[":
                    current_chunk.append((tp, NEW_GENERICS[val]))
                else:
                    current_chunk.append((tp, val))
            except IndexError:
                current_chunk.append((tp, val))
        elif tp == OP and val == "|":
            has_union = True
            union_chunks.append(current_chunk)
            current_chunk = []
        else:
            current_chunk.append((tp, val))

    if current_chunk:
        union_chunks.append(current_chunk)

    if has_union:
        new_tokens = [
            (NAME, f"{TYPING_NAME}.Union"),
            (OP, "["),
        ]
        for chunk in union_chunks[:-1]:
            new_tokens.extend(chunk)
            new_tokens.append((OP, ","))
        new_tokens.extend(union_chunks[-1])
        new_tokens.append((OP, "]"))
        return new_tokens
    else:
        return [token for chunk in union_chunks for token in chunk]


def _is_in_generic(tp: int, val: str, tokens: List[Tuple[int, str]]) -> bool:
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
    result: List[Tuple[int, str]] = []
    tokens_to_change: List[Tuple[int, str]] = []

    for tp, val, *_ in g:
        if tp == NAME or _is_in_generic(tp, val, tokens_to_change):
            tokens_to_change.append((tp, val))
        else:
            result.extend(transform_tokens(tokens_to_change))
            result.append((tp, val))
            tokens_to_change = []

    res = untokenize(result).decode("utf-8", errors)
    return res, len(content)


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
