#!/usr/bin/env python3
from parser import Parser
from lexer import Lexer
from errors import InvalidSyntaxError
from utils import *
import pytest


def get_tokens(text):
    return Lexer(text, "").run()


def test_simple():
    parser = Parser(get_tokens(""))
    parser.run()

def test_empty_struct():
    parser = Parser(get_tokens("struct test { }"))
    parser.run()

def test_struct_members():
    Parser(get_tokens("struct test { uint8 member, }")).run()
    Parser(get_tokens("struct test { uint8 member1, float member2, }")).run()
    Parser(get_tokens("struct test { uint8[1] member,}")).run()
    Parser(get_tokens("struct test { uint8[] member,}")).run()
    Parser(get_tokens("struct test { uint8[] member1, uint16[] member2,}")).run()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, }")).run()
    Parser(get_tokens("struct test { uint8 member1, float[member1] member2, }")).run()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, int24[15] member3, }")).run()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, int24[] member3, }")).run()
    Parser(get_tokens("struct test { (1 == 1 ? uint8 : uint16)[] member,}")).run()
    Parser(get_tokens("struct test { (1 != 1 ? uint8 : SomeIdentifier) member,}")).run()
    Parser(get_tokens("struct test { LE (1 != 1 ? uint8 : uint16) member1, (2 == 2 ? uint16 : int16) member2, }")).run()
    Parser(get_tokens("struct test { (1 != 1 ? SomeIdentifier : SomeIdentifier) member,}")).run()
    Parser(get_tokens("struct test { uint8 member1, LE (2 == 2 ? uint16 : int16) member2, }")).run()
    Parser(get_tokens("struct test { SomeIndentifier member, }")).run()
    Parser(get_tokens("struct test { SomeIndentifier member1, float member2, AnotherIdentifier member3, }")).run()
    Parser(get_tokens("struct test { SomeIndentifier member1, float member2, AnotherIdentifier[3] member3, AnotherOne[] member4,}")).run()

def test_struct_members_with_expressions():
    Parser(get_tokens("struct test { uint8[1+1] member, }")).run()
    Parser(get_tokens("struct test { uint8[1+1] member1, uint8[15-3] member2, }")).run()
    Parser(get_tokens("struct test { uint8[1+1] member1, int16 member2, uint8[-3+24] member2, }")).run()
    Parser(get_tokens("struct test { uint8[3*(2+3)] member1, int16 member2, uint8[-(-3*12)] member3, }")).run()
    Parser(get_tokens("struct test { uint8 member1, int16[some_struct.member_value*2] member2, }")).run()
    Parser(get_tokens("struct test { uint8[] member1, int16 member2, uint8[2*3-(3)] member2, }")).run()

def test_struct_endian():
    stmts = Parser(get_tokens("struct test { } BE struct test2 { }")).run()
    assert stmts[0].endian == BIG_ENDIAN
    assert stmts[1].endian == BIG_ENDIAN

    stmts = Parser(get_tokens("LE struct test { }")).run()
    assert stmts[0].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("struct test { uint8 member, } BE struct test2 { uint8 member, }")).run()
    assert stmts[0].endian == BIG_ENDIAN
    assert stmts[1].endian == BIG_ENDIAN

    stmts = Parser(get_tokens("LE struct test { uint8 member, }")).run()
    assert stmts[0].endian == LITTLE_ENDIAN

