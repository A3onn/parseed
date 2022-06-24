#!/usr/bin/env python3
from typing import Any, List
from abc import ABC, abstractmethod
from parser import StructDefNode
from utils import Token


class FloatNumber:
    def __init__(self, value_token: Token):
        if value_token.value is None:
            return  # disable mypy warning
        self.value = float(value_token.value)


class IntNumber:
    def __init__(self, value_token: Token):
        if value_token.value is None:
            return  # disable mypy warning
        self.value = int(value_token.value)


class StructMember:
    def __init__(self, name_token: Token, type_token: Token, is_list: bool = False, list_len_expr: Any = 0) -> None:
        self.name: str = str(name_token.value)
        self.type: str = str(type_token.value)
        self.is_list: bool = is_list
        self.list_len_expr: Any = list_len_expr


class Struct:
    def __init__(self, name_token: Token) -> None:
        self.name: str = str(name_token.value)
        self.members: List[StructMember] = []


class ParseedOutputGenerator(ABC):
    def __init__(self, ast: List[Any]):
        self.structs: List[Struct] = []
        self._init_intermediate_ast(ast)

    @abstractmethod
    def generate(self) -> str:
        pass

    def _init_intermediate_ast(self, ast: List[Any]):
        for node in ast:
            if isinstance(node, StructDefNode):
                struct: Struct = Struct(node.name_token)
                for struct_member_node in node.struct_members:
                    struct_member: StructMember = StructMember(
                        struct_member_node.name_token,
                        struct_member_node.type_token,
                        struct_member_node.is_list,
                        struct_member_node.list_length_node
                    )
                    struct.members.append(struct_member)

                self.structs.append(struct)
