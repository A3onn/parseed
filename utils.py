#!/usr/bin/env python3
from typing import List


# ENDIANNESS
LITTLE_ENDIAN = "LE"
BIG_ENDIAN = "BE"

KEYWORDS = ["struct", "bitfield", LITTLE_ENDIAN, BIG_ENDIAN, "match"]
DATA_TYPES = [
    "uint8", "int8",
    "uint16", "int16",
    "uint24", "int24",
    "uint32", "int32",
    "uint40", "int40",
    "uint48", "int48",
    "uint64", "int64",
    "uint128", "int128",
    "float", "double"
    "string",
]


class Position:
    def __init__(self, idx: int, ln: int, col: int, filename: str, file_text: str):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.filename = filename
        self.file_text = file_text

    def advance(self, current_char: str = None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

    def get_line_text(self) -> str:
        lines: List[str] = self.file_text.split("\n")
        return lines[self.ln]

    def get_copy(self):
        return Position(self.idx, self.ln, self.col, self.filename, self.file_text)

    def __repr__(self) -> str:
        return f"Position(idx={self.idx}, ln={self.ln}, col={self.col}, filename={self.filename}, file_text=\"{self.file_text}\")"
