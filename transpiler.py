#!/usr/bin/env python3
from typing import Any, List
from abc import ABC, abstractmethod
from parser import BitfieldDefNode, StructDefNode
from errors import UnknownTypeError, RecursiveStructError
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
    """
    This helper class represents the generated code from the generator.
    It can be seen as a stack of _Block.
    Each _Block represents a part of code with a certain depth (=indentation).
    This class keeps a list of _Block that are root block (depth=0).
    """
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
        """
        Return the full generated code from root blocks.
        """
        return "\n".join([str(block) for block in self.blocks])


class ParseedOutputGenerator(ABC):
    """
    Abstract class that must be used as a base class for generators.
    This class contains one abstract method that is 'generate'.
    """
    def __init__(self, ast: List[Any]):
        self.structs: List[StructDefNode] = []
        self.bitfields: List[BitfieldDefNode] = []
        self._init_intermediate_ast(ast)

    @abstractmethod
    def generate(self, writer: Writer):
        """
        This method is where the code will be generated.
        An instance of the Writer class is given in parameter and should be filled with the generated code.
        You can access the list of struct and bitfields from the 'self.structs' and 'self.bitfields' attributes.
        This abstract method must be defined in the child class, and it will be called automatically.
        """
        pass

    def _init_intermediate_ast(self, ast: List[Any]):
        """
        Initialize some variables and perform some checks one the AST.
        This function MUST NOT be called in the 'generate' method, as it only used in the constructor.
        """
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
                    
                    self._verify_recursive_struct_member(member, [])

    def _verify_recursive_struct_member(self, visited_member, structs_stack):
        """
        Verify if a struct is using itself in one of its members.
        A stack containing the visited structs is used.
        If the same struct appears twice in the stack, it means there is a recursion. 
        This function MUST NOT be called in the 'generate' method, as it only used in the _init_intermediate_ast method.
        """
        if visited_member.type in DATA_TYPES: # base case, cannot visit native data types as they are not structs
            return
        elif visited_member.type in structs_stack:
            raise RecursiveStructError(structs_stack)

        structs_stack.append(visited_member.type)
        for member in self._get_struct_by_name(visited_member.type).members:
            self._verify_recursive_struct_member(member, structs_stack)
        structs_stack.pop()


    def _get_struct_by_name(self, name):
        """
        Returns a struct instance present in the self.struct attribute from it name.
        """
        struct_res = [struct for struct in self.structs if struct.name == name]
        if len(struct_res) == 0:
            return None
        return struct_res[0]


class DataType:
    """
    This helper class gives informations about a data-type from its name.
    It is especially useful for knowing a data-type's size and if it is signed.
    """
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
