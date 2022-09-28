#!/usr/bin/env python3
from typing import List, Optional, Union, Dict
from lexer import Token
from utils import BIG_ENDIAN, DataType
from abc import ABC, abstractmethod

class ASTNode(ABC):
    """
    Abstract class for nodes forming the AST of the Parseed code.
    """

    @abstractmethod
    def to_str(self, depth: int = 0):
        r"""
        Method used to print the AST in a pretty form.
        This function must be called from children nodes if the class has some (with depth=depth+1).
        The depth parameter must be used to add some padding ('\\t') before printing anything.

        :param depth: Number of '\\t' to add before, defaults to 0
        :type depth: int, optional
        """
        pass


class FloatNumberNode(ASTNode):
    """
    Represent a floating-point number.
    """

    def __init__(self, value_token: Token):
        """
        :param value_token: Token of the float number.
        :type value_token: Token
        """
        self._value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "FloatNumberNode(" + str(self._value_token.value) + ")\n"

    @property
    def value(self) -> float:
        """
        Value of this node as a float.
        """
        return float(self._value_token.value)


class IntNumberNode(ASTNode):
    """
    Represent an integer number.
    """

    def __init__(self, value_token: Token):
        """
        :param value_token: Token of the integer number.
        :type value_token: Token
        """
        self._value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "IntNumberNode(" + str(self._value_token.value) + ")\n"

    @property
    def value(self) -> int:
        """
        Value of this node as an int.
        """
        return int(self._value_token.value)


# operators
class BinOpNode(ASTNode):
    """
    Represent a binary operation between a two nodes (value or expression).
    """
    def __init__(self, left_node: ASTNode, op_token: Token, right_node: ASTNode):
        """
        :param left_node: Left node of the operation.
        :type left_node: ASTNode
        :param op_token: Token representing the operand.
        :type op_token: Token
        :param right_node: Right node of the operation.
        :type right_node: ASTNode
        """
        self._left_node: ASTNode = left_node
        self._op_token: Token = op_token
        self._right_node: ASTNode = right_node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "BinOpNode(\n" + self._left_node.to_str(depth + 1) \
            + ("\t" * (depth + 1)) + str(self._op_token) + "\n" \
            + self._right_node.to_str(depth + 1) \
            + ("\t" * depth) + ")\n"

    @property
    def op(self) -> str:
        """
        Operand token as a string.
        """
        return str(self._op_token.value)

    @property
    def left_node(self) -> ASTNode:
        """
        Left node of the operation.
        """
        return self._left_node

    @property
    def right_node(self) -> ASTNode:
        """
        Right node of the operation.
        """
        return self._right_node


class UnaryOpNode(ASTNode):
    """
    Represent an unary operation between an operand (-, +, /, etc...) and a node (value or expression).
    """
    def __init__(self, op_token: Token, node: ASTNode):
        """
        :param op_token: Token representing the operand.
        :type op_token: Token
        :param node: Node representing the value of the operation.
        :type node: ASTNode
        """
        self._op_token: Token = op_token
        self._node: ASTNode = node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "UnaryOpNode(\n" + ("\t" * (depth + 1)) + str(self._op_token) + "\n" + self._node.to_str(depth + 1) + ("\t" * depth) + ")\n"

    @property
    def op(self) -> str:
        """
        Operand node as a string.
        """
        return str(self._op_token.value)

    @property
    def value(self) -> ASTNode:
        """
        Node place a the right of the operand (thus the value).
        """
        return self._node


# struct
class IdentifierAccessNode(ASTNode):
    """
    This class contains the name of an identifier accessed.
    """
    def __init__(self, identifier_name: str):
        """
        :param identifier_name: Identifier as a string.
        :type identifier_name: str
        """
        self._name: str = identifier_name

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "IdentifierAccessNode(" + str(self._name) + ")\n"

    @property
    def name(self) -> str:
        """
        Name of the identifier.
        """
        return self._name


