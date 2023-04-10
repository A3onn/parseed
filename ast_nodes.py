#!/usr/bin/env python3
from typing import Generator, List, Optional, Union, Dict, NewType
from lexer import *
from abc import ABC, abstractmethod
from utils import DataType

# Just to have better typing annotations
ComparisonOperatorType = NewType("ComparisonOperatorType", str)
MathOperationType = NewType("MathOperationType", str)


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
class MathOperatorNode(ASTNode):
    """
    Represent a mathematical operator (+, -, /, *) or a binary operator (&, |, ^, ~, <<, >>).
    """

    ADD: MathOperationType = MathOperationType("ADD")
    SUBTRACT: MathOperationType = MathOperationType("SUBTRACT")
    DIVIDE: MathOperationType = MathOperationType("DIVIDE")
    MULTIPLY: MathOperationType = MathOperationType("MULTIPLY")
    AND: MathOperationType = MathOperationType("AND")
    OR: MathOperationType = MathOperationType("OR")
    XOR: MathOperationType = MathOperationType("XOR")
    NOT: MathOperationType = MathOperationType("NOT")
    LEFT_SHIFT: MathOperationType = MathOperationType("LEFT_SHIFT")
    RIGHT_SHIFT: MathOperationType = MathOperationType("RIGHT_SHIFT")

    def __init__(self, op_token):
        self._math_op_token: Token = op_token

    def to_str(self, depth: int = 0):
        return ("\t" * depth) + "MathOperationNode(" + self.type + ")\n"

    @property
    def type(self) -> MathOperationType:
        """
        Type of the operator.
        Is one of:
        - MathOperatorNode.ADD
        - MathOperatorNode.SUBTRACT
        - MathOperatorNode.DIVIDE
        - MathOperatorNode.MULTIPLY
        - MathOperatorNode.AND
        - MathOperatorNode.OR
        - MathOperatorNode.XOR
        - MathOperatorNode.NOT
        - MathOperatorNode.LEFT_SHIFT
        - MathOperatorNode.RIGHT_SHIFT
        """
        math_op_dict: Dict[str, MathOperationType] = {
            TT_PLUS: MathOperatorNode.ADD,
            TT_MINUS: MathOperatorNode.SUBTRACT,
            TT_DIV: MathOperatorNode.DIVIDE,
            TT_MULT: MathOperatorNode.MULTIPLY,
            TT_BIN_AND: MathOperatorNode.AND,
            TT_BIN_OR: MathOperatorNode.OR,
            TT_BIN_XOR: MathOperatorNode.XOR,
            TT_BIN_NOT: MathOperatorNode.NOT,
            TT_BIN_LSHIFT: MathOperatorNode.LEFT_SHIFT,
            TT_BIN_RSHIFT: MathOperatorNode.RIGHT_SHIFT
        }
        return math_op_dict[self._math_op_token.type]

    def __eq__(self, o) -> bool:
        return self.type == o


class BinOpNode(ASTNode):
    """
    Represent a binary operation between a two nodes (value or expression).
    """
    def __init__(self, left_node: ASTNode, math_op: MathOperatorNode, right_node: ASTNode):
        """
        :param left_node: Left node of the operation.
        :type left_node: ASTNode
        :param math_op: Operand of the operation.
        :type math_op: MathOperatorNode
        :param right_node: Right node of the operation.
        :type right_node: ASTNode
        """
        self._left_node: ASTNode = left_node
        self._math_op: MathOperatorNode = math_op
        self._right_node: ASTNode = right_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "BinOpNode(\n"
        res += self._left_node.to_str(depth + 1)
        res += self._math_op.to_str(depth + 1)
        res += self._right_node.to_str(depth + 1)
        res += ("\t" * depth) + ")\n"
        return res

    @property
    def op(self) -> MathOperatorNode:
        """
        Operator of the operation.
        """
        return self._math_op

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
    Represent an unary operation between an mathematical operator and a node (value or expression).
    """
    def __init__(self, math_op: MathOperatorNode, node: ASTNode):
        """
        :param math_op: Mathematical operator of the operation.
        :type math_op: MathOperatorNode
        :param node: Node representing the value of the operation.
        :type node: ASTNode
        """
        self._math_op: MathOperatorNode = math_op
        self._node: ASTNode = node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "UnaryOpNode(\n"
        res += self._math_op.to_str(depth + 1)
        res += self._node.to_str(depth + 1)
        res += ("\t" * depth) + ")\n"
        return res

    @property
    def op(self) -> MathOperatorNode:
        """
        Operator of the operation.
        """
        return self._math_op

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
        Name of the whole identifier (meaning with dots).
        """
        return self._name

    def get_names(self) -> Generator:
        """
        Generator returning each sub-identifier composing this identifier.
        Example:
            my_val.sub_member.another_sub_member

            This will return:
                IdentifierAccessNode(my_val)
                IdentifierAccessNode(sub_member)
                IdentifierAccessNode(another_sub_member)

        :return: a generator for sub-identifier
        :rtype: Generator[IdentifierAccessNode]
        """
        for name in self.name.split("."):
            yield IdentifierAccessNode(name)


