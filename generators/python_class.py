#!/usr/bin/env python3
from transpiler import *

class Python_Class(ParseedOutputGenerator):
    def generate(self, writer):

        for struct in self.structs:
            current_block = writer.add_block()

            current_block.add_line("import struct")
            current_block.add_empty_line()
            current_block.add_line(f"class {struct.name}:")

            current_block = current_block.add_block()
            current_block.add_line(f"def __init__(self, buf):")

            current_block = current_block.add_block()
            current_block.add_line("curr_index = 0")
            for member in struct.members:
                if member.is_list():
                    current_block.add_line(f"self.{member.name} = []")
                    current_block.add_line(f"for i in range(0, {member.list_length}):")
                    current_block = current_block.add_block()
                    current_block.add_line(f"self.{member.name}.append(struct.unpack_from(\"{self.get_data_type_as_struct_format(member)}\", buf, curr_index)[0])")
                    current_block.add_line(f"curr_index += {DataType(member.type).size}")
                    current_block = current_block.end_block()
                else:
                    current_block.add_line(f"self.{member.name} = struct.unpack_from(\"{self.get_data_type_as_struct_format(member)}\", buf, curr_index)[0]")
                    current_block.add_line(f"curr_index += {DataType(member.type).size}")
            current_block = current_block.end_block()
            current_block.add_empty_line()

            # generate __str__ function
            current_block.add_line("def __str__(self):")
            current_block = current_block.add_block()

            current_block.add_line(f"res = \"{struct.name}(\" + \\")
            current_block = current_block.add_block() # just to have a better indentation
            for member in struct.members:
                current_block.add_line(f"\"{member.name} = \" + str(self.{member.name}) + \"\\n\" \\")
            current_block = current_block.end_block()
            current_block.add_line(f"\")\"")
            current_block.add_line(f"return res")

    def get_data_type_as_struct_format(self, member):
        # see: https://docs.python.org/3/library/struct.html#format-characters
        dt = DataType(member.type)
        if dt.is_byte():
            return "c"
        elif dt.is_string():
            raise NotImplementedError("String is not yet implemented in Python_Class.")
        elif dt.is_float():
            return "f"
        elif dt.is_double():
            return "d"
        else:
            res = ""
            if dt.size == 1:
                res += "b"
            elif dt.size == 2:
                res += "h"
            elif dt.size == 3:
                raise NotImplementedError("String is not yet implemented in Python_Class.")
            elif dt.size == 4:
                res += "i"
            elif dt.size == 5:
                raise NotImplementedError("String is not yet implemented in Python_Class.")
            elif dt.size == 6:
                raise NotImplementedError("String is not yet implemented in Python_Class.")
            elif dt.size == 8:
                res += "q"
            elif dt.size == 16:
                raise NotImplementedError("String is not yet implemented in Python_Class.")

            if not dt.signed:
                res = res.upper()
            return res