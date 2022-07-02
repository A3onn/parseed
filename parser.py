#!/usr/bin/env python3
from typing import List, Any, Optional
from errors import InvalidSyntaxError
from utils import *


# NODES
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
    def __init__(self, type_token: Token, name_token: Token, is_list: bool, list_length_node: Optional[Any] = None):
        self.type_token: Token = type_token
        self.name_token: Token = name_token
        self.is_list: bool = is_list
        self.list_length_node: Optional[Any] = list_length_node

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "StructMemberDeclareNode(" + str(self.type_token) + " " + str(self.name_token)
        if self.is_list and self.list_length_node:
            res += " [\n" + self.list_length_node.to_str(depth + 1) + ("\t" * depth) + "]"
        return res + ")\n"

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def type(self) -> str:
        return str(self.type_token.value)


class StructDefNode:
    def __init__(self, name_token: Token):
        self.name_token: Token = name_token
        self.struct_members: List[StructMemberDeclareNode] = []

    def add_member_node(self, member_node: StructMemberDeclareNode) -> None:
        self.struct_members.append(member_node)

    def to_str(self, depth: int = 0) -> str:
        res: str = ("\t" * depth) + "struct " + str(self.name_token) + "(\n"
        for node in self.struct_members:
            res += node.to_str(depth + 1)
        return res + ")\n"

    @property
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def members(self) -> List[StructMemberDeclareNode]:
        return self.struct_members


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
    def size(self) -> Any:
        return self.bits_count_node

    @property
    def name(self) -> str:
        return str(self.name_token.value)


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
    def name(self) -> str:
        return str(self.name_token.value)

    @property
    def size(self) -> Any:
        return self.bitfield_bytes_count_token

    @property
    def members(self) -> List[BitfieldMemberNode]:
        return self.bitfield_members


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.token_index: int = -1

        # self.tokens contains at least a TT_EOF token
        self.current_token: Token = self.tokens[0]
        self.advance()

    def run(self) -> list:
        return self.statements()

    def advance(self) -> Token:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        if self.current_token.type == TT_COMMENT:
            # just ignore comments, we don't need them when parsing
            self.advance()
        return self.current_token

    def statements(self) -> list:
        res: list = []
        while self.current_token.type != TT_EOF:
            res.append(self.statement())
        return res

    def statement(self):
        token: Token = self.current_token

        if token.type == TT_KEYWORD:
            if token.value == "struct":
                return self.struct_stmt()
            elif token.value == "bitfield":
                return self.bitfield_stmt()

        self.advance()

    def bitfield_member_def(self) -> BitfieldMemberNode:
        """
        IDENTIFIER (RPAREN no-identifier-expr LPAREN)? COMMA
        """
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        bitfield_name_token: Token = self.current_token
        self.advance()

        res_bitfield_member_node: BitfieldMemberNode = BitfieldMemberNode(bitfield_name_token)

        if self.current_token.type == TT_LPAREN:
            self.advance()
            res_bitfield_member_node.set_explicit_size(self.no_identifier_expr())
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()

        if self.current_token.type != TT_COMMA:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")
        self.advance()

        return res_bitfield_member_node

    def bitfield_stmt(self) -> BitfieldDefNode:
        """
        Explicit size:
        KEYWORD:bitfield IDENTIFIER LPAREN no-identifier-expr RPAREN LCURLY bitfield-member-def+ RCURLY // bitfield with size specified between parenthesis (in bytes)
        Implicit size:
        KEYWORD:bitfield IDENTIFIER LCURLY bitfield-member-def+ RCURLY
        """
        self.advance()
        res_bitfield_def_node: BitfieldDefNode = BitfieldDefNode(self.current_token)

        self.advance()
        if self.current_token.type == TT_LPAREN:
            self.advance()
            res_bitfield_def_node.set_explicit_size(self.no_identifier_expr())
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()

        if self.current_token.type != TT_LCURLY:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        while self.current_token.type not in [TT_RCURLY, TT_EOF]:
            res_bitfield_def_node.add_member_node(self.bitfield_member_def())

        if self.current_token.type == TT_EOF:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '}'")

        self.advance()
        return res_bitfield_def_node

    def struct_stmt(self) -> StructDefNode:
        """
        KEYWORD:struct IDENTIFIER LCURLY struct-member-def RCURLY
        """
        self.advance()
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        res_struct_def_node: StructDefNode = StructDefNode(self.current_token)

        self.advance()
        if self.current_token.type != TT_LCURLY:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        while self.current_token.type not in [TT_RCURLY, TT_EOF]:
            res_struct_def_node.add_member_node(self.struct_member_def())

        if self.current_token.type == TT_EOF:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '}'")
        self.advance()

        return res_struct_def_node

    def struct_member_def(self) -> StructMemberDeclareNode:
        """
        (DATA-TYPE | IDENTIFIER) IDENTIFIER COMMA
        (DATA-TYPE | IDENTIFIER) LBRACK expr RBRACK IDENTIFIER COMMA
        """
        if self.current_token.type not in [TT_DATA_TYPE, TT_IDENTIFIER]:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected data-type or identifier")

        member_type: Token = self.current_token
        self.advance()

        is_list: bool = False
        list_length_node: Any = None

        if self.current_token.type == TT_IDENTIFIER:  # nothing to do, just continue parsing
            pass
        elif self.current_token.type == TT_LBRACK:
            is_list = True
            self.advance()
            list_length_node = self.expr()
            if self.current_token.type != TT_RBRACK:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ']'")
            self.advance()
        else:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier or '['")

        member_name: Token = self.current_token
        self.advance()

        if self.current_token.type == TT_COMMA:
            self.advance()
        else:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")

        return StructMemberDeclareNode(member_type, member_name, is_list, list_length_node)

    def no_identifier_factor(self) -> Any:
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS]:
            self.advance()
            return UnaryOpNode(token, self.no_identifier_factor())
        elif token.type == TT_LPAREN:
            self.advance()
            expr = self.no_identifier_expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return expr
        elif token.type == TT_NUM_INT:
            self.advance()
            return IntNumberNode(token)
        elif token.type == TT_NUM_FLOAT:
            self.advance()
            return FloatNumberNode(token)
        raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value")

    def no_identifier_expr(self) -> Any:
        return self.binary_op(self.no_identifier_term, [TT_PLUS, TT_MINUS])

    def no_identifier_term(self) -> Any:
        return self.binary_op(self.no_identifier_factor, [TT_MULT, TT_DIV])

    def factor(self) -> Any:
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS]:
            self.advance()
            return UnaryOpNode(token, self.factor())
        elif token.type == TT_LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return expr
        elif token.type == TT_NUM_INT:
            self.advance()
            return IntNumberNode(token)
        elif token.type == TT_NUM_FLOAT:
            self.advance()
            return FloatNumberNode(token)
        elif token.type == TT_IDENTIFIER:
            self.advance()
            return StructMemberAccessNode(token)
        raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier or value")

    def expr(self) -> Any:
        return self.binary_op(self.term, [TT_PLUS, TT_MINUS])

    def term(self) -> Any:
        return self.binary_op(self.factor, [TT_MULT, TT_DIV])

    def binary_op(self, func, operators) -> BinOpNode:
        left_token = func()

        if left_token is None:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value or expression")

        while self.current_token.type in operators:
            op_token = self.current_token
            self.advance()
            right_token = func()

            if right_token is None:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value or expression")

            left_token = BinOpNode(left_token, op_token, right_token)
        return left_token
