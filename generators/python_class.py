#!/usr/bin/env python3
from transpiler import *

class Python_Class(ParseedOutputGenerator):
    def generate(self) -> str:
        print(self.structs)
        return ""