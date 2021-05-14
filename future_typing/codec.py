import codecs
import encodings
import io
import sys
from tokenize import NAME, NUMBER, OP, STRING, cookie_re, tokenize, untokenize
from typing import Any, List, Tuple

from .utils import Token, transform_tokens

utf_8 = encodings.search_function("utf8")


def decode(
    content: bytes, errors: str = "strict", typing_module_name: str = "typing___"
) -> Tuple[str, int]:
    """
    Replace generic type hints and `|` union operator if needed to be interpreted
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

    if sys.version_info < (3, 10):
        lines.insert(
            typing_import_line,
            f"import typing as {typing_module_name}\n".encode("utf-8"),
        )

    content = b"".join(lines)

    g = tokenize(io.BytesIO(content).readline)
    result: List[Token] = []
    tokens_to_change: List[Token] = []

    for tp, val, *_ in g:
        if tp in (NUMBER, NAME, STRING) or _is_in_generic(tp, val, tokens_to_change):
            tokens_to_change.append((tp, val))
        else:
            result.extend(transform_tokens(tokens_to_change, typing_module_name))
            result.append((tp, val))
            tokens_to_change = []

    res = untokenize(result).decode("utf-8", errors)
    return res, len(content)


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


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):  # pragma: no cover
        if not final:
            return "", 0

        return decode(input, errors)


def search_function(_: Any) -> codecs.CodecInfo:
    return codecs.CodecInfo(
        encode=utf_8.encode,
        decode=decode,  # type: ignore[arg-type]
        streamreader=utf_8.streamreader,
        streamwriter=utf_8.streamwriter,
        incrementalencoder=utf_8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        name="future_typing",
    )


def register():  # pragma: no cover
    codecs.register(search_function)