class ComparisonOperatorNode(ASTNode):
    """
    Represents a relational operator (e.g. !=, ==, <, etc...).
    """

    LESS_THAN: ComparisonOperatorType = ComparisonOperatorType("LESS_THAN")
    GREATER_THAN: ComparisonOperatorType = ComparisonOperatorType("GREATER_THAN")
    EQUAL: ComparisonOperatorType = ComparisonOperatorType("EQUAL")
    NOT_EQUAL: ComparisonOperatorType = ComparisonOperatorType("NOT_EQUAL")
    LESS_OR_EQUAL: ComparisonOperatorType = ComparisonOperatorType("LESS_OR_EQUAL")
    GREATER_OR_EQUAL: ComparisonOperatorType = ComparisonOperatorType("GREATER_OR_EQUAL")
    AND: ComparisonOperatorType = ComparisonOperatorType("AND")
    OR: ComparisonOperatorType = ComparisonOperatorType("OR")

    def __init__(self, comp_op_token: Token):
        """
        :param comp_op_token: Token of the comparison operator.
        :type comp_op_token: Token
        """
        self._comp_op_token: Token = comp_op_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "ComparisonOperatorNode(" + str(self.type) + ")\n"

    @property
    def type(self) -> ComparisonOperatorType:
        """
        Type of the comparison operator.
        Is one of:
        - ComparisonOperatorNode.LESS_THAN
        - ComparisonOperatorNode.GREATER_THAN
        - ComparisonOperatorNode.EQUAL
        - ComparisonOperatorNode.NOT_EQUAL
        - ComparisonOperatorNode.LESS_OR_EQUAL
        - ComparisonOperatorNode.GREATER_OR_EQUAL
        - ComparisonOperatorNode.AND
        - ComparisonOperatorNode.OR
        """
        comp_dict: Dict[str, ComparisonOperatorType] = {
            TT_COMP_EQ: ComparisonOperatorNode.EQUAL,
            TT_COMP_NE: ComparisonOperatorNode.NOT_EQUAL,
            TT_COMP_GT: ComparisonOperatorNode.GREATER_THAN,
            TT_COMP_LT: ComparisonOperatorNode.LESS_THAN,
            TT_COMP_GEQ: ComparisonOperatorNode.GREATER_OR_EQUAL,
            TT_COMP_LEQ: ComparisonOperatorNode.LESS_OR_EQUAL,
            TT_COMP_AND: ComparisonOperatorNode.AND,
            TT_COMP_OR: ComparisonOperatorNode.OR
        }
        return comp_dict[self._comp_op_token.type]

    def __eq__(self, o) -> bool:
        return self.type == o

class ComparisonNode(ASTNode):
    """
    Represent a comparison between two AST nodes.
    """
    def __init__(self, left_node: ASTNode, comparison_op: ComparisonOperatorNode, right_node: ASTNode):
        """
        :param left_node: Left part of the comparison.
        :type left_node: ASTNode
        :param comparison_op: Relational operator of the comparison.
        :type comparison_op: ComparisonOperatorNode
        :param right_node: Right part of the comparison.
        :type right_node: ASTNode
        """
        self._left_node: ASTNode = left_node
        self._comparison_op: ComparisonOperatorNode = comparison_op
        self._right_node: ASTNode = right_node

    def to_str(self, depth: int = 0):
        res: str = self._left_node.to_str(depth)
        res += self._comparison_op.to_str(depth)
        res += self._right_node.to_str(depth)
        return res + "\n"

    @property
    def left_node(self) -> ASTNode:
        """
        Left node of the comparison.
        """
        return self._left_node

    @property
    def right_node(self) -> ASTNode:
        """
        Right node of the comparison.
        """
        return self._right_node

    @property
    def comparison_op(self) -> ComparisonOperatorNode:
        """
        Relational operator of the comparison.
        """
        return self._comparison_op


