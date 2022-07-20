#!/usr/bin/env python3
from typing import Any, List
from abc import ABC, abstractmethod
from parser import BitfieldDefNode, StructDefNode
from errors import UnknownTypeError
from utils import DATA_TYPES


class _Block:
    """
    Represents a block of code.
    This class can be viewed as a stack, you can push with add_block and pop with end_block.
    It helps with the formatting of the generated code.
    """
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
        Add a new code block that is on top of this instance block.
        """
        res = _Block(self.depth + 1, self)
        self.text.append(res)
        return res

    def end_block(self):
        """
        Pop this block and return the new block at the top of the block stack.
        """
        return self.parent

    def __str__(self) -> str:
        """
        Generate and return this block's code and blocks' code above.
        """
        return "".join([str(block) for block in self.text])


class Writer:
    def __init__(self):
        self.text = ""
        self.blocks: List[_Block] = []

    def add_block(self) -> _Block:
        """
        Create a new root code block and returns it.
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
            if isinstance(node, BitfieldDefNode):
                self.bitfields.append(node)
            elif isinstance(node, StructDefNode):
                self.structs.append(node)
        
        # verify that everything is correct
        for struct in self.structs:
            for member in struct.members:
                if member.type not in DATA_TYPES:
                    # check for unknown types
                    if member.type not in [struct.name for struct in self.structs] and \
                        member.type not in [bitfield.name for bitfield in self.bitfields]:
                        raise UnknownTypeError(member.type, struct.name)
                    
                    self._verify_recursive_struct_member(member)

    def _verify_recursive_struct_member(self, member):
        """
        The 'member' parameter should be a valid data type, meaning it should be in the self.structs list.
        """
        # TODO
        pass

    def _get_struct_by_name(self, name):
        struct_res = [struct for struct in self.structs if struct.name == name]
        if len(struct_res) == 0:
            return None
        return struct_res[0]


class DataType:
    def __init__(self, name: str):
        self.name = name
        self.size = -1
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
            self.size = -1
        # other type have been checked by the ParseedOutputGenerator class

    def is_string(self) -> bool:
        return self.name == "string"

    def is_byte(self) -> bool:
        return self.name == "byte"

    def is_float(self) -> bool:
        return self.name == "float"

    def is_double(self) -> bool:
        return self.name == "double"
