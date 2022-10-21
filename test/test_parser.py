#!/usr/bin/env python3
from parser import Parser
from ast_nodes import *
from lexer import Lexer
from errors import InvalidSyntaxError
from utils import *
import pytest


"""
Call to_str() method for each statement to be sure that no name or logic errors are present in this method.
"""

def get_tokens(text):
    return Lexer(text, "").run()


def test_simple():
    parser = Parser(get_tokens(""))
    parser.run()

def test_empty_struct():
    parser = Parser(get_tokens("struct test { }"))
    parser.run()

def test_struct_members():
    Parser(get_tokens("struct test { uint8 member, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8 member1, float member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[1] member,}")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[] member,}")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[] member1, uint16[] member2,}")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8 member1, float[member1] member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, int24[15] member3, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[4] member1, float member2, int24[] member3, }")).run()[0].to_str()
    Parser(get_tokens("struct test { (1 == 1 ? uint8 : uint16)[] member,}")).run()[0].to_str()
    Parser(get_tokens("struct test { (1 != 1 ? uint8 : SomeIdentifier) member,}")).run()[0].to_str()
    Parser(get_tokens("struct test { LE (1 != 1 ? uint8 : uint16) member1, (2 == 2 ? uint16 : int16) member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { (1 != 1 ? SomeIdentifier : SomeIdentifier) member,}")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8 member1, LE (2 == 2 ? uint16 : int16) member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { SomeIndentifier member, }")).run()[0].to_str()
    Parser(get_tokens("struct test { SomeIndentifier member1, float member2, AnotherIdentifier member3, }")).run()[0].to_str()
    Parser(get_tokens("struct test { SomeIndentifier member1, float member2, AnotherIdentifier[3] member3, AnotherOne[] member4,}")).run()[0].to_str()

def test_struct_members_with_expressions():
    stmts = Parser(get_tokens("struct test { uint8[1+1] member, }")).run()
    assert isinstance(stmts[0].members[0].infos.list_length, BinOpNode)
    assert isinstance(stmts[0].members[0].infos.list_length.left_node, IntNumberNode)
    assert isinstance(stmts[0].members[0].infos.list_length.right_node, IntNumberNode)
    assert stmts[0].members[0].infos.list_length.op.type == MathOperatorNode.ADD
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { uint8[-1] member, }")).run()
    assert isinstance(stmts[0].members[0].infos.list_length, UnaryOpNode)
    assert isinstance(stmts[0].members[0].infos.list_length.value, IntNumberNode)
    assert stmts[0].members[0].infos.list_length.value.value == 1
    assert stmts[0].members[0].infos.list_length.op.type == MathOperatorNode.SUBTRACT
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { uint8[1+1] member1, uint8[15-3] member2, }")).run()
    assert isinstance(stmts[0].members[1].infos.list_length, BinOpNode)
    assert isinstance(stmts[0].members[1].infos.list_length.left_node, IntNumberNode)
    assert isinstance(stmts[0].members[1].infos.list_length.right_node, IntNumberNode)
    assert stmts[0].members[1].infos.list_length.op.type == MathOperatorNode.SUBTRACT
    stmts[0].to_str()

    Parser(get_tokens("struct test { uint8[1+1] member1, int16 member2, uint8[-3+24] member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[3*(2+3)] member1, int16 member2, uint8[-(-3*12)] member3, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8 member1, int16[some_struct.member_value*2] member2, }")).run()[0].to_str()
    Parser(get_tokens("struct test { uint8[] member1, int16 member2, uint8[2*3-(3)] member2, }")).run()[0].to_str()

def test_struct_endian():
    stmts = Parser(get_tokens("struct test { } BE struct test2 { }")).run()
    assert stmts[0].endian == Endian.BIG
    assert stmts[1].endian == Endian.BIG
    stmts[0].to_str()
    stmts[1].to_str()

    stmts = Parser(get_tokens("LE struct test { }")).run()
    assert stmts[0].endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { uint8 member, } BE struct test2 { uint8 member, }")).run()
    assert stmts[0].endian == Endian.BIG
    assert stmts[1].endian == Endian.BIG
    stmts[0].to_str()
    stmts[1].to_str()

    stmts = Parser(get_tokens("LE struct test { uint8 member, }")).run()
    assert stmts[0].endian == Endian.LITTLE
    stmts[0].to_str()

    with pytest.raises(InvalidSyntaxError):
        stmts = Parser(get_tokens("(1 == 1 ? LE : BE) struct test { uint8 member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        stmts = Parser(get_tokens("(1 != test ? LE : BE) struct test { uint8 member, }")).run()

def test_struct_member_endian():
    stmts = Parser(get_tokens("struct test { uint8 member, } BE struct test2 { BE uint8 member, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.BIG
    assert stmts[1].members[0].infos.endian == Endian.BIG
    stmts[0].to_str()
    stmts[1].to_str()

    stmts = Parser(get_tokens("struct test { LE uint8 member, } BE struct test2 { LE uint8 member, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.LITTLE
    assert stmts[1].members[0].infos.endian == Endian.LITTLE
    stmts[0].to_str()
    stmts[1].to_str()

    stmts = Parser(get_tokens("struct test { BE uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.BIG
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.BIG
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { uint8 member, uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.LITTLE
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.LITTLE
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { LE uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.LITTLE
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("BE struct test { uint8 member, LE uint8 member2, }")).run()
    assert stmts[0].members[0].infos.endian == Endian.BIG
    assert stmts[0].members[1].infos.endian == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { (1 == 1 ? BE : LE) uint8 member, }")).run()
    assert isinstance(stmts[0].members[0].infos.endian, TernaryEndianNode)
    assert stmts[0].members[0].infos.endian.if_true == Endian.BIG
    assert stmts[0].members[0].infos.endian.if_false == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { (1 == 1 ? BE : LE) uint8 member, }")).run()
    assert isinstance(stmts[0].members[0].infos.endian, TernaryEndianNode)
    assert stmts[0].members[0].infos.endian.if_true == Endian.BIG
    assert stmts[0].members[0].infos.endian.if_false == Endian.LITTLE
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { (1 == 1 ? LE : BE) uint8 member, }")).run()
    assert isinstance(stmts[0].members[0].infos.endian, TernaryEndianNode)
    assert stmts[0].members[0].infos.endian.if_true == Endian.LITTLE
    assert stmts[0].members[0].infos.endian.if_false == Endian.BIG
    stmts[0].to_str()

    stmts = Parser(get_tokens("LE struct test { (1 == 1 ? LE : BE) (2 == 1 ? uint16 : uint8) member, }")).run()
    assert isinstance(stmts[0].members[0].infos.endian, TernaryEndianNode)
    assert stmts[0].members[0].infos.endian.if_true == Endian.LITTLE
    assert stmts[0].members[0].infos.endian.if_false == Endian.BIG
    stmts[0].to_str()

def test_struct_members_string():
    stmts = Parser(get_tokens(r"struct test { string test, }")).run()
    assert stmts[0].members[0].infos.type == "string"
    assert stmts[0].members[0].infos.string_delimiter == r"\0"
    assert stmts[0].members[0].infos.as_data_type().string_delimiter == r"\0"
    stmts[0].to_str()

    stmts = Parser(get_tokens(r"struct test { string(\0) test, }")).run()
    assert stmts[0].members[0].infos.type == "string"
    assert stmts[0].members[0].infos.string_delimiter == r"\0"
    assert stmts[0].members[0].infos.as_data_type().string_delimiter == r"\0"
    stmts[0].to_str()

    stmts = Parser(get_tokens(r"struct test { string(\x15) test, }")).run()
    assert stmts[0].members[0].infos.type == "string"
    assert stmts[0].members[0].infos.string_delimiter == r"\x15"
    assert stmts[0].members[0].infos.as_data_type().string_delimiter == r"\x15"
    stmts[0].to_str()

    stmts = Parser(get_tokens(r"struct test { string(test) test, }")).run()
    assert stmts[0].members[0].infos.type == "string"
    assert stmts[0].members[0].infos.string_delimiter == "test"
    assert stmts[0].members[0].infos.as_data_type().string_delimiter == "test"
    stmts[0].to_str()

def test_struct_members_match():
    stmts = Parser(get_tokens("struct test { match(1+1) {1: uint8,} member, }")).run()
    assert isinstance(stmts[0].members[0], MatchNode)
    assert isinstance(stmts[0].members[0].condition, BinOpNode)
    assert stmts[0].members[0].member_name == "member"
    assert len(stmts[0].members[0].cases) == 1
    cases = stmts[0].members[0].cases
    assert isinstance(list(cases.keys())[0], IntNumberNode) # first case element
    assert cases[list(cases.keys())[0]].type == "uint8" # first case element
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { match(1+1) {1: uint8, 2: uint16,} member, }")).run()
    assert len(stmts[0].members[0].cases) == 2
    assert stmts[0].members[0].member_name == "member"
    cases = stmts[0].members[0].cases
    assert isinstance(list(cases.keys())[0], IntNumberNode) # first case element
    assert cases[list(cases.keys())[0]].type == "uint8" # first case element
    assert isinstance(list(cases.keys())[1], IntNumberNode) # second case element
    assert cases[list(cases.keys())[1]].type == "uint16" # second case element
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { match(15+(-3)*2) {-15*2: uint8, (95): uint16,} member, }")).run()
    cases = stmts[0].members[0].cases
    assert isinstance(list(cases.keys())[0], BinOpNode)
    assert isinstance(stmts[0].members[0].condition, BinOpNode)
    assert cases[list(cases.keys())[0]].type == "uint8"
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { uint16 first_member, match(first_member*2) {first_member+3: uint8, first_member*3: uint16,} second_member,}")).run()
    assert isinstance(stmts[0].members[1], MatchNode)
    cases = stmts[0].members[1].cases
    assert isinstance(list(cases.keys())[0], BinOpNode)
    assert isinstance(list(cases.keys())[1], BinOpNode)
    stmts = Parser(get_tokens("struct test { match(1+1) {1: {uint8 member1, uint8 member2,}, 2: {uint16 member1, uint16 member2,},},}")).run()
    cases = stmts[0].members[0].cases
    # first case
    assert len(cases[list(cases.keys())[0]]) == 2
    assert isinstance(cases[list(cases.keys())[0]][0], StructMemberDeclareNode)
    assert isinstance(cases[list(cases.keys())[0]][1], StructMemberDeclareNode)
    # second case
    assert len(cases[list(cases.keys())[1]]) == 2
    assert isinstance(cases[list(cases.keys())[1]][0], StructMemberDeclareNode)
    assert isinstance(cases[list(cases.keys())[1]][1], StructMemberDeclareNode)
    stmts[0].to_str()

    stmts = Parser(get_tokens("struct test { match(1+1) {1: {uint8 some_member1, uint8 some_member2,}, 2: {uint16 member1, uint16 member2,},}, }")).run()
    stmts[0].to_str()

def test_struct_members_match_errors():
    with pytest.raises(InvalidSyntaxError):
        # missing comma
        Parser(get_tokens("struct test { match(1+1) {1: uint8} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing match expression
        Parser(get_tokens("struct test { match() {: uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing left parenthesis
        Parser(get_tokens("struct test { match 1+1) {1: uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing right parenthesis
        Parser(get_tokens("struct test { match(1+1 {1: uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing opening curl-bracket
        Parser(get_tokens("struct test { match(1+1) 1: uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing closing curl-bracket
        Parser(get_tokens("struct test { match(1+1) {1: uint8, member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing case expression
        Parser(get_tokens("struct test { match(1+1) {: uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing colon
        Parser(get_tokens("struct test { match(1+1) {1 uint8,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing type
        Parser(get_tokens("struct test { match(1+1) {1: ,} member, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # identifier not needed
        Parser(get_tokens("struct test { match(1+1) {1: {uint8 member,}} not_here, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing member name
        Parser(get_tokens("struct test { match(1+1) {1: uint8 }, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # missing closing curly-bracket
        Parser(get_tokens("struct test { match(1+1) {1: {uint8 member}, }")).run()

    with pytest.raises(InvalidSyntaxError):
        # identifier not supposed to be there
        Parser(get_tokens("struct test { match(1+1) {1: uint8, invalid-identifier} member, }")).run()

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
    parser = Parser(get_tokens("bitfield test { }")).run()[0].to_str()

def test_empty_bitfield_with_size_in_bytes():
    Parser(get_tokens("bitfield test (1) { }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (1+3) { }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (2-1*(3*5)) { }")).run()[0].to_str()

def test_bitfield_members():
    Parser(get_tokens("bitfield test { member, }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1, member2, }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1, member2, member3, member4, }")).run()[0].to_str()

def test_bitfield_members_with_size():
    Parser(get_tokens("bitfield test { member (2), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1 (1), member2 (3), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1 (1), member2 (3 + 2), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1(1), member2, }")).run()[0].to_str()
    Parser(get_tokens("bitfield test { member1, member2 (3 + 2), }")).run()[0].to_str()

def test_bitfield_with_size_with_members():
    Parser(get_tokens("bitfield test (5) { member (1), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (5) { member1 (1), member2 (5+2), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (5) { member1, member2 (5+2), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (5) { member1(3*(2+3)), member2 (5+2), }")).run()[0].to_str()
    Parser(get_tokens("bitfield test (5) { member1(3*(2+3)), member2, }")).run()[0].to_str()

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