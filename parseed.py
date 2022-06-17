#!/usr/bin/env python3
from lexer import *
from parser import *
import argparse

def main():
    argparser = argparse.ArgumentParser(description="A simple language simplifying the creation of parsers.")
    argparser.add_argument("file", help="File to parse", nargs="?", default="")
    argparser.add_argument("-L", "--lexer", action="store_true", help="Print the lexer's list of tokens", dest="show_lexer")
    argparser.add_argument("-A", "--ast", action="store_true", help="Print the abstract syntax tree", dest="show_ast")

    arguments = argparser.parse_args()

    if arguments.file == "":
        while True:
            try:
                lexer = Lexer(input("parseed > "), "<stdin>")
            except EOFError:
                print("Quitting...")
                break
            except KeyboardInterrupt:
                print("Quitting...")
                break
            run(lexer, arguments)
    else:
        with open(arguments.file, "r") as f:
            lexer = Lexer(f.read(), arguments.file)
            run(lexer, arguments)

def run(lexer, arguments):
    tokens, error = lexer.run()
    if arguments.show_lexer:
        print("[i] LEXER OUTPUT: ", end="")
        if error:
            print(error)
        else:
            print(tokens)

    if error:
        print(error)
        return 

    parser = Parser(tokens)
    ast = parser.run()
    if arguments.show_ast:
        print("[i] AST:", ast)

if __name__ == "__main__":
    main()