#!/usr/bin/env python3
from utils import *


class ParseedBaseError(BaseException):
    def _underline_error(self, pos_start: Position, pos_end: Position) -> str:
        res_text: List[str] = []
        res_underline: List[str] = []

        # start at the beginning to have the beginning of the line printed out in the error
        curr_pos = pos_start.get_copy().go_to_beginning_of_line()
        tmp_res_text = ""
        tmp_res_underline = ""
        while curr_pos != pos_end:
            curr_char = curr_pos.file_text[curr_pos.idx]

            if curr_char == "\n":
                res_text.append(tmp_res_text)
                res_underline.append(tmp_res_underline)
                tmp_res_text = ""
                tmp_res_underline = ""
            else:
                tmp_res_text += curr_char
                # as we start at the beginning of the line, we need
                # to check if we are in the error part to underline it
                if curr_pos >= pos_start:
                    tmp_res_underline += "~"
                else:
                    tmp_res_underline += " "
            curr_pos.advance()

        res_text.append(tmp_res_text)
        res_underline.append(tmp_res_underline)

        res: str = ""
        for i in range(len(res_text)):
            res += res_text[i] + "\n"
            res += res_underline[i] + "\n"
        return res


class ParseedSimpleUnderlinedError(ParseedBaseError):
    def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str):
        self.pos_start: Position = pos_start
        self.pos_end: Position = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self):
        return f"\nFile {self.pos_start.filename}, on line {self.pos_start.ln + 1}\n{self._underline_error(self.pos_start, self.pos_end)}\n{self.error_name}: {self.details}"


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
            res += f"\n\non line {self.pos_start[i].ln + 1},\n{self._underline_error(self.pos_start[i], self.pos_end[i])}"

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
        super().__init__(pos_start, pos_end, "Expected more chars error", list_chars)


class UnknownTypeError(ParseedSimpleUnderlinedError):
    def __init__(self, pos_start: Position, pos_end: Position, type_name: str, struct_name: str):
        super().__init__(pos_start, pos_end, "Unknown data type error", f"\"{type_name}\" in struct {struct_name}")


class RecursiveStructError(ParseedMultipleUnderlinedError):
    def __init__(self, structs):
        pos_start: List[Position] = [s._name_token.pos_start for s in structs]
        pos_end: List[Position] = [s._name_token.pos_end for s in structs]
        super().__init__(pos_start, pos_end, "Recursive nested structs error", " -> ".join([s.name for s in structs]))


class DuplicateMemberError(ParseedMultipleUnderlinedError):
    def __init__(self, members, struct_name: str):
        pos_start: List[Position] = [m._name_token.pos_start for m in members]
        pos_end: List[Position] = [m._name_token.pos_end for m in members]
        super().__init__(pos_start, pos_end, "Duplicate member error", members[0].name)


class DuplicateStructOrBitfieldError(ParseedMultipleUnderlinedError):
    def __init__(self, nodes):
        pos_start: List[Position] = [n._name_token.pos_start for n in nodes]
        pos_end: List[Position] = [n._name_token.pos_end for n in nodes]
        super().__init__(pos_start, pos_end, "Duplicate struct or bitfield error", nodes[0].name)


class InvalidStateError(Exception):
    """
    This error is used in the parser to indicate some intern invalid state,
    but not an error from the code.
    """
    pass
