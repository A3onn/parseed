#!/usr/bin/env python3
from transpiler import *
from ast_nodes import *
from math import ceil

class Python_Class(ParseedOutputGenerator):

    PYGMENT_HIGHLIGHTER = "Python"

    def generate(self, writer: Writer):
        cb = writer.add_block()
        cb.add_line("#!/usr/bin/env python3")
        cb.add_line("import struct")
        cb.add_empty_line()
        for struct in self.structs:
            self.add_struct(struct, cb)
            cb.add_empty_line()
            self.generate_str(struct, cb.add_block())
            cb.add_empty_line()
        
        for bitfield in self.bitfields:
            # TODO
            pass

    def add_struct(self, struct: StructDefNode, cb: CodeBlock):
        cb.add_line(f"class {struct.name}:")
        cb = cb.add_block()

        # __init__
        cb.add_line("def __init__(self, buf):")
        cb = cb.add_block()

        cb.add_line("self.cursor = 0")  # will be used when a member's type is another struct defined in the source-file
        for member in struct.members:
            if isinstance(member, MatchNode):
                if member.member_name is not None:  # this match-node is used to select the type of a member
                    cb.add_line(f"self.{member.member_name} = None")

                    for index, case in enumerate(member.cases.keys()):
                        if index == 0:
                            cb.add_line(f"if {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        else:
                            cb.add_line(f"elif {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        cb = cb.add_block()
                        cb.add_line(f"self.{member.member_name} = {self.member_read_struct(member.cases[case], member.cases[case].endian)}")
                        cb = cb.end_block()
                else:  # multiple members declared
                    for index, case in enumerate(member.cases.keys()):
                        if index == 0:
                            cb.add_line(f"if {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        else:
                            cb.add_line(f"elif {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        cb = cb.add_block()
                        for member_match in member.cases[case]:
                            if self.is_member_match_type_struct(member_match.infos.type):
                                cb.add_line(f"self.{member_match.name} = {member_match.name}(buf[self.cursor:])") # pass the buffer to the class representing the type
                                cb.add_line(f"self.cursor += self.{member_match.name}.cursor") # continue to parse the buffer after the called class has parsed
                            else:
                                cb.add_line(f"self.{member_match.name} = {self.member_read_struct(member_match.name, member_match.infos.endian)}")
                        cb = cb.end_block()
            else: # simple member
                if isinstance(member.infos.type, TernaryDataTypeNode):
                    tdtn: TernaryDataTypeNode = member.infos.type
                    cb.add_line(f"if {self.comparison_as_str(tdtn.comparison)}:")
                    cb = cb.add_block()
                    if isinstance(tdtn.if_true, IdentifierAccessNode):
                        cb.add_line(f"self.{member.name} = {tdtn.if_true.name}(buf[self.cursor:])") # pass the buffer to the class representing the type
                        cb.add_line(f"self.cursor += self.{member.name}.cursor") # continue to parse the buffer after the called class has parsed
                    else:
                        cb.add_line(f"self.{member.name} = {self.member_read_struct(tdtn.if_true, member.infos.endian)}")
                    cb = cb.end_block()
                    cb.add_line(f"else:")
                    cb = cb.add_block()
                    if isinstance(tdtn.if_false, IdentifierAccessNode):
                        cb.add_line(f"self.{member.name} = {tdtn.if_false.name}(buf[self.cursor:])")
                        cb.add_line(f"self.cursor += self.{member.name}.cursor") # continue to parse the buffer after the called class has parsed
                    else:
                        cb.add_line(f"self.{member.name} = {self.member_read_struct(tdtn.if_false, member.infos.endian)}")
                    cb = cb.end_block()
                    continue

                if member.infos.is_list:
                    if member.infos.list_length is None: # no length given
                        cb.add_line(f"self.{member.name} = []")
                        # TODO: calculate remaining length of buffer
                    else:
                        cb.add_line(f"self.{member.name} = []")
                        cb.add_line(f"for i in range({self.expression_as_str(member.infos.list_length)}):")
                        cb = cb.add_block()
                        if self.is_member_type_struct(member.infos.type):
                            cb.add_line(f"{member.infos.type}_tmp = {member.infos.type}(buf[self.cursor:])")
                            cb.add_line(f"self.{member.name}.append({member.infos.type}_tmp)")
                            cb.add_line(f"self.cursor += {member.infos.type}_tmp.cursor") # continue to parse the buffer after the called class has parsed
                        else:
                            cb.add_line(f"self.{member.name}.append(" + self.member_read_struct(member.infos, member.infos.endian) + ")")
                            cb.add_line(f"self.cursor += {member.infos.size}")
                        cb = cb.end_block()
                else:
                    if member.infos.is_string() or member.infos.is_bytes():
                        cb.add_line(f"self.{member.name} = b\"\"")
                        if isinstance(member.infos.delimiter, IdentifierAccessNode):
                            cb.add_line(f"while buf[self.cursor:self.cursor+{member.infos.delimiter.name})] != {member.infos.delimiter.name}:")
                            cb = cb.add_block()
                            cb.add_line(f"self.{member.name} += buf[self.cursor:self.cursor+len(b\"{member.infos.delimiter}\")]")
                            cb.add_line(f"self.cursor += len(b\"{member.infos.delimiter}\")")
                            cb = cb.end_block()
                        elif isinstance(member.infos.delimiter, IntNumberNode):
                            bytes_length: int = ceil(member.infos.delimiter.value.bit_length() / 8)
                            cb.add_line(f'while int.from_bytes(buf[self.cursor:self.cursor+{bytes_length}], byteorder="big", signed=False) != {member.infos.delimiter.value}:')
                            cb = cb.add_block()
                            cb.add_line(f"self.{member.name} += buf[self.cursor:self.cursor+{bytes_length}]")
                            cb.add_line(f"self.cursor += {bytes_length}")
                            cb = cb.end_block()
                        else: # delimiter is either a StringNode or a CharNode
                            cb.add_line(f"while buf[self.cursor:self.cursor+len(b\"{member.infos.delimiter.value}\")] != b\"{member.infos.delimiter.value}\":")
                            cb = cb.add_block()
                            cb.add_line(f"self.{member.name} += buf[self.cursor:self.cursor+len(b\"{member.infos.delimiter.value}\")]")
                            cb.add_line(f"self.cursor += len(b\"{member.infos.delimiter.value}\")")
                            cb = cb.end_block()
                        if member.infos.is_string():
                            cb.add_line(f"self.{member.name} = self.{member.name}.decode(\"utf-8\")")
                    elif self.is_member_type_struct(member.infos.type):
                        cb.add_line(f"self.{member.name} = {member.infos.type}(buf[self.cursor:])")
                        cb.add_line(f"self.cursor += self.{member.name}.cursor") # continue to parse the buffer after the called class has parsed
                    else:
                        cb.add_line(f"self.{member.name} = {self.member_read_struct(member.infos, member.infos.endian)}")
                        cb.add_line(f"self.cursor += {member.infos.size}")
        cb = cb.end_block()

    def member_read_struct(self, infos: StructMemberInfoNode, endian: Union[Endian, TernaryEndianNode]) -> str:
        if isinstance(endian, TernaryEndianNode):
            return f"({self.member_read_struct(infos, endian.if_true)} if {self.comparison_as_str(endian.comparison)} else {self.member_read_struct(infos, endian.if_false)})"


        if infos.is_float():
            res = "struct.unpack('<f'" if endian == Endian.LITTLE else "struct.unpack('>f'"
            res += f", buf[self.cursor:self.cursor+{infos.size}])[0]"
            return res
        elif infos.is_double():
            res = "struct.unpack('<d'" if endian == Endian.LITTLE else "struct.unpack('>d'"
            res += f", buf[self.cursor:self.cursor+{infos.size}])[0]"
            return res

        return f"int.from_bytes(buf[self.cursor:self.cursor+{infos.size}], byteorder='{'big' if infos.endian == Endian.BIG else 'little'}', signed={infos.signed})"

    def expression_as_str(self, node: Union[FloatNumberNode, IntNumberNode, BinOpNode, UnaryOpNode, IdentifierAccessNode]):
        res = ""
        if type(node) in (FloatNumberNode, IntNumberNode):
            res = str(node.value)
        elif isinstance(node, IdentifierAccessNode):
            res = "self." + node.name
        elif isinstance(node, UnaryOpNode):
            res = node.op
            if type(node.value) in (FloatNumberNode, IntNumberNode):
                res += str(node.value.value)
            elif isinstance(node, IdentifierAccessNode):
                res += node.value.name
            else:
                res += self.expression_as_str(node.value)
        elif isinstance(node, BinOpNode):
            if type(node.left_node) in (FloatNumberNode, IntNumberNode):
                res = str(node.left_node.value)
            elif isinstance(node.left_node, IdentifierAccessNode):
                res = node.left_node.name
            else:
                res = self.expression_as_str(node.left_node)

            res += node.op

            if type(node.right_node) in (FloatNumberNode, IntNumberNode):
                res += str(node.right_node.value)
            elif isinstance(node.right_node, IdentifierAccessNode):
                res += node.right_node.name
            else:
                res += self.expression_as_str(node.right_node)
        return res


    def comparison_as_str(self, comp: ComparisonNode) -> str:
        res: str = ""

        if isinstance(comp.left_node, ComparisonNode):
            res += "(" + self.comparison_as_str(comp.left_node) + ")"
        else:
            res += self.expression_as_str(comp.left_node)
        
        res += " " + self.comparison_op_as_str(comp.comparison_op) + " "

        if isinstance(comp.right_node, ComparisonNode):
            res += "(" + self.comparison_as_str(comp.right_node) + ")"
        else:
            res += self.expression_as_str(comp.right_node)

        return res


    def comparison_op_as_str(self, op: ComparisonOperatorNode):
        if op == ComparisonOperatorNode.AND:
            return "and"
        elif op == ComparisonOperatorNode.EQUAL:
            return "=="
        elif op == ComparisonOperatorNode.GREATER_OR_EQUAL:
            return ">="
        elif op == ComparisonOperatorNode.GREATER_THAN:
            return ">"
        elif op == ComparisonOperatorNode.LESS_OR_EQUAL:
            return "<="
        elif op == ComparisonOperatorNode.LESS_THAN:
            return "<"
        elif op == ComparisonOperatorNode.NOT_EQUAL:
            return "!="
        elif op == ComparisonOperatorNode.OR:
            return "or"

    def generate_str(self, struct: StructDefNode, cb: CodeBlock):
        cb.add_line("def _custom_str(self, depth=0):")
        cb = cb.add_block()
        cb.add_line(f'res = "{struct.name}(\\n"')

        cb.add_line(f'depth += 1') # increase depth here to have attributes indented and not the struct's name

        for member in struct.members:
            if isinstance(member, MatchNode):
                if member.member_name is not None: # match statement to choose the type of the identifier
                    cb.add_line(f"if isinstance(self.{member.member_name}, list):")
                    cb = cb.add_block()
                    cb.add_line(f'res += ("\\t"*depth) + "{member.member_name} = " + "\\n".join([m.custom_str(depth+1) for m in self.{member.member_name}._custom_str(depth+1)]) + "\\n"')
                    cb = cb.end_block()
                    cb.add_line(f"else:")
                    cb = cb.add_block()
                    cb.add_line(f'res += ("\\t"*depth) + "{member.member_name} = " + self.{member.member_name}._custom_str(depth+1) + "\\n"')
                    cb = cb.end_block()
                else:
                    for case in member.cases.keys():
                        for member_match in member.cases[case]:
                            cb.add_line(f'if hasattr(self, "{member_match.name}"):')
                            cb = cb.add_block()
                            cb.add_line(f'res += ("\\t"*depth) + "{member_match.name} = " + self.{member_match.name}')
                            cb = cb.end_block()
                        cb = cb.end_block()
            else:
                if isinstance(member.infos.type, TernaryDataTypeNode):
                    cb.add_line(f'res += ("\\t"*depth) + "{member.name} = " + self.{member.name}._custom_str(depth+1) + "\\n"')
                elif member.infos.is_string():
                    cb.add_line(f'res += ("\\t"*depth) + "{member.name} = " + self.{member.name} + "\\n"')
                else:
                    if member.infos.is_basic_type():
                        cb.add_line(f'res += ("\\t"*depth) + "{member.name} = " + str(self.{member.name}) + "\\n"')
                    else:
                        cb.add_line(f'res += ("\\t"*depth) + "{member.name} = " + self.{member.name}._custom_str(depth+1) + "\\n"')

        cb.add_line('res += ("\\t"*(depth-1)) + ")"')
        cb.add_line("return res")

        cb = cb.end_block()
        cb.add_empty_line()
        cb.add_line("def __str__(self):")
        cb = cb.add_block()
        cb.add_line("return self._custom_str()")
        cb = cb.end_block()
