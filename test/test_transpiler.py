#!/usr/bin/env python3
from transpiler import ParseedOutputGenerator
from lexer import Lexer
from parser import Parser

def get_AST(text):
    tokens = Lexer(text, "").run()
    return Parser(tokens).run()

class TranspilerTest(ParseedOutputGenerator):
    def generate():
        return ""

def test_getStructs():
    tt = TranspilerTest(get_AST(""))
    assert len([struct for struct in tt.getStructs()]) == 0

    tt = TranspilerTest(get_AST("struct test {}"))
    res = [struct for struct in tt.getStructs()]
    assert len(res) == 1
    assert res[0].name_token.value == "test"

    tt = TranspilerTest(get_AST("bitfield test {}"))
    assert len([struct for struct in tt.getStructs()]) == 0

    tt = TranspilerTest(get_AST("struct test {} struct test2 {}"))
    res = [struct for struct in tt.getStructs()]
    assert len(res) == 2
    assert res[0].name_token.value == "test"
    assert res[1].name_token.value == "test2"

    tt = TranspilerTest(get_AST("struct test {} bitfield test2 {}"))
    assert len([struct for struct in tt.getStructs()]) == 1

    tt = TranspilerTest(get_AST("struct test { uint8 member1, uint16 member2, }"))
    assert len([struct for struct in tt.getStructs()]) == 1

    tt = TranspilerTest(get_AST("struct test {} bitfield test2 {} struct test3 {}"))
    res = [struct for struct in tt.getStructs()]
    assert len(res) == 2
    assert res[0].name_token.value == "test"
    assert res[1].name_token.value == "test3"

def test_getBitfields():
    tt = TranspilerTest(get_AST(""))
    assert len([bitfield for bitfield in tt.getStructs()]) == 0

    tt = TranspilerTest(get_AST("bitfield test {}"))
    res = [bitfield for bitfield in tt.getBitfields()]
    assert len(res) == 1
    assert res[0].name_token.value == "test"

    tt = TranspilerTest(get_AST("struct test {}"))
    assert len([bitfield for bitfield in tt.getBitfields()]) == 0

    tt = TranspilerTest(get_AST("bitfield test {} bitfield test2 {}"))
    res = [bitfield for bitfield in tt.getBitfields()]
    assert len(res) == 2
    assert res[0].name_token.value == "test"
    assert res[1].name_token.value == "test2"

    tt = TranspilerTest(get_AST("bitfield test {} struct test2 {}"))
    assert len([bitfield for bitfield in tt.getBitfields()]) == 1

    tt = TranspilerTest(get_AST("bitfield test { member1, member2(4), }"))
    assert len([bitfield for bitfield in tt.getBitfields()]) == 1

    tt = TranspilerTest(get_AST("bitfield test {} struct test2 {} bitfield test3 {}"))
    res = [bitfield for bitfield in tt.getBitfields()]
    assert len(res) == 2
    assert res[0].name_token.value == "test"
    assert res[1].name_token.value == "test3"