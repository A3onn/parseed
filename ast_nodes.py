#!/usr/bin/env python3
from typing import List, Optional, Union
from lexer import Token
from utils import BIG_ENDIAN, DataType
from abc import ABC, abstractmethod

class ASTNode(ABC):
    """
    Abstract class for nodes forming the AST of the Parseed code.
    """
    @abstractmethod
    def to_str(self, depth: int = 0):
        """
        Method used to print the AST in a pretty form.
        This function must be called from children nodes if the class has some (with depth=depth+1).
        The depth parameter must be used to add some padding ('\\t') before printing anything.
        """
        pass


class FloatNumberNode(ASTNode):
    """
    Represent a floating-point number.
    """
    def __init__(self, value_token: Token):
        self.value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "FloatNumberNode(" + str(self.value_token.value) + ")\n"

    @property
    def value(self) -> float:
        """
        Value of this node as a float.
        """
        return float(self.value_token.value)


class IntNumberNode(ASTNode):
    """
    Represent an integer number.
    """
    def __init__(self, value_token: Token):
        self.value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "IntNumberNode(" + str(self.value_token.value) + ")\n"

    @property
    def value(self) -> int:
        """
        Value of this node as an int.
        """
        return int(self.value_token.value)


# operators
class BinOpNode(ASTNode):
    """
    Represent a binary operation between a two nodes (value or expression).
    """
    def __init__(self, left_node: ASTNode, op_token: Token, right_node: ASTNode):
        self.left_node: ASTNode = left_node
        self.op_token: Token = op_token
        self.right_node: ASTNode = right_node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "BinOpNode(\n" + self.left_node.to_str(depth + 1) \
            + ("\t" * (depth + 1)) + str(self.op_token) + "\n" \
            + self.right_node.to_str(depth + 1) \
            + ("\t" * depth) + ")\n"

    @property
    def op(self) -> str:
        """
        Operand token as a string.
        """
        return str(self.op_token.value)

    @property
    def left(self) -> ASTNode:
        """
        Left node.
        """
        return self.left_node

    @property
    def right(self) -> ASTNode:
        """
        Right node.
        """
        return self.right_node


class UnaryOpNode(ASTNode):
    """
    Represent an unary operation between an operand (-, +, /, etc...) and a node (value or expression).
    """
    def __init__(self, op_token: Token, node: ASTNode):
        self.op_token: Token = op_token
        self.node: ASTNode = node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "UnaryOpNode(\n" + ("\t" * (depth + 1)) + str(self.op_token) + "\n" + self.node.to_str(depth + 1) + ("\t" * depth) + ")\n"

    @property
    def op(self) -> str:
        """
        Operand node as a string.
        """
        return str(self.op_token.value)

    @property
    def value(self) -> ASTNode:
        """
        Return the node place a the right of the operand (thus the value).
        """
        return self.node


# struct
class IdentifierAccessNode(ASTNode):
    """
    This class contains the name of an identifier accessed.
    """
    def __init__(self, struct_name: str):
        self.struct_name: str = struct_name

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "IdentifierAccessNode(" + str(self.struct_name) + ")\n"


class ComparisonNode(ASTNode):
    """
    Represent a comparison between two AST nodes.
    """
    def __init__(self, left_cond_op: Token, condition_op: Token, right_cond_op: Token):
        self.left_cond_op: Token = left_cond_op
        self.condition_op: Token = condition_op
        self.right_cond_op: Token = right_cond_op

    def to_str(self, depth: int = 0):
        res: str = ("\t" * depth) + str(self.left_cond_op) + " "
        res += str(self.condition_op) + " "
        res += str(self.right_cond_op)
        return res + "\n"


class TernaryDataTypeNode(ASTNode):
    """
    This class represents a ternary operator for data-types.
    """
    def __init__(self, comparison_node: ComparisonNode, if_true: Union[IdentifierAccessNode, DataType], if_false: Union[IdentifierAccessNode, DataType]):
        self.comparison: ComparisonNode = comparison_node
        self.if_true: Union[IdentifierAccessNode, DataType] = if_true
        self.if_false: Union[IdentifierAccessNode, DataType] = if_false

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "TernaryDataType(\n"
        res += self.comparison.to_str(depth+1)
        res += ("\t" * (depth+1)) + "?\n"

        if isinstance(self.if_true, IdentifierAccessNode):
            res += self.if_true.to_str(depth+2) + "\n"
        else:
            res += ("\t" * (depth+1)) + str(self.if_true) + "\n"

        res += ("\t" * (depth+1)) + ":\n"

        if isinstance(self.if_false, IdentifierAccessNode):
            res += self.if_false.to_str(depth+2) + "\n)"
        else:
            res += ("\t" * (depth+1)) + str(self.if_false) + "\n"
        return res + ("\t" * depth) + ")" + "\n"


