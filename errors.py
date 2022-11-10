#!/usr/bin/env python3
from utils import *
from typing import Union


class ParseedBaseError(BaseException):
    """
    Base class for internal errors.
    This class implements the _underline_error method that underline the text from a Position to another Position.
    """

    def _underline_error(self, pos_start: Position, pos_end: Position) -> str:
        """
        Underline where the error occured.
        Note that both position should have the same text (meaning: pos_start.file_text == pos_end.file_text).
        :param post_start: Position where to start the underline.
        :type post_start: Position
        :param post_end: Position where to stop the underline.
        :type post_end: Position
        """
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
    """
    Error with one line containing the error.
    If there the error is present on multiple different lines, ParseedMultipleUnderlinedError should be used.
    """

    def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str):
        """
        :param pos_start: Start position of the error.
        :type pos_start: Position
        :param pos_end: End position of the error.
        :type pos_end: Position
        :param error_name: Name of the error.
        :type error_name: str
        :param details: Details about the error.
        :type details: str
        """
        self.pos_start: Position = pos_start
        self.pos_end: Position = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self):
        return f"\nFile {self.pos_start.filename}, on line {self.pos_start.ln + 1}\n{self._underline_error(self.pos_start, self.pos_end)}\n{self.error_name}: {self.details}"


class ParseedMultipleUnderlinedError(ParseedBaseError):
    """
    Error with multiple lines containing the error.
    If there the error is present on only one line, ParseedSimpleUnderlinedError should be used.
    """

    def __init__(self, pos_start: List[Position], pos_end: List[Position], error_name: str, details: str):
        """
        :param pos_start: Start positions of the error.
        :type pos_start: List[Position]
        :param pos_end: End positions of the error.
        :type pos_end: List[Position]
        :param error_name: Name of the error.
        :type error_name: str
        :param details: Details about the error.
        :type details: str
        """
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
    """
    Should be raised when a character was not expected.
    """

    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        """
        :param pos_start: Start position of the error.
        :type pos_start: Position
        :param pos_end: End position of the error.
        :type pos_end: Position
        :param details: Details about the error.
        :type details: str
        """
        super().__init__(pos_start, pos_end, "Illegal character error", f"{details}, col {pos_start.col}")


class InvalidSyntaxError(ParseedSimpleUnderlinedError):
    """
    Should be raised when the syntax is invalid (thrown by the parser).
    """

    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        """
        :param pos_start: Start position of the error.
        :type pos_start: Position
        :param pos_end: End position of the error.
        :type pos_end: Position
        :param details: Details about the error.
        :type details: str
        """
        super().__init__(pos_start, pos_end, "Invalid syntax error", details)


class ExpectedMoreCharError(ParseedSimpleUnderlinedError):
    """
    Should be raised when some characters where expected but not found.
    """

    def __init__(self, pos_start: Position, pos_end: Position, expected_chars: List[str]):
        """
        :param pos_start: Start position of the error.
        :type pos_start: Position
        :param pos_end: End position of the error.
        :type pos_end: Position
        :param expected_chars: List of characters expected.
        :type expected_chars: List[str]
        """
        list_chars: str = ", ".join([f"'{c}'" for c in expected_chars])
        super().__init__(pos_start, pos_end, "Expected more chars error", list_chars)


class UnknownTypeError(ParseedSimpleUnderlinedError):
    """
    Sould be raised when an unkown data-type is found and no bitfield or struct have the same name.
    """

    def __init__(self, pos_start: Position, pos_end: Position, type_name: str, struct_name: str):
        """
        :param pos_start: Start position of the error.
        :type pos_start: Position
        :param pos_end: End position of the error.
        :type pos_end: Position
        :param type_name: Name of the unknown type.
        :type type_name: str
        :param struct_name: Name of the struct where the type was found.
        :type struct_name: str
        """
        super().__init__(pos_start, pos_end, "Unknown data type error", f"\"{type_name}\" in struct {struct_name}")


class RecursiveStructError(ParseedMultipleUnderlinedError):
    """
    Should be raised when a struct includes itself (by a member or sub-member of any depth).
    """

    def __init__(self, structs):
        """
        :param structs: List of structs where the recursion occurs.
        :type structs: List[StructDefNode]
        """
        pos_start: List[Position] = [s._name_token.pos_start for s in structs]
        pos_end: List[Position] = [s._name_token.pos_end for s in structs]
        super().__init__(pos_start, pos_end, "Recursive nested structs error", " -> ".join([s.name for s in structs]))


class DuplicateMemberError(ParseedMultipleUnderlinedError):
    """
    Should be raised when multiple members in the same bifield or struct share the same name.
    """

    def __init__(self, members, struct_or_bitfield_name: str):
        """
        :param members: Members sharing the same name.
        :type members: List[Union[StructDefNode, BitfieldDefNode]]
        :param struct_or_bitfield_name: Name of the struct or bitfield containing the duplicated members.
        :type struct_or_bitfield_name: str
        """
        pos_start: List[Position] = [m._name_token.pos_start for m in members]
        pos_end: List[Position] = [m._name_token.pos_end for m in members]
        super().__init__(pos_start, pos_end, f"Duplicate member error", struct_or_bitfield_name)


class DuplicateStructOrBitfieldError(ParseedMultipleUnderlinedError):
    """
    Should be raised when multiple structs or bitfield share the same name.
    """

    def __init__(self, nodes):
        """
        :param nodes: List of structs and bitfields sharing the same name.
        :type nodes: Union[StructDefNode, BitfieldDefNode]
        """
        pos_start: List[Position] = [n._name_token.pos_start for n in nodes]
        pos_end: List[Position] = [n._name_token.pos_end for n in nodes]
        super().__init__(pos_start, pos_end, "Duplicate struct or bitfield error", nodes[0].name)


class InvalidStateError(Exception):
    """
    This error is used in the parser to indicate some intern invalid state,
    but not an error from the code.
    It should be captured internally.
    """
    pass
