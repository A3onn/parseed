#!/usr/bin/env python3
from typing import Any, List
from lexer import Token
from abc import ABC, abstractmethod
from ast_nodes import BitfieldDefNode, StructDefNode, StructMemberDeclareNode, TernaryDataTypeNode
from errors import *
from utils import DATA_TYPES, DataType


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
        self.__init_intermediate_ast(ast)

    @abstractmethod
    def generate(self, writer: Writer):
        """
        This method is where the code will be generated.
        An instance of the Writer class is given in parameter and should be filled with the generated code.
        You can access the list of struct and bitfields from the 'self.structs' and 'self.bitfields' attributes.
        This abstract method must be defined in the child class, and it will be called automatically.
        """
        pass

    def __init_intermediate_ast(self, ast: List[Any]):
        """
        Initialize some variables and perform some checks one the AST.
        This function MUST NOT be called in the 'generate' method, as it only used in the constructor.
        """
        for node in ast:
            if isinstance(node, BitfieldDefNode):
                self.bitfields.append(node)
            elif isinstance(node, StructDefNode):
                self.structs.append(node)

        self.__check_duplicate_structs_and_bitfields()

        # verify that everything is correct
        # unknown types
        for struct in self.structs:
            self.__check_duplicate_members(struct)
            for member in struct.members:
                if not isinstance(member, StructMemberDeclareNode):
                    # TODO
                    continue
                if member.infos.type not in DATA_TYPES:
                    # check for unknown types
                    if isinstance(member.infos._type, Token) and member.infos.type not in [struct.name for struct in self.structs] and \
                            member.infos.type not in [bitfield.name for bitfield in self.bitfields]:
                        raise UnknownTypeError(member.infos._type.pos_start, member.infos._type.pos_end, member.infos._type, struct.name)

        # if there is no unknown types, now we can check for recursive structs
        for struct in self.structs:
            for member in struct.members:
                self.__verify_recursive_struct_member(member, [])

    def __check_duplicate_members(self, struct):
        """
        Check if a struct contains multiple members with the same name.
        """
        tmp = []
        for member in struct.members:
            if not isinstance(member, StructMemberDeclareNode):
                # TODO
                continue
            if member.name in tmp:
                members = [m for m in struct.members if m.name == member.name]
                raise DuplicateMemberError(members, struct.name)
            tmp.append(member.name)

    def __check_duplicate_structs_and_bitfields(self):
        """
        Check if some structs or bitfields share the same name.
        """
        tmp = []
        # check in structs
        for struct in self.structs:
            if struct.name in tmp:
                nodes = [s for s in self.structs if s.name == struct.name] + \
                        [b for b in self.bitfields if b.name == struct.name]
                raise DuplicateStructOrBitfieldError(nodes)
            tmp.append(struct.name)
        # check in bitfields
        for bitfield in self.bitfields:
            if bitfield.name in tmp:
                nodes = [s for s in self.structs if s.name == bitfield.name] + \
                        [b for b in self.bitfields if b.name == bitfield.name]
                raise DuplicateStructOrBitfieldError(nodes)
            tmp.append(bitfield.name)

    def __verify_recursive_struct_member(self, visited_member, structs_stack):
        """
        Verify if a struct is using itself in one of its members.
        A stack containing the visited structs is used.
        If the same struct appears twice in the stack, it means there is a recursion.
        This function MUST NOT be called in the 'generate' method, as it only used in the _init_intermediate_ast method.
        """
        if not isinstance(visited_member, StructMemberDeclareNode):
            # TODO
            return
        elif isinstance(visited_member.infos.type, TernaryDataTypeNode):
            # TODO
            return 

        if visited_member.infos.type in DATA_TYPES:  # base case, cannot visit native data types as they are not structs
            return
        elif visited_member.infos.type in structs_stack:
            raise RecursiveStructError([self.get_struct_by_name(s) for s in structs_stack])

        structs_stack.append(visited_member.infos.type)

        for member in self.get_struct_by_name(visited_member.infos.type).members:
            self.__verify_recursive_struct_member(member, structs_stack)
        structs_stack.pop()

    def get_struct_by_name(self, name):
        """
        Returns a struct instance present in the self.struct attribute from it name.
        """
        struct_res = [struct for struct in self.structs if struct.name == name]
        if len(struct_res) == 0:
            return None
        return struct_res[0]
