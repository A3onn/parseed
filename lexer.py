#!/usr/bin/env python3
from string import digits as DIGITS

# LIST OF TOKENS
# Numerical values
TT_NUM_INT = "NUM_INT"
TT_NUM_FLOAT = "NUM_FLOAT"

# Data types
TT_STRING = "STRING"
TT_FLOAT = "FLOAT"
TT_UINT8 = "UINT8"
TT_INT8 = "INT8"
TT_UINT16 = "UINT16"
TT_INT16 = "INT16"
TT_UINT24 = "UINT24"
TT_INT24 = "INT24"
TT_UINT32 = "UINT32"
TT_INT32 = "INT32"

# Operators
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"

# Comparators
TT_COMP_EQ = "COMP_EQ"
TT_COMP_NE = "COMP_NE"
TT_COMP_GT = "COMP_GT"
TT_COMP_LT = "COMP_LT"
TT_COMP_GE = "COMP_GE"
TT_COMP_LE = "COMP_LE"

# Others
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_LBRACK = "LBRACK"
TT_RBRACK = "RBRACK"

class ParseedError:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def __str__(self):
        return f"On line {self.pos_start.ln + 1}: {self.error_name}: {self.details}"

class IllegalCharacterError(ParseedError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "IllegalCharacterError", details)

class Position:
    def __init__(self, idx, ln, col, filename, file_text):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.filename = filename
        self.file_text = file_text
    
    def advance(self, current_char):
        self.idx +=1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
    
    def get_copy(self):
        return Position(self.idx, self.ln, self.col, self.filename, self.file_text)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"

class Lexer:
    def __init__(self, text, filename):
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.text = text

    def run(self):
        self._next_token() # init
        tokens, error = self._make_tokens()
        return tokens, error
    
    def _next_token(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def _make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in [" ", "\t"]:
                self._next_token()
            elif self.current_char in DIGITS:
                tokens.append(self._make_number())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self._next_token()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self._next_token()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self._next_token()
            elif self.current_char == "*":
                tokens.append(Token(TT_MULT))
                self._next_token()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self._next_token()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self._next_token()
            elif self.current_char == "[":
                tokens.append(Token(TT_LBRACK))
                self._next_token()
            elif self.current_char == "]":
                tokens.append(Token(TT_RBRACK))
                self._next_token()
            elif self.current_char == "{":
                tokens.append(Token(TT_LCURLY))
                self._next_token()
            elif self.current_char == "}":
                tokens.append(Token(TT_RCURLY))
                self._next_token()
            else:
                pos_start = self.pos.get_copy()
                char = self.current_char
                self._next_token()
                return [], IllegalCharacterError(pos_start, self.pos, "'" + char + "'")
        return tokens, None

    def _make_number(self):
        res_num = ""
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                res_num += "."
            res_num += self.current_char
            self._next_token()
        if dot_count == 0:
            return Token(TT_NUM_INT, res_num)
        else:
            return Token(TT_NUM_FLOAT, res_num)