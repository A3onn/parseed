from lexer import *

def test_simple():
    lexer = Lexer("", "")

def test_eof():
    lexer = Lexer("", "")
    tokens = lexer.run()
    assert len(tokens) == 1
    assert tokens[0].type == TT_EOF
    assert tokens[0].value == None

def test_num_float():
    lexer = Lexer("3.5    3. 29.12345 -0.2  -0.  ", "")
    tokens = lexer.run()
    assert len(tokens) == 6
    assert tokens[0].type == TT_NUM_FLOAT
    assert tokens[0].value == "3.5"
    assert tokens[1].type == TT_NUM_FLOAT
    assert tokens[1].value == "3."
    assert tokens[2].type == TT_NUM_FLOAT
    assert tokens[2].value == "29.12345"
    assert tokens[3].type == TT_NUM_FLOAT
    assert tokens[3].value == "-0.2"
    assert tokens[4].type == TT_NUM_FLOAT
    assert tokens[4].value == "-0."
    assert tokens[5].type == TT_EOF

def test_num_int():
    lexer = Lexer("3 136   -12 -87  9", "")
    tokens = lexer.run()
    assert len(tokens) == 6
    assert tokens[0].type == TT_NUM_INT
    assert tokens[0].value == "3"
    assert tokens[1].type == TT_NUM_INT
    assert tokens[1].value == "136"
    assert tokens[2].type == TT_NUM_INT
    assert tokens[2].value == "-12"
    assert tokens[3].type == TT_NUM_INT
    assert tokens[3].value == "-87"
    assert tokens[4].type == TT_NUM_INT
    assert tokens[4].value == "9"
    assert tokens[5].type == TT_EOF

def test_multiple_minus():
    lexer = Lexer(" --6 - ---3.7", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_MINUS
    assert tokens[1].type == TT_NUM_INT
    assert tokens[1].value == "-6"
    assert tokens[2].type == TT_MINUS
    assert tokens[3].type == TT_MINUS
    assert tokens[4].type == TT_MINUS
    assert tokens[5].type == TT_NUM_FLOAT

def test_comments_and_div():
    lexer = Lexer(" / / 123 // some test //", "")
    tokens = lexer.run()
    assert tokens[0].type == TT_DIV
    assert tokens[1].type == TT_DIV
    assert tokens[2].type == TT_NUM_INT
    assert tokens[3].type == TT_COMMENT
    assert tokens[3].value == " some test //"