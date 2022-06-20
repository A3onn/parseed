#!/usr/bin/env python3
from typing import List, Any
from errors import *
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


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.token_index: int = -1
        self.advance()

    def run(self) -> Any:
        return self.expr()

    def advance(self) -> Token:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token: Token = self.tokens[self.token_index]
        return self.current_token

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
