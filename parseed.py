#!/usr/bin/env python3
from lexer import *
from parser import *

def main():
    while True:
        # lexer
        lexer = Lexer(input("shell > "), "<stdin>")
        tokens, error = lexer.run()

        # parser
        parser = Parser(tokens)
        print(parser.run())

if __name__ == "__main__":
    main()