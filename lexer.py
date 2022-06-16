#!/usr/bin/env python3
from string import digits as DIGITS
from string import ascii_letters as LETTERS
from errors import *
from utils import *

LETTERS_DIGITS = LETTERS + DIGITS

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
                tokens.append(self._make_div_or_comment())
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
            elif self.current_char in LETTERS:
                tokens.append(self._make_identifier())
            else:
                pos_start = self.pos.get_copy()
                char = self.current_char
                self._next_token()
                return [], IllegalCharacterError(pos_start, self.pos, "'" + char + "'")
        return tokens, None

    def _make_identifier(self):
        res_identifier = ""
        pos_start = self.pos.get_copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            res_identifier += self.current_char
            self._next_token()
        
        if res_identifier in KEYWORDS:
            token_type = TT_KEYWORD
        elif res_identifier in DATA_TYPES:
            token_type = TT_DATA_TYPE
        else:
            token_type = TT_IDENTIFIER

        return Token(token_type, res_identifier)

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

    def _make_div_or_comment(self):
        div_count = 1

        self._next_token()
        while self.current_char != None and self.current_char == "/":
            div_count += 1
            self._next_token()
        if div_count == 1:
            return Token(TT_DIV)
        else:
            return Token(TT_COMMENT, self._read_until("\n\r"))

    def _read_until(self, stop_chars):
        res = ""
        self._next_token()
        while self.current_char != None and self.current_char not in stop_chars:
            res += self.current_char
            self._next_token()
        return res
    