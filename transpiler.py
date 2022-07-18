#!/usr/bin/env python3
from typing import Any, List
from abc import ABC, abstractmethod
from parser import *

from errors import ParseedError


class _Block:
    def __init__(self, depth: int, parent):
        self.text: List = []
        self.depth: int = depth
        self.parent: _Block = parent

    def add_line(self, line: str) -> None:
        """
        Add a line in this block of code. The line will be automatically indented.
        """
        self.text.append(("\t" * self.depth) + line + "\n")

    def add_empty_line(self) -> None:
        """
        Add an empty line in the code.
        This function can be used in order to have a more readable code.
        """
        self.text += "\n"

    def add_block(self):
        """
        Add a new code block that is a sub-block of the current block.
        """
        res = _Block(self.depth + 1, self)
        self.text.append(res)
        return res

    def end_block(self):
        """
        End the current code block and return the parent block.
        """
        return self.parent

    def __str__(self) -> str:
        return "".join([str(block) for block in self.text])


class Writer:
    def __init__(self):
        self.text = ""
        self.blocks: List[_Block] = []

    def add_block(self) -> _Block:
        """
        Create a new code block and returns it.
        """
        res: _Block = _Block(0, None)
        self.blocks.append(res)
        return res

    def generate_code(self) -> str:
        return "\n".join([str(block) for block in self.blocks])


class ParseedOutputGenerator(ABC):
    def __init__(self, ast: List[Any]):
        self.structs: List[StructDefNode] = []
        self.bitfields: List[BitfieldDefNode] = []
        self._init_intermediate_ast(ast)

    @abstractmethod
    def generate(self, writer: Writer):
        pass

    def _init_intermediate_ast(self, ast: List[Any]):
        for node in ast:
            if isinstance(node, StructDefNode):
                self.structs.append(node)
            elif isinstance(node, BitfieldDefNode):
                self.bitfields.append(node)


class DataType:
    ENDIAN_LITTLE: str = "LITTLE"
    ENDIAN_BIG: str = "BIG"

    def __init__(self, name: str):
        self.name = name
        self.endian = -1
        self.size = -1
        if name == "uint8":
            self.size = 1
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int8":
            self.size = 1
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint16":
            self.size = 2
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int16":
            self.size = 2
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint24":
            self.size = 3
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int24":
            self.size = 3
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint32":
            self.size = 4
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int32":
            self.size = 4
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint40":
            self.size = 5
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int40":
            self.size = 5
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint48":
            self.size = 6
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int48":
            self.size = 6
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint64":
            self.size = 8
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int64":
            self.size = 8
            self.endian = DataType.ENDIAN_BIG
        elif name == "uint128":
            self.size = 16
            self.endian = DataType.ENDIAN_LITTLE
        elif name == "int128":
            self.size = 16
            self.endian = DataType.ENDIAN_BIG
        elif name == "float":
            self.size = 4
            self.endian = ""
        elif name == "double":
            self.size = 8
            self.endian = ""
        elif name == "byte":
            self.size = 1
            self.endian = DataType.ENDIAN_BIG
        elif name == "string":
            self.size = -1
            self.endian = ""
        else:
            raise Exception("Unknown data-type: " + name)

    def is_string(self) -> bool:
        return self.name == "string"

    def is_byte(self) -> bool:
        return self.name == "byte"

    def is_float(self) -> bool:
        return self.name == "float"

    def is_double(self) -> bool:
        return self.name == "double"
