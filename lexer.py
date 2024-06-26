#!/usr/bin/env python3
from typing import List, Optional
from string import digits as DIGITS, ascii_letters as LETTERS
from errors import IllegalCharacterError, ExpectedMoreCharError, InvalidSyntaxError
from utils import *

LETTERS_DIGITS = LETTERS + DIGITS

# Keywords
STRUCT_KEYWORD = "struct"
BITFIELD_KEYWORD = "bitfield"
MATCH_KEYWORD = "match"
LITTLE_ENDIAN_KEYWORD = "LE"
BIG_ENDIAN_KEYWORD = "BE"

ENDIANNESS_KEYWORDS = [LITTLE_ENDIAN_KEYWORD, BIG_ENDIAN_KEYWORD]

KEYWORDS = [
    STRUCT_KEYWORD,
    BITFIELD_KEYWORD,
    MATCH_KEYWORD,
    LITTLE_ENDIAN_KEYWORD,
    BIG_ENDIAN_KEYWORD,
]

# List of tokens
# Numerical values
TT_NUM_INT = "NUM_INT"
TT_NUM_FLOAT = "NUM_FLOAT"

# Operators
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"
TT_BIN_AND = "BIN_AND"
TT_BIN_OR = "BIN_OR"
TT_BIN_XOR = "BIN_XOR"
TT_BIN_NOT = "BIN_NOT"
TT_BIN_LSHIFT = "BIN_LSHIFT"
TT_BIN_RSHIFT = "BIN_RSHIFT"

# Comparators
TT_COMP_EQ = "COMP_EQ"
TT_COMP_NE = "COMP_NE"
TT_COMP_GT = "COMP_GT"
TT_COMP_LT = "COMP_LT"
TT_COMP_GEQ = "COMP_GEQ"  # greater than
TT_COMP_LEQ = "COMP_LEQ"  # less than
TT_COMP_AND = "COMP_AND"
TT_COMP_OR = "COMP_OR"

# Others
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_LBRACK = "LBRACK"
TT_RBRACK = "RBRACK"
TT_COMMENT = "COMMENT"
TT_COMMA = "COMMA"
TT_DOT = "DOT"
TT_SEMICOL = "SEMICOL"
TT_BACKSLASH = "BACKSLASH"
TT_STRING = "STRING"
TT_CHAR = "CHAR"

# for ternary operator
TT_COLON = "COLON"
TT_QUESTION_MARK = "QUESTION_MARK"

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_DATA_TYPE = "DATA_TYPE"

TT_EOF = "EOF"


