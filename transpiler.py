#!/usr/bin/env python3
from typing import Any, List
from abc import ABC, abstractmethod
from parser import *


class ParseedOutputGenerator(ABC):
    def __init__(self, ast: List[Any]):
        self.structs: List[StructDefNode] = []
        self.bitfields: List[BitfieldDefNode] = []
        self._init_intermediate_ast(ast)

    @abstractmethod
    def generate(self) -> str:
        pass

    def _init_intermediate_ast(self, ast: List[Any]):
        for node in ast:
            if isinstance(node, StructDefNode):
                self.structs.append(node)
            elif isinstance(node, BitfieldDefNode):
                self.bitfields.append(node)
