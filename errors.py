#!/usr/bin/env python3
from utils import Position
from typing import List, Optional


# LEXER AND PARSER ERRORS
class ParseedLexerParserError(BaseException):
    def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str):
        self.pos_start: Position = pos_start
        self.pos_end: Position = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self):
        error_line_text: str = self.pos_end.get_line_text()
        return f"\nFile {self.pos_start.filename}, on line {self.pos_start.ln + 1}\n{error_line_text}\n{self._underline_error(error_line_text)}\n{self.error_name}: {self.details}"

    def _underline_error(self, error_line_text: str) -> str:
        res: str = ""
        for i in range(0, self.pos_start.col):
            res += " "
        for i in range(0, self.pos_end.col - self.pos_start.col):
            res += "~"
        return res


class IllegalCharacterError(ParseedLexerParserError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Illegal character error", f"{details}, col {pos_start.col}")


class InvalidSyntaxError(ParseedLexerParserError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Invalid syntax error", details)


class ExpectedMoreCharError(ParseedLexerParserError):
    def __init__(self, pos_start: Position, pos_end: Position, expected_chars: List[str]):
        list_chars: str = ", ".join([f"'{c}'" for c in expected_chars])
        super().__init__(pos_start, pos_end, "Expected more chars", list_chars)


# TRANSPILER ERRORS
class ParseedTranspilerError(BaseException):
    pass


class RecursiveStructError(ParseedTranspilerError):
    def __init__(self, structs):
        self.structs = structs

    def __str__(self) -> str:
        return f"Recursive nested structs found: {' -> '.join(self.structs)}"


class UnknownTypeError(ParseedTranspilerError):
    def __init__(self, type_name: str, struct_name: Optional[str]):
        self.type_name = type_name
        self.struct_name = struct_name

    def __str__(self) -> str:
        if self.struct_name is None:
            return f"Unknown data type '{self.type_name}'."
        return f"Unknown data type '{self.type_name}' in {self.struct_name}."
