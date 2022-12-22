#!/usr/bin/env python3
from transpiler import ParseedOutputGenerator
from lexer import Lexer
from parser import Parser
from errors import *
import pytest

def get_AST(text):
    tokens = Lexer(text, "").run()
    return Parser(tokens).run()

class TranspilerTest(ParseedOutputGenerator):
    def generate(writer):
        pass

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

def test_duplicate_members():
    with pytest.raises(DuplicateMemberError):
        TranspilerTest(get_AST("struct my_struct { uint8 test, uint8 test, }"))

    with pytest.raises(DuplicateMemberError):
        TranspilerTest(get_AST("struct my_struct { uint8 test, uint8[1] test, }"))

    with pytest.raises(DuplicateMemberError):
        TranspilerTest(get_AST("struct my_struct { string test, uint8 test, }"))

    with pytest.raises(DuplicateMemberError):
        TranspilerTest(get_AST("struct my_struct { string test, uint8 test, uint8 test2, }"))

    with pytest.raises(DuplicateMemberError):
        TranspilerTest(get_AST("struct my_struct { string test, uint8[1] test, }"))

    # same name but in different structs
    TranspilerTest(get_AST("struct my_struct { uint8 test,} struct another_struct{ uint8 test, }"))

def test_duplicate_structs_and_bitfields():
    with pytest.raises(DuplicateStructOrBitfieldError):
        TranspilerTest(get_AST("struct my_struct { } struct my_struct { }"))

    with pytest.raises(DuplicateStructOrBitfieldError):
        TranspilerTest(get_AST("struct my_struct { } struct my_struct { uint8 member, }"))

    with pytest.raises(DuplicateStructOrBitfieldError):
        TranspilerTest(get_AST("struct some_name { } bitfield some_name { }"))


def test_nested_structs():
    # just to check if there is an error thrown when using nested structs
    TranspilerTest(get_AST("struct root_struct { nested_struct test, } struct nested_struct {uint8 data, }"))

    with pytest.raises(UnknownTypeError):
        TranspilerTest(get_AST("struct test { some_type test, }"))

    with pytest.raises(RecursiveStructError):
        TranspilerTest(get_AST("struct root_struct { nested_struct test, } struct nested_struct { root_struct should_not_work, }"))

    with pytest.raises(RecursiveStructError):
        TranspilerTest(get_AST("struct root_struct { nested_struct_1 test, } struct nested_struct_1 { nested_struct_2 should_not_work, } struct nested_struct_2 { root_struct should_not_work , }"))

def unknwon_types():
    with pytest.raises(UnknownTypeError):
        # unknown struct in ternary data-type
        Parser(get_tokens("struct test { (1 == 1 ? Unknown_Struct : uint8) some_member, }")).run()