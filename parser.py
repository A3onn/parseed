#!/usr/bin/env python3
from typing import List, Any, Optional
from errors import InvalidSyntaxError
from utils import *


# NODES
class NumberNode:
    def __init__(self, token: Token):
        self.token: Token = token

    def __repr__(self):
        return f"({self.token})"


# operators
class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node}, {self.op_token}, {self.right_node})"


class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

    def __repr__(self):
        return f"({self.op_token}, {self.node})"


# struct
class StructMemberNode:
    def __init__(self, type_token: Token, name_token: Token, is_list: bool, list_length_node: Optional[Any] = None):
        self.type_token: Token = type_token
        self.name_token: Token = name_token
        self.is_list = is_list
        self.list_length_node: Optional[Any] = list_length_node

    def __repr__(self) -> str:
        if self.is_list:
            return f"(StructMember {self.type_token}[{self.list_length_node}]: {self.name_token})"
        return f"(StructMember {self.type_token}: {self.name_token})"


class StructDefNode:
    def __init__(self, struct_name_token):
        self.struct_name_token: Token = struct_name_token
        self.struct_members: List[StructMemberNode] = []

    def add_member_node(self, member_node: StructMemberNode) -> None:
        self.struct_members.append(member_node)

    def __repr__(self) -> str:
        return f"(StructDef {self.struct_name_token} {self.struct_members})"


# bitfield
class BitfieldMemberNode:
    def __init__(self, name_token: Token, bits_count_node: Optional[Any] = None):
        self.name_token: Token = name_token
        self.bits_count_node: Optional[Any] = bits_count_node

    def set_explicit_size(self, bit_count_node: Any):
        self.bits_count_node = bit_count_node

    def __repr__(self) -> str:
        return f"(BitfieldMember {self.name_token}: {self.bits_count_node})"


class BitfieldDefNode:
    def __init__(self, bitfield_name_token: Token, bitfield_bytes_count_token: Optional[Token] = None):
        self.bitfield_name_token: Token = bitfield_name_token
        self.bitfield_bytes_count_token: Optional[Token] = bitfield_bytes_count_token
        self.bitfield_members: List[BitfieldMemberNode] = []

    def set_explicit_size(self, bitfield_bytes_count_token: Token):
        self.bitfield_bytes_count_token = bitfield_bytes_count_token

    def add_member_node(self, member_node: BitfieldMemberNode) -> None:
        self.bitfield_members.append(member_node)

    def __repr__(self) -> str:
        return f"(BitfieldDef {self.bitfield_name_token}({self.bitfield_bytes_count_token}) {self.bitfield_members})"


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
        IDENTIFIER (RPAREN expr LPAREN)? COMMA
        """
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        bitfield_name_token: Token = self.current_token
        self.advance()

        res_bitfield_member_node: BitfieldMemberNode = BitfieldMemberNode(bitfield_name_token)

        if self.current_token.type == TT_LPAREN:
            self.advance()
            res_bitfield_member_node.set_explicit_size(self.expr())
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()

        if self.current_token.type != TT_COMMA:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")
        self.advance()

        return res_bitfield_member_node

    def bitfield_stmt(self) -> BitfieldDefNode:
        """
        Without size in bytes:
        KEYWORD:bitfield IDENTIFIER LPAREN expr RPAREN LCURLY bitfield-member-def+ RCURLY
        Implicit size:
        KEYWORD:bitfield IDENTIFIER LCURLY bitfield-member-def+ RCURLY
        """
        self.advance()
        res_bitfield_def_node: BitfieldDefNode = BitfieldDefNode(self.current_token)

        self.advance()
        if self.current_token.type == TT_LPAREN:
            self.advance()
            res_bitfield_def_node.set_explicit_size(self.expr())
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')")
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

    def struct_member_def(self) -> StructMemberNode:
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

        return StructMemberNode(member_type, member_name, is_list, list_length_node)

    def factor(self) -> Any:
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS]:
            self.advance()
            return UnaryOpNode(token, self.factor())
        elif token.type == TT_LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type is TT_RPAREN:
                self.advance()
                return expr
        elif token.type in [TT_NUM_INT, TT_NUM_FLOAT]:
            self.advance()
            return NumberNode(token)

    def expr(self) -> Any:
        return self.binary_op(self.term, [TT_PLUS, TT_MINUS])

    def term(self) -> Any:
        return self.binary_op(self.factor, [TT_MULT, TT_DIV])

    def binary_op(self, func, operators) -> BinOpNode:
        left_token = func()

        while self.current_token.type in operators:
            op_token = self.current_token
            self.advance()
            right_token = func()
            left_token = BinOpNode(left_token, op_token, right_token)
        return left_token