class ComparisonNode(ASTNode):
    """
    Represent a comparison between two AST nodes.
    """
    def __init__(self, left_cond_op: ASTNode, condition_op: str, right_cond_op: ASTNode):
        """
        :param left_cond_op: Left part of the comparison.
        :type left_cond_op: ASTNode
        :param condition_op: Comparison (eg. ==, !=, <) as a string.
        :type condition_op: str
        :param right_cond_op: Right part of the comparison.
        :type right_cond_op: ASTNode
        """
        self._left_cond_op: ASTNode = left_cond_op
        self._condition_op: str = condition_op
        self._right_cond_op: ASTNode = right_cond_op

    def to_str(self, depth: int = 0):
        res: str = self._left_cond_op.to_str(depth)
        res += ("\t" * depth) + self._condition_op + "\n"
        res += self._right_cond_op.to_str(depth)
        return res + "\n"

    @property
    def left_op(self) -> ASTNode:
        """
        Left operand of the comparison.
        """
        return self._left_cond_op

    @property
    def right_op(self) -> ASTNode:
        """
        Right operand of the comparison.
        """
        return self._right_cond_op

    @property
    def condition(self) -> str:
        """
        Condition operand of the comparison.
        """
        return self._condition_op


class TernaryDataTypeNode(ASTNode):
    """
    This class represents a ternary operator for data-types.
    """
    def __init__(self, comparison_node: ComparisonNode, if_true: Union[IdentifierAccessNode, DataType], if_false: Union[IdentifierAccessNode, DataType]):
        """
        :param comparison_node: Comparison of the ternary operator.
        :type comparison_node: ComparisonNode
        :param if_true: Type used if the comparison is true.
        :type if_true: Union[IdentifierAccessNode, DataType]
        :param if_false: Type used if the comparison if false.
        :type if_false: Union[IdentifierAccessNode, DataType]
        """
        self._comparison: ComparisonNode = comparison_node
        self._if_true: Union[IdentifierAccessNode, DataType] = if_true
        self._if_false: Union[IdentifierAccessNode, DataType] = if_false

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "TernaryDataType(\n"
        res += self._comparison.to_str(depth+1)
        res += ("\t" * (depth+1)) + "?\n"

        if isinstance(self._if_true, IdentifierAccessNode):
            res += self._if_true.to_str(depth+2) + "\n"
        else:
            res += ("\t" * (depth+1)) + str(self._if_true) + "\n"

        res += ("\t" * (depth+1)) + ":\n"

        if isinstance(self._if_false, IdentifierAccessNode):
            res += self._if_false.to_str(depth+2) + "\n)"
        else:
            res += ("\t" * (depth+1)) + str(self._if_false) + "\n"
        return res + ("\t" * depth) + ")" + "\n"
    
    @property
    def comparison(self) -> ComparisonNode:
        """
        Comparison node of ternary operator.
        """
        return self._comparison

    @property
    def if_true(self) -> Union[IdentifierAccessNode, DataType]:
        """
        Node used if the comparison is true.
        """
        return self._if_true

    @property
    def if_false(self) -> Union[IdentifierAccessNode, DataType]:
        """
        Node used if the comparison is false.
        """
        return self._if_false


