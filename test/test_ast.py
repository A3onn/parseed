#!/usr/bin/env python3
from lexer import Lexer, TT_COMP_EQ
from parser import Parser
from ast_nodes import *
from utils import Endian

def get_AST(text):
    tokens = Lexer(text, "").run()
    return Parser(tokens).run()

def test_struct():
    ast = get_AST("struct test { }")
    assert len(ast) == 1
    assert isinstance(ast[0], StructDefNode)
    assert ast[0].name == "test"
    assert len(ast[0].members) == 0
    assert ast[0].endian == Endian.BIG

def test_struct_members():
    ast = get_AST("struct test { uint8 some_member, }")
    assert len(ast) == 1
    assert len(ast[0].members) == 1

    member = ast[0].members[0]
    assert isinstance(member, StructMemberDeclareNode)
    assert member.name == "some_member"
    assert member.infos.type == "uint8"
    assert member.infos.endian == Endian.BIG


    ast = get_AST("struct test { uint8 some_member, LE uint16 member2,}")
    assert len(ast[0].members) == 2

    assert isinstance(ast[0].members[0], StructMemberDeclareNode)
    assert ast[0].members[0].name == "some_member"
    assert ast[0].members[0].infos.type == "uint8"
    assert ast[0].members[0].infos.endian == Endian.BIG
    assert isinstance(ast[0].members[1], StructMemberDeclareNode)
    assert ast[0].members[1].name == "member2"
    assert ast[0].members[1].infos.type == "uint16"
    assert ast[0].members[1].infos.endian == Endian.LITTLE
    
def test_struct_member_ternary_type():
    ast = get_AST("struct test { (1 == 1 ? uint8 : uint16) member, }")
    assert len(ast) == 1
    assert len(ast[0].members) == 1

    member = ast[0].members[0]
    assert isinstance(member, StructMemberDeclareNode)
    assert member.name == "member"
    assert member.infos.endian == Endian.BIG
    assert isinstance(member.infos.type, TernaryDataTypeNode)
    assert isinstance(member.infos.type.if_true, DataType)
    assert isinstance(member.infos.type.if_false, DataType)

    assert isinstance(member.infos.type.comparison, ComparisonNode)
    assert member.infos.type.comparison.left_node.value == 1
    assert member.infos.type.comparison.right_node.value == 1
    assert member.infos.type.comparison.comparison_op.type == ComparisonOperatorNode.EQUAL
