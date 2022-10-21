#!/usr/bin/env python3
from transpiler import *
from ast_nodes import *

class Python_Class(ParseedOutputGenerator):
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

    def add_struct(self, struct, cb):
        cb.add_line(f"class {struct.name}:")
        cb = cb.add_block()

        # __init__
        cb.add_line("def __init__(self, buf):")
        cb = cb.add_block()

        cb.add_line("cursor = 0")
        for member in struct.members:
            if isinstance(member, MatchNode):
                if member.member_name is not None:  # this match is used to select the type of a member
                    cb.add_line(f"self.{member.member_name} = None")

                    for index, case in enumerate(member.cases.keys()):
                        if index == 0:
                            cb.add_line(f"if {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        else:
                            cb.add_line(f"elif {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        cb = cb.add_block()
                        cb.add_line(f"self.{member.member_name} = {self.member_read_struct(member.cases[case].as_data_type(), member.cases[case].endian)}")
                        cb = cb.end_block()
                else:  # multiple members declared
                    for index, case in enumerate(member.cases.keys()):
                        if index == 0:
                            cb.add_line(f"if {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        else:
                            cb.add_line(f"elif {self.expression_as_str(member.condition)} == {self.expression_as_str(case)}:")
                        cb = cb.add_block()
                        for member_match in member.cases[case]:
                            cb.add_line(f"self.{member_match.name} = {self.member_read_struct(member_match.infos.as_data_type(), member_match.infos.endian)}")
                        cb = cb.end_block()
            else:
                if isinstance(member.infos.type, TernaryDataTypeNode):
                    # TODO
                    continue
                datatype: DataType = member.infos.as_data_type()
                if member.infos.is_list:
                    if member.infos.list_length is None:
                        cb.add_line(f"self.{member.name} = []")
                        # TODO
                    else:
                        cb.add_line(f"self.{member.name} = []")
                        cb.add_line(f"for i in range({self.expression_as_str(member.infos.list_length)}):")
                        cb = cb.add_block()
                        cb.add_line(f"self.{member.name}.append(" + self.member_read_struct(datatype, member.infos.endian) + ")")
                        cb.add_line(f"cursor += {datatype.size}")
                        cb = cb.end_block()
                else:
                    if datatype.is_string():
                        cb.add_line(f"self.{member.name} = b\"\"")
                        cb.add_line(f"self.{member.name} = b\"\"")
                        cb.add_line(f"while buf[cursor:cursor+len(b\"{datatype.string_delimiter}\")] != b\"{datatype.string_delimiter}\":")
                        cb = cb.add_block()
                        cb.add_line(f"self.{member.name} += buf[cursor:cursor+len(b\"{datatype.string_delimiter}\")]")
                        cb.add_line(f"cursor += len(b\"{datatype.string_delimiter}\")")

                        cb = cb.end_block()
                        cb.add_line(f"self.{member.name} = self.{member.name}.decode(\"utf-8\")")
                    else:
                        cb.add_line(f"self.{member.name} = {self.member_read_struct(datatype, member.infos.endian)}")
                        cb.add_line(f"cursor += {datatype.size}")
        cb = cb.end_block()

    def member_read_struct(self, datatype: DataType, endian: Endian):
        res = "struct.unpack(\""
        res += "<" if endian == Endian.LITTLE else ">"

        c = ""
        if datatype.is_float():
            c = "f"
        elif datatype.is_double():
            c = "d"
        elif datatype.size == 1:
            c = "b"
        elif datatype.size == 2:
            c = "h"
        elif datatype.size == 3:
            c = "h"
        elif datatype.size == 4:
            c = "i"
        elif datatype.size == 5:
            c = "i"
        elif datatype.size == 6:
            c = "i"
        elif datatype.size == 8:
            c = "q"
        elif datatype.size == 16:
            c = "q"

        if not datatype.signed and not datatype.is_float() and not datatype.is_double():
            c = c.upper()
        res += c

        res += f"\", buf[cursor:cursor+{datatype.size}])[0]"
        return res

    def expression_as_str(self, node):
        res = ""
        if type(node) in (FloatNumberNode, IntNumberNode):
            res += str(node.value)
        elif isinstance(node, IdentifierAccessNode):
            res += node.name
        elif isinstance(node, UnaryOpNode):
            res += node.op
            if type(node.value) in (FloatNumberNode, IntNumberNode):
                res += str(node.value.value)
            elif isinstance(node, IdentifierAccessNode):
                res += node.value.name
            else:
                res += self.expression_as_str(node.value)
        elif isinstance(node, BinOpNode):
            if type(node.left_node) in (FloatNumberNode, IntNumberNode):
                res += str(node.left_node.value)
            elif isinstance(node.left_node, IdentifierAccessNode):
                res += node.left_node.name
            else:
                res += self.expression_as_str(node.left_node)

            res += node.op

            if type(node.right_node) in (FloatNumberNode, IntNumberNode):
                res += str(node.right_node.value)
            elif isinstance(node.right_node, IdentifierAccessNode):
                res += node.right_node.name
            else:
                res += self.expression_as_str(node.right_node)
        return res

    def generate_str(self, struct, cb):
        cb.add_line("def __str__(self):")
        cb = cb.add_block()
        cb.add_line(f"res = \"{struct.name}(\\n\"")
        for member in struct.members:
            if isinstance(member, MatchNode):
                if member.member_name is not None:
                    cb.add_line(f"if isinstance(self.{member.member_name}, list):")
                    cb = cb.add_block()
                    cb.add_line(f"res += \"\\t{member.member_name} = \" + \", \".join([str(m) for m in self.{member.member_name}]) + \"\\n\"")
                    cb = cb.end_block()
                    cb.add_line(f"else:")
                    cb = cb.add_block()
                    cb.add_line(f"res += \"\\t{member.member_name} = \" + str(self.{member.member_name}) + \"\\n\"")
                    cb = cb.end_block()
                else:
                    for case in member.cases.keys():
                        for member_match in member.cases[case]:
                            cb.add_line(f"if hasattr(self, \"{member_match.name}\"):")
                            cb = cb.add_block()
                            cb.add_line(f"res += \"\\t{member_match.name} = \" + self.{member_match.name}")
                            cb = cb.end_block()
                        cb = cb.end_block()
            else:
                datatype: DataType = member.infos.as_data_type()
                if isinstance(member.infos.type, TernaryDataTypeNode):
                    # TODO
                    continue
                if datatype.is_string():
                    cb.add_line(f"res += \"\\t{member.name} = \" + self.{member.name} + \"\\n\"")
                elif member.infos.is_list:
                    cb.add_line(f"res += \"\\t{member.name} = \" + \", \".join([str(m) for m in self.{member.name}]) + \"\\n\"")
                else:
                    cb.add_line(f"res += \"\\t{member.name} = \" + str(self.{member.name}) + \"\\n\"")

        cb.add_line("res += \")\"")
        cb.add_line("return res")
