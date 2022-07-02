#!/usr/bin/env python3
from transpiler import *

class Python_Class(ParseedOutputGenerator):
    def generate(self) -> str:
        datatype_struct_mapping = {
            "uint8": "B",
            "int8": "b",
            "uint16": "H",
            "int16": "h",
            "uint32": "B",
            "int32": "b",
        }

        res = ""
        for struct in self.structs:
            res += "import struct\n"
            res += f"class {struct.name}:\n"
            for index, member in enumerate(struct.members):
                res += f"\t{member.name} = None\n\n"
            res += f"\tdef __init__(self, buf):\n"
            res += f"\t\ttmp = struct.unpack('"
            for member in struct.members:
                res += datatype_struct_mapping[member.type]
            res += "')\n"

            for index, member in enumerate(struct.members):
                res += f"\t\tself.{member.name} = res[{index}]\n"

        return res