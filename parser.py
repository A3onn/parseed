#!/usr/bin/env python3
from typing import List, Any, Union, Dict
from lexer import *
from ast_nodes import *
from errors import InvalidSyntaxError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.token_index: int = -1

        # self.tokens contains at least a TT_EOF token
        self.current_token: Token = self.tokens[0]
        self.advance()

    def run(self) -> list:
        """
        Returns a list of nodes (AST).
        """
        return self.statements()

    def advance(self) -> Token:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        if self.current_token.type == TT_COMMENT:
            # just ignore comments, we don't need them when parsing
            self.advance()
        return self.current_token

    def statements(self) -> list:
        res: list = []
        while self.current_token.type != TT_EOF:
            res.append(self.statement())
        return res

    def statement(self):
        token: Token = self.current_token

        if token.type == TT_KEYWORD:
            if token.value == "struct" or token.value in (BIG_ENDIAN, LITTLE_ENDIAN):
                return self.struct_stmt()
            elif token.value == "bitfield":
                return self.bitfield_stmt()
        else:
            raise InvalidSyntaxError(token.pos_start, token.pos_end, "expected struct or bitfield statement")

        self.advance()

    def bitfield_member_def(self) -> BitfieldMemberNode:
        """
        <bitfield_member_def> ::= <identifier> "(" <no_identifier_expr> ")"? ","
        """
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        name_token: Token = self.current_token
        self.advance()

        bits_count: ASTNode = None  # size of the member
        if self.current_token.type == TT_LPAREN:
            self.advance()
            size = self.no_identifier_expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()

        if self.current_token.type != TT_COMMA:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")
        self.advance()

        return BitfieldMemberNode(name_token, bits_count)

    def bitfield_stmt(self) -> BitfieldDefNode:
        """
        <bitfield_stmt> ::= "bitfield" <identifier> "{" <bitfield_member_def>+ "}"
                            | "bitfield" <identifier> "(" <no_identifier_expr> ")" "{" <bitfield_member_def>+ "}"
        """
        self.advance()
        name: str = self.current_token

        self.advance()
        bytes_count: ASTNode = None  # size of the bitfield
        if self.current_token.type == TT_LPAREN:
            self.advance()
            size = self.no_identifier_expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()

        if self.current_token.type != TT_LCURLY:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        members: List = []
        while self.current_token.type not in [TT_RCURLY, TT_EOF]:
            members.append(self.bitfield_member_def())

        if self.current_token.type == TT_EOF:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '}'")

        self.advance()
        return BitfieldDefNode(name, members, bytes_count)

    def struct_stmt(self) -> StructDefNode:
        """
        <struct_stmt> ::= ["LE" | "BE"] "struct" <identifier> "{" (<struct_member_def> | <match_stmt>)+ "}"
        """
        endian = BIG_ENDIAN
        if self.current_token.value in (BIG_ENDIAN, LITTLE_ENDIAN):
            if self.current_token.value == LITTLE_ENDIAN:
                endian = LITTLE_ENDIAN
            self.advance()

        self.advance()
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        struct_name = self.current_token
        self.advance()

        if self.current_token.type != TT_LCURLY:  # '{', start of struct
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        struct_members: List[StructMemberDeclareNode] = []
        while self.current_token.type not in [TT_RCURLY, TT_EOF]:
            if self.current_token.type == TT_KEYWORD and self.current_token.value == "match":
                struct_members.append(self.match_stmt(endian))
            else:
                struct_members.append(self.struct_member_def(endian))

        if self.current_token.type == TT_EOF:  # if missing '}'
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '}'")
        self.advance()

        return StructDefNode(struct_name, struct_members, endian)
    
    def struct_member_type(self, struct_endian: str) -> StructMemberTypeNode:
        """
        <struct_member_type> ::= ["LE" | "BE"] (<data_type> | <ternary_data_type> | <identifier>)
                                | ["LE" | "BE"] (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
                                | ["LE" | "BE"] (<data_type> | <ternary_data_type> | <identifier>) "[]"  ;; repeat this member until the end of the buffer
        """
        endian = struct_endian
        if self.current_token.value in (BIG_ENDIAN, LITTLE_ENDIAN):
            if self.current_token.value == LITTLE_ENDIAN:
                endian = LITTLE_ENDIAN
            self.advance()

        if self.current_token.type not in [TT_DATA_TYPE, TT_IDENTIFIER, TT_LPAREN]:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected data-type, identifier or ternary operator")

        if self.current_token.type == TT_LPAREN:
            member_type: TernaryDataTypeNode = self.ternary_data_type()
        else:
            member_type: Token = self.current_token
            self.advance()

        is_list: bool = False
        list_length_node: Any = None

        if self.current_token.type == TT_IDENTIFIER:  # nothing to do, just continue parsing
            return StructMemberTypeNode(member_type, endian)
        elif self.current_token.type == TT_LPAREN and member_type.value == "string":
            self.advance()

            delimiter: str = ""
            if self.current_token.type == TT_BACKSLASH:
                delimiter += "\\"
                self.advance()
            delimiter += self.current_token.value
            
            if delimiter == "" or delimiter == "\\" or delimiter == None:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected character as delimiter")
            self.advance()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return StructMemberTypeNode(member_type, endian, string_delimiter=delimiter)
        elif self.current_token.type == TT_LBRACK:
            is_list = True
            self.advance()
            list_length_node = None
            if self.current_token.type != TT_RBRACK:
                list_length_node = self.expr()
            if self.current_token.type != TT_RBRACK:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ']'")
            self.advance()

        return StructMemberTypeNode(member_type, endian, is_list, list_length_node)

    def struct_member_def(self, struct_endian: str) -> StructMemberDeclareNode:
        """
        <struct_member_def> ::= <struct_member_type> <identifier> ","
        """
        member_type: StructMemberTypeNode = self.struct_member_type(struct_endian)
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")
        member_name: Token = self.current_token
        self.advance()

        if self.current_token.type == TT_COMMA:
            self.advance()
        else:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")

        return StructMemberDeclareNode(member_type, member_name)

    def match_stmt(self, struct_endian: str) -> MatchNode:
        """
        <match_stmt> ::= "match (" <expr> ") {" (<expr> ":" <struct_member_type> ",")+ "}" <identifier> ","
                        | "match (" <expr> ") {" (<expr> ": {" <struct_member_def>+ "},")+ "},"  ;; multiple members in the match case
        """
        self.advance()
        if self.current_token.type != TT_LPAREN:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '('")
        self.advance()

        condition: ASTNode = self.expr()

        if self.current_token.type != TT_RPAREN:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
        self.advance()

        if self.current_token.type != TT_LCURLY:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        # start of match cases
        cases: Dict = {}
        is_multiple_members: bool = False  # need to know to check after this while loop if an identifier is needed
        while self.current_token.type != TT_RCURLY:
            case_value: ASTNode = self.expr()
            if self.current_token.type != TT_COLON:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ':'")
            self.advance()

            if self.current_token.type == TT_LCURLY:  # multiple members
                is_multiple_members = True
                self.advance()
                while self.current_token.type != TT_RCURLY:
                    cases.update({case_value: self.struct_member_def(struct_endian)})
                self.advance()
            else:
                cases.update({case_value: self.struct_member_type(struct_endian)})

            if self.current_token.type != TT_COMMA:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")
            self.advance()

        self.advance()

        member_name: str = None
        if not is_multiple_members:
            if self.current_token.type != TT_IDENTIFIER:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")
            member_name = self.current_token.value
            self.advance()

        if self.current_token.type != TT_COMMA:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")
        self.advance()

        return MatchNode(condition, cases, member_name)

    def ternary_data_type(self) -> TernaryDataTypeNode:
        """
        <ternary_data_type> ::= "(" <comparison> "?" <data_type> ":" <data_type> ")"
        """
        self.advance()
        comparison_node: ComparisonNode = self.comparison()
        if self.current_token.type != TT_QUESTION_MARK:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '?'")
        self.advance()

        if_true_token: Token = self.current_token

        self.advance()
        if self.current_token.type != TT_COLON:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ':'")
        self.advance()

        if_false_token: Token = self.current_token

        self.advance()
        if self.current_token.type != TT_RPAREN:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
        self.advance()

        if_true: IdentifierAccessNode = IdentifierAccessNode(if_true_token.value)
        if if_true_token.value in DATA_TYPES:
            if_true = DataType(if_true_token.value)

        if_false: IdentifierAccessNode = IdentifierAccessNode(if_false_token.value)
        if if_false_token.value in DATA_TYPES:
            if_false = DataType(if_false_token.value)

        return TernaryDataTypeNode(comparison_node, if_true, if_false)

    def comparison(self) -> ComparisonNode:
        """
        <comparison> ::= <expr> <comparator> <expr>
        """
        left_cond_op: Token = self.expr()
        comparator_token: Token = self.current_token
        comparators_dict: Dict = {TT_COMP_EQ: "==", TT_COMP_NE: "!=", TT_COMP_GT: ">", TT_COMP_LT: "<", TT_COMP_GEQ: ">=", TT_COMP_LEQ: "<="}
        if comparator_token.type not in comparators_dict.keys():
            list_comp: str = ", ".join([f"'{c}'" for c in comparators_dict.values()])
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"expected one of: " + list_comp)
        self.advance()
        right_cond_op: Token = self.expr()

        return ComparisonNode(left_cond_op, comparators_dict[comparator_token.type], right_cond_op)

    def no_identifier_factor(self) -> Any:
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS]:
            self.advance()
            return UnaryOpNode(token, self.no_identifier_factor())
        elif token.type == TT_LPAREN:
            self.advance()
            expr = self.no_identifier_expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return expr
        elif token.type == TT_NUM_INT:
            self.advance()
            return IntNumberNode(token)
        elif token.type == TT_NUM_FLOAT:
            self.advance()
            return FloatNumberNode(token)
        raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value")

    def no_identifier_expr(self) -> Any:
        return self.binary_op(self.no_identifier_term, [TT_PLUS, TT_MINUS])

    def no_identifier_term(self) -> Any:
        return self.binary_op(self.no_identifier_factor, [TT_MULT, TT_DIV])

    def factor(self) -> Any:
        """
        <factor> ::= <num_int> | <num_float>
                    | ("+" | "-") <factor>
                    | "(" <expr> ")"
                    | <identifier> ("." <identifier>)*
        """
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS]:
            self.advance()
            return UnaryOpNode(token, self.factor())
        elif token.type == TT_LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return expr
        elif token.type == TT_NUM_INT:
            self.advance()
            return IntNumberNode(token)
        elif token.type == TT_NUM_FLOAT:
            self.advance()
            return FloatNumberNode(token)
        elif token.type == TT_IDENTIFIER:
            identifier_name: str = self.current_token.value
            pos_start: Position = self.current_token.pos_start.get_copy()  # for errors
            self.advance()
            if self.current_token.type == TT_DOT:  # handle identifiers with '.' in them
                while True:  # consume tokens until there is another thing than a valid identifier
                    self.advance()
                    if self.current_token.type != TT_IDENTIFIER:  # check if it is a valid identifier (avoid having numbers in the middle of the whole identifier for exemple)
                        raise InvalidSyntaxError(pos_start, self.current_token.pos_end, "invalid identifier")
                    identifier_name += "." + self.current_token.value
                    self.advance()
                    if self.current_token.type != TT_DOT:
                        break
            return IdentifierAccessNode(identifier_name)
        raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier or value")

    def expr(self) -> Any:
        return self.binary_op(self.term, [TT_PLUS, TT_MINUS])

    def term(self) -> Any:
        return self.binary_op(self.factor, [TT_MULT, TT_DIV])

    def binary_op(self, func, operators) -> BinOpNode:
        left_token = func()

        if left_token is None:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value or expression")

        while self.current_token.type in operators:
            op_token = self.current_token
            self.advance()
            right_token = func()

            if right_token is None:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected value or expression")

            left_token = BinOpNode(left_token, op_token, right_token)
        return left_token