class StructMemberTypeNode(ASTNode):
    """
    Represents the type of a member.
    This class contains the type, the endianness, if it is a list and it length (if it has one).
    """
    def __init__(self, type_token: Union[Token,TernaryDataTypeNode], endian: str = BIG_ENDIAN, is_list: bool = False, list_length_node: Union[None,UnaryOpNode,BinOpNode] = None, string_delimiter: str = r"\0"):
        r"""
        :param type_token: Token or ternary operator for the type of the member.
        :type type_token: Union[Token,TernaryDataTypeNode]
        :param endian: Endianness of the member, defaults to big.
        :type endian: str, optional
        :param is_list: If the member is a list, defaults to False.
        :type is_list: bool, optional
        :param list_length_node: Length of the list if this member is a list, defaults to None
        :type list_length_node: Union[None,UnaryOpNode,BinOpNode]
        :param string_delimiter: If the type is a string, the delimiter of the string, default to '\\0'.
        :type string_delimiter: str
        """
        self._type: Union[Token,TernaryDataTypeNode] = type_token
        self._endian: str = endian
        self._is_list: bool = is_list
        self._list_length_node: Union[None,UnaryOpNode,BinOpNode] = list_length_node
        self._string_delimiter: str = string_delimiter

    def to_str(self, depth: int = 0) -> str:
        if self._is_list:
            if self._list_length_node != None:
                return ("\t" * depth) + "StructMemberTypeNode(" + str(self._type) + f"[\n{self._list_length_node.to_str(depth+1)}" + ("\t" * depth) + "])\n"
            return ("\t" * depth) + "StructMemberTypeNode(" + str(self._type) + f"[])\n"
        return ("\t" * depth) + "StructMemberTypeNode(" + str(self._type) + ")\n"

    @property
    def type(self) -> Union[str,TernaryDataTypeNode]:
        """
        Type of the member.
        """
        if isinstance(self._type, Token):
            return str(self._type.value)
        return self._type

    @property
    def endian(self) -> str:
        """
        Endianness of the member.
        """
        return self._endian

    @property
    def is_list(self) -> bool:
        """
        True if this member a list.
        """
        return self._is_list

    @property
    def list_length(self) -> Union[None,UnaryOpNode,BinOpNode]:
        """
        The length of this member (if it is a list, otherwise None).
        """
        return self._list_length_node

    @property
    def string_delimiter(self) -> str:
        """
        Delimiter of the string, if the type is a string.
        """
        return self._string_delimiter

    def as_data_type(self) -> Optional[DataType]:
        """
        Return the type as a DataType if the type is not a ternary operator.

        :return: The type as DataType.
        :rtype: DataType, optional
        """
        if isinstance(self.type, TernaryDataTypeNode):
            return None
        return DataType(self.type, string_delimiter=self.string_delimiter)


class StructMemberDeclareNode(ASTNode):
    """
    Represent a member of a struct.
    It contains the name and the type of the member.
    """
    def __init__(self, type_: StructMemberTypeNode, name_token: Token):
        """
        :param type_: Type of the member.
        :type type_: StructMemberTypeNode
        :param name_token: Token representing the name of the member.
        :type name_token: Token
        """
        self._type: StructMemberTypeNode = type_
        self._name_token: Token = name_token

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "StructMemberDeclareNode(\n"
        res += self._type.to_str(depth+1)
        res += ("\t" * (depth+1)) + str(self._name_token) + "\n" + ("\t" * depth) + ")\n"
        return res

    @property
    def type(self) -> StructMemberTypeNode:
        """
        Type of the member.
        """
        return self._type

    @property
    def name(self) -> str:
        """
        Member's name.
        """
        return str(self._name_token.value)


class MatchNode(ASTNode):
    """
    Represent a match expression inside structs.
    """
    def __init__(self, condition: ASTNode, cases: Dict[ASTNode,Union[StructMemberTypeNode,List[StructMemberDeclareNode]]], member_name: str = None):
        """
        :param condition: The condition that one case must match.
        :type condition: ASTNode
        :param cases: Cases of the match expression.
        :type cases: Dict[ASTNode,Union[StructMemberTypeNode,List[StructMemberDeclareNode]]]
        :param member_name: If this match is used to select the type of a member, this is its name, defaults to None.
        :type member_name: str, optional
        """
        self._condition: ASTNode = condition
        self._cases: Dict[ASTNode,Union[StructMemberTypeNode,List[StructMemberDeclareNode]]] = cases
        self._member_name: str = member_name

    def to_str(self, depth: int = 0):
        res: str = ("\t" * depth) + "MatchNode((\n"
        res += self._condition.to_str(depth+2)
        res += ("\t" * (depth+1)) + "),\n"
        for case in self._cases.keys():
            res += case.to_str(depth+1)
            res += ("\t" * (depth+1)) + "=>\n"
            res += self._cases[case].to_str(depth+1)
        res += ("\t" * depth) + ")\n"
        return res

    @property
    def condition(self) -> ASTNode:
        """
        The condition the cases will have to match.
        """
        return self._condition

    @property
    def cases(self) -> Dict[ASTNode,Union[StructMemberTypeNode,List[StructMemberDeclareNode]]]:
        """
        Cases of this match expression.
        """
        return self._cases

    @property
    def member_name(self) -> str:
        """
        Member's name if this match is used to select the type of a member.
        """
        return self._member_name