class TernaryDataTypeNode(ASTNode):
    """
    This class represents a ternary operator for data-types.
    """
    def __init__(self, comparison_node: ComparisonNode, if_true, if_false):
        """
        :param comparison_node: Comparison of the ternary operator.
        :type comparison_node: ComparisonNode
        :param if_true: Type used if the comparison is true (endian property won't be used).
        :type if_true: StructMemberInfoNode
        :param if_false: Type used if the comparison if false (endian property won't be used).
        :type if_false: StructMemberInfoNode
        """
        self._comparison: ComparisonNode = comparison_node
        self._if_true = if_true
        self._if_false = if_false

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "TernaryDataType(\n"
        res += self._comparison.to_str(depth + 1)
        res += ("\t" * (depth + 1)) + "?\n"

        if isinstance(self._if_true, IdentifierAccessNode) or isinstance(self._if_false, StructMemberInfoNode):
            res += self._if_true.to_str(depth + 2) + "\n"
        else:
            res += ("\t" * (depth + 1)) + str(self._if_true) + "\n"

        res += ("\t" * (depth + 1)) + ":\n"

        if isinstance(self._if_false, IdentifierAccessNode) or isinstance(self._if_false, StructMemberInfoNode):
            res += self._if_false.to_str(depth + 2) + "\n"
        else:
            res += ("\t" * (depth + 1)) + str(self._if_false) + "\n"
        return res + ("\t" * depth) + ")" + "\n"

    @property
    def comparison(self) -> ComparisonNode:
        """
        Comparison node of ternary operator.
        """
        return self._comparison

    @property
    def if_true(self):
        """
        Data-type used if the comparison is true.
        """
        return self._if_true

    @property
    def if_false(self):
        """
        Data-type used if the comparison is false.
        """
        return self._if_false


class TernaryEndianNode(ASTNode):
    """
    This class represents a ternary operator for endianness.
    """
    def __init__(self, comparison_node: ComparisonNode, if_true: Endian, if_false: Endian):
        """
        :param comparison_node: Comparison of the ternary operator.
        :type comparison_node: ComparisonNode
        :param if_true: Endian used if the comparison is true.
        :type if_true: Endian
        :param if_false: Endian used if the comparison if false.
        :type if_false: Endian
        """
        self._comparison: ComparisonNode = comparison_node
        self._if_true: Endian = if_true
        self._if_false: Endian = if_false

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "TernaryEndianType(\n"
        res += self._comparison.to_str(depth + 1)
        res += ("\t" * (depth + 1)) + "?\n"
        res += ("\t" * (depth + 1)) + str(self._if_true) + "\n"

        res += ("\t" * (depth + 1)) + ":\n"
        res += ("\t" * (depth + 1)) + str(self._if_false) + "\n"

        return res + ("\t" * depth) + ")" + "\n"

    @property
    def comparison(self) -> ComparisonNode:
        """
        Comparison node of ternary operator.
        """
        return self._comparison

    @property
    def if_true(self) -> Endian:
        """
        Node used if the comparison is true.
        """
        return self._if_true

    @property
    def if_false(self) -> Endian:
        """
        Node used if the comparison is false.
        """
        return self._if_false


