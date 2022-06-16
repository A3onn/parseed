#!/usr/bin/env python3
from lexer import *

def main():
    while True:
        lexer = Lexer(input("shell > "), "<stdin>")
        tokens, error = lexer.run()
        print(tokens, error)

if __name__ == "__main__":
    main()