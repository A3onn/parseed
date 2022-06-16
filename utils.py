#!/usr/bin/env python3

class Position:
    def __init__(self, idx, ln, col, filename, file_text):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.filename = filename
        self.file_text = file_text
    
    def advance(self, current_char):
        self.idx +=1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
    
    def get_copy(self):
        return Position(self.idx, self.ln, self.col, self.filename, self.file_text)