class StructMemberInfoNode(ASTNode):
    """
    Represents the type of a member.
    This class contains the type, the endianness, if it is a list and it length (if it has one).
    """
    def __init__(self, type_token: Union[Token, TernaryDataTypeNode], endian: Union[Endian, TernaryEndianNode] = Endian.BIG, is_list: bool = False, list_length_node: Union[None, UnaryOpNode, BinOpNode, ComparisonNode] = None, delimiter: str = r"\0"):
        r"""
        :param type_token: Token or ternary operator for the type of the member.
        :type type_token: Union[Token,TernaryDataTypeNode]
        :param endian: Endianness of the member, defaults to big.
        :type endian: Union[Endian, TernaryEndianNode]
        :param is_list: If the member is a list, defaults to False.
        :type is_list: bool, optional
        :param list_length_node: Length of the list (as a integer or a comparison if the member is repeated) if this member is a list, can be None to indicates no length is specified, defaults to None.
        :type list_length_node: Union[None,UnaryOpNode,BinOpNode,ComparisonNode]
        :param delimiter: If the type is a string or a bytes, the delimiter of the string or the bytes, default to '\\0'.
        :type delimiter: str
        """
        self._type: Union[Token, TernaryDataTypeNode] = type_token
        self._endian: Union[Endian, TernaryEndianNode] = endian
        self._is_list: bool = is_list
        self._list_length_node: Union[None, UnaryOpNode, BinOpNode, ComparisonNode] = list_length_node
        self._delimiter: str = delimiter

    def to_str(self, depth: int = 0) -> str:
        type_str: str = ""
        endian_str: str = ""
        list_str: str = ""

        if isinstance(self._type, TernaryDataTypeNode):
            type_str = self._type.to_str(depth + 1)
        else:
            type_str = ("\t" * (depth + 1)) + str(self._type) + "\n"

        if isinstance(self._endian, TernaryEndianNode):
            endian_str = self._endian.to_str(depth + 1)
        else:
            endian_str = ("\t" * (depth + 1)) + str(self._endian) + "\n"

        if self._is_list:
            if self._list_length_node is not None:
                list_str = ("\t" * (depth + 1)) + "[\n" + self._list_length_node.to_str(depth + 2) + ("\t" * (depth + 1)) + "]\n"
            else:
                list_str = "[]\n"

        res: str = ("\t" * depth) + "StructMemberInfoNode(\n"
        if endian_str != "":
            res += endian_str
        res += type_str
        if list_str != "":
            res += list_str
        res += ("\t" * depth) + ")\n"
        return res

    @property
    def type(self) -> Union[str, TernaryDataTypeNode]:
        """
        Type of the member.
        """
        if isinstance(self._type, Token):
            return str(self._type.value)
        return self._type

    @property
    def endian(self) -> Union[Endian, TernaryEndianNode]:
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
    def list_length(self) -> Union[None, UnaryOpNode, BinOpNode, ComparisonNode]:
        """
        The length of this member (if it is a list, otherwise None).
        """
        return self._list_length_node

    @property
    def delimiter(self) -> str:
        """
        Delimiter of the string or bytes, if the type is a string or a bytes.
        """
        return self._delimiter

    def as_data_type(self) -> Optional[DataType]:
        """
        Return the type as a DataType if the type is not a ternary operator.
        The type can be an identifier.

        :return: The type as DataType.
        :rtype: DataType, optional
        """
        if isinstance(self.type, TernaryDataTypeNode):
            return None
        return DataType(self.type, delimiter=self.delimiter)


class StructMemberDeclareNode(ASTNode):
    """
    Represent a member of a struct.
    It contains the name and the type of the member.
    """
    def __init__(self, infos: StructMemberInfoNode, name_token: Token):
        """
        :param infos: Type of the member.
        :type infos: StructMemberInfoNode
        :param name_token: Token representing the name of the member.
        :type name_token: Token
        """
        self._infos: StructMemberInfoNode = infos
        self._name_token: Token = name_token

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "StructMemberDeclareNode(\n"
        res += self._infos.to_str(depth + 1)
        res += ("\t" * (depth + 1)) + str(self._name_token) + "\n" + ("\t" * depth) + ")\n"
        return res

    @property
    def infos(self) -> StructMemberInfoNode:
        """
        Informations about the member (type, endian, is_list etc...) as a StructMemberInfoNode.
        """
        return self._infos

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
    def __init__(self, condition: ASTNode, cases: Dict[ASTNode, Union[StructMemberInfoNode, List[StructMemberDeclareNode]]], member_name: str = None):
        """
        :param condition: The condition that one case must match.
        :type condition: ASTNode
        :param cases: Cases of the match expression.
        :type cases: Dict[ASTNode,Union[StructMemberInfoNode,List[StructMemberDeclareNode]]]
        :param member_name: If this match is used to select the type of a member, this is its name, defaults to None.
        :type member_name: str, optional
        """
        self._condition: ASTNode = condition
        self._cases: Dict[ASTNode, Union[StructMemberInfoNode, List[StructMemberDeclareNode]]] = cases
        self._member_name: Optional[str] = member_name

    def to_str(self, depth: int = 0):
        res: str = ("\t" * depth) + "MatchNode((\n"
        res += self._condition.to_str(depth + 2)
        res += ("\t" * (depth + 1)) + "),\n"
        for case in self._cases.keys():
            res += case.to_str(depth + 1)
            res += ("\t" * (depth + 1)) + "=>\n"
            if isinstance(self._cases[case], list):
                res += ("\t" * (depth + 1)) + "{"
                for struct_member in self._cases[case]:
                    res += struct_member.to_str(depth + 2)
                res += ("\t" * (depth + 1)) + "}"
            else:
                res += self._cases[case].to_str(depth + 1)
        res += ("\t" * depth) + ")\n"
        return res

    @property
    def condition(self) -> ASTNode:
        """
        The condition the cases will have to match.
        """
        return self._condition

    @property
    def cases(self) -> Dict[ASTNode, Union[StructMemberInfoNode, List[StructMemberDeclareNode]]]:
        """
        Cases of this match expression.
        """
        return self._cases

    @property
    def member_name(self) -> Optional[str]:
        """
        Member's name if this match is used to select the type of a member.
        """
        return self._member_name