class StructMemberTypeNode(ASTNode):
    def __init__(self, type_token: Union[Token,TernaryDataTypeNode], endian: str = BIG_ENDIAN, is_list: bool = False, list_length_node: Union[None,UnaryOpNode,BinOpNode] = None):
        self.type_name: Union[Token,TernaryDataTypeNode] = type_token
        self.endian: str = endian
        self.is_list: bool = is_list
        self.list_length_node: Optional[ASTNode] = list_length_node
    
    def to_str(self, depth: int = 0) -> str:
        if self.is_list:
            if self.list_length_node != None:
                return ("\t" * depth) + "StructMemberTypeNode(" + str(self.type_name) + f"[\n{self.list_length_node.to_str(depth+1)}" + ("\t" * depth) + "])\n"
            return ("\t" * depth) + "StructMemberTypeNode(" + str(self.type_name) + f"[])\n"
        return ("\t" * depth) + "StructMemberTypeNode(" + str(self.type_name) + ")\n"


class StructMemberDeclareNode(ASTNode):
    """
    Represent a member of a struct.
    It contains the name and the type of the member.
    """
    def __init__(self, type_: StructMemberTypeNode, name_token: Token):
        self.type: StructMemberTypeNode = type_
        self.name_token: Token = name_token

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "StructMemberDeclareNode(\n"
        res += self.type.to_str(depth+1)
        res += ("\t" * (depth+1)) + str(self.name_token) + "\n" + ("\t" * depth) + ")\n"
        return res

    @property
    def name(self) -> str:
        """
        Member's name.
        """
        return str(self.name_token.value)


class MatchNode(ASTNode):
    """
    Represent a match expression inside structs.
    """
    def __init__(self, condition: ASTNode):
        self.condition: ASTNode = condition
        self.cases: Dict[ASTNode,Union[StructMemberTypeNode,StructMemberDeclareNode]] = {}
        self.member_name: str = None  # if a cases are: {ASTNode: DataType}

    def to_str(self, depth: int = 0):
        res: str = ("\t" * depth) + "MatchNode((\n"
        res += self.condition.to_str(depth+2)
        res += ("\t" * (depth+1)) + "),\n"
        for case in self.cases.keys():
            res += case.to_str(depth+1)
            res += ("\t" * (depth+1)) + "=>\n"
            res += self.cases[case].to_str(depth+1)
        res += ("\t" * depth) + ")\n"
        return res


class StructDefNode(ASTNode):
    """
    Represent a struct with its name, endianness and members.
    """
    def __init__(self, name_token: Token, endian: str = BIG_ENDIAN):
        self.name_token: Token = name_token
        self._members: List[StructMemberDeclareNode] = []
        self.endian: str = endian

    def add_member_node(self, member_node: Union[StructMemberDeclareNode, MatchNode]) -> None:
        """
        Add a new member in this struct.
        """
        self._members.append(member_node)

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "struct " + str(self.name_token) + "(\n"
        for node in self._members:
            res += node.to_str(depth + 1)
        return res + ")\n"

    @property
    def name(self) -> str:
        """
        Struct's name.
        """
        return str(self.name_token.value)

    @property
    def members(self) -> List[StructMemberDeclareNode]:
        """
        Struct's members.
        """
        return self._members


# bitfield
class BitfieldMemberNode(ASTNode):
    """
    Represent a member of a bitfield.
    """
    def __init__(self, name_token: Token, bits_count_node: Optional[ASTNode] = None):
        self.name_token: Token = name_token
        self.bits_count_node: Optional[ASTNode] = bits_count_node

    def set_explicit_size(self, bit_count_node: ASTNode):
        """
        Set the size of this member in bits.
        """
        self.bits_count_node = bit_count_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self.name_token)
        if self.bits_count_node is not None:
            res += "(\n" + self.bits_count_node.to_str(depth + 1) + ("\t" * depth) + ")"
        return res + "\n"

    @property
    def name(self) -> str:
        """
        Member's name.
        """
        return str(self.name_token.value)

    @property
    def size(self) -> ASTNode:
        """
        Member's size in bits as an expression.
        """
        return self.bits_count_node


class BitfieldDefNode(ASTNode):
    """
    Represent a bitfield with its members and its size (in bytes).
    """
    def __init__(self, name_token: Token, bitfield_bytes_count_token: Optional[ASTNode] = None):
        self.name_token: Token = name_token
        self.bitfield_bytes_count_token: Optional[ASTNode] = bitfield_bytes_count_token
        self.bitfield_members: List[BitfieldMemberNode] = []

    def set_explicit_size(self, bitfield_bytes_count_token: Token):
        """
        Set the size of this bitfield in bytes.
        Note that the size cannot be less than the sum of the size of its members.
        """
        self.bitfield_bytes_count_token = bitfield_bytes_count_token

    def add_member_node(self, member_node: BitfieldMemberNode) -> None:
        """
        Add a new member in this bitfield.
        """
        self.bitfield_members.append(member_node)

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self.name_token) + "\n"
        for node in self.bitfield_members:
            res += node.to_str(depth + 1)
        return res + "\n"

    @property
    def name(self) -> str:
        """
        Bitfield's name.
        """
        return str(self.name_token.value)

    @property
    def size(self) -> ASTNode:
        """
        Bitfield's size in bytes as an expression.
        """
        return self.bitfield_bytes_count_token

    @property
    def members(self) -> List[BitfieldMemberNode]:
        """
        Bitfield's members.
        """
        return self.bitfield_members
