#!/usr/bin/env python3
from transpiler import *
from ast_nodes import *

class Python_Class(ParseedOutputGenerator):
    def generate(self, writer: Writer):
        writer.add_block().add_line("TODO")