class StructDefNode(ASTNode):
    """
    Represent a struct with its name, endianness and members.
    """
    def __init__(self, name_token: Token, members: List[Union[StructMemberDeclareNode, MatchNode]], endian: Union[TernaryEndianNode, Endian] = Endian.BIG):
        """
        :param name_token: Token representing the name of the struct.
        :type name_token: Token
        :param members: List of members of this struct.
        :type members: List[Union[StructMemberDeclareNode, MatchNode]]
        :param endian: Endianness of the struct, defaults to big.
        :type endian: Union[TernaryEndianNode, Endian]
        """
        self._name_token: Token = name_token
        self._members: List[Union[StructMemberDeclareNode, MatchNode]] = members
        self._endian: Union[TernaryEndianNode, Endian] = endian

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
    def members(self) -> List[Union[StructMemberDeclareNode, MatchNode]]:
        """
        Struct's members.
        """
        return self._members

    @property
    def endian(self) -> Union[TernaryEndianNode, Endian]:
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
        res: str = ("\t" * depth) + str(self.name)
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
        If the size was not declare, returns IntNumberNode of 1
        """
        if self._bits_count_node is None:
            return IntNumberNode(Token(TT_NUM_INT, "1"))
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
        :param bitfield_bytes_count_token: How many bytes this bitfield takes, defaults to None.
        :type bitfield_bytes_count_token: ASTNode, optional
        """
        self._name_token: Token = name_token
        self._bitfield_bytes_count_token: Optional[ASTNode] = bitfield_bytes_count_token
        self._bitfield_members: List[BitfieldMemberNode] = members

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "BitfieldDefNode(" + str(self._name_token) + "\n"
        res += ("\t" * (depth + 1)) + "(\n"
        res += self.size.to_str(depth + 1)
        res += ("\t" * (depth + 1)) + ")\n"
        for node in self._bitfield_members:
            res += node.to_str(depth + 1)
        res += ("\t" * depth) + ")\n"
        return res

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
        If the size was not given, this size will be the sum of all members' size of this bitfield.
        """
        if self._bitfield_bytes_count_token is not None:
            return self._bitfield_bytes_count_token

        if len(self.members) == 0:
            return IntNumberNode(Token(TT_NUM_INT, "0"))
        if len(self.members) == 1:
            return self.members[0].size
        elif len(self.members) == 2:
            return BinOpNode(self.members[0].size, MathOperatorNode(Token(TT_PLUS)), self.members[1].size)

        # generate the sum of sizes
        res: BinOpNode = BinOpNode(self.members[0].size, MathOperatorNode(Token(TT_PLUS)), None)

        tmp: BinOpNode = BinOpNode(None, MathOperatorNode(Token(TT_PLUS)), None)
        res._right_node = tmp
        for i in range(1, len(self.members) - 2):
            tmp._left_node = self.members[i].size
            tmp._math_op = MathOperatorNode(Token(TT_PLUS))
            tmp._right_node = BinOpNode(None, MathOperatorNode(Token(TT_PLUS)), None)
            tmp = tmp._right_node

        tmp._left_node = self.members[-2].size
        tmp._math_op = MathOperatorNode(Token(TT_PLUS))
        tmp._right_node = self.members[-1].size
        print(self.members[-2].to_str())
        return res

    @property
    def members(self) -> List[BitfieldMemberNode]:
        """
        Members of this bitfield.
        """
        return self._bitfield_members
