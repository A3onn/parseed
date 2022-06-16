#!/usr/bin/env python3

KEYWORDS = ["struct", "bitfield"]

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

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"

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