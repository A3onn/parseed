#!/usr/bin/env python3
from typing import List, Any, Union, Dict
from lexer import *
from ast_nodes import *
from errors import InvalidStateError, InvalidSyntaxError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.token_index: int = -1

        # self.tokens contains at least a TT_EOF token
        self.current_token: Token = self.tokens[0]
        self.advance()

    def _rollback_to(self, token: Token):
        """
        Rollback parser to specified token.
        The token must be in the self.tokens.

        :param token: Token to rollback to.
        :type token: Token, must be an instance present in the self.tokens list.
        """
        for i, t in enumerate(self.tokens):
            if t == token:
                self.current_token = t
                self.token_index = i

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
            if token.value == STRUCT_KEYWORD or token.value in ENDIANNESS_KEYWORDS:
                return self.struct_stmt()
            elif token.value == BITFIELD_KEYWORD:
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
            bits_count = self.no_identifier_expr()
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
        name: Token = self.current_token

        self.advance()
        bytes_count: Optional[ASTNode] = None  # size of the bitfield
        if self.current_token.type == TT_LPAREN:
            self.advance()
            bytes_count = self.no_identifier_expr()
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
        <struct_stmt> ::= (<endian> | <ternary_endian>)+ "struct" <identifier> "{" (<struct_member_def> | <match_stmt>)+ "}"

        <endian> ::= "LE" | "BE"
        <ternary_endian> ::= "(" <comparison> "?" <endian> ":" <endian> ")"
        """
        endian = Endian.BIG
        if self.current_token.value == LITTLE_ENDIAN_KEYWORD:
            endian = Endian.LITTLE
            self.advance()
        elif self.current_token.value == BIG_ENDIAN_KEYWORD:
            endian = Endian.BIG
            self.advance()

        self.advance()
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")

        struct_name = self.current_token
        self.advance()

        if self.current_token.type != TT_LCURLY:  # '{', start of struct
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '{'")
        self.advance()

        struct_members: List[Union[StructMemberDeclareNode, MatchNode]] = []
        while self.current_token.type not in [TT_RCURLY, TT_EOF]:
            if self.current_token.type == TT_KEYWORD and self.current_token.value == MATCH_KEYWORD:
                struct_members.append(self.match_stmt(endian))
            else:
                struct_members.append(self.struct_member_def(endian))

        if self.current_token.type == TT_EOF:  # if missing '}'
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '}'")
        self.advance()

        return StructDefNode(struct_name, struct_members, endian)

    def struct_member_type(self, struct_endian: Endian) -> StructMemberInfoNode:
        """
        <struct_member_type> ::= (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>)
                                | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
                                | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"  ;; repeat this member until the end of the buffer

        <endian> ::= "LE" | "BE"
        <ternary_endian> ::= "(" <comparison> "?" <endian> ":" <endian> ")"
        """
        endian = struct_endian
        # check endian without ternary
        if self.current_token.type == TT_KEYWORD and self.current_token.value == LITTLE_ENDIAN_KEYWORD:
            endian = Endian.LITTLE
            self.advance()
        elif self.current_token.type == TT_KEYWORD and self.current_token.value == BIG_ENDIAN_KEYWORD:
            endian = Endian.BIG
            self.advance()

        if self.current_token.type not in [TT_DATA_TYPE, TT_IDENTIFIER, TT_LPAREN]:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected data-type, identifier or ternary operator")

        member_type: Union[Token, TernaryDataTypeNode]

        if self.current_token.type == TT_LPAREN:
            # either endian or type, we cannot know now
            res: Union[TernaryEndianNode, TernaryDataTypeNode] = self._handle_ternary_member_type_or_endian()
            if isinstance(res, TernaryDataTypeNode):
                member_type = res
            else:
                endian = res
                # now that we are sure we passed the endian, we can check for the type
                if self.current_token.type == TT_LPAREN:
                    member_type = self.ternary_data_type()
                else:
                    member_type = self.current_token
                    self.advance()
        else:
            # endian and ternary data type was check just before
            # we are sure that we are dealing with the type here
            member_type = self.current_token
            self.advance()

        is_list: bool = False
        list_length_node: Any = None

        if self.current_token.type == TT_IDENTIFIER:  # nothing to do, just continue parsing
            return StructMemberInfoNode(member_type, endian)
        elif self.current_token.type == TT_LPAREN and isinstance(member_type, Token) and member_type.value == "string":
            self.advance()

            delimiter: str = ""
            if self.current_token.type == TT_BACKSLASH:
                delimiter += "\\"
                self.advance()

            if self.current_token.value == "" or self.current_token.value == "\\" or self.current_token.value is None:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected character as delimiter")
            delimiter += self.current_token.value

            self.advance()
            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
            self.advance()
            return StructMemberInfoNode(member_type, endian, string_delimiter=delimiter)
        elif self.current_token.type == TT_LBRACK:
            is_list = True
            self.advance()
            list_length_node = None
            if self.current_token.type != TT_RBRACK:
                list_length_node = self.expr()
            if self.current_token.type != TT_RBRACK:
                raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ']'")
            self.advance()

        return StructMemberInfoNode(member_type, endian, is_list, list_length_node)

    def struct_member_def(self, struct_endian: Endian) -> StructMemberDeclareNode:
        """
        <struct_member_def> ::= <struct_member_type> <identifier> ","
        """
        member_type: StructMemberInfoNode = self.struct_member_type(struct_endian)
        if self.current_token.type != TT_IDENTIFIER:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected identifier")
        member_name: Token = self.current_token
        self.advance()

        if self.current_token.type == TT_COMMA:
            self.advance()
        else:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ','")

        return StructMemberDeclareNode(member_type, member_name)

    def match_stmt(self, struct_endian: Endian) -> MatchNode:
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
                    if case_value in cases.keys():
                        cases[case_value].append(self.struct_member_def(struct_endian))
                    else:
                        cases.update({case_value: [self.struct_member_def(struct_endian)]})
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

    def _handle_ternary_member_type_or_endian(self) -> Union[TernaryEndianNode, TernaryDataTypeNode]:
        tmp_curr_token = self.current_token
        try:
            return self.ternary_endian()
        except InvalidStateError:
            self._rollback_to(tmp_curr_token)
            return self.ternary_data_type()

    def ternary_endian(self) -> TernaryEndianNode:
        """
        <endian> ::= "LE" | "BE"

        <ternary_endian> ::= "(" <comparison> "?" <endian> ":" <endian> ")"
        """
        self.advance()
        comparison_node: ComparisonNode = self.comparison()
        if self.current_token.type != TT_QUESTION_MARK:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected '?'")
        self.advance()

        if self.current_token.type != TT_KEYWORD or self.current_token.value not in ENDIANNESS_KEYWORDS:
            raise InvalidStateError("Not a ternary endian.")
        if_true: Endian = Endian.from_token(self.current_token)
        self.advance()

        if self.current_token.type != TT_COLON:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ':'")
        self.advance()

        if self.current_token.type != TT_KEYWORD or self.current_token.value not in ENDIANNESS_KEYWORDS:
            raise InvalidStateError("Not a ternary endian.")

        if_false: Endian = Endian.from_token(self.current_token)
        self.advance()

        if self.current_token.type != TT_RPAREN:
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'")
        self.advance()

        return TernaryEndianNode(comparison_node, if_true, if_false)

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

        if_true: Union[IdentifierAccessNode, DataType] = IdentifierAccessNode(if_true_token.value)
        if if_true_token.value in DATA_TYPES:
            if_true = DataType(if_true_token.value)

        if_false: Union[IdentifierAccessNode, DataType] = IdentifierAccessNode(if_false_token.value)
        if if_false_token.value in DATA_TYPES:
            if_false = DataType(if_false_token.value)

        return TernaryDataTypeNode(comparison_node, if_true, if_false)

    def comparison(self) -> ComparisonNode:
        """
        <comparison> ::= <expr> <comparison_operator> <expr>
        <comparison_operator> ::= "<=" | "<" | "==" | ">" | ">=" | "!=" | "&&" | "||"
        """
        left_node: ASTNode = self.expr()
        comparison_op_token: Token = self.current_token
        comparison_op_dict: Dict = {TT_COMP_EQ: "==", TT_COMP_NE: "!=", TT_COMP_GT: ">", TT_COMP_LT: "<", TT_COMP_GEQ: ">=", TT_COMP_LEQ: "<=", TT_COMP_AND: "&&", TT_COMP_OR: "||"}
        if comparison_op_token.type not in comparison_op_dict.keys():
            list_comp: str = ", ".join([f"'{c}'" for c in comparison_op_dict.values()])
            raise InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"expected one of: " + list_comp)
        self.advance()
        right_node: ASTNode = self.expr()

        return ComparisonNode(left_node, ComparisonOperatorNode(comparison_op_token), right_node)

    def no_identifier_factor(self) -> Any:
        """
        <no_identifier_factor> ::=  <num_int> | <num_float>
                                    | ("+" | "-" | <logical_operator>) <no_identifier_factor>
                                    | "(" <no_identifier_expr> ")"

        <logical_operator> ::= "&" | "|" | "^" | "<<" | ">>" | "~"
        """
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS, TT_BIN_OR, TT_BIN_AND, TT_BIN_NOT, TT_BIN_XOR, TT_BIN_LSHIFT, TT_BIN_RSHIFT]:
            self.advance()
            return UnaryOpNode(MathOperatorNode(token), self.no_identifier_factor())
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
        return self.binary_op(self.no_identifier_term, [TT_PLUS, TT_MINUS, TT_BIN_OR, TT_BIN_AND, TT_BIN_NOT, TT_BIN_XOR, TT_BIN_LSHIFT, TT_BIN_RSHIFT])

    def no_identifier_term(self) -> Any:
        return self.binary_op(self.no_identifier_factor, [TT_MULT, TT_DIV])

    def factor(self) -> Any:
        """
        <factor> ::= <num_int> | <num_float>
                    | ("+" | "-" | <logical_operator>) <factor>
                    | "(" <expr> ")"
                    | <identifier> ("." <identifier>)*

        <logical_operator> ::= "&" | "|" | "^" | "<<" | ">>" | "~"
        """
        token: Token = self.current_token

        if token.type in [TT_PLUS, TT_MINUS, TT_BIN_OR, TT_BIN_AND, TT_BIN_NOT, TT_BIN_XOR, TT_BIN_LSHIFT, TT_BIN_RSHIFT]:
            self.advance()
            return UnaryOpNode(MathOperatorNode(token), self.factor())
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
        return self.binary_op(self.term, [TT_PLUS, TT_MINUS, TT_BIN_OR, TT_BIN_AND, TT_BIN_NOT, TT_BIN_XOR, TT_BIN_LSHIFT, TT_BIN_RSHIFT])

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

            left_token = BinOpNode(left_token, MathOperatorNode(op_token), right_token)
        return left_token
