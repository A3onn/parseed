#!/usr/bin/env python3
from typing import Any, List, Optional
from lexer import Token
from utils import BIG_ENDIAN


class FloatNumberNode:
    def __init__(self, value_token: Token):
        self.value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "FloatNumberNode(" + str(self.value_token.value) + ")\n"

    @property
    def value(self) -> float:
        return float(self.value_token.value)


class IntNumberNode:
    def __init__(self, value_token: Token):
        self.value_token: Token = value_token

    def to_str(self, depth: int = 0) -> str:
        return "\t" * depth + "IntNumberNode(" + str(self.value_token.value) + ")\n"

    @property
    def value(self) -> int:
        return int(self.value_token.value)


# operators
class BinOpNode:
    def __init__(self, left_node: Any, op_token: Token, right_node: Any):
        self.left_node: Any = left_node
        self.op_token: Token = op_token
        self.right_node: Any = right_node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "BinOpNode(\n" + self.left_node.to_str(depth + 1) \
            + ("\t" * (depth + 1)) + str(self.op_token) + "\n" \
            + self.right_node.to_str(depth + 1) \
            + ("\t" * depth) + ")\n"

    @property
    def op(self) -> str:
        return str(self.op_token.value)

    @property
    def left(self) -> Any:
        return self.left_node

    @property
    def right(self) -> Any:
        return self.right_node


class UnaryOpNode:
    def __init__(self, op_token: Token, node: Any):
        self.op_token: Token = op_token
        self.node: Any = node

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "UnaryOpNode(\n" + ("\t" * (depth + 1)) + str(self.op_token) + "\n" + self.node.to_str(depth + 1) + ")\n"

    @property
    def op(self) -> str:
        return str(self.op_token.value)

    @property
    def value(self) -> Any:
        return self.node


# struct
class StructMemberAccessNode:
    def __init__(self, name_token: Token):
        self.name_token: Token = name_token

    def to_str(self, depth: int = 0) -> str:
        return ("\t" * depth) + "StructMemberAccessNode(" + str(self.name_token) + ")\n"

    @property
    def name(self) -> str:
        return str(self.name_token.value)


class StructMemberDeclareNode:
    def __init__(self, type_token: Token, name_token: Token, is_list: bool, list_length_node: Optional[Any] = None, endian: str = BIG_ENDIAN):
        self.type_token: Token = type_token
        self.name_token: Token = name_token
        self._is_list: bool = is_list
        self._endian: str = endian
        self.list_length_node: Optional[Any] = list_length_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "StructMemberDeclareNode(" + str(self.type_token) + " " + str(self.name_token)
        if self.is_list and self.list_length_node:
            res += " [\n" + self.list_length_node.to_str(depth + 1) + ("\t" * depth) + "]"
        return res + ")\n"

    @property
    def token_name(self) -> Token:
        return self.name_token

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def type(self) -> str:
        return str(self.type_token.value)

    @property
    def list_length(self) -> int:
        return int(self.list_length_node.value)

    def is_list(self) -> bool:
        return self._is_list

    @property
    def endian(self) -> str:
        return self._endian


class StructDefNode:
    def __init__(self, name_token: Token, endian: str = BIG_ENDIAN):
        self.name_token: Token = name_token
        self.struct_members: List[StructMemberDeclareNode] = []
        self._endian: str = endian

    def add_member_node(self, member_node: StructMemberDeclareNode) -> None:
        self.struct_members.append(member_node)

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "struct " + str(self.name_token) + "(\n"
        for node in self.struct_members:
            res += node.to_str(depth + 1)
        return res + ")\n"

    @property
    def token_name(self) -> Token:
        return self.name_token

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def members(self) -> List[StructMemberDeclareNode]:
        return self.struct_members

    @property
    def endian(self) -> str:
        return self._endian


# bitfield
class BitfieldMemberNode:
    def __init__(self, name_token: Token, bits_count_node: Optional[Any] = None):
        self.name_token: Token = name_token
        self.bits_count_node: Optional[Any] = bits_count_node

    def set_explicit_size(self, bit_count_node: Any):
        self.bits_count_node = bit_count_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self.name_token)
        if self.bits_count_node is not None:
            res += "(\n" + self.bits_count_node.to_str(depth + 1) + ("\t" * depth) + ")"
        return res + "\n"

    @property
    def token_name(self) -> Token:
        return self.name_token

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def size(self) -> Any:
        return self.bits_count_node


class BitfieldDefNode:
    def __init__(self, name_token: Token, bitfield_bytes_count_token: Optional[Any] = None):
        self.name_token: Token = name_token
        self.bitfield_bytes_count_token: Optional[Any] = bitfield_bytes_count_token
        self.bitfield_members: List[BitfieldMemberNode] = []

    def set_explicit_size(self, bitfield_bytes_count_token: Token):
        self.bitfield_bytes_count_token = bitfield_bytes_count_token

    def add_member_node(self, member_node: BitfieldMemberNode) -> None:
        self.bitfield_members.append(member_node)

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + str(self.name_token) + "\n"
        for node in self.bitfield_members:
            res += node.to_str(depth + 1)
        return res + "\n"

    @property
    def token_name(self) -> Token:
        return self.name_token

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def size(self) -> Any:
        return self.bitfield_bytes_count_token

    @property
    def members(self) -> List[BitfieldMemberNode]:
        return self.bitfield_members
