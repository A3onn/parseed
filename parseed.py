#!/usr/bin/env python3
from lexer import *
from parser import *

def main():
    while True:
        # lexer
        lexer = Lexer(input("shell > "), "<stdin>")
        tokens, error = lexer.run()
        print("LEXER OUTPUT:")
        if error:
            print(error)
        else:
            print(tokens)

        # parser
        parser = Parser(tokens)
        print(parser.run())

if __name__ == "__main__":
    main()