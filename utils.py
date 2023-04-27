#!/usr/bin/env python3
from typing import List
from enum import Enum


class Endian(Enum):
    BIG = "BIG"
    LITTLE = "LITTLE"

    @staticmethod
    def from_token(token):
        if token.value == "LE":
            return Endian.LITTLE
        elif token.value == "BE":
            return Endian.BIG


DATA_TYPES = [
    "uint8", "int8",
    "uint16", "int16",
    "uint24", "int24",
    "uint32", "int32",
    "uint40", "int40",
    "uint48", "int48",
    "uint64", "int64",
    "uint128", "int128",
    "float", "double",
    "string", "bytes"
]


class Position:
    def __init__(self, idx: int, ln: int, col: int, filename: str, file_text: str):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.filename = filename
        self.file_text = file_text

    def advance(self, current_char: str = None):
        if self.idx == len(self.file_text):
            return
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def get_line_text(self) -> str:
        lines: List[str] = self.file_text.split("\n")
        return lines[self.ln]

    def get_copy(self):
        return Position(self.idx, self.ln, self.col, self.filename, self.file_text)

    def go_to_end_of_line(self):
        """
        Move this cursor to the end of the current line.

        :return: This instance.
        :rtype: Position
        """
        while self.file_text[self.col] != "\n":
            self.advance()
        return self

    def go_to_beginning_of_line(self):
        """
        Move this cursor to the beginning of the current line.

        :return: This instance.
        :rtype: Position
        """
        self.idx -= self.col
        self.col = 0
        return self

    def __repr__(self) -> str:
        return f"Position(idx={self.idx}, ln={self.ln}, col={self.col}, filename={self.filename}, file_text=\"{self.file_text}\")"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx == __o.idx and __o.file_text == self.file_text

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx < __o.idx and self.file_text == __o.file_text

    def __le__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx <= __o.idx and self.file_text == __o.file_text

    def __gt__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx > __o.idx and self.file_text == __o.file_text

    def __ge__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx >= __o.idx and self.file_text == __o.file_text

    def __ne__(self, __o: object) -> bool:
        if not isinstance(__o, Position):
            raise TypeError(f"Cannot compare Position with '{type(__o).__name__}'")
        return self.idx != __o.idx and self.file_text == __o.file_text
