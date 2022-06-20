#!/usr/bin/env python3
from typing import List, Any
from errors import InvalidSyntaxError
from utils import *


# NODES
class NumberNode:
    def __init__(self, token: Token):
        self.token: Token = token

    def __repr__(self):
        return str(self.token)


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


class StructMemberNode:
    def __init__(self, struct_type_token: Token, struct_name_token: Token):
        self.member_type_token: Token = struct_type_token
        self.member_name_token: Token = struct_name_token

    def __repr__(self) -> str:
        return f"(StructMember {self.member_type_token}: {self.member_name_token})"


class StructDefNode:
    def __init__(self, struct_name_token):
        self.struct_name_token: Token = struct_name_token
        self.struct_members: List[StructMemberNode] = []

    def add_member_node(self, member_node: StructMemberNode) -> None:
        self.struct_members.append(member_node)

    def __repr__(self) -> str:
        return f"(StructDef {self.struct_name_token} {self.struct_members})"


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

    def struct_stmt(self) -> StructDefNode:
        """
        KEYWORD:struct IDENTIFIER LCURLY struct-member-def RCURLY
        """
        self.advance()
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
        TODO: (DATA-TYPE | IDENTIFIER) LBRACK NUM_INT RBRACK IDENTIFIER COMMA
        """
        if self.current_token.type not in [TT_DATA_TYPE, TT_IDENTIFIER]:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected data-type or identifier")

        member_type: Token = self.current_token
        self.advance()

        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        member_name: Token = self.current_token
        self.advance()

        if self.current_token.type == TT_COMMA:
            self.advance()
        else:
            # todo
            pass

        return StructMemberNode(member_type, member_name)

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