def test_struct_member_endian():
    stmts = Parser(get_tokens("struct test { uint8 member, } BE struct test2 { BE uint8 member, }")).run()
    assert stmts[0].members[0].endian == BIG_ENDIAN
    assert stmts[1].members[0].endian == BIG_ENDIAN

    stmts = Parser(get_tokens("struct test { LE uint8 member, } BE struct test2 { LE uint8 member, }")).run()
    assert stmts[0].members[0].endian == LITTLE_ENDIAN
    assert stmts[1].members[0].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("struct test { BE uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].endian == BIG_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].endian == BIG_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("LE struct test { uint8 member, uint8 member2, }")).run()
    assert stmts[0].members[0].endian == LITTLE_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("LE struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].endian == LITTLE_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("LE struct test { LE uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].endian == LITTLE_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

    stmts = Parser(get_tokens("BE struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].endian == BIG_ENDIAN
    assert stmts[0].members[1].endian == LITTLE_ENDIAN

def test_struct_members_errors():
    with pytest.raises(InvalidSyntaxError):
        # missing identifier
        Parser(get_tokens("struct { }")).run()

    with pytest.raises(InvalidSyntaxError):
        # keyword instead of identifier
        Parser(get_tokens("struct struct { }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing curly-braces
        Parser(get_tokens("struct MyStruct")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing first curly-brace
        Parser(get_tokens("struct MyStruct } ")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right curly-brace
        Parser(get_tokens("struct MyStruct { ")).run()

    with pytest.raises(InvalidSyntaxError):
        # member name with dot in it
        Parser(get_tokens("struct MyStruct { uint8 mem.ber,")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right curly-brace
        Parser(get_tokens("struct MyStruct { uint8 member,")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right curly-brace and comma
        Parser(get_tokens("struct MyStruct { uint8 member ")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing identifier
        Parser(get_tokens("struct MyStruct { uint8, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing identifier
        Parser(get_tokens("struct MyStruct { SomeIndentifier, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # invalid element after
        Parser(get_tokens("struct test { } uint8 member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma at the end of member
        Parser(get_tokens("struct test { uint8 member }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma separating members
        Parser(get_tokens("struct MyStruct { uint8 member1 uint8 member2, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right brack
        Parser(get_tokens("struct MyStruct { uint8[ member }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left brack
        Parser(get_tokens("struct MyStruct { uint8] member }")).run()
    
    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("struct test { 1 != 1 ? uint8 : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right parenthesis
        Parser(get_tokens("struct test { (1 != 1 ? uint8 : uint16 member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comparison
        Parser(get_tokens("struct test { (1  1 ? uint8 : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left part of comparison 
        Parser(get_tokens("struct test { ( != 1 ? uint8 : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right part of comparison 
        Parser(get_tokens("struct test { (1 !=  ? uint8 : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing question mark
        Parser(get_tokens("struct test { (1 != 1  uint8 : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing colon
        Parser(get_tokens("struct test { (1 != 1 ? uint8  uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing if true part
        Parser(get_tokens("struct test { (1 != 1 ?  : uint16) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing if false part
        Parser(get_tokens("struct test { (1 != 1 ? uint8 : ) member,}")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing condition results
        Parser(get_tokens("struct test { (1 != 1 ?  : ) member,}")).run()

def test_struct_members_with_expressions_errors():
    with pytest.raises(InvalidSyntaxError):
        # missing right parenthesis
        Parser(get_tokens("struct MyStruct { uint8[(1+2] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("struct MyStruct { uint8[1+2)] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("struct MyStruct { uint8[1 struct] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # wrong number of closing parenthesis
        Parser(get_tokens("struct MyStruct { uint8[((1+2)] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # wrong number of closing parenthesis
        Parser(get_tokens("struct MyStruct { uint8[((1+2)+1*(2*3)] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # wrong number of opening parenthesis
        Parser(get_tokens("struct MyStruct { uint8[(1+2))] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left operand
        Parser(get_tokens("struct MyStruct { uint8[/2] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right operand
        Parser(get_tokens("struct MyStruct { uint8[2/] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left operand
        Parser(get_tokens("struct MyStruct { uint8[/(2+5*3)] member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right operand
        Parser(get_tokens("struct MyStruct { uint8[(2+5*3)/] member, }")).run()

def test_empty_bitfield():
    parser = Parser(get_tokens("bitfield test { }")).run()

def test_empty_bitfield_with_size_in_bytes():
    Parser(get_tokens("bitfield test (1) { }")).run()
    Parser(get_tokens("bitfield test (1+3) { }")).run()
    Parser(get_tokens("bitfield test (2-1*(3*5)) { }")).run()

def test_bitfield_members():
    Parser(get_tokens("bitfield test { member, }")).run()
    Parser(get_tokens("bitfield test { member1, member2, }")).run()
    Parser(get_tokens("bitfield test { member1, member2, member3, member4, }")).run()

def test_bitfield_members_with_size():
    Parser(get_tokens("bitfield test { member (2), }")).run()
    Parser(get_tokens("bitfield test { member1 (1), member2 (3), }")).run()
    Parser(get_tokens("bitfield test { member1 (1), member2 (3 + 2), }")).run()
    Parser(get_tokens("bitfield test { member1(1), member2, }")).run()
    Parser(get_tokens("bitfield test { member1, member2 (3 + 2), }")).run()

def test_bitfield_with_size_with_members():
    Parser(get_tokens("bitfield test (5) { member (1), }")).run()
    Parser(get_tokens("bitfield test (5) { member1 (1), member2 (5+2), }")).run()
    Parser(get_tokens("bitfield test (5) { member1, member2 (5+2), }")).run()
    Parser(get_tokens("bitfield test (5) { member1(3*(2+3)), member2 (5+2), }")).run()
    Parser(get_tokens("bitfield test (5) { member1(3*(2+3)), member2, }")).run()

def test_bitfield_with_members_with_errors():
    with pytest.raises(InvalidSyntaxError):
        # missing size
        Parser(get_tokens("bitfield test () { }")).run()

    with pytest.raises(InvalidSyntaxError):
        # invalid size (keyword)
        Parser(get_tokens("bitfield test (bitfield) { }")).run()

    with pytest.raises(InvalidSyntaxError):
        # invalid size (identifier)
        Parser(get_tokens("bitfield test (some_identifier) { }")).run()

    with pytest.raises(InvalidSyntaxError):
        # invalid size (keyword)
        Parser(get_tokens("bitfield test (bitfield) { some_flag, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # invalid size (identifier)
        Parser(get_tokens("bitfield test (some_identifier) { some_flag, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("bitfield test ) { some_flag, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right parenthesis
        Parser(get_tokens("bitfield test ( { some_flag, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing identifier
        Parser(get_tokens("bitfield test { , }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left curl-brace
        Parser(get_tokens("bitfield test }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right curl-brace
        Parser(get_tokens("bitfield test {")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left curl-brace
        Parser(get_tokens("bitfield test (2) }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right curl-brace
        Parser(get_tokens("bitfield test (2) {")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma
        Parser(get_tokens("bitfield test (2) { some_flag }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma
        Parser(get_tokens("bitfield test { some_flag }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing size in parenthesis
        Parser(get_tokens("bitfield test { some_flag() }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma
        Parser(get_tokens("bitfield test { some_flag (bitfield) }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("bitfield test { some_flag 8), }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right parenthesis
        Parser(get_tokens("bitfield test { some_flag (8, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing comma
        Parser(get_tokens("bitfield test { some_flag (8) }")).run()