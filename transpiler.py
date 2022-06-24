#!/usr/bin/env python3
from typing import Any, Generator, List
from abc import ABC, abstractmethod
from parser import StructDefNode, BitfieldDefNode


class ParseedOutputGenerator(ABC):
    def __init__(self, ast: List[Any]):
        self.ast: List[Any] = ast

    @abstractmethod
    def generate(self) -> str:
        pass

    def getStructs(self) -> Generator[StructDefNode, None, None]:
        for node in self.ast:
            if isinstance(node, StructDefNode):
                yield node

    def getBitfields(self) -> Generator[BitfieldDefNode, None, None]:
        for node in self.ast:
            if isinstance(node, BitfieldDefNode):
                yield node