class StructDefNode(ASTNode):
    """
    Represent a struct with its name, endianness and members.
    """
    def __init__(self, name_token: Token, members: List[Union[StructMemberDeclareNode, MatchNode]], endian: str = BIG_ENDIAN):
        """
        :param name_token: Token representing the name of the struct.
        :type name_token: Token
        :param members: List of members of this struct.
        :type members: List[Union[StructMemberDeclareNode, MatchNode]]
        :param endian: Endianness of the struct, defaults to big.
        :type endian: str, optional
        """
        self._name_token: Token = name_token
        self._members: List[Union[StructMemberDeclareNode, MatchNode]] = members
        self._endian: str = endian

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "struct " + str(self._name_token) + "(\n"
        for node in self._members:
            res += node.to_str(depth + 1)
        return res + ")\n"

    @property
    def name(self) -> str:
        """
        Struct's name.
        """
        return str(self._name_token.value)

    @property
    def members(self) -> List[StructMemberDeclareNode]:
        """
        Struct's members.
        """
        return self._members

    @property
    def endian(self) -> str:
        """
        Endianness of the struct.
        """
        return self._endian


# bitfield
class BitfieldMemberNode(ASTNode):
    """
    Represent a member of a bitfield.
    """
    def __init__(self, name_token: Token, bits_count_node: Optional[ASTNode] = None):
        """
        :param name_token: Token representing the name of the member.
        :type name_token: Token
        :param bits_count_node: How many bits this member takes (if declared), defaults to None
        :type bits_count_node: Optional[ASTNode], optional
        """
        self._name_token: Token = name_token
        self._bits_count_node: Optional[ASTNode] = bits_count_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self.name_token)
        if self._bits_count_node is not None:
            res += "(\n" + self._bits_count_node.to_str(depth + 1) + ("\t" * depth) + ")"
        return res + "\n"

    @property
    def name(self) -> str:
        """
        Member's name.
        """
        return str(self._name_token.value)

    @property
    def size(self) -> ASTNode:
        """
        Member's size in bits as an expression.
        """
        return self._bits_count_node


class BitfieldDefNode(ASTNode):
    """
    Represent a bitfield with its members and its size (in bytes).
    """
    def __init__(self, name_token: Token, members: List[BitfieldMemberNode], bitfield_bytes_count_token: Optional[ASTNode] = None):
        """
        :param name_token: Token representing the name of the bitfield.
        :type name_token: Token
        :param members: List of members in the bitfield.
        :type members: List[BitfieldMemberNode]
        :param bitfield_bytes_count_token: How many bytes this bitfield takes (if declared), defaults to None
        :type bitfield_bytes_count_token: Optional[ASTNode], optional
        """
        self._name_token: Token = name_token
        self._bitfield_bytes_count_token: Optional[ASTNode] = bitfield_bytes_count_token
        self._bitfield_members: List[BitfieldMemberNode] = members

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self._name_token) + "\n"
        for node in self._bitfield_members:
            res += node.to_str(depth + 1)
        return res + "\n"

    @property
    def name(self) -> str:
        """
        Name of this bitfield.
        """
        return str(self._name_token.value)

    @property
    def size(self) -> ASTNode:
        """
        Size of this bitfield in bytes as an expression.
        """
        return self._bitfield_bytes_count_token

    @property
    def members(self) -> List[BitfieldMemberNode]:
        """
        Members of this bitfield.
        """
        return self._bitfield_members
