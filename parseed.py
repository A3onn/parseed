#!/usr/bin/env python3
from lexer import Lexer, Token
from parser import Parser
from transpiler import ParseedOutputGenerator, Writer
from generators import *
from errors import ParseedBaseError
from typing import List
import argparse


def main():
    argparser = argparse.ArgumentParser(description="A simple language simplifying the creation of parsers.")
    argparser.add_argument("file", help="File to parse", nargs="?", default="")
    argparser.add_argument("-L", "--lexer", action="store_true", help="Print the lexer's list of tokens", dest="show_lexer")
    argparser.add_argument("-A", "--ast", action="store_true", help="Print the abstract syntax tree", dest="show_ast")
    argparser.add_argument("-g", "--generator", help="The generator to use", dest="generator",
                            choices=[c.__name__ for c in ParseedOutputGenerator.__subclasses__()], default=ParseedOutputGenerator.__subclasses__()[0].__name__)

    arguments = argparser.parse_args()

    # reference of the generator's class
    generator_class = next(filter(lambda cls: cls.__name__ == arguments.generator, ParseedOutputGenerator.__subclasses__()))

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
            run(lexer, arguments, generator_class)
    else:
        with open(arguments.file, "r") as f:
            lexer = Lexer(f.read(), arguments.file)
            run(lexer, arguments, generator_class)


def run(lexer, arguments, generator_class):
    try:
        tokens = lexer.run()
    except ParseedBaseError as e:
        print(e)  # just print the error
        return

    if arguments.show_lexer:
        print("[i] LEXER OUTPUT:\n", lexer_pprint(tokens), sep="")

    parser = Parser(tokens)
    try:
        ast = parser.run()
    except ParseedBaseError as e:
        print(e)  # just print the error
        return
    if arguments.show_ast:
        print("[i] AST:\n", AST_pprint(ast), sep="")

    writer: Writer = Writer()
    try:
        generator_class(ast).generate(writer)
    except ParseedBaseError as e:
        print(e)  # just print the error
        return

    print(writer.generate_code())


def AST_pprint(ast: List) -> str:
    if ast is None:
        return "<Empty>"
    return "\n".join([node.to_str() for node in ast])


def lexer_pprint(tokens: List[Token]):
    if tokens is None:
        return "<Empty>"

    last_token: Token = tokens[0]
    res: str = f"({last_token.type}:{last_token.value} "
    for token in tokens[1:]:
        if last_token.pos_start.ln != token.pos_start.ln:
            res += "\n" + (" " * token.pos_start.col)

        if token.value is not None:
            res += f"({token.type}:{token.value}) "
        else:
            res += f"{token.type} "
        last_token = token
    return res


if __name__ == "__main__":
    main()