class Token:
    def __init__(self, type_: str, value: Optional[str] = None, pos_start: Position = None, pos_end: Position = None) -> None:
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.get_copy()
            self.pos_end = pos_start.get_copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.get_copy()

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, text: str, filename: str):
        self.pos: Position = Position(-1, 0, -1, filename, text)
        self.current_char: Optional[str] = None
        self.text: str = text

    def run(self) -> List[Token]:
        """
        Run the lexer on the text given in the constructor and return a list of Token.
        """
        self._next_token()  # init lexer
        return self._make_tokens()

    def _next_token(self) -> None:
        """
        Returns the next character in the text if there is one.
        It also updates the current position.
        """
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def _make_tokens(self) -> List[Token]:
        """
        Returns a list of Tokens gathered in self.text.
        """
        tokens: List[Token] = []

        while self.current_char is not None:
            if self.current_char in [" ", "\t", "\n"]:
                self._next_token()
            elif self.current_char == "'":
                tokens.append(self._make_char())
            elif self.current_char == "\\":
                tokens.append(Token(TT_BACKSLASH, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "\"":
                tokens.append(self._make_string())
            elif self.current_char in DIGITS:
                tokens.append(self._make_number_or_dot())
            elif self.current_char == "?":
                tokens.append(Token(TT_QUESTION_MARK, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "/":
                tokens.append(self._make_div_or_comment())
            elif self.current_char == "*":
                tokens.append(Token(TT_MULT, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "&":
                tokens.append(self._make_bin_and_or_comp_and())
            elif self.current_char == "|":
                tokens.append(self._make_bin_or_or_comp_or())
            elif self.current_char == "^":
                tokens.append(Token(TT_BIN_XOR, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "~":
                tokens.append(Token(TT_BIN_NOT, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self._next_token()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "[":
                tokens.append(Token(TT_LBRACK, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "]":
                tokens.append(Token(TT_RBRACK, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "{":
                tokens.append(Token(TT_LCURLY, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "}":
                tokens.append(Token(TT_RCURLY, pos_start=self.pos))
                self._next_token()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self._next_token()
            elif self.current_char == ".":
                tokens.append(self._make_number_or_dot())
            elif self.current_char == ";":
                tokens.append(Token(TT_SEMICOL, pos_start=self.pos))
                self._next_token()
            elif self.current_char == ":":
                tokens.append(Token(TT_COLON, pos_start=self.pos))
                self._next_token()
            elif self.current_char == "!":
                tokens.append(self._make_not_equal())
            elif self.current_char == "=":
                tokens.append(self._make_equal())
            elif self.current_char == "<":
                tokens.append(self._make_less_than_or_left_bitshift())
            elif self.current_char == ">":
                tokens.append(self._make_greater_than_or_right_bitshift())
            elif self.current_char in LETTERS:
                tokens.append(self._make_identifier())
            else:
                pos_start: Position = self.pos.get_copy()
                char: str = self.current_char
                self._next_token()
                raise IllegalCharacterError(pos_start, self.pos, f"'{char}'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens

    def _make_identifier(self) -> Token:
        """
        Tokenize a word by checking if it is an identifier, data-type or a keyword.
        """
        res_identifier: str = ""
        pos_start: Position = self.pos.get_copy()

        # identifiers can have numbers and '_' in their name, but as this function is called
        # when a letter is founc, they cannot start with a number nor a '_'
        while self.current_char is not None and self.current_char in LETTERS_DIGITS + "_":
            res_identifier += self.current_char
            self._next_token()

        if res_identifier in KEYWORDS:
            token_type = TT_KEYWORD
        elif res_identifier in DATA_TYPES:
            token_type = TT_DATA_TYPE
        else:
            token_type = TT_IDENTIFIER

        return Token(token_type, res_identifier, pos_start, self.pos)

    def _make_number_or_dot(self) -> Token:
        """
        Tokenize a word by checking if it is a number (integer or float) or a simple dot ('.').
        """
        pos_start: Position = self.pos.get_copy()
        res_num: str = ""
        dot_count: int = 0

        while self.current_char is not None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                # As floating number cannot begin with a '.' and have to begin with a number before,
                # we can assume that '.' without any number before are TT_DOT
                if len(res_num) == 0:
                    self._next_token()
                    return Token(TT_DOT, pos_start=pos_start)
                if dot_count == 1:  # if we already encounter a dot before
                    break
                dot_count += 1
            res_num += self.current_char
            self._next_token()

        if dot_count == 0:
            return Token(TT_NUM_INT, res_num, pos_start, self.pos)
        else:
            return Token(TT_NUM_FLOAT, res_num, pos_start, self.pos)

    def _make_div_or_comment(self) -> Token:
        """
        Tokenize a word by checking if it is a comment ('//') or a simple divide.
        """
        pos_start: Position = self.pos.get_copy()
        div_count: int = 1

        self._next_token()
        while self.current_char is not None and self.current_char == "/":
            div_count += 1
            self._next_token()

        if div_count == 1:
            return Token(TT_DIV, pos_start=pos_start, pos_end=self.pos)
        else:
            return Token(TT_COMMENT, self._read_until("\n\r"), pos_start, self.pos)

    # comparisons
    def _make_not_equal(self) -> Token:
        """
        Handle token for not equal comparison ('!=').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char != "=":
            raise ExpectedMoreCharError(pos_start, self.pos, ["="])

        self._next_token()
        return Token(TT_COMP_NE, pos_start=pos_start, pos_end=self.pos)

    def _make_equal(self) -> Token:
        """
        Handle token for equal comparison ('==').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char != "=":
            raise ExpectedMoreCharError(pos_start, self.pos, ["="])

        self._next_token()
        return Token(TT_COMP_EQ, pos_start=pos_start, pos_end=self.pos)

    def _make_less_than_or_left_bitshift(self) -> Token:
        """
        Handle token for less than, ('<'), less or equal ('<=') or left bitshift ('<<').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char == "=":
            self._next_token()
            return Token(TT_COMP_LEQ, pos_start=pos_start, pos_end=self.pos)
        elif self.current_char == "<":
            self._next_token()
            return Token(TT_BIN_LSHIFT, pos_start=pos_start, pos_end=self.pos)
        return Token(TT_COMP_LT, pos_start=pos_start, pos_end=self.pos)

    def _make_greater_than_or_right_bitshift(self) -> Token:
        """
        Handle token for greater than, ('<'), greater or equal ('<=') or right bitshift ('>>').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char == "=":
            self._next_token()
            return Token(TT_COMP_GEQ, pos_start=pos_start, pos_end=self.pos)
        elif self.current_char == ">":
            self._next_token()
            return Token(TT_BIN_RSHIFT, pos_start=pos_start, pos_end=self.pos)
        return Token(TT_COMP_GT, pos_start=pos_start, pos_end=self.pos)

    def _make_bin_and_or_comp_and(self) -> Token:
        """
        Handle token for comparison and ('&&') or binary and ('&').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char == "&":
            self._next_token()
            return Token(TT_COMP_AND, pos_start=pos_start, pos_end=self.pos)
        return Token(TT_BIN_AND, pos_start=pos_start, pos_end=self.pos)

    def _make_bin_or_or_comp_or(self) -> Token:
        """
        Handle token for comparison or ('||') or binary or ('|').
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()

        if self.current_char == "|":
            self._next_token()
            return Token(TT_COMP_OR, pos_start=pos_start, pos_end=self.pos)
        return Token(TT_BIN_OR, pos_start=pos_start, pos_end=self.pos)
    
    def _make_string(self) -> Token:
        """
        Handle token for strings.
        """
        pos_start: Position = self.pos.get_copy()
        self._next_token()
        res: str = ""
        while True:
            res += self._read_until("\"")

            if self.current_char is None:
                raise ExpectedMoreCharError(pos_start, self.pos, ["\""])
            
            if self.text[self.pos.idx-1] == "\\":
                res = res[:-1]
                res += "\""
                self._next_token()
            else:
                self._next_token()
                return Token(TT_STRING, res, pos_start, self.pos)

    def _make_char(self) -> Token:
        """
        Handle token for a char.
        """
        pos_start: Position = self.pos.get_copy()
        res: str = ""
        self._next_token()
        while True:
            res += self._read_until("\'")

            if self.current_char is None:
                raise ExpectedMoreCharError(pos_start, self.pos, ["\""])

            if self.text[self.pos.idx-1] == "\\":
                res += "'"
                self._next_token()
            else:
                if res[0] != "\\" and len(res) > 1:
                    raise InvalidSyntaxError(pos_start, self.pos, f"A char must have a length of 1 or have a format of \"\\xx\"")

                self._next_token()
                return Token(TT_CHAR, res, pos_start, self.pos)

    def _read_until(self, stop_chars: str) -> str:
        """
        Calls self._next_token() until a character from the stop_chars parameter is reached.
        This functions returns all characters read until the stop character is reached.
        This function is useful for comments for example.
        """
        res: str = ""
        while self.current_char is not None and self.current_char not in stop_chars:
            res += self.current_char
            self._next_token()
        return res

def convert_token_as_str(token: Token) -> str:
    """
    Give a Token its corresponding string.

    :param token: Token to convert.
    :type token: Token
    """
    if token.type == TT_EOF:
        return ""
    elif token.type == TT_PLUS:
        return "+"
    elif token.type == TT_MINUS:
        return "-"
    elif token.type == TT_MULT:
        return "*"
    elif token.type == TT_DIV:
        return "/"
    elif token.type == TT_BIN_AND:
        return "&"
    elif token.type == TT_BIN_OR:
        return "|"
    elif token.type == TT_BIN_XOR:
        return "^"
    elif token.type == TT_BIN_NOT:
        return "!"
    elif token.type == TT_BIN_LSHIFT:
        return "<<"
    elif token.type == TT_BIN_RSHIFT:
        return ">>"
    elif token.type == TT_COMP_EQ:
        return "=="
    elif token.type == TT_COMP_NE:
        return "!="
    elif token.type == TT_COMP_GT:
        return ">"
    elif token.type == TT_COMP_LT:
        return "<"
    elif token.type == TT_COMP_GEQ:
        return ">="
    elif token.type == TT_COMP_LEQ:
        return "<="
    elif token.type == TT_COMP_AND:
        return "&&"
    elif token.type == TT_COMP_OR:
        return "||"
    elif token.type == TT_LPAREN:
        return "("
    elif token.type == TT_RPAREN:
        return ")"
    elif token.type == TT_LCURLY:
        return "{"
    elif token.type == TT_RCURLY:
        return "}"
    elif token.type == TT_LBRACK:
        return "["
    elif token.type == TT_RBRACK:
        return "]"
    elif token.type == TT_COMMENT:
        return "//"
    elif token.type == TT_COMMA:
        return ","
    elif token.type == TT_DOT:
        return "."
    elif token.type == TT_SEMICOL:
        return ";"
    elif token.type == TT_STRING:
        return "\"" + token.value + "\""
    elif token.type == TT_CHAR:
        return "'" + token.value + "'"
    elif token.type == TT_BACKSLASH:
        return "\\"
    elif token.type == TT_COLON:
        return ":"
    elif token.type == TT_QUESTION_MARK:
        return "?"
    return token.value
