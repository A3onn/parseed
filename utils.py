#!/usr/bin/env python3
from typing import List

KEYWORDS = ["struct", "bitfield", "stop"]
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
    "byte",
]

# LIST OF TOKENS
# Numerical values
TT_NUM_INT = "NUM_INT"
TT_NUM_FLOAT = "NUM_FLOAT"

# Operators
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"

# Comparators
TT_COMP_EQ = "COMP_EQ"
TT_COMP_NE = "COMP_NE"
TT_COMP_GT = "COMP_GT"
TT_COMP_LT = "COMP_LT"
TT_COMP_GEQ = "COMP_GEQ"  # greater than
TT_COMP_LEQ = "COMP_LEQ"  # less than

# Others
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_LBRACK = "LBRACK"
TT_RBRACK = "RBRACK"
TT_COMMENT = "COMMENT"
TT_COMMA = "COMMA"
TT_DOT = "DOT"
TT_SEMICOL = "SEMICOL"

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_DATA_TYPE = "DATA_TYPE"

TT_EOF = "EOF"


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


class Token:
    def __init__(self, type_: str, value: object = None, pos_start: Position = None, pos_end: Position = None) -> None:
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.get_copy()
            self.pos_end = pos_start.get_copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


def AST_pprint(ast: List):
    if ast is None:
        return "<Empty>"
    return "\n".join([node.to_str() for node in ast])
