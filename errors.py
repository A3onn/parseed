#!/usr/bin/env python3
from utils import *


class ParseedBaseError(BaseException):
    def _underline_error(self, pos_start: Position, pos_end: Position, error_line_text: str) -> str:
        res: str = ""
        for i in range(0, pos_start.col):
            res += " "
        for i in range(0, pos_end.col - pos_start.col):
            res += "~"
        return res


class ParseedSimpleUnderlinedError(ParseedBaseError):
    def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str):
        self.pos_start: Position = pos_start
        self.pos_end: Position = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self):
        error_line_text: str = self.pos_end.get_line_text()
        return f"\nFile {self.pos_start.filename}, on line {self.pos_start.ln + 1}\n{error_line_text}\n{self._underline_error(error_line_text)}\n{self.error_name}: {self.details}"


class ParseedMultipleUnderlinedError(ParseedBaseError):
    def __init__(self, pos_start: List[Position], pos_end: List[Position], error_name: str, details: str):
        assert len(pos_start) == len(pos_end)
        self.pos_start: List[Position] = pos_start
        self.pos_end: List[Position] = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self):
        res = f"\nFile {self.pos_start[0].filename},"

        for i in range(len(self.pos_start)):  # same thing if it was self.pos_end
            error_line_text: str = self.pos_start[i].get_line_text()
            res += f"\n\non line {self.pos_start[i].ln + 1},\n{error_line_text}\n{self._underline_error(self.pos_start[i], self.pos_end[i], error_line_text)}"

        res += f"\n{self.error_name}: {self.details}\n"
        return res


class IllegalCharacterError(ParseedSimpleUnderlinedError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Illegal character error", f"{details}, col {pos_start.col}")


class InvalidSyntaxError(ParseedSimpleUnderlinedError):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Invalid syntax error", details)


class ExpectedMoreCharError(ParseedSimpleUnderlinedError):
    def __init__(self, pos_start: Position, pos_end: Position, expected_chars: List[str]):
        list_chars: str = ", ".join([f"'{c}'" for c in expected_chars])
        super().__init__(pos_start, pos_end, "Expected more chars", list_chars)


class UnknownTypeError(ParseedSimpleUnderlinedError):
    def __init__(self, pos_start: Position, pos_end: Position, type_name: str, struct_name: str):
        super().__init__(pos_start, pos_end, f"Unknown data type in struct \"{struct_name}\"", type_name)


class RecursiveStructError(ParseedMultipleUnderlinedError):
    def __init__(self, structs):
        pos_start: List[Position] = [s.token_name.pos_start for s in structs]
        pos_end: List[Position] = [s.token_name.pos_end for s in structs]
        super().__init__(pos_start, pos_end, "Found recursive nested structs", structs[0].name)


class DuplicateMemberError(ParseedMultipleUnderlinedError):
    def __init__(self, members, struct_name: str):
        pos_start: List[Position] = [m.token_name.pos_start for m in members]
        pos_end: List[Position] = [m.token_name.pos_end for m in members]
        super().__init__(pos_start, pos_end, f"Found multiple members of the struct {struct_name} sharing the same name", members[0].name)


class DuplicateStructOrBitfieldError(ParseedMultipleUnderlinedError):
    def __init__(self, nodes):
        pos_start: List[Position] = [n.token_name.pos_start for n in nodes]
        pos_end: List[Position] = [n.token_name.pos_end for n in nodes]
        super().__init__(pos_start, pos_end, "Found multiple structs or bitfields sharing the same name", nodes[0].name)
