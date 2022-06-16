#!/usr/bin/env python3
from errors import *
from utils import *
from lexer import *

class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return str(self.token)

class BinOpNode:
    def __init__(self, left_node, op_node, right_node):
        self.left_node = left_node
        self.op_node = op_node
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node}, {self.op_node}, {self.right_node})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()
    
    def run(self):
        return self.expr()
    
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def factor(self):
        token = self.current_token

        if token.type in [TT_NUM_INT, TT_NUM_FLOAT]:
            self.advance()
            return NumberNode(token)

    def expr(self):
        return self.binary_op(self.term, [TT_PLUS, TT_MINUS])
    
    def term(self):
        return self.binary_op(self.factor, [TT_MULT, TT_DIV])
    
    def binary_op(self, func, operators):
        left_token = func()

        while self.current_token.type in operators:
            op_token = self.current_token
            self.advance()
            right_token = func()
            left_token = BinOpNode(left_token, op_token, right_token)
        return left_token