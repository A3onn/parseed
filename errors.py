#!/usr/bin/env python3
from utils import Position
from typing import List


class ParseedError(BaseException):
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


class IllegalCharacterError(ParseedError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Illegal character error", f"{details}, col {pos_start.col}")


class InvalidSyntaxError(ParseedError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Invalid syntax error", details)


class ExpectedMoreCharError(ParseedError):
    def __init__(self, pos_start: Position, pos_end: Position, expected_chars: List[str]):
        list_chars: str = ", ".join([f"'{c}'" for c in expected_chars])
        super().__init__(pos_start, pos_end, "Expected more chars", list_chars)
