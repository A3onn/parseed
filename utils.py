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
    "float", "double",
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

class DataType:
    """
    This helper class gives informations about a data-type from its name.
    It is especially useful for knowing a data-type's size and if it is signed.
    """

    name: str = ""
    size: int = -1
    signed = False
    string_delimiter = ""

    def __init__(self, name: str, string_delimiter=r"\0"):
        """
        :param name: Name of the type, must not be an identifier.
        :type name: str
        """
        self.name = name
        self.size = -1
        self.string_delimiter = string_delimiter
        if name == "uint8":
            self.size = 1
            self.signed = False
        elif name == "int8":
            self.size = 1
            self.signed = True
        elif name == "uint16":
            self.size = 2
            self.signed = False
        elif name == "int16":
            self.size = 2
            self.signed = True
        elif name == "uint24":
            self.size = 3
            self.signed = False
        elif name == "int24":
            self.size = 3
            self.signed = True
        elif name == "uint32":
            self.size = 4
            self.signed = False
        elif name == "int32":
            self.size = 4
            self.signed = True
        elif name == "uint40":
            self.size = 5
            self.signed = False
        elif name == "int40":
            self.size = 5
            self.signed = True
        elif name == "uint48":
            self.size = 6
            self.signed = False
        elif name == "int48":
            self.size = 6
            self.signed = True
        elif name == "uint64":
            self.size = 8
            self.signed = False
        elif name == "int64":
            self.size = 8
            self.signed = True
        elif name == "uint128":
            self.size = 16
            self.signed = False
        elif name == "int128":
            self.size = 16
            self.signed = False
        elif name == "float":
            self.size = 4
        elif name == "double":
            self.size = 8
        elif name == "byte":
            self.size = 1
            self.signed = False
        elif name == "string":
            pass
        # other type have been checked by the ParseedOutputGenerator class

    def is_string(self) -> bool:
        """
        Returns if the data-type is a string.
        """
        return self.name == "string"

    def is_byte(self) -> bool:
        """
        Returns if the data-type is a byte.
        """
        return self.name == "byte"

    def is_float(self) -> bool:
        """
        Returns if the data-type is a float.
        Use the 'is_double' method to check if it a double.
        """
        return self.name == "float"

    def is_double(self) -> bool:
        """
        Returns if the data-type is a double.
        Use the 'is_float' method to check if it a float.
        """
        return self.name == "double"
    
    def __str__(self) -> str:
        res: str = f"(DATATYPE:{self.name}"
        if hasattr(self, "size"):
            res += f" size: {self.size}"
        if hasattr(self, "signed"):
            res += f" signed: {self.signed}"
        res += ")"
        return res
