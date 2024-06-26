import pytest
from lexer import *
from errors import *

def test_simple():
    lexer = Lexer("", "")

def test_eof():
    lexer = Lexer("", "")
    tokens = lexer.run()
    assert len(tokens) == 1
    assert tokens[0].type == TT_EOF
    assert tokens[0].value == None

def test_num_float():
    lexer = Lexer("3.5    3. 29.12345 0.2  0.  ", "")
    tokens = lexer.run()
    assert len(tokens) == 6
    assert tokens[0].type == TT_NUM_FLOAT
    assert tokens[0].value == "3.5"
    assert tokens[1].type == TT_NUM_FLOAT
    assert tokens[1].value == "3."
    assert tokens[2].type == TT_NUM_FLOAT
    assert tokens[2].value == "29.12345"
    assert tokens[3].type == TT_NUM_FLOAT
    assert tokens[3].value == "0.2"
    assert tokens[4].type == TT_NUM_FLOAT
    assert tokens[4].value == "0."
    assert tokens[5].type == TT_EOF

def test_num_int():
    lexer = Lexer("3 136   12 87  9", "")
    tokens = lexer.run()
    assert len(tokens) == 6
    assert tokens[0].type == TT_NUM_INT
    assert tokens[0].value == "3"
    assert tokens[1].type == TT_NUM_INT
    assert tokens[1].value == "136"
    assert tokens[2].type == TT_NUM_INT
    assert tokens[2].value == "12"
    assert tokens[3].type == TT_NUM_INT
    assert tokens[3].value == "87"
    assert tokens[4].type == TT_NUM_INT
    assert tokens[4].value == "9"
    assert tokens[5].type == TT_EOF

def test_arithmetic():
    lexer = Lexer("- + * /", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_MINUS
    assert tokens[1].type == TT_PLUS
    assert tokens[2].type == TT_MULT
    assert tokens[3].type == TT_DIV

def test_binary_operators():
    lexer = Lexer("& | ^ << >> ~", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_BIN_AND
    assert tokens[1].type == TT_BIN_OR
    assert tokens[2].type == TT_BIN_XOR
    assert tokens[3].type == TT_BIN_LSHIFT
    assert tokens[4].type == TT_BIN_RSHIFT
    assert tokens[5].type == TT_BIN_NOT

def test_comments_and_div():
    lexer = Lexer(" / / 123 // some test //", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_DIV
    assert tokens[1].type == TT_DIV
    assert tokens[2].type == TT_NUM_INT
    assert tokens[3].type == TT_COMMENT
    assert tokens[3].value == " some test //"

def test_struct():
    lexer = Lexer("struct  struct", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_KEYWORD
    assert tokens[0].value == STRUCT_KEYWORD 
    assert tokens[1].type == TT_KEYWORD
    assert tokens[1].value == STRUCT_KEYWORD
    assert tokens[2].type == TT_EOF

def test_bitfield():
    lexer = Lexer("bitfield   bitfield", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_KEYWORD
    assert tokens[0].value == BITFIELD_KEYWORD
    assert tokens[1].type == TT_KEYWORD
    assert tokens[1].value == BITFIELD_KEYWORD
    assert tokens[2].type == TT_EOF

def test_curly():
    lexer = Lexer("{{ }{}}", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_LCURLY
    assert tokens[1].type == TT_LCURLY
    assert tokens[2].type == TT_RCURLY
    assert tokens[3].type == TT_LCURLY
    assert tokens[4].type == TT_RCURLY
    assert tokens[5].type == TT_RCURLY

def test_brack():
    lexer = Lexer("[[ ][]]", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_LBRACK
    assert tokens[1].type == TT_LBRACK
    assert tokens[2].type == TT_RBRACK
    assert tokens[3].type == TT_LBRACK
    assert tokens[4].type == TT_RBRACK
    assert tokens[5].type == TT_RBRACK

def test_parenthesis():
    lexer = Lexer("(( )()) ", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_LPAREN
    assert tokens[1].type == TT_LPAREN
    assert tokens[2].type == TT_RPAREN
    assert tokens[3].type == TT_LPAREN
    assert tokens[4].type == TT_RPAREN
    assert tokens[5].type == TT_RPAREN

def test_strings():
    lexer = Lexer("\"test\" \" test \"", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_STRING
    assert tokens[0].value == "test"
    assert tokens[1].type == TT_STRING
    assert tokens[1].value == " test "

    with pytest.raises(ExpectedMoreCharError):
        lexer = Lexer("\"test", "")
        tokens = lexer.run()

def test_chars():
    lexer = Lexer("'c' '0' '\\00' '\\0' '\\''", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_CHAR
    assert tokens[0].value == "c"
    assert tokens[1].type == TT_CHAR
    assert tokens[1].value == "0"
    assert tokens[2].type == TT_CHAR
    assert tokens[2].value == r"\00"
    assert tokens[3].type == TT_CHAR
    assert tokens[3].value == r"\0"
    assert tokens[4].type == TT_CHAR
    assert tokens[4].value == "\\'"

    with pytest.raises(InvalidSyntaxError):
        lexer = Lexer("'invalid'", "")
        tokens = lexer.run()

    with pytest.raises(ExpectedMoreCharError):
        lexer = Lexer("'a", "")
        tokens = lexer.run()

def test_comma_colon_semicolon_dot_question_mark():
    lexer = Lexer(",, ; ; .. . :: : ? ??", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_COMMA
    assert tokens[1].type == TT_COMMA
    assert tokens[2].type == TT_SEMICOL
    assert tokens[3].type == TT_SEMICOL
    assert tokens[4].type == TT_DOT
    assert tokens[5].type == TT_DOT
    assert tokens[6].type == TT_DOT
    assert tokens[7].type == TT_COLON
    assert tokens[8].type == TT_COLON
    assert tokens[9].type == TT_COLON
    assert tokens[10].type == TT_QUESTION_MARK
    assert tokens[11].type == TT_QUESTION_MARK
    assert tokens[12].type == TT_QUESTION_MARK

def test_comparator():
    lexer = Lexer("==  <= <   >= > != && ||", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_COMP_EQ
    assert tokens[1].type == TT_COMP_LEQ
    assert tokens[2].type == TT_COMP_LT
    assert tokens[3].type == TT_COMP_GEQ
    assert tokens[4].type == TT_COMP_GT
    assert tokens[5].type == TT_COMP_NE
    assert tokens[6].type == TT_COMP_AND
    assert tokens[7].type == TT_COMP_OR

    with pytest.raises(ExpectedMoreCharError):
        lexer = Lexer("!", "")
        tokens = lexer.run()

    with pytest.raises(ExpectedMoreCharError):
        lexer = Lexer("=", "")
        tokens = lexer.run()

def test_keywords():
    lexer = Lexer(" ".join(KEYWORDS), "")
    tokens = lexer.run()
    for i in range(len(KEYWORDS)):
        assert tokens[i].type == TT_KEYWORD
        assert tokens[i].value == KEYWORDS[i]

    assert tokens[-1].type == TT_EOF

def test_keywords():
    identifiers = ["some_identifier", "someidentifier", "someidentifierwithnumbera123", "SOME_IDENTIFIER", "SomeIdentifier"]
    lexer = Lexer(" ".join(identifiers), "")
    tokens = lexer.run()

    for i in range(len(identifiers)):
        assert tokens[i].type == TT_IDENTIFIER
        assert tokens[i].value == identifiers[i]

    assert tokens[len(identifiers)].type == TT_EOF
