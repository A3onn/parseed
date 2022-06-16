#!/usr/bin/env python3
from utils import *

class ParseedError:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def __str__(self):
        return f"On line {self.pos_start.ln + 1}: {self.error_name}: {self.details}"

class IllegalCharacterError(ParseedError):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "IllegalCharacterError", details)