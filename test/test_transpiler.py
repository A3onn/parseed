#!/usr/bin/env python3
from transpiler import ParseedOutputGenerator
from lexer import Lexer
from parser import Parser
from errors import RecursiveNestedStructError
import pytest

def get_AST(text):
    tokens = Lexer(text, "").run()
    return Parser(tokens).run()

class TranspilerTest(ParseedOutputGenerator):
    def generate(writer):
        return ""

def test_structs():
    tt = TranspilerTest(get_AST(""))
    assert len(tt.structs) == 0

    tt = TranspilerTest(get_AST("struct test {}"))
    assert len(tt.structs) == 1
    assert len(tt.structs[0].members) == 0
    assert tt.structs[0].name == "test"

    tt = TranspilerTest(get_AST("struct test1 {} struct test2 {}"))
    assert len(tt.structs) == 2
    assert len(tt.structs[0].members) == 0
    assert tt.structs[0].name == "test1"
    assert len(tt.structs[1].members) == 0
    assert tt.structs[1].name == "test2"

    tt = TranspilerTest(get_AST("struct test1 {} bitfield test2 {}"))
    assert len(tt.structs) == 1
    assert len(tt.structs[0].members) == 0
    assert tt.structs[0].name == "test1"

    tt = TranspilerTest(get_AST("struct test1 {} bitfield test2 {} struct test3 {}"))
    assert len(tt.structs) == 2
    assert len(tt.structs[0].members) == 0
    assert tt.structs[0].name == "test1"
    assert len(tt.structs[1].members) == 0
    assert tt.structs[1].name == "test3"

    tt = TranspilerTest(get_AST("struct test { uint8 member,}"))
    assert len(tt.structs) == 1
    assert len(tt.structs[0].members) == 1
    assert tt.structs[0].name == "test"

    tt = TranspilerTest(get_AST("struct test { uint8 member1, uint16[2] member2, }"))
    assert len(tt.structs) == 1
    assert len(tt.structs[0].members) == 2
    assert tt.structs[0].name == "test"


def test_nested_structs():
    # just to check if there is an error thrown when using nested structs
    TranspilerTest(get_AST("struct root_struct { nested_struct test, } struct nested_struct {uint8 data, }"))

    with pytest.raises(RecursiveNestedStructError):
        TranspilerTest(get_AST("struct root_struct { nested_struct test, } struct nested_struct { root_struct should_not_work, }